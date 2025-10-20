from chatagent.node_registry import NodeRegistry
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from chatagent.config.init import llm
from chatagent.agents.create_agent_tool import make_agent_tool_node
from chatagent.utils import log_tool_event
from langgraph.types import interrupt
from chatagent.model.tool_output import ToolOutput
from langchain_core.runnables import RunnableConfig
from chatagent.utils import get_user_id
from chatagent.agents.social_media_manager.youtube.youtube_api import get_channel_details

class YouTubeChannelDetailsInput(BaseModel):
    """Input schema for fetching YouTube channel details."""
    channel_name: str = Field(..., description="The name of the YouTube channel to fetch details for.")

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
    print("Fetched YouTube Channel Details:", data )
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

youtube_tool_register = NodeRegistry()
youtube_tool_register.add("fetch_youtube_channel_details", fetch_youtube_channel_details, "tool")

youtube_agent_node = make_agent_tool_node(
    llm=llm,
    members=youtube_tool_register,
    prompt=(
        "You are a YouTube agent. You can fetch channel details. "
        "Choose the correct tool based on the user request."
    ),
    node_name="youtube_agent_node",
    parent_node="task_dispatcher_node",
)