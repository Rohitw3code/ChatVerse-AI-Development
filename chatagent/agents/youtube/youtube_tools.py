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
    YouTubeVideoListInput,
    YouTubeVideoDetailsInput,
    YouTubeCommentsInput,
    YouTubeSearchInput,
    YouTubeTrafficSourcesInput,
    YouTubeDemographicsInput,
    YouTubeGeographyInput,
)
from langchain_core.runnables import RunnableConfig
from chatagent.utils import get_user_id
from chatagent.agents.youtube.youtube_api import (
    get_channel_details,
    get_analytics_overview,
    get_top_videos,
    get_channel_videos,
    get_video_details,
    get_video_comments,
    search_channel_content,
    get_traffic_sources,
    get_demographics,
    get_geography_analytics,
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
    """login to youtube account tool to handle auth issues or connection issues or based on the user query"""
    print("youtube connection issue")
    
    interrupt_request = InterruptRequest.create_connect(
        name="youtube_error",
        platform="youtube",
        title=params,
        content=""
    )
    
    user_input = interrupt(interrupt_request.to_dict())
    return str(user_input)


@tool("fetch_youtube_channel_videos", args_schema=YouTubeVideoListInput)
async def fetch_youtube_channel_videos(max_results: int = 10, order: str = "date", config: RunnableConfig = None):
    """Fetches a list of videos from the authenticated user's YouTube channel."""
    user_id = get_user_id(config)
    log_tool_event(
        tool_name="fetch_youtube_channel_videos",
        status="started",
        params={"max_results": max_results, "order": order},
        parent_node="youtube_agent_node",
    )

    data = await get_channel_videos(user_id, max_results, order)
    tool_output = ToolOutput(output=data, show=True, type="format")
    log_tool_event(
        tool_name="fetch_youtube_channel_videos",
        status="success",
        params={"max_results": max_results, "order": order},
        parent_node="youtube_agent_node",
        tool_output=tool_output,
    )
    return tool_output


@tool("fetch_youtube_video_details", args_schema=YouTubeVideoDetailsInput)
async def fetch_youtube_video_details(video_id: str, config: RunnableConfig = None):
    """Fetches detailed statistics and information for a specific YouTube video."""
    user_id = get_user_id(config)
    log_tool_event(
        tool_name="fetch_youtube_video_details",
        status="started",
        params={"video_id": video_id},
        parent_node="youtube_agent_node",
    )

    data = await get_video_details(user_id, video_id)
    tool_output = ToolOutput(output=data, show=True, type="format")
    log_tool_event(
        tool_name="fetch_youtube_video_details",
        status="success",
        params={"video_id": video_id},
        parent_node="youtube_agent_node",
        tool_output=tool_output,
    )
    return tool_output


@tool("fetch_youtube_video_comments", args_schema=YouTubeCommentsInput)
async def fetch_youtube_video_comments(video_id: str, max_results: int = 20, config: RunnableConfig = None):
    """Fetches comments for a specific YouTube video."""
    user_id = get_user_id(config)
    log_tool_event(
        tool_name="fetch_youtube_video_comments",
        status="started",
        params={"video_id": video_id, "max_results": max_results},
        parent_node="youtube_agent_node",
    )

    data = await get_video_comments(user_id, video_id, max_results)
    tool_output = ToolOutput(output=data, show=True, type="format")
    log_tool_event(
        tool_name="fetch_youtube_video_comments",
        status="success",
        params={"video_id": video_id, "max_results": max_results},
        parent_node="youtube_agent_node",
        tool_output=tool_output,
    )
    return tool_output


@tool("search_youtube_channel", args_schema=YouTubeSearchInput)
async def search_youtube_channel(query: str, max_results: int = 10, config: RunnableConfig = None):
    """Searches for videos within the authenticated user's YouTube channel."""
    user_id = get_user_id(config)
    log_tool_event(
        tool_name="search_youtube_channel",
        status="started",
        params={"query": query, "max_results": max_results},
        parent_node="youtube_agent_node",
    )

    data = await search_channel_content(user_id, query, max_results)
    tool_output = ToolOutput(output=data, show=True, type="format")
    log_tool_event(
        tool_name="search_youtube_channel",
        status="success",
        params={"query": query, "max_results": max_results},
        parent_node="youtube_agent_node",
        tool_output=tool_output,
    )
    return tool_output


@tool("fetch_youtube_traffic_sources", args_schema=YouTubeTrafficSourcesInput)
async def fetch_youtube_traffic_sources(start_date: str, end_date: str, max_results: int = 10, config: RunnableConfig = None):
    """Fetches traffic source analytics showing where views are coming from."""
    user_id = get_user_id(config)
    log_tool_event(
        tool_name="fetch_youtube_traffic_sources",
        status="started",
        params={"start_date": start_date, "end_date": end_date, "max_results": max_results},
        parent_node="youtube_agent_node",
    )

    data = await get_traffic_sources(user_id, start_date, end_date, max_results)
    tool_output = ToolOutput(output=data, show=True, type="format")
    log_tool_event(
        tool_name="fetch_youtube_traffic_sources",
        status="success",
        params={"start_date": start_date, "end_date": end_date, "max_results": max_results},
        parent_node="youtube_agent_node",
        tool_output=tool_output,
    )
    return tool_output


@tool("fetch_youtube_demographics", args_schema=YouTubeDemographicsInput)
async def fetch_youtube_demographics(start_date: str, end_date: str, config: RunnableConfig = None):
    """Fetches audience demographics data (age groups and gender distribution)."""
    user_id = get_user_id(config)
    log_tool_event(
        tool_name="fetch_youtube_demographics",
        status="started",
        params={"start_date": start_date, "end_date": end_date},
        parent_node="youtube_agent_node",
    )

    data = await get_demographics(user_id, start_date, end_date)
    tool_output = ToolOutput(output=data, show=True, type="format")
    log_tool_event(
        tool_name="fetch_youtube_demographics",
        status="success",
        params={"start_date": start_date, "end_date": end_date},
        parent_node="youtube_agent_node",
        tool_output=tool_output,
    )
    return tool_output


@tool("fetch_youtube_geography", args_schema=YouTubeGeographyInput)
async def fetch_youtube_geography(start_date: str, end_date: str, max_results: int = 10, config: RunnableConfig = None):
    """Fetches geographic analytics showing views by country."""
    user_id = get_user_id(config)
    log_tool_event(
        tool_name="fetch_youtube_geography",
        status="started",
        params={"start_date": start_date, "end_date": end_date, "max_results": max_results},
        parent_node="youtube_agent_node",
    )

    data = await get_geography_analytics(user_id, start_date, end_date, max_results)
    tool_output = ToolOutput(output=data, show=True, type="format")
    log_tool_event(
        tool_name="fetch_youtube_geography",
        status="success",
        params={"start_date": start_date, "end_date": end_date, "max_results": max_results},
        parent_node="youtube_agent_node",
        tool_output=tool_output,
    )
    return tool_output


def get_youtube_tool_registry() -> NodeRegistry:
    """
    Returns a NodeRegistry containing all YouTube tools.
    This function centralizes tool registration.
    """
    youtube_tool_register = NodeRegistry()
    youtube_tool_register.add("fetch_youtube_channel_details", fetch_youtube_channel_details, "tool")
    # youtube_tool_register.add("login_youtube_account", login_youtube_account, "tool")
    youtube_tool_register.add("fetch_youtube_analytics_overview", fetch_youtube_analytics_overview, "tool")
    youtube_tool_register.add("fetch_youtube_top_videos", fetch_youtube_top_videos, "tool")
    youtube_tool_register.add("fetch_youtube_channel_videos", fetch_youtube_channel_videos, "tool")
    youtube_tool_register.add("fetch_youtube_video_details", fetch_youtube_video_details, "tool")
    youtube_tool_register.add("fetch_youtube_video_comments", fetch_youtube_video_comments, "tool")
    youtube_tool_register.add("search_youtube_channel", search_youtube_channel, "tool")
    youtube_tool_register.add("fetch_youtube_traffic_sources", fetch_youtube_traffic_sources, "tool")
    youtube_tool_register.add("fetch_youtube_demographics", fetch_youtube_demographics, "tool")
    youtube_tool_register.add("fetch_youtube_geography", fetch_youtube_geography, "tool")
    return youtube_tool_register



