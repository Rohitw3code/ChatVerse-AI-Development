from chatagent.utils import State, usages
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.graph import END
from langgraph.types import Command
from chatagent.utils import State
from langchain_core.messages import AIMessage, ToolMessage,SystemMessage
from langchain_community.callbacks.openai_info import OpenAICallbackHandler
from chatagent.utils import usages
from langgraph.config import get_stream_writer
from chatagent.node_registry import NodeRegistry
from chatagent.model.tool_output import ToolOutput
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
        "You are a helpful agent. Choose the best single tool based on the user's request and the tool descriptions.\n"
        "If no tool is needed, respond normally. Keep it simple.\n\n"
        "Available tools (name [type]: description):\n"
        f"{members.prompt_block('agent')}\n\n"
        "Auth handling (simple):\n"
        "- If a tool output or error indicates token expired / not connected / not authenticated,\n"
        "  first try a verify-connection tool (name contains 'verify' and 'connection'). If not available,\n"
        "  call a login/connect tool (name contains 'login' or 'connect'). Then continue the task.\n"
    )

    async def agent_tool_node(state: State) -> Command:
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
        
        messages = [*state.get("messages", []),SystemMessage(content=system_prompt)]
        
        print("agent tool runs : ", members.runs())

        with get_openai_callback() as cb:
            print("members tools : ", members.runs())
            ai_msg: AIMessage = await stream_llm.bind_tools(members.runs()).ainvoke(
                    messages, config={"callbacks": [callback_handler]}
                )

        print("\n\nAI Message from agent tool node:", ai_msg,"\n\n")

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

                    out = await tool_to_run.ainvoke(
                        tool_input, config={"callbacks": [callback_handler]}
                    )

                    print(f"\n\nTool '{name}' executed successfully with output: {out}\n\n")

                    # Normalize output to string for checks/storage
                    if isinstance(out, (dict, list)):
                        out_str = json.dumps(out, ensure_ascii=False)
                        out_for_storage = out
                    else:
                        out_str = str(out)
                        out_for_storage = out_str

                    # Append the original tool result; the LLM will see it and decide next steps (e.g., verify/login)
                    tool_results.append(
                        ToolMessage(tool_call_id=tool_id, name=name, content=out_str)
                    )
                    tools_info.append(
                        {
                            "name": name,
                            "tool_call_id": tool_id,
                            "output": out_for_storage,
                            "id": None,
                        }
                    )
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
                # The above block already appends a ToolMessage for known tools.
                # Only append this generic message for unknown tool branch.
                if name not in tools:
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
                    "messages": state.get('messages', []) + [ai_msg] + tool_results,
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
                    "task_status": "completed",
                },
            )

    if prompt:
        agent_tool_node.__doc__ = prompt

    agent_tool_node.__name__ = node_name
    return agent_tool_node