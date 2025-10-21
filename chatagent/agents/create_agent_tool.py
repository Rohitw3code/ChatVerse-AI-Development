from chatagent.utils import State, usages
from langchain_core.messages import AIMessage, ToolMessage
from typing import Literal
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import END
from langgraph.types import Command
from chatagent.utils import State
from langchain_core.messages import AIMessage, ToolMessage,SystemMessage
import inspect
from typing import Literal
from langchain_community.callbacks.openai_info import OpenAICallbackHandler
from chatagent.utils import usages
from langgraph.config import get_stream_writer
from chatagent.node_registry import NodeRegistry
from chatagent.model.tool_output import ToolOutput
from langchain_core.runnables import RunnableConfig
from langchain_community.callbacks import get_openai_callback


callback_handler = OpenAICallbackHandler()
import json

def make_agent_tool_node(
    members: NodeRegistry,
    prompt: str | None = None,
    node_name: str = "agent_tool_node",
    parent_node: str = "task_dispatcher"
):

    print("agent ===> ", members.prompt_block('agent'))

    system_prompt = (
        "You are an agent capable of choosing and using various tools to complete tasks.\n"
        f"{members.prompt_block('agent')}\n\n"
        "AUTHENTICATION & CONNECTION HANDLING:\n"
        "- If you encounter authentication/connection errors (token expired, not connected, not authenticated), "
        "FIRST check if there's a verification/login/connection tool available (e.g., 'verify_gmail_connection', "
        "'instagram_auth_verification') and call it to attempt reconnection.\n"
        "- If the verification tool indicates the account is NOT connected and there's no automatic login tool, "
        "respond with: 'Need to login first' and do NOT call any other tools.\n"
        "- If reconnection succeeds, retry the original task.\n\n"
        "RETRY LOGIC:\n"
        "- If a tool does not return useful data, you may retry the SAME tool up to 3 times max "
        "with slightly different parameter values to improve the results.\n"
        "- Always state which tool you used and summarize the final result.\n"
        "- If a tool still fails after retries, continue gracefully or report failure.\n"
        "- If no tool is needed, respond normally.\n"
    )

    async def agent_tool_node(state: State) -> Command[Literal[parent_node]]:
        # Import stream_llm for regular text generation with tools
        from chatagent.config.init import stream_llm
        
        writer = get_stream_writer()
        writer(
            {
                node_name: {
                    "current_message": [
                        {
                            "role": "ai",
                            "content": f"Using {node_name} Node to get information ",
                        }
                    ],
                    "messages": state.get("messages", []) + [AIMessage(content="Using {node_name} Node to get information")],
                    "reason": f"I need to execute the {node_name}",
                    "next_node": "tool",
                    "type": "agent",
                    "next_type": "tool",
                    "status": "started",
                    "params": {},
                    "tool_output": ToolOutput().to_dict(),
                    "usages": {},
                }
            }
        )
        
        messages = [SystemMessage(content=system_prompt), *state["messages"]]        
        
        print("agent tool runs : ", members.runs())

        with get_openai_callback() as cb:
            print("members tools : ", members.runs())
            ai_msg: AIMessage = await stream_llm.bind_tools(members.runs()).ainvoke(
                    messages, config={"callbacks": [callback_handler]}
                )

        usages_data = usages(cb)
        tools = members.tools()
        out = None

        tool_results: list[ToolMessage] = []
        tools_info = []

        if getattr(ai_msg, "tool_calls", None):
            for tc in ai_msg.tool_calls:
                name = tc.get("name")
                args = tc.get("args", {})
                tool_id = tc.get("id")

                if name in tools:
                    tool_to_run = tools[name]
                    tool_input = {**args}
                    func_to_inspect = None
                    if hasattr(tool_to_run, 'func') and callable(tool_to_run.func):
                        func_to_inspect = tool_to_run.func
                    elif callable(tool_to_run):
                        func_to_inspect = tool_to_run

                    if func_to_inspect:
                        try:
                            sig = inspect.signature(func_to_inspect)
                            if 'state' in sig.parameters:
                                tool_input['state'] = state
                        except TypeError:
                            print(f"Warning: Could not inspect signature for tool {name}. Proceeding without state injection.")
                    try:
                        out = await tool_to_run.ainvoke(
                            tool_input, config={"callbacks": [callback_handler]}
                        )
                        print("\n\ntool calling : ", out)
                        if isinstance(out, str):
                            auth_keywords = ['not connected', 'not authenticated', 'token expired', 
                                           'authentication required', 'need to connect', 'account is not connected']
                            out_lower = out.lower()
                            
                            if any(keyword in out_lower for keyword in auth_keywords):
                                verification_tools = {
                                    'gmail': 'verify_gmail_connection',
                                    'instagram': 'instagram_auth_verification',
                                    'email': 'verify_gmail_connection'
                                }
                                platform = None
                                for plat, tool_name in verification_tools.items():
                                    if plat in name.lower() or plat in out_lower:
                                        platform = plat
                                        break
                                if platform and verification_tools.get(platform) in tools:
                                    out = f"{out}\n\n💡 Hint: Try calling '{verification_tools[platform]}' tool first to check/reconnect the {platform} account."
                                else:
                                    out = f"{out}\n\n⚠️ Need to login first - no automatic connection tool available."
                                    
                    except Exception as e:
                        error_message = f"Tool '{name}' failed: {type(e).__name__}: {str(e)}"
                        print(f"\n\nTool execution error: {error_message}")
                        
                        error_str = str(e).lower()
                        auth_error_keywords = ['authentication', 'unauthorized', 'token', 'credentials', 
                                              'not authenticated', 'access denied', 'permission denied']
                        
                        if any(keyword in error_str for keyword in auth_error_keywords):
                            out = f"❌ Authentication Error: {type(e).__name__} - {str(e)}\n\n⚠️ Need to login first."
                        else:
                            out = f"❌ Error executing {name}: {type(e).__name__} - {str(e)}"
                else:
                    out = {"error": "bad tool name, retry"}

                if isinstance(out, (dict, list)):
                    out_str = json.dumps(out, ensure_ascii=False)
                    out_for_storage = out
                else:
                    out_str = str(out)
                    out_for_storage = out_str

                tool_msg = ToolMessage(
                    tool_call_id=tool_id,
                    name=name,
                    content=out_str
                )
                tool_results.append(tool_msg)

                tools_info.append({
                    "name": name,
                    "tool_call_id": tool_id,
                    "output": out_for_storage,
                    "id": getattr(tool_msg, "id", None),
                })

        tool_output = ToolOutput(output={"tools": tools_info}).to_dict()

        if tool_results:
            return Command(
                goto=node_name,
                update={
                    "input": state["input"],
                    "messages": state.get('messages',[])+[ai_msg] + tool_results,
                    "current_message": tool_results,
                    "reason": ai_msg.content,
                    "provider_id": state.get("provider_id"),
                    "next_node": node_name,
                    "type": "executor",
                    "next_type": "agent",
                    "tool_output": tool_output,
                    "usages": usages_data,
                    "plans": state.get("plans", []),
                    "current_task": state.get("current_task", "NO TASK"),
                    "max_message": state.get("max_message", 10),
                    # mark as in progress while tools are being executed
                    "task_status": "in_progress",
                },
            )
        else:
            return Command(
                goto=parent_node,
                update={
                    "input": state["input"],
                    "messages": [ai_msg],
                    "current_message": [ai_msg],
                    "reason": ai_msg.content,
                    "provider_id": state.get("provider_id"),
                    "next_node": parent_node,
                    "type": "thinker",
                    "next_type": "supervisor",
                    "tool_output": tool_output,
                    "usages": usages_data,
                    "plans": state.get("plans", []),
                    "current_task": state.get("current_task", "NO TASK"),
                    "max_message": state.get("max_message", 10),
                    # agent did not request any tools -> assume task done
                    "task_status": "completed",
                },
            )

    if prompt:
        agent_tool_node.__doc__ = prompt

    agent_tool_node.__name__ = node_name
    return agent_tool_node