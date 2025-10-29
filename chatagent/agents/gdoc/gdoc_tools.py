"""
Google Docs Tools Module
Contains tools for Google Docs operations including creation, formatting, and styling.
"""

from chatagent.node_registry import NodeRegistry
from langchain_core.tools import tool
from pydantic import Field
from langgraph.types import interrupt
from chatagent.model.tool_output import ToolOutput
from chatagent.model.interrupt_model import InterruptRequest
from chatagent.utils import log_tool_event, get_user_id
from langchain_core.runnables import RunnableConfig
from chatagent.agents.gdoc.gdoc_models import (
    GDocCreateInput,
    GDocAppendTextInput,
    GDocInsertTextInput,
    GDocReadInput,
    GDocListDocsInput,
    GDocDeleteTextInput,
    GDocReplaceTextInput,
)
from chatagent.agents.gdoc.gdoc_api import (
    create_document,
    append_text,
    insert_text,
    read_document,
    list_documents,
    delete_text,
    replace_text,
)


@tool("ask_human_input")
async def ask_human_input(prompt: str = Field(..., description="What to ask the human for clarification")):
    """
    Requests clarification from user when information is missing or unclear. Use when missing document ID, text content, or formatting details.
    Interrupts flow to wait for user response. Examples: "Which document to edit?", "What text to add?", "What color (RGB values)?".
    """
    interrupt_request = InterruptRequest.create_input_field(
        name="gdoc_ask_human",
        title=prompt,
    )
    user_input = interrupt(interrupt_request.to_dict())
    return f"AI: {prompt}\nHuman: {user_input}"


@tool("login_gdoc_account")
async def login_gdoc_account(reason: str = Field(..., description="Reason for requesting login (e.g., auth error/token expired)")):
    """
    Handles Google Docs authentication errors and prompts user to connect Google account via OAuth. Use when account not connected or token expired.
    Initiates OAuth flow for necessary permissions. Returns authentication confirmation or cancellation status.
    """
    interrupt_request = InterruptRequest.create_connect(
        name="gdoc_error",
        platform="gdoc",
        title=reason,
        content="",
    )
    user_input = interrupt(interrupt_request.to_dict())
    return str(user_input)


@tool("create_gdoc_document", args_schema=GDocCreateInput)
async def create_gdoc_document(title: str, content: str | None = None, config: RunnableConfig = None):
    """
    Creates a new Google Doc with specified title and optional initial content. Use when user wants to create/make a new document.
    Examples: "create a doc called Report", "make a new document with title Meeting Notes". Returns document ID and URL.
    """
    user_id = get_user_id(config)
    log_tool_event(
        tool_name="create_gdoc_document",
        status="started",
        params={"title": title, "has_content": bool(content)},
        parent_node="gdoc_agent_node",
    )

    data = await create_document(user_id, title, content)
    tool_output = ToolOutput(output=data, show=True, type="format")
    log_tool_event(
        tool_name="create_gdoc_document",
        status="success" if "error" not in data else "failed",
        params={"title": title},
        parent_node="gdoc_agent_node",
        tool_output=tool_output,
    )
    return tool_output


@tool("append_gdoc_text", args_schema=GDocAppendTextInput)
async def append_gdoc_text(document_id: str, text: str, config: RunnableConfig = None):
    """
    Appends text to the end of an existing Google Doc. Use when user wants to add/append text to bottom of document.
    Examples: "add this paragraph to my doc", "append text to document". Returns document URL and confirmation.
    """
    user_id = get_user_id(config)
    log_tool_event(
        tool_name="append_gdoc_text",
        status="started",
        params={"document_id": document_id},
        parent_node="gdoc_agent_node",
    )

    data = await append_text(user_id, document_id, text)
    tool_output = ToolOutput(output=data, show=True, type="format")
    log_tool_event(
        tool_name="append_gdoc_text",
        status="success" if "error" not in data else "failed",
        params={"document_id": document_id},
        parent_node="gdoc_agent_node",
        tool_output=tool_output,
    )
    return tool_output


@tool("insert_gdoc_text", args_schema=GDocInsertTextInput)
async def insert_gdoc_text(document_id: str, text: str, index: int, config: RunnableConfig = None):
    """
    Inserts text at specific position in Google Doc. Use when user wants to insert text at specific location (not at end).
    Index 1 is document start. Examples: "insert at position 10", "add text at the beginning". Returns document URL.
    """
    user_id = get_user_id(config)
    log_tool_event(
        tool_name="insert_gdoc_text",
        status="started",
        params={"document_id": document_id, "index": index},
        parent_node="gdoc_agent_node",
    )

    data = await insert_text(user_id, document_id, text, index)
    tool_output = ToolOutput(output=data, show=True, type="format")
    log_tool_event(
        tool_name="insert_gdoc_text",
        status="success" if "error" not in data else "failed",
        params={"document_id": document_id},
        parent_node="gdoc_agent_node",
        tool_output=tool_output,
    )
    return tool_output


@tool("read_gdoc_document", args_schema=GDocReadInput)
async def read_gdoc_document(document_id: str, config: RunnableConfig = None):
    """
    Reads and retrieves content from Google Doc including title and full text. Use when user wants to see/read/view document content.
    Examples: "show me my document", "read this doc", "what's in the document". Returns title and content.
    """
    user_id = get_user_id(config)
    log_tool_event(
        tool_name="read_gdoc_document",
        status="started",
        params={"document_id": document_id},
        parent_node="gdoc_agent_node",
    )

    data = await read_document(user_id, document_id)
    tool_output = ToolOutput(output=data, show=True, type="format")
    log_tool_event(
        tool_name="read_gdoc_document",
        status="success" if "error" not in data else "failed",
        params={"document_id": document_id},
        parent_node="gdoc_agent_node",
        tool_output=tool_output,
    )
    return tool_output


@tool("list_gdoc_documents", args_schema=GDocListDocsInput)
async def list_gdoc_documents(max_results: int = 10, config: RunnableConfig = None):
    """
    Lists all Google Docs in user's Drive with IDs, names, and timestamps. Use when user wants to see/find their documents.
    Examples: "show my docs", "list my documents", "what docs do I have". Returns list with document details.
    """
    user_id = get_user_id(config)
    log_tool_event(
        tool_name="list_gdoc_documents",
        status="started",
        params={"max_results": max_results},
        parent_node="gdoc_agent_node",
    )

    data = await list_documents(user_id, max_results)
    tool_output = ToolOutput(output=data, show=True, type="format")
    log_tool_event(
        tool_name="list_gdoc_documents",
        status="success" if "error" not in data else "failed",
        params={},
        parent_node="gdoc_agent_node",
        tool_output=tool_output,
    )
    return tool_output


@tool("delete_gdoc_text", args_schema=GDocDeleteTextInput)
async def delete_gdoc_text(document_id: str, start_index: int, end_index: int, config: RunnableConfig = None):
    """
    Deletes text from specific range in Google Doc. Use when user wants to remove/delete text from document.
    ⚠️ Permanently removes text. Examples: "delete text from position 5 to 20", "remove this paragraph". Specify start/end index.
    """
    user_id = get_user_id(config)
    log_tool_event(
        tool_name="delete_gdoc_text",
        status="started",
        params={"document_id": document_id, "start": start_index, "end": end_index},
        parent_node="gdoc_agent_node",
    )

    data = await delete_text(user_id, document_id, start_index, end_index)
    tool_output = ToolOutput(output=data, show=True, type="format")
    log_tool_event(
        tool_name="delete_gdoc_text",
        status="success" if "error" not in data else "failed",
        params={"document_id": document_id},
        parent_node="gdoc_agent_node",
        tool_output=tool_output,
    )
    return tool_output


@tool("replace_gdoc_text", args_schema=GDocReplaceTextInput)
async def replace_gdoc_text(document_id: str, find_text: str, replace_text: str, match_case: bool = False, config: RunnableConfig = None):
    """
    Finds and replaces all occurrences of text in Google Doc. Use for find/replace operations throughout document.
    Examples: "replace old with new", "change all mentions of X to Y", "find Hello and replace with Hi". Optional case matching.
    """
    user_id = get_user_id(config)
    log_tool_event(
        tool_name="replace_gdoc_text",
        status="started",
        params={"document_id": document_id, "find": find_text, "replace": replace_text},
        parent_node="gdoc_agent_node",
    )

    data = await replace_text(user_id, document_id, find_text, replace_text, match_case)
    tool_output = ToolOutput(output=data, show=True, type="format")
    log_tool_event(
        tool_name="replace_gdoc_text",
        status="success" if "error" not in data else "failed",
        params={"document_id": document_id},
        parent_node="gdoc_agent_node",
        tool_output=tool_output,
    )
    return tool_output


def get_gdoc_tool_registry() -> NodeRegistry:
    """Return a NodeRegistry of all Google Docs tools."""
    reg = NodeRegistry()
    reg.add("ask_human_input", ask_human_input, "tool")
    reg.add("login_gdoc_account", login_gdoc_account, "tool")
    reg.add("create_gdoc_document", create_gdoc_document, "tool")
    reg.add("append_gdoc_text", append_gdoc_text, "tool")
    reg.add("insert_gdoc_text", insert_gdoc_text, "tool")
    reg.add("read_gdoc_document", read_gdoc_document, "tool")
    reg.add("list_gdoc_documents", list_gdoc_documents, "tool")
    reg.add("delete_gdoc_text", delete_gdoc_text, "tool")
    reg.add("replace_gdoc_text", replace_gdoc_text, "tool")
    return reg
