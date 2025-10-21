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
from chatagent.agents.create_agent_tool import make_agent_tool_node
from langchain_community.callbacks import get_openai_callback
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from supabase_client import supabase
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from chatagent.model.tool_output import ToolOutput
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from chatagent.utils import get_user_id
import os

load_dotenv()

google_client_id = os.environ["GOOGLE_CLIENT_ID"]
google_client_secret = os.environ["GOOGLE_CLIENT_SECRET"]


class SendGmailInput(BaseModel):
    """Schema for sending a Gmail via the send_gmail tool."""

    recipient: str = Field(..., description="The recipient's email address.")
    subject: str = Field(..., description="The subject line of the email.")
    body: str = Field(..., description="The full body content of the email.")


class GmailCount(BaseModel):
    message_count: int = Field(
        5, description="Number of Gmail messages to fetch. Defaults to 5."
    )


@tool("verify_gmail_connection")
def verify_gmail_connection(config: RunnableConfig):
    """
    Verifies if the user's Gmail account is connected.
    Returns a success message if connected, otherwise indicates that authentication is required.
    """
    user_id = get_user_id(config)

    print("insta verify pid : ", user_id)
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
        tool_output = "Gmail account is not connected ask the user to connect or `END`"
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
    Fetches a specified number of recent Gmail messages, including sender, subject, and a snippet. Defaults to 5 messages.
    """
    user_id = get_user_id(config)

    print("getting the gmail_data ===> ")
    print("message count ==> ", message_count)
    print("state ==> ", user_id)

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


@tool("ask_human")
def ask_human(
    params: str = Field(..., description="What clarification is needed from the user")
) -> str:
    """
    Asks the user for clarification or missing information. Use when details like a recipient's email or message content are needed.
    """
    user_input = interrupt({"type": "input_field", "data": {"title": params}})
    return f"AI : {params}\nHuman : {user_input}"


@tool("gmail_error")
def gmail_error(params: str = Field(..., description="error reason")) -> str:
    """
    Notifies the user of a Gmail connection error and asks them to connect their account.
    if user has not connected the gmail
    """
    print("gmail connection issue")
    user_input = interrupt(
        {
            "name": "gmail_error",
            "type": "connect",
            "platform": "gmail",
            "data": {"title": params, "content": ""},
        }
    )
    print(f"connection state started====> userinput {user_input}")
    return str(user_input)


class GmailDraft(BaseModel):
    subject: str = Field(..., description="The subject line of the Gmail")
    body: str = Field(..., description="The professional Gmail body text")


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
    4. do not inlcude a blank field
    5. do not include any irrelavnt data whcih is not mention by the user
    6. use by chatverse as your assistant name
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

    print("too out : ", tool_output)
    print("sub : ", tool_output.subject)
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
def send_gmail(recipient: str, subject: str, body: str) -> str:
    """
    Sends a Gmail after getting final approval from the user. Requires the recipient, subject, and body.
    """
    params = SendGmailInput(recipient=recipient, subject=subject, body=body)
    content = f"""{body}"""

    approval = interrupt(
        {
            "name": "send_gmail",
            "type": "input_option",
            "data": {
                "title": "Do you want to send this Gmail??",
                "content": content,
                "options": ["Yes", "No"],
            },
        }
    )

    print("approval : ", approval)

    if approval.strip().lower() == "yes":
        tool_output = f"""
        ✅ Gmail sent!
        To: {params.recipient}
        Subject: {params.subject}
        Body (preview): {params.body[:100]}
        """

        log_tool_event(
            tool_name="send_gmail",
            status="success",
            params=params.dict(),
            parent_node="gmail_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output
    if approval.strip().lower() == "no":
        tool_output = "Human choosed option: No that means Gmail is rejected by the Human no need to send the Gmail"
        log_tool_event(
            tool_name="send_gmail",
            status="failed",
            params=params.dict(),
            parent_node="gmail_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output
    else:
        tool_output = f"Human did not chooes any option but added new message followe this message : {approval}"
        log_tool_event(
            tool_name="send_gmail",
            status="failed",
            params=params.dict(),
            parent_node="gmail_agent_node",
            tool_output=ToolOutput(output=tool_output),
        )
        return tool_output


class GmailUnreadCount(BaseModel):
    message_count: int = Field(
        5, description="Number of unread Gmail messages to fetch. Defaults to 5."
    )


@tool("fetch_unread_gmail", args_schema=GmailUnreadCount)
def fetch_unread_gmail(message_count: int = 5, config: RunnableConfig = None):
    """
    Fetches a specified number of unread Gmail messages, providing the sender, subject, and a snippet. Defaults to 5 messages.
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
            "User has not autheticated the gmail ask to firstly connect your gmail"
        )

    print("unread : ", gmail_data)

    log_tool_event(
        tool_name="fetch_unread_gmail",
        status="success",
        params={},
        parent_node="gmail_agent_node",
        tool_output=ToolOutput(output=tool_output),
    )
    return tool_output


gmail_tool_register = NodeRegistry()
gmail_tool_register.add("draft_gmail", draft_gmail, "tool")
gmail_tool_register.add("send_gmail", send_gmail, "tool")
gmail_tool_register.add("ask_human", ask_human, "tool")
gmail_tool_register.add("fetch_recent_gmail", fetch_recent_gmail, "tool")
gmail_tool_register.add("gmail_error", gmail_error, "tool")
gmail_tool_register.add("fetch_unread_gmail", fetch_unread_gmail, "tool")
gmail_tool_register.add("verify_gmail_connection", verify_gmail_connection, "tool")


gmail_agent_node = make_agent_tool_node(
    members=gmail_tool_register,
    prompt=(
        "You are a Gmail agent with access to the following tools:\n"
        "- verify_gmail_connection: Check if the user's Gmail is connected before trying other actions.\n"
        "- draft_gmail: Draft professional gmails based pass the subject and body\n"
        "- send_gmail: Send completed gmails once all details are provided and approved.\n"
        "- fetch_recent_gmail: Fetch recent Gmail messages.\n"
        "- fetch_unread_gmail: Fetch only unread Gmail messages.\n"
        "- ask_human: Ask the user for any missing details.\n\n"
        "Guidelines:\n"
        "1. First, always use 'verify_gmail_connection' to ensure the user is logged in.\n"
        "2. Always clarify missing information with 'ask_human' before drafting or sending gmails.\n"
        "3. Use 'fetch_recent_gmail' for general requests about emails, and 'fetch_unread_gmail' only when the user explicitly asks for 'unread' messages.\n"
    ),
    node_name="gmail_agent_node",
    parent_node="task_dispatcher_node",
)
