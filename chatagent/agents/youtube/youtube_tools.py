"""
YouTube Tools Module
Contains all YouTube-related tools and their implementations.
No hardcoded prompts - all prompts are managed through agents_config.py
"""

from chatagent.node_registry import NodeRegistry
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from chatagent.utils import log_tool_event
from langgraph.types import interrupt
from chatagent.model.tool_output import ToolOutput
from chatagent.agents.youtube.youtube_models import YouTubeChannelDetailsInput
from langchain_core.runnables import RunnableConfig
from chatagent.utils import get_user_id
from chatagent.agents.youtube.youtube_api import get_channel_details
from chatagent.model.tool_output import ToolOutput
from chatagent.model.interrupt_model import InterruptRequest


@tool("fetch_youtube_channel_details", args_schema=YouTubeChannelDetailsInput)
async def fetch_youtube_channel_details(channel_name: str, config: RunnableConfig):
    """Fetches details for a given YouTube channel."""
    user_id = get_user_id(config)
    log_tool_event(
        tool_name="fetch_youtube_channel_details",
        status="started",
        params={},
        parent_node="youtube_agent_node",
    )
    data = await get_channel_details(user_id)
    print("\n\n\n\n")
    print("Fetched YouTube Channel Details:", data)
    print("\n\n\n\n")
    tool_output = ToolOutput(output=data, show=True, type="format")
    log_tool_event(
        tool_name="fetch_youtube_channel_details",
        status="success",
        params={"channel_name": channel_name},
        parent_node="youtube_agent_node",
        tool_output=tool_output,
    )
    return tool_output

@tool("login_youtube_account")
async def login_youtube_account(params: str = Field(..., description="error reason")):
    """Initiates YouTube account login process."""
    print("youtube connection issue")
    
    interrupt_request = InterruptRequest.create_connect(
        name="youtube_error",
        platform="youtube",
        title=params,
        content=""
    )
    
    user_input = interrupt(interrupt_request.to_dict())
    return str(user_input)


def get_youtube_tool_registry() -> NodeRegistry:
    """
    Returns a NodeRegistry containing all YouTube tools.
    This function centralizes tool registration.
    """
    youtube_tool_register = NodeRegistry()
    youtube_tool_register.add("fetch_youtube_channel_details", fetch_youtube_channel_details, "tool")
    youtube_tool_register.add("login_youtube_account", login_youtube_account, "tool")
    return youtube_tool_register



