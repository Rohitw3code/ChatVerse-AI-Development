from langchain_core.tools import tool
from chatagent.agents.social_media_manager.youtube.youtube_api import get_channel_details
import asyncio
from typing import Annotated, Optional
from langgraph.prebuilt import InjectedState
from chatagent.utils import State
from chatagent.node_registry import NodeRegistry
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.types import interrupt
from pydantic import BaseModel, Field
from chatagent.config.init import llm
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


@tool("youtube_channel_details")
async def youtube_channel_details(user_id: str) -> str:
    """
    Fetches details for the user's connected YouTube channel, including snippet and statistics.
    This tool should be used when the user asks for their YouTube channel information, stats, or details.
    The user_id must be the provider_id from the database.
    """
    if not user_id:
        return "Error: A user_id must be provided to fetch YouTube channel details."
        
    details = await get_channel_details(user_id)
    return f"Successfully fetched YouTube channel details: {details}"


yt_tool_register = NodeRegistry()
yt_tool_register.add("youtube_channel_details", youtube_channel_details, "tool")


youtube_agent_node = make_agent_tool_node(
    llm=llm,
    members=yt_tool_register,
    prompt=(
        "You are a YouTube Manager Agent.\n"
        "Your responsibility is to handle ONLY tasks related to fetching YouTube channel details.\n"
    ),
    node_name="youtube_agent_node",
    parent_node="task_dispatcher_node",
)
