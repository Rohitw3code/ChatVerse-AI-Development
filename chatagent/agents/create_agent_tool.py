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
    llm: "BaseChatModel",
    members: NodeRegistry,
    prompt: str | None = None,
    node_name: str = "agent_tool_node",
    parent_node: str = "main_supervisor",
    handoff: bool = False,
):

    system_prompt = (
        "You are an agent that can choose and call the following tools when needed.\n"
        f"{members.prompt_block('agent')}\n"
        "Decide which tool to call next based on the user request and context.\n"
        "If no tool is needed, respond normally.\n"
        "if you dont have the capability just say it"
        "You must mention with proper format what you got the data from the tool you called"
    )

    async def agent_tool_node(state: State) -> Command[Literal[parent_node]]:
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
                    "messages": state.get("messages", []) + [AIMessage(content="Using instagram_agent_node Node to get information")],
                    "reason": f"I need to execute the {node_name}",
                    "next_node": "tool",
                    "node_type": "agent",
                    "type": "executor",
                    "next_type": "tool",
                    "status": "started",
                    "params": {},
                    "tool_output": ToolOutput().to_dict(),
                    "usages": {},
                }
            }
        )
        
        recent_messages = state["messages"]
        sanitized_messages = []
        for i, msg in enumerate(recent_messages):
            if isinstance(msg, ToolMessage):
                if i > 0 and isinstance(recent_messages[i-1], AIMessage) and getattr(recent_messages[i-1], "tool_calls", None):
                    sanitized_messages.append(msg)
                else:
                    continue
            else:
                sanitized_messages.append(msg)

        messages = [SystemMessage(content=system_prompt)] + sanitized_messages
        
        with get_openai_callback() as cb:
            ai_msg: AIMessage = await llm.bind_tools(members.runs()).ainvoke(
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
                    
                    # <<< START OF ROBUST FIX >>>
                    # Safely find the actual callable to inspect its signature.
                    func_to_inspect = None
                    if hasattr(tool_to_run, 'func') and callable(tool_to_run.func):
                        # Handles standard LangChain Tool objects
                        func_to_inspect = tool_to_run.func
                    elif callable(tool_to_run):
                        # Handles raw functions or other callable objects (like graph nodes)
                        func_to_inspect = tool_to_run

                    # Only inspect if we found a valid callable function.
                    if func_to_inspect:
                        try:
                            sig = inspect.signature(func_to_inspect)
                            if 'state' in sig.parameters:
                                tool_input['state'] = state
                        except TypeError:
                            # Failsafe for unusual callables that inspect can't handle.
                            print(f"Warning: Could not inspect signature for tool {name}. Proceeding without state injection.")
                    # <<< END OF ROBUST FIX >>>
                        
                    out = await tool_to_run.ainvoke(
                        tool_input, config={"callbacks": [callback_handler]}
                    )
                    print("\n\ntool calling : ", out)
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
                    "node_type": "agent",
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
                    "node_type": "agent",
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