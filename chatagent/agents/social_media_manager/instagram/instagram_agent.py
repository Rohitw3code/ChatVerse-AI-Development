from chatagent.node_registry import NodeRegistry
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from chatagent.agents.create_agent_tool import make_agent_tool_node
from chatagent.utils import log_tool_event
from langgraph.types import interrupt
from chatagent.agents.social_media_manager.instagram import instagram_profile
from supabase_client import supabase
from chatagent.model.tool_output import ToolOutput
from chatagent.utils import get_user_id
from langchain_core.runnables import RunnableConfig
from typing_extensions import Annotated
from langgraph.prebuilt import InjectedState

@tool("ask_human")
def ask_human(
    params: str = Field(...,
                        description="What clarification is needed from the user")
) -> str:
    """
    Ask the human user for additional input or confirmation.
    Only call this tool when you have valid evidence that specific input data is required—do not assume.
    For example, do not ask for an ID or any other detail unless the requirement has already been explicitly mentioned.
    This tool is used when the Instagram agent does not have enough information to proceed or when explicit confirmation from the user is necessary.
    """
    user_input = interrupt(
        {"name": "ask_human", "type": "input_field", "data": {"title": params}}
    )
    return str(user_input)


@tool("instagram_error")
def instagram_error(params: str = Field(...,
                                        description="error reason")) -> str:
    """
    Ask the user to solve the error
    the error could be related to the authentication
    ask the user to connect the instagram account
    """
    user_input = interrupt(
        {
            "name": "instagram_error",
            "type": "connect",
            "platform": "instagram",
            "data": {"title": params, "content": ""},
        }
    )
    return str(user_input)


@tool("instagram_auth_verification")
def instagram_auth_verification(config: RunnableConfig, state: Annotated[dict, InjectedState],):
    """
    This tool is to to verify the instagram connection if a user has connected the account or not
    this tool always used when user ask for any instagram related task which required instagram api
    """
    user_id = get_user_id(config)


    print("insta verify pid : ", user_id)
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
    You dont need anything to get profile
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


instagram_tool_register = NodeRegistry()
instagram_tool_register.add("profile_insight", profile_insight, "tool")
instagram_tool_register.add("ask_human", ask_human, "tool")
instagram_tool_register.add(
    "instagram_auth_verification", instagram_auth_verification, "tool"
)
instagram_tool_register.add("instagram_error", instagram_error, "tool")


instagram_agent_node = make_agent_tool_node(
    members=instagram_tool_register,
    prompt=(
        "You are an Instagram agent with access to the following tools:\n"
        "- profile_insight: Get account-level statistics (followers, following, engagement rate, bio).\n"
        "- posts_data: Get recent posts with captions, likes, and comments.\n"
        "- instagram_error: Ask the user to resolve authentication issues (e.g., connect Instagram account).\n"
        "- instagram_auth_verification: Verify if the Instagram account is connected and ready to use.\n"
        "- ask_human: Ask the user directly if you need clarification or extra information.\n\n"
        "Guidelines:\n"
        "1. Do not assume anything. If something is unclear, always use `ask_human` to clarify.\n"
        "2. If an Instagram account is required but not connected, first use `instagram_auth_verification`. "
        "If not connected, then call `instagram_error` to request user action.\n"
        "3. Choose the correct tool based on the user request. "
        "Use `profile_insight` or `posts_data` only after verifying authentication.\n"
        "4. Always return results clearly and concisely."),
    node_name="instagram_agent_node",
    parent_node="task_dispatcher_node",
)
