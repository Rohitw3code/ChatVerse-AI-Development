"""
Instagram Tools Module
Contains all Instagram-related tools and their implementations.
No hardcoded prompts - all prompts are managed through agents_config.py
"""

from chatagent.node_registry import NodeRegistry
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from chatagent.utils import log_tool_event
from langgraph.types import interrupt
from chatagent.agents.instagram import instagram_profile
from supabase_client import supabase
from chatagent.model.tool_output import ToolOutput
from chatagent.model.interrupt_model import InterruptRequest
from chatagent.utils import get_user_id
from langchain_core.runnables import RunnableConfig


@tool("instagram_auth_verification")
def instagram_auth_verification(config: RunnableConfig):
    """
    This tool is to verify the instagram connection if a user has connected the account or not.
    This tool always used when user asks for any instagram related task which required instagram api.
    """
    user_id = get_user_id(config)

    print("insta verify pid:", user_id)
    log_tool_event(
        tool_name="instagram_auth_verification",
        status="started",
        params={"platform_user_id": user_id},
        parent_node="instagram_agent_node",
    )

    existing = (
        supabase.table("connected_accounts")
        .select("platform_user_id")
        .eq("provider_id", user_id)
        .eq("platform", "instagram")
        .execute()
    )

    if existing.data:
        tool_output = f"yes the instagram is connected and ready to use {existing}"
        log_tool_event(
            tool_name="instagram_auth_verification",
            status="success",
            params={},
            parent_node="instagram_agent_node",
            tool_output=ToolOutput(output=tool_output).to_dict(),
        )
        return tool_output
    else:
        tool_output = (
            "Instagram account is not connected ask the user to connect or `END`"
        )
        log_tool_event(
            tool_name="instagram_auth_verification",
            status="failed",
            params={},
            parent_node="instagram_agent_node",
            tool_output=ToolOutput(output=tool_output).to_dict(),
        )
        return tool_output


@tool("profile_insight")
async def profile_insight(config: RunnableConfig):
    """
    Fetch profile insights such as followers, following, engagement rate, etc.
    Use this tool whenever you need Instagram profile insights.
    You don't need anything to get profile.
    """
    user_id = get_user_id(config)

    existing = (
        supabase.table("connected_accounts")
        .select("platform_user_id")
        .eq("provider_id", user_id)
        .eq("platform", "instagram")
        .execute()
    )

    if existing.data:
        platform_user_id = existing.data[0]["platform_user_id"]
        log_tool_event(
            tool_name="profile_insight",
            status="started",
            params={"platform_user_id": platform_user_id},
            parent_node="instagram_agent_node",
        )

        tool_output = await instagram_profile.getInstagramInsight(platform_user_id)
        
        log_tool_event(
            tool_name="profile_insight",
            status="success",
            params={},
            parent_node="instagram_agent_node",
            tool_output=ToolOutput(output=tool_output).to_dict(),
        )
        return tool_output
    else:
        tool_output = "No instagram account found connected ask the user to connect it"
        log_tool_event(
            tool_name="profile_insight",
            status="success",
            params={},
            parent_node="instagram_agent_node",
            tool_output=ToolOutput(output=tool_output).to_dict(),
        )
        return tool_output


@tool("ask_human")
def ask_human(params: str = Field(..., description="What to ask the human")) -> str:
    """
    Ask the human user for additional input or confirmation.
    Only call this tool when you have valid evidence that specific input data is required—do not assume.
    For example, do not ask for an ID or any other detail unless the requirement has already been explicitly mentioned.
    This tool is used when the Instagram agent does not have enough information to proceed or when explicit confirmation from the user is necessary.
    """
    interrupt_request = InterruptRequest.create_input_field(
        name="ask_human",
        title=params
    )
    
    user_input = interrupt(interrupt_request.to_dict())
    return str(user_input)


@tool("instagram_error")
def instagram_error(params: str = Field(..., description="error reason")) -> str:
    """
    Ask the user to solve the error.
    The error could be related to the authentication.
    Ask the user to connect the instagram account.
    """
    interrupt_request = InterruptRequest.create_connect(
        name="instagram_error",
        platform="instagram",
        title=params,
        content=""
    )
    
    user_input = interrupt(interrupt_request.to_dict())
    return str(user_input)


def get_instagram_tool_registry() -> NodeRegistry:
    """
    Returns a NodeRegistry containing all Instagram tools.
    This function centralizes tool registration.
    """
    instagram_tool_register = NodeRegistry()
    instagram_tool_register.add("instagram_auth_verification", instagram_auth_verification, "tool")
    instagram_tool_register.add("profile_insight", profile_insight, "tool")
    instagram_tool_register.add("ask_human", ask_human, "tool")
    instagram_tool_register.add("instagram_error", instagram_error, "tool")
    return instagram_tool_register
