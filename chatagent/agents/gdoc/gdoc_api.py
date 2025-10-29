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
