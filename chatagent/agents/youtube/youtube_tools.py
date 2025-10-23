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
from chatagent.agents.youtube.youtube_models import (
    YouTubeChannelDetailsInput,
    YouTubeAnalyticsRequest,
)
from langchain_core.runnables import RunnableConfig
from chatagent.utils import get_user_id
from chatagent.agents.youtube.youtube_api import (
    get_channel_details,
    get_analytics_overview,
    get_top_videos,
)
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


@tool("fetch_youtube_analytics_overview", args_schema=YouTubeAnalyticsRequest)
async def fetch_youtube_analytics_overview(start_date: str, end_date: str, metrics: str = None, max_results: int = 5, config: RunnableConfig = None):
    """Fetches aggregated analytics for the authenticated user's channel over a date range."""
    user_id = get_user_id(config)
    log_tool_event(
        tool_name="fetch_youtube_analytics_overview",
        status="started",
        params={"start_date": start_date, "end_date": end_date, "metrics": metrics},
        parent_node="youtube_agent_node",
    )

    if metrics is None:
        metrics = "views,estimatedMinutesWatched"

    data = await get_analytics_overview(user_id, start_date, end_date, metrics)
    tool_output = ToolOutput(output=data, show=True, type="format")
    log_tool_event(
        tool_name="fetch_youtube_analytics_overview",
        status="success",
        params={"start_date": start_date, "end_date": end_date, "metrics": metrics},
        parent_node="youtube_agent_node",
        tool_output=tool_output,
    )
    return tool_output


@tool("fetch_youtube_top_videos", args_schema=YouTubeAnalyticsRequest)
async def fetch_youtube_top_videos(start_date: str, end_date: str, metrics: str = None, max_results: int = 5, config: RunnableConfig = None):
    """Fetches top videos by views for the authenticated user's channel over a date range."""
    user_id = get_user_id(config)
    log_tool_event(
        tool_name="fetch_youtube_top_videos",
        status="started",
        params={"start_date": start_date, "end_date": end_date, "max_results": max_results},
        parent_node="youtube_agent_node",
    )

    data = await get_top_videos(user_id, start_date, end_date, max_results)
    tool_output = ToolOutput(output=data, show=True, type="format")
    log_tool_event(
        tool_name="fetch_youtube_top_videos",
        status="success",
        params={"start_date": start_date, "end_date": end_date, "max_results": max_results},
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
    youtube_tool_register.add("fetch_youtube_analytics_overview", fetch_youtube_analytics_overview, "tool")
    youtube_tool_register.add("fetch_youtube_top_videos", fetch_youtube_top_videos, "tool")
    return youtube_tool_register



