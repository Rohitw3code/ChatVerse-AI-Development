"""
Gmail Tools Module
Contains all Gmail-related tools and their implementations.
No hardcoded prompts - all prompts are managed through agents_config.py
"""

from typing import Annotated, Optional
from langgraph.prebuilt import InjectedState
from chatagent.utils import State
from chatagent.node_registry import NodeRegistry
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.types import interrupt
from pydantic import BaseModel, Field
from chatagent.config.init import non_stream_llm
from chatagent.utils import usages, log_tool_event
from langchain_community.callbacks import get_openai_callback
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from supabase_client import supabase
from chatagent.model.tool_output import ToolOutput
from chatagent.model.interrupt_model import InterruptRequest
from chatagent.agents.gmail.gmail_models import (
    SendGmailInput,
    GmailCount,
    GmailUnreadCount,
    GmailDraft,
    SearchGmailInput,
    EmailIdInput,
    ReplyEmailInput,
    ForwardEmailInput,
    LabelOperationInput,
)
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from chatagent.utils import get_user_id
from email.mime.text import MIMEText
import base64
import os
import json

load_dotenv()

# Load Gmail credentials from gmail.json
gmail_json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "gmail.json")
with open(gmail_json_path, 'r') as f:
    gmail_config = json.load(f)
    google_client_id = gmail_config["web"]["client_id"]
    google_client_secret = gmail_config["web"]["client_secret"]


@tool("verify_gmail_connection")
def verify_gmail_connection(config: RunnableConfig):
    """
    Verifies if the user's Gmail account is connected.
    Returns a success message if connected, otherwise indicates that authentication is required.
    """
    user_id = get_user_id(config)

    print("gmail verify pid:", user_id)
    log_tool_event(
        tool_name="verify_gmail_connection",
        status="started",
        params={"platform_user_id": user_id},
        parent_node="gmail_agent_node",
    )

    existing = (
        supabase.table("connected_accounts")
        .select("platform_user_id")
        .eq("provider_id", user_id)
        .eq("platform", "gmail")
        .execute()
    )
    
    if existing.data:
        tool_output = f"yes the gmail is connected and ready to use {existing}"
        log_tool_event(
            tool_name="verify_gmail_connection",
            status="success",
            params={},
            parent_node="gmail_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output
    else:
        tool_output = "Gmail account is not connected ask the user to login to gmail use login gmail tool"
        log_tool_event(
            tool_name="verify_gmail_connection",
            status="failed",
            params={},
            parent_node="gmail_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output


@tool("fetch_recent_gmail", args_schema=GmailCount)
def fetch_recent_gmail(message_count: int = 5, config: RunnableConfig = None):
    """
    Fetches a specified number of recent Gmail messages, including sender, subject, and a snippet. 
    Defaults to 5 messages.
    """
    user_id = get_user_id(config)

    print("getting the gmail_data ==>")
    print("message count ==>", message_count)
    print("state ==>", user_id)

    log_tool_event(
        tool_name="fetch_recent_gmail",
        status="started",
        params={},
        parent_node="gmail_agent_node",
    )
    
    gmail_data = (
        supabase.table("connected_accounts")
        .select("*")
        .eq("provider_id", user_id)
        .eq("platform", "gmail")
        .execute()
    )

    if gmail_data.data:
        data = gmail_data.data[0]
        creds = Credentials.from_authorized_user_info(
            {
                "token": data["access_token"],
                "refresh_token": data["refresh_token"],
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": google_client_id,
                "client_secret": google_client_secret,
                "scopes": data["scopes"],
                "universe_domain": "googleapis.com",
            }
        )

        service = build("gmail", "v1", credentials=creds)

        results = (
            service.users()
            .messages()
            .list(userId="me", maxResults=message_count)
            .execute()
        )
        messages = results.get("messages", [])

        if not messages:
            tool_output = "No messages found"
        else:
            tool_output = ""
            for msg in messages:
                msg_data = (
                    service.users()
                    .messages()
                    .get(
                        userId="me",
                        id=msg["id"],
                        format="metadata",
                        metadataHeaders=["From", "Subject"],
                    )
                    .execute()
                )
                headers = msg_data.get("payload", {}).get("headers", [])
                snippet = msg_data.get("snippet", "")

                sender = next(
                    (h["value"] for h in headers if h["name"] == "From"),
                    "Unknown Sender",
                )
                subject = next(
                    (h["value"] for h in headers if h["name"] == "Subject"),
                    "No Subject",
                )

                tool_output += (
                    f"From: {sender}\nSubject: {subject}\nSnippet: {snippet}\n\n"
                )
        status = "success"
    else:
        tool_output = "No account connected you need to connect gmail account first"
        status = "failed"

    log_tool_event(
        tool_name="fetch_recent_gmail",
        status=status,
        params={},
        parent_node="gmail_agent_node",
        tool_output=ToolOutput(output=tool_output, show=True, type="format"),
    )
    return tool_output


@tool("fetch_unread_gmail", args_schema=GmailUnreadCount)
def fetch_unread_gmail(message_count: int = 5, config: RunnableConfig = None):
    """
    Fetches a specified number of unread Gmail messages, providing the sender, subject, and a snippet. 
    Defaults to 5 messages.
    """
    print("getting the unread gmail_data")
    log_tool_event(
        tool_name="fetch_unread_gmail",
        status="started",
        params={},
        parent_node="gmail_agent_node",
    )
    user_id = get_user_id(config)

    gmail_data = (
        supabase.table("connected_accounts")
        .select("*")
        .eq("provider_id", user_id)
        .eq("platform", "gmail")
        .execute()
    )

    if gmail_data.data:
        data = gmail_data.data[0]
        creds = Credentials.from_authorized_user_info(
            {
                "token": data["access_token"],
                "refresh_token": data["refresh_token"],
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": google_client_id,
                "client_secret": google_client_secret,
                "scopes": data["scopes"],
                "universe_domain": "googleapis.com",
            }
        )

        service = build("gmail", "v1", credentials=creds)

        results = (
            service.users()
            .messages()
            .list(userId="me", labelIds=["UNREAD"], maxResults=message_count)
            .execute()
        )
        messages = results.get("messages", [])

        if not messages:
            tool_output = "No unread messages found"
        else:
            tool_output = ""
            for msg in messages:
                msg_data = (
                    service.users()
                    .messages()
                    .get(
                        userId="me",
                        id=msg["id"],
                        format="metadata",
                        metadataHeaders=["From", "Subject"],
                    )
                    .execute()
                )
                headers = msg_data.get("payload", {}).get("headers", [])
                snippet = msg_data.get("snippet", "")

                sender = next(
                    (h["value"] for h in headers if h["name"] == "From"),
                    "Unknown Sender",
                )
                subject = next(
                    (h["value"] for h in headers if h["name"] == "Subject"),
                    "No Subject",
                )

                tool_output += (
                    f"From: {sender}\nSubject: {subject}\nSnippet: {snippet}\n\n"
                )
    else:
        tool_output = (
            "User has not authenticated the gmail ask to firstly connect your gmail"
        )

    log_tool_event(
        tool_name="fetch_unread_gmail",
        status="success",
        params={},
        parent_node="gmail_agent_node",
        tool_output=ToolOutput(output=tool_output),
    )
    return tool_output


@tool("draft_gmail")
def draft_gmail(
    params: str = Field(..., description="The request or instructions for the gmail")
) -> dict:
    """
    Drafts a professional Gmail from a user's request, generating a subject and a well-structured body.
    """
    log_tool_event(
        tool_name="draft_gmail",
        status="started",
        params={"request": params},
        parent_node="gmail_agent_node",
    )

    gmail_prompt = f"""
    Gmail Request: {params}

    Create a professional Gmail:
    1. Subject line
    2. Well-structured body
    3. Professional tone
    4. do not include a blank field
    5. do not include any irrelevant data which is not mentioned by the user
    6. use 'by chatverse' as your assistant name
    """

    with get_openai_callback() as cb:
        tool_output = non_stream_llm.with_structured_output(GmailDraft).invoke(
            [
                SystemMessage(
                    content=f"You are a professional Gmail writer. {gmail_prompt}"
                ),
                HumanMessage(content=params),
            ]
        )

    usage = usages(cb)

    print("tool out:", tool_output)
    print("sub:", tool_output.subject)
    result = {"subject": tool_output.subject, "body": tool_output.body}
    log_tool_event(
        tool_name="draft_gmail",
        status="success",
        params={"request": params},
        parent_node="gmail_agent_node",
        tool_output=ToolOutput(output=result, type="draft_email", show=True),
        usages=usage,
    )

    return result


@tool("send_gmail", args_schema=SendGmailInput)
def send_gmail(recipient: str, subject: str, body: str, config: RunnableConfig = None) -> str:
    """
    Sends a Gmail after getting final approval from the user. Requires the recipient, subject, and body.
    """
    params = SendGmailInput(recipient=recipient, subject=subject, body=body)
    
    # Show email preview to user
    preview_content = f"""
        📧 Email Preview:
        To: {recipient}
        Subject: {subject}

        {body}
    """

    interrupt_request = InterruptRequest.create_input_option(
        name="send_gmail",
        title="Do you want to send this email?",
        content=preview_content,
        options=["Yes", "No"]
    )
    
    response_json = interrupt(interrupt_request.to_dict())

    response_json = json.loads(response_json)

    print("\n\n\ response json ", " modified_text : ",response_json['modified_text'], " human_response : ",response_json['human_response'],"\n\n")

    print("\n\n SEND GMAIL approval: ", response_json, type(response_json),"\n\n")

    if response_json['human_response'].strip().lower() == "yes":
        # Actually send the email
        try:
            user_id = get_user_id(config)
            
            # Get Gmail credentials from database
            gmail_data = (
                supabase.table("connected_accounts")
                .select("*")
                .eq("provider_id", user_id)
                .eq("platform", "gmail")
                .execute()
            )

            if not gmail_data.data:
                tool_output = "❌ Gmail account is not connected. Please connect your Gmail account first."
                log_tool_event(
                    tool_name="send_gmail",
                    status="failed",
                    params=params.dict(),
                    parent_node="gmail_agent_node",
                    tool_output=ToolOutput(output=tool_output),
                )
                return tool_output

            # Build credentials
            data = gmail_data.data[0]
            creds = Credentials.from_authorized_user_info(
                {
                    "token": data["access_token"],
                    "refresh_token": data["refresh_token"],
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "client_id": google_client_id,
                    "client_secret": google_client_secret,
                    "scopes": data["scopes"],
                    "universe_domain": "googleapis.com",
                }
            )

            service = build("gmail", "v1", credentials=creds)

            # Create email message
            message = MIMEText(response_json['modified_text'])
            message['to'] = recipient
            message['subject'] = subject
            
            # Encode the message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            # Send the email
            send_result = service.users().messages().send(
                userId="me",
                body={'raw': raw_message}
            ).execute()

            tool_output = f"""
                ✅ Email sent successfully!
                To: {recipient}
                Subject: {subject}
                Message ID: {send_result.get('id', 'N/A')}
                Your email has been delivered successfully! 📬
            """

            log_tool_event(
                tool_name="send_gmail",
                status="success",
                params=params.dict(),
                parent_node="gmail_agent_node",
                tool_output=ToolOutput(output=tool_output, show=True),
            )
            return tool_output

        except Exception as e:
            error_message = str(e)
            tool_output = f"❌ Failed to send email: {error_message}"
            log_tool_event(
                tool_name="send_gmail",
                status="failed",
                params=params.dict(),
                parent_node="gmail_agent_node",
                tool_output=ToolOutput(output=tool_output),
            )
            return tool_output
            
    elif response_json['human_response'].strip().lower() == "no":
        tool_output = "❌ Email cancelled. The email was not sent as per your request."
        log_tool_event(
            tool_name="send_gmail",
            status="cancelled",
            params=params.dict(),
            parent_node="gmail_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output
    else:
        tool_output = f"User Response : {response_json['human_response']}"
        log_tool_event(
            tool_name="send_gmail",
            status="failed",
            params=params.dict(),
            parent_node="gmail_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output


@tool("ask_human")
def ask_human(
    params: str = Field(..., description="What clarification is needed from the user")
) -> str:
    """
    Asks the user for clarification or missing information. Use when details like a recipient's email or message content are needed.
    """
    interrupt_request = InterruptRequest.create_input_field(
        name="ask_human",
        title=params
    )

    
    user_input = interrupt(interrupt_request.to_dict())

    print("\n\n User Input : ", user_input,"\n\n")


    return f"AI : {params}\nHuman : {user_input}"


@tool("login_to_gmail")
def login_to_gmail(params: str = Field(..., description="error reason")) -> str:
    """
    if user has not connected the gmail, user ask to connect the gmail account
    if gmail connection issue occurs, ask the user to reconnect the gmail account
    if gmail token expired, ask the user to reconnect the gmail account
    """
    print("gmail connection issue")
    
    interrupt_request = InterruptRequest.create_connect(
        name="gmail_error",
        platform="gmail",
        title=params,
        content=""
    )
    
    user_input = interrupt(interrupt_request.to_dict())
    return str(user_input)


@tool("search_gmail", args_schema=SearchGmailInput)
def search_gmail(query: str, max_results: int = 10, config: RunnableConfig = None):
    """
    Searches Gmail messages using Gmail search operators. 
    Examples: 'from:example@gmail.com', 'subject:meeting', 'is:unread', 'has:attachment', 'after:2024/01/01'
    """
    user_id = get_user_id(config)
    
    log_tool_event(
        tool_name="search_gmail",
        status="started",
        params={"query": query, "max_results": max_results},
        parent_node="gmail_agent_node",
    )
    
    gmail_data = (
        supabase.table("connected_accounts")
        .select("*")
        .eq("provider_id", user_id)
        .eq("platform", "gmail")
        .execute()
    )

    if not gmail_data.data:
        tool_output = "No Gmail account connected. Please connect your Gmail account first."
        log_tool_event(
            tool_name="search_gmail",
            status="failed",
            params={"query": query},
            parent_node="gmail_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output

    data = gmail_data.data[0]
    creds = Credentials.from_authorized_user_info(
        {
            "token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": google_client_id,
            "client_secret": google_client_secret,
            "scopes": data["scopes"],
            "universe_domain": "googleapis.com",
        }
    )

    service = build("gmail", "v1", credentials=creds)

    try:
        results = (
            service.users()
            .messages()
            .list(userId="me", q=query, maxResults=max_results)
            .execute()
        )
        messages = results.get("messages", [])

        if not messages:
            tool_output = f"No messages found matching query: {query}"
        else:
            tool_output = f"Found {len(messages)} message(s):\n\n"
            for msg in messages:
                msg_data = (
                    service.users()
                    .messages()
                    .get(
                        userId="me",
                        id=msg["id"],
                        format="metadata",
                        metadataHeaders=["From", "Subject", "Date"],
                    )
                    .execute()
                )
                headers = msg_data.get("payload", {}).get("headers", [])
                snippet = msg_data.get("snippet", "")

                sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown")
                subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
                date = next((h["value"] for h in headers if h["name"] == "Date"), "Unknown")

                tool_output += f"📧 ID: {msg['id']}\nFrom: {sender}\nSubject: {subject}\nDate: {date}\nSnippet: {snippet}\n\n"

        log_tool_event(
            tool_name="search_gmail",
            status="success",
            params={"query": query, "max_results": max_results},
            parent_node="gmail_agent_node",
            tool_output=ToolOutput(output=tool_output, show=True, type="format"),
        )
        return tool_output

    except Exception as e:
        tool_output = f"Error searching Gmail: {str(e)}"
        log_tool_event(
            tool_name="search_gmail",
            status="failed",
            params={"query": query},
            parent_node="gmail_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output


@tool("get_email_by_id", args_schema=EmailIdInput)
def get_email_by_id(email_id: str, config: RunnableConfig = None):
    """
    Retrieves the full content of a specific email by its ID, including body, attachments info, and all headers.
    """
    user_id = get_user_id(config)
    
    log_tool_event(
        tool_name="get_email_by_id",
        status="started",
        params={"email_id": email_id},
        parent_node="gmail_agent_node",
    )
    
    gmail_data = (
        supabase.table("connected_accounts")
        .select("*")
        .eq("provider_id", user_id)
        .eq("platform", "gmail")
        .execute()
    )

    if not gmail_data.data:
        tool_output = "No Gmail account connected. Please connect your Gmail account first."
        log_tool_event(
            tool_name="get_email_by_id",
            status="failed",
            params={"email_id": email_id},
            parent_node="gmail_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output

    data = gmail_data.data[0]
    creds = Credentials.from_authorized_user_info(
        {
            "token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": google_client_id,
            "client_secret": google_client_secret,
            "scopes": data["scopes"],
            "universe_domain": "googleapis.com",
        }
    )

    service = build("gmail", "v1", credentials=creds)

    try:
        msg_data = (
            service.users()
            .messages()
            .get(userId="me", id=email_id, format="full")
            .execute()
        )
        
        headers = msg_data.get("payload", {}).get("headers", [])
        parts = msg_data.get("payload", {}).get("parts", [])
        
        # Extract headers
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown")
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
        date = next((h["value"] for h in headers if h["name"] == "Date"), "Unknown")
        to = next((h["value"] for h in headers if h["name"] == "To"), "Unknown")
        
        # Extract body
        body = ""
        if parts:
            for part in parts:
                if part.get("mimeType") == "text/plain":
                    body_data = part.get("body", {}).get("data", "")
                    if body_data:
                        body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
                        break
        else:
            body_data = msg_data.get("payload", {}).get("body", {}).get("data", "")
            if body_data:
                body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
        
        tool_output = f"""
📧 Email Details (ID: {email_id})

From: {sender}
To: {to}
Subject: {subject}
Date: {date}

Body:
{body[:1000]}{'...' if len(body) > 1000 else ''}
        """
        
        log_tool_event(
            tool_name="get_email_by_id",
            status="success",
            params={"email_id": email_id},
            parent_node="gmail_agent_node",
            tool_output=ToolOutput(output=tool_output, show=True, type="format"),
        )
        return tool_output

    except Exception as e:
        tool_output = f"Error retrieving email: {str(e)}"
        log_tool_event(
            tool_name="get_email_by_id",
            status="failed",
            params={"email_id": email_id},
            parent_node="gmail_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output


@tool("mark_email_read", args_schema=EmailIdInput)
def mark_email_read(email_id: str, config: RunnableConfig = None):
    """
    Marks a specific email as read by removing the UNREAD label.
    """
    user_id = get_user_id(config)
    
    log_tool_event(
        tool_name="mark_email_read",
        status="started",
        params={"email_id": email_id},
        parent_node="gmail_agent_node",
    )
    
    gmail_data = (
        supabase.table("connected_accounts")
        .select("*")
        .eq("provider_id", user_id)
        .eq("platform", "gmail")
        .execute()
    )

    if not gmail_data.data:
        tool_output = "No Gmail account connected."
        return tool_output

    data = gmail_data.data[0]
    creds = Credentials.from_authorized_user_info(
        {
            "token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": google_client_id,
            "client_secret": google_client_secret,
            "scopes": data["scopes"],
            "universe_domain": "googleapis.com",
        }
    )

    service = build("gmail", "v1", credentials=creds)

    try:
        service.users().messages().modify(
            userId="me",
            id=email_id,
            body={"removeLabelIds": ["UNREAD"]}
        ).execute()
        
        tool_output = f"✅ Email {email_id} marked as read."
        
        log_tool_event(
            tool_name="mark_email_read",
            status="success",
            params={"email_id": email_id},
            parent_node="gmail_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output

    except Exception as e:
        tool_output = f"Error marking email as read: {str(e)}"
        log_tool_event(
            tool_name="mark_email_read",
            status="failed",
            params={"email_id": email_id},
            parent_node="gmail_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output


@tool("mark_email_unread", args_schema=EmailIdInput)
def mark_email_unread(email_id: str, config: RunnableConfig = None):
    """
    Marks a specific email as unread by adding the UNREAD label.
    """
    user_id = get_user_id(config)
    
    log_tool_event(
        tool_name="mark_email_unread",
        status="started",
        params={"email_id": email_id},
        parent_node="gmail_agent_node",
    )
    
    gmail_data = (
        supabase.table("connected_accounts")
        .select("*")
        .eq("provider_id", user_id)
        .eq("platform", "gmail")
        .execute()
    )

    if not gmail_data.data:
        tool_output = "No Gmail account connected."
        return tool_output

    data = gmail_data.data[0]
    creds = Credentials.from_authorized_user_info(
        {
            "token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": google_client_id,
            "client_secret": google_client_secret,
            "scopes": data["scopes"],
            "universe_domain": "googleapis.com",
        }
    )

    service = build("gmail", "v1", credentials=creds)

    try:
        service.users().messages().modify(
            userId="me",
            id=email_id,
            body={"addLabelIds": ["UNREAD"]}
        ).execute()
        
        tool_output = f"✅ Email {email_id} marked as unread."
        
        log_tool_event(
            tool_name="mark_email_unread",
            status="success",
            params={"email_id": email_id},
            parent_node="gmail_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output

    except Exception as e:
        tool_output = f"Error marking email as unread: {str(e)}"
        log_tool_event(
            tool_name="mark_email_unread",
            status="failed",
            params={"email_id": email_id},
            parent_node="gmail_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output



@tool("reply_to_email", args_schema=ReplyEmailInput)
def reply_to_email(email_id: str, body: str, config: RunnableConfig = None):
    """
    Replies to an existing email thread.
    """
    user_id = get_user_id(config)
    
    log_tool_event(
        tool_name="reply_to_email",
        status="started",
        params={"email_id": email_id},
        parent_node="gmail_agent_node",
    )
    
    gmail_data = (
        supabase.table("connected_accounts")
        .select("*")
        .eq("provider_id", user_id)
        .eq("platform", "gmail")
        .execute()
    )

    if not gmail_data.data:
        tool_output = "No Gmail account connected."
        return tool_output

    data = gmail_data.data[0]
    creds = Credentials.from_authorized_user_info(
        {
            "token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": google_client_id,
            "client_secret": google_client_secret,
            "scopes": data["scopes"],
            "universe_domain": "googleapis.com",
        }
    )

    service = build("gmail", "v1", credentials=creds)

    try:
        # Get original email
        original = service.users().messages().get(userId="me", id=email_id, format="metadata").execute()
        headers = original.get("payload", {}).get("headers", [])
        
        thread_id = original.get("threadId")
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
        to = next((h["value"] for h in headers if h["name"] == "From"), "")
        
        # Create reply
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = f"Re: {subject}" if not subject.startswith("Re:") else subject
        message['In-Reply-To'] = email_id
        message['References'] = email_id
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        send_result = service.users().messages().send(
            userId="me",
            body={'raw': raw_message, 'threadId': thread_id}
        ).execute()
        
        tool_output = f"✅ Reply sent successfully to {to}\nMessage ID: {send_result.get('id')}"
        
        log_tool_event(
            tool_name="reply_to_email",
            status="success",
            params={"email_id": email_id},
            parent_node="gmail_agent_node",
            tool_output=ToolOutput(output=tool_output, show=True),
        )
        return tool_output

    except Exception as e:
        tool_output = f"Error replying to email: {str(e)}"
        log_tool_event(
            tool_name="reply_to_email",
            status="failed",
            params={"email_id": email_id},
            parent_node="gmail_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output


@tool("get_gmail_labels")
def get_gmail_labels(config: RunnableConfig = None):
    """
    Retrieves all Gmail labels/folders for the authenticated user's account.
    """
    user_id = get_user_id(config)
    
    log_tool_event(
        tool_name="get_gmail_labels",
        status="started",
        params={},
        parent_node="gmail_agent_node",
    )
    
    gmail_data = (
        supabase.table("connected_accounts")
        .select("*")
        .eq("provider_id", user_id)
        .eq("platform", "gmail")
        .execute()
    )

    if not gmail_data.data:
        tool_output = "No Gmail account connected."
        return tool_output

    data = gmail_data.data[0]
    creds = Credentials.from_authorized_user_info(
        {
            "token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": google_client_id,
            "client_secret": google_client_secret,
            "scopes": data["scopes"],
            "universe_domain": "googleapis.com",
        }
    )

    service = build("gmail", "v1", credentials=creds)

    try:
        results = service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])
        
        if not labels:
            tool_output = "No labels found."
        else:
            tool_output = f"📁 Found {len(labels)} labels:\n\n"
            for label in labels:
                label_name = label.get("name", "Unknown")
                label_id = label.get("id", "Unknown")
                label_type = label.get("type", "Unknown")
                tool_output += f"• {label_name} (ID: {label_id}, Type: {label_type})\n"
        
        log_tool_event(
            tool_name="get_gmail_labels",
            status="success",
            params={},
            parent_node="gmail_agent_node",
            tool_output=ToolOutput(output=tool_output, show=True, type="format"),
        )
        return tool_output

    except Exception as e:
        tool_output = f"Error fetching labels: {str(e)}"
        log_tool_event(
            tool_name="get_gmail_labels",
            status="failed",
            params={},
            parent_node="gmail_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output


def get_gmail_tool_registry() -> NodeRegistry:
    """
    Returns a NodeRegistry containing all Gmail tools.
    This function centralizes tool registration.
    """
    gmail_tool_register = NodeRegistry()
    gmail_tool_register.add("verify_gmail_connection", verify_gmail_connection, "tool")
    gmail_tool_register.add("fetch_recent_gmail", fetch_recent_gmail, "tool")
    gmail_tool_register.add("fetch_unread_gmail", fetch_unread_gmail, "tool")
    gmail_tool_register.add("draft_gmail", draft_gmail, "tool")
    gmail_tool_register.add("send_gmail", send_gmail, "tool")
    gmail_tool_register.add("ask_human", ask_human, "tool")
    gmail_tool_register.add("login_to_gmail", login_to_gmail, "tool")
    gmail_tool_register.add("search_gmail", search_gmail, "tool")
    gmail_tool_register.add("get_email_by_id", get_email_by_id, "tool")
    gmail_tool_register.add("mark_email_read", mark_email_read, "tool")
    gmail_tool_register.add("mark_email_unread", mark_email_unread, "tool")
    gmail_tool_register.add("reply_to_email", reply_to_email, "tool")
    gmail_tool_register.add("get_gmail_labels", get_gmail_labels, "tool")
    return gmail_tool_register
