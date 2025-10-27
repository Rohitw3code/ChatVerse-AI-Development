"""
Google Docs/Drive API Module
Handles Google Docs & Drive operations for creating and updating documents.
"""

import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from supabase_client import supabase

# Resolve gdoc.json from repo root
_GDOC_JSON_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "gdoc.json",
)

with open(_GDOC_JSON_PATH, "r") as f:
    _gdoc_config = json.load(f)
    _google_client_id = _gdoc_config["web"]["client_id"]
    _google_client_secret = _gdoc_config["web"]["client_secret"]


async def _get_creds(user_id: str):
    account_query = (
        supabase.table("connected_accounts")
        .select("*")
        .eq("provider_id", user_id)
        .eq("platform", "docs")
        .execute()
    )

    if not account_query.data:
        raise Exception("Google Docs account not connected for this user.")

    account_data = account_query.data[0]

    creds_info = {
        "token": account_data.get("access_token"),
        "refresh_token": account_data.get("refresh_token"),
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": _google_client_id,
        "client_secret": _google_client_secret,
        "scopes": account_data.get("scopes"),
    }
    return Credentials.from_authorized_user_info(creds_info)


async def get_drive_service(user_id: str):
    creds = await _get_creds(user_id)
    return build("drive", "v3", credentials=creds)


async def get_docs_service(user_id: str):
    creds = await _get_creds(user_id)
    return build("docs", "v1", credentials=creds)


async def create_document(user_id: str, title: str, content: str | None = None) -> dict:
    # try:
    drive = await get_drive_service(user_id)
    # Create a Google Doc via Drive API
    file_metadata = {
        "name": title,
        "mimeType": "application/vnd.google-apps.document",
    }
    created = (
        drive.files()
        .create(body=file_metadata, fields="id, webViewLink")
        .execute()
    )
    doc_id = created.get("id")

    # Optionally insert content using Docs API
    if content:
        docs = await get_docs_service(user_id)
        # Insert at the start index 1 (after document start)
        docs.documents().batchUpdate(
            documentId=doc_id,
            body={
                "requests": [
                    {
                        "insertText": {
                            "location": {"index": 1},
                            "text": content,
                        }
                    }
                ]
            },
        ).execute()

    # Ensure we have a webViewLink
    details = (
        drive.files().get(fileId=doc_id, fields="id, webViewLink").execute()
    )
    return {
        "document_id": doc_id,
        "url": details.get("webViewLink"),
        "title": title,
    }
    # except Exception as e:
    #     return {"error": f"Failed to create document: {str(e)}"}


async def append_text(user_id: str, document_id: str, text: str) -> dict:
    try:
        docs = await get_docs_service(user_id)
        # Get current end index
        doc = docs.documents().get(documentId=document_id).execute()
        end_index = (
            doc.get("body", {}).get("content", [{}])[-1].get("endIndex", 1)
        )
        insert_index = max(1, int(end_index) - 1)

        docs.documents().batchUpdate(
            documentId=document_id,
            body={
                "requests": [
                    {
                        "insertText": {
                            "location": {"index": insert_index},
                            "text": text,
                        }
                    }
                ]
            },
        ).execute()

        # Get URL from Drive
        drive = await get_drive_service(user_id)
        details = (
            drive.files()
            .get(fileId=document_id, fields="id, webViewLink")
            .execute()
        )
        return {
            "document_id": document_id,
            "url": details.get("webViewLink"),
            "appended": True,
        }
    except Exception as e:
        return {"error": f"Failed to append text: {str(e)}"}


async def insert_text(user_id: str, document_id: str, text: str, index: int) -> dict:
    try:
        docs = await get_docs_service(user_id)
        docs.documents().batchUpdate(
            documentId=document_id,
            body={
                "requests": [
                    {
                        "insertText": {
                            "location": {"index": index},
                            "text": text,
                        }
                    }
                ]
            },
        ).execute()
        
        drive = await get_drive_service(user_id)
        details = drive.files().get(fileId=document_id, fields="id, webViewLink").execute()
        return {
            "document_id": document_id,
            "url": details.get("webViewLink"),
            "inserted": True,
        }
    except Exception as e:
        return {"error": f"Failed to insert text: {str(e)}"}


async def format_text(user_id: str, document_id: str, start_index: int, end_index: int, 
                     bold=None, italic=None, underline=None, font_size=None, font_family=None,
                     text_color_red=None, text_color_green=None, text_color_blue=None,
                     heading_level=None, alignment=None) -> dict:
    """
    Applies all text styling to a range using native Google Docs API.
    Supports: bold, italic, underline, font size/family, color, heading, alignment.
    All formatting is applied natively - NOT markdown.
    """
    try:
        docs = await get_docs_service(user_id)
        requests = []
        
        # Text style formatting (bold, italic, underline, font)
        text_style = {}
        if bold is not None:
            text_style["bold"] = bold
        if italic is not None:
            text_style["italic"] = italic
        if underline is not None:
            text_style["underline"] = underline
        if font_size is not None:
            text_style["fontSize"] = {"magnitude": font_size, "unit": "PT"}
        if font_family is not None:
            text_style["weightedFontFamily"] = {"fontFamily": font_family}
        
        # Text color
        if text_color_red is not None and text_color_green is not None and text_color_blue is not None:
            text_style["foregroundColor"] = {
                "color": {
                    "rgbColor": {
                        "red": text_color_red, 
                        "green": text_color_green, 
                        "blue": text_color_blue
                    }
                }
            }
        
        # Apply text styles if any
        if text_style:
            fields = ",".join(text_style.keys())
            requests.append({
                "updateTextStyle": {
                    "range": {"startIndex": start_index, "endIndex": end_index},
                    "textStyle": text_style,
                    "fields": fields,
                }
            })
        
        # Heading style (paragraph-level)
        if heading_level is not None:
            style_map = {1: "TITLE", 2: "HEADING_1", 3: "HEADING_2", 4: "HEADING_3"}
            named_style = style_map.get(heading_level, "HEADING_1")
            requests.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": start_index, "endIndex": end_index},
                    "paragraphStyle": {"namedStyleType": named_style},
                    "fields": "namedStyleType",
                }
            })
        
        # Alignment (paragraph-level)
        if alignment is not None:
            requests.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": start_index, "endIndex": end_index},
                    "paragraphStyle": {"alignment": alignment},
                    "fields": "alignment",
                }
            })
        
        # Execute all requests in one batch
        if requests:
            docs.documents().batchUpdate(
                documentId=document_id,
                body={"requests": requests},
            ).execute()
        
        drive = await get_drive_service(user_id)
        details = drive.files().get(fileId=document_id, fields="id, webViewLink").execute()
        return {
            "document_id": document_id,
            "url": details.get("webViewLink"),
            "styled": True,
            "native_formatting": True,
        }
    except Exception as e:
        return {"error": f"Failed to apply styling: {str(e)}"}


async def color_text(user_id: str, document_id: str, start_index: int, end_index: int, 
                    red: float, green: float, blue: float) -> dict:
    try:
        docs = await get_docs_service(user_id)
        docs.documents().batchUpdate(
            documentId=document_id,
            body={
                "requests": [
                    {
                        "updateTextStyle": {
                            "range": {"startIndex": start_index, "endIndex": end_index},
                            "textStyle": {
                                "foregroundColor": {
                                    "color": {
                                        "rgbColor": {"red": red, "green": green, "blue": blue}
                                    }
                                }
                            },
                            "fields": "foregroundColor",
                        }
                    }
                ]
            },
        ).execute()
        
        drive = await get_drive_service(user_id)
        details = drive.files().get(fileId=document_id, fields="id, webViewLink").execute()
        return {
            "document_id": document_id,
            "url": details.get("webViewLink"),
            "colored": True,
        }
    except Exception as e:
        return {"error": f"Failed to color text: {str(e)}"}


async def apply_heading(user_id: str, document_id: str, start_index: int, end_index: int, heading_level: int) -> dict:
    try:
        docs = await get_docs_service(user_id)
        
        # Map heading level: 1=TITLE, 2=HEADING_1, 3=HEADING_2, 4=HEADING_3
        style_map = {1: "TITLE", 2: "HEADING_1", 3: "HEADING_2", 4: "HEADING_3"}
        named_style = style_map.get(heading_level, "HEADING_1")
        
        docs.documents().batchUpdate(
            documentId=document_id,
            body={
                "requests": [
                    {
                        "updateParagraphStyle": {
                            "range": {"startIndex": start_index, "endIndex": end_index},
                            "paragraphStyle": {"namedStyleType": named_style},
                            "fields": "namedStyleType",
                        }
                    }
                ]
            },
        ).execute()
        
        drive = await get_drive_service(user_id)
        details = drive.files().get(fileId=document_id, fields="id, webViewLink").execute()
        return {
            "document_id": document_id,
            "url": details.get("webViewLink"),
            "heading_applied": True,
        }
    except Exception as e:
        return {"error": f"Failed to apply heading: {str(e)}"}


async def read_document(user_id: str, document_id: str) -> dict:
    try:
        docs = await get_docs_service(user_id)
        doc = docs.documents().get(documentId=document_id).execute()
        
        title = doc.get("title", "Untitled")
        content = doc.get("body", {}).get("content", [])
        
        # Extract text content
        text_content = ""
        for element in content:
            if "paragraph" in element:
                paragraph = element.get("paragraph", {})
                for text_run in paragraph.get("elements", []):
                    if "textRun" in text_run:
                        text_content += text_run.get("textRun", {}).get("content", "")
        
        return {
            "document_id": document_id,
            "title": title,
            "content": text_content,
        }
    except Exception as e:
        return {"error": f"Failed to read document: {str(e)}"}


async def list_documents(user_id: str, max_results: int = 10) -> dict:
    try:
        drive = await get_drive_service(user_id)
        results = drive.files().list(
            q="mimeType='application/vnd.google-apps.document'",
            pageSize=max_results,
            fields="files(id, name, createdTime, modifiedTime, webViewLink)"
        ).execute()
        
        files = results.get("files", [])
        return {
            "documents": files,
            "count": len(files),
        }
    except Exception as e:
        return {"error": f"Failed to list documents: {str(e)}"}


async def delete_text(user_id: str, document_id: str, start_index: int, end_index: int) -> dict:
    try:
        docs = await get_docs_service(user_id)
        docs.documents().batchUpdate(
            documentId=document_id,
            body={
                "requests": [
                    {
                        "deleteContentRange": {
                            "range": {"startIndex": start_index, "endIndex": end_index}
                        }
                    }
                ]
            },
        ).execute()
        
        drive = await get_drive_service(user_id)
        details = drive.files().get(fileId=document_id, fields="id, webViewLink").execute()
        return {
            "document_id": document_id,
            "url": details.get("webViewLink"),
            "deleted": True,
        }
    except Exception as e:
        return {"error": f"Failed to delete text: {str(e)}"}


async def replace_text(user_id: str, document_id: str, find_text: str, replace_text: str, match_case: bool = False) -> dict:
    try:
        docs = await get_docs_service(user_id)
        docs.documents().batchUpdate(
            documentId=document_id,
            body={
                "requests": [
                    {
                        "replaceAllText": {
                            "containsText": {
                                "text": find_text,
                                "matchCase": match_case,
                            },
                            "replaceText": replace_text,
                        }
                    }
                ]
            },
        ).execute()
        
        drive = await get_drive_service(user_id)
        details = drive.files().get(fileId=document_id, fields="id, webViewLink").execute()
        return {
            "document_id": document_id,
            "url": details.get("webViewLink"),
            "replaced": True,
        }
    except Exception as e:
        return {"error": f"Failed to replace text: {str(e)}"}


async def apply_bullet_list(user_id: str, document_id: str, start_index: int, end_index: int) -> dict:
    try:
        docs = await get_docs_service(user_id)
        docs.documents().batchUpdate(
            documentId=document_id,
            body={
                "requests": [
                    {
                        "createParagraphBullets": {
                            "range": {"startIndex": start_index, "endIndex": end_index},
                            "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE",
                        }
                    }
                ]
            },
        ).execute()
        
        drive = await get_drive_service(user_id)
        details = drive.files().get(fileId=document_id, fields="id, webViewLink").execute()
        return {
            "document_id": document_id,
            "url": details.get("webViewLink"),
            "bullet_list_applied": True,
        }
    except Exception as e:
        return {"error": f"Failed to apply bullet list: {str(e)}"}


async def apply_numbered_list(user_id: str, document_id: str, start_index: int, end_index: int) -> dict:
    try:
        docs = await get_docs_service(user_id)
        docs.documents().batchUpdate(
            documentId=document_id,
            body={
                "requests": [
                    {
                        "createParagraphBullets": {
                            "range": {"startIndex": start_index, "endIndex": end_index},
                            "bulletPreset": "NUMBERED_DECIMAL_ALPHA_ROMAN",
                        }
                    }
                ]
            },
        ).execute()
        
        drive = await get_drive_service(user_id)
        details = drive.files().get(fileId=document_id, fields="id, webViewLink").execute()
        return {
            "document_id": document_id,
            "url": details.get("webViewLink"),
            "numbered_list_applied": True,
        }
    except Exception as e:
        return {"error": f"Failed to apply numbered list: {str(e)}"}


async def apply_alignment(user_id: str, document_id: str, start_index: int, end_index: int, alignment: str) -> dict:
    try:
        docs = await get_docs_service(user_id)
        docs.documents().batchUpdate(
            documentId=document_id,
            body={
                "requests": [
                    {
                        "updateParagraphStyle": {
                            "range": {"startIndex": start_index, "endIndex": end_index},
                            "paragraphStyle": {"alignment": alignment},
                            "fields": "alignment",
                        }
                    }
                ]
            },
        ).execute()
        
        drive = await get_drive_service(user_id)
        details = drive.files().get(fileId=document_id, fields="id, webViewLink").execute()
        return {
            "document_id": document_id,
            "url": details.get("webViewLink"),
            "alignment_applied": True,
        }
    except Exception as e:
        return {"error": f"Failed to apply alignment: {str(e)}"}
