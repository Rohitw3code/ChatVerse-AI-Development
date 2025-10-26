"""
Google Docs Tools Module
Contains tools for Google Docs operations.
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
)
from chatagent.agents.gdoc.gdoc_api import create_document, append_text


@tool("ask_human_input")
async def ask_human_input(prompt: str = Field(..., description="What to ask the human for clarification")):
    """Ask the human for missing details or confirmation."""
    interrupt_request = InterruptRequest.create_input_field(
        name="gdoc_ask_human",
        title=prompt,
    )
    user_input = interrupt(interrupt_request.to_dict())
    return f"AI: {prompt}\nHuman: {user_input}"


@tool("login_gdoc_account")
async def login_gdoc_account(reason: str = Field(..., description="Reason for requesting login (e.g., auth error/token expired)")):
    """Trigger login/connect flow for Google Docs when auth is missing or expired."""
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
    """Create a new Google Doc with a title and optional content, returning document_id and url."""
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


@tool("append_gdoc_text_return_url", args_schema=GDocAppendTextInput)
async def append_gdoc_text_return_url(document_id: str, text: str, config: RunnableConfig = None):
    """Append text to an existing Google Doc and return the document URL."""
    user_id = get_user_id(config)
    log_tool_event(
        tool_name="append_gdoc_text_return_url",
        status="started",
        params={"document_id": document_id},
        parent_node="gdoc_agent_node",
    )

    data = await append_text(user_id, document_id, text)
    tool_output = ToolOutput(output=data, show=True, type="format")
    log_tool_event(
        tool_name="append_gdoc_text_return_url",
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
    reg.add("append_gdoc_text_return_url", append_gdoc_text_return_url, "tool")
    return reg
