from chatagent.utils import State, usages
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.graph import END
from langgraph.types import Command
from chatagent.utils import State
from langchain_core.messages import AIMessage, ToolMessage, SystemMessage, HumanMessage
from langchain_community.callbacks.openai_info import OpenAICallbackHandler
from chatagent.utils import usages
from langgraph.config import get_stream_writer
from chatagent.node_registry import NodeRegistry
from chatagent.model.tool_output import ToolOutput
from chatagent.config.init import stream_llm
from typing import Literal
import inspect
from pydantic import BaseModel, Field


callback_handler = OpenAICallbackHandler()
import json

class AgentDecision(BaseModel):
    """Model for agent decision making."""
    next_node:Literal['END','RETRY']  = Field(
        description="if a same tool is called multiple times in a row output END else RETRY"
    )
    reason: str = Field(
        description="Explanation of why the agent decided to transition to the specified next node."
    )


def make_agent_tool_node(
    members: NodeRegistry,
    prompt: str | None = None,
    node_name: str = "agent_tool_node",
    parent_node: str = "task_dispatcher_node"
):

    system_prompt = (
        "You are an agent that can choose and call the following tools when needed.\n"
        f"{members.prompt_block('agent')}\n"
        "Decide which tool to call next based on the user request and context.\n"
        "If no tool is needed, respond normally.\n"
        "if you dont have the capability just say it"
        "Your is only to call tools not to perform any plan task just focus on tool calling and current task"
        "if there a tool fialed to get relavant data you can try calling it again max 2 times"
        "if there is token expire or auth issue or error you must check for any connect or login tool available and call it to fix the issue"
        "You must mention with proper format what you got the data from the tool you called"
    )


    async def agent_tool_node(state: State) -> Command[Literal["task_dispatcher_node"] | str]:
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
                    "next_node_type": "tool",
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
        
        # Sanitize messages to handle orphaned tool_calls and ToolMessages
        sanitized_messages = []
        i = 0
        while i < len(recent_messages):
            msg = recent_messages[i]
            
            # Handle AIMessage with tool_calls
            if isinstance(msg, AIMessage) and hasattr(msg, "tool_calls") and msg.tool_calls:
                # Check if next message(s) are ToolMessages
                has_tool_response = False
                if i + 1 < len(recent_messages) and isinstance(recent_messages[i + 1], ToolMessage):
                    has_tool_response = True
                
                if has_tool_response:
                    # Include AIMessage and its ToolMessage responses
                    sanitized_messages.append(msg)
                    i += 1
                    while i < len(recent_messages) and isinstance(recent_messages[i], ToolMessage):
                        sanitized_messages.append(recent_messages[i])
                        i += 1
                    continue
                else:
                    # Create a copy without tool_calls
                    msg_copy = AIMessage(content=msg.content if msg.content else "Continuing...")
                    sanitized_messages.append(msg_copy)
            elif isinstance(msg, ToolMessage):
                # Skip orphaned ToolMessages (already handled above)
                pass
            else:
                # Regular message
                sanitized_messages.append(msg)
            
            i += 1

        messages = [SystemMessage(content=system_prompt)] + sanitized_messages

        print("\n\n\n[BIND TOOL ] ",members.runs(), "\n\n\n")
        
        ai_msg: AIMessage = await stream_llm.bind_tools(members.runs()).ainvoke(
            messages, config={"callbacks": [callback_handler]}
        )

        print("\n\n\n[AGENT TOOL NODE] LLM Message:", ai_msg, "\n\n\n")

        usages_data = usages(callback_handler)
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
                        # Handles standard LangChain Tool objects
                        func_to_inspect = tool_to_run.func
                    elif callable(tool_to_run):
                        # Handles raw functions or other callable objects (like graph nodes)
                        func_to_inspect = tool_to_run

                    if func_to_inspect:
                        sig = inspect.signature(func_to_inspect)
                        if 'state' in sig.parameters:
                            tool_input['state'] = state
                        
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

        # For decision making, only use recent messages to avoid context overflow
        # and ensure proper message pairing
        decision_messages = []
        recent_for_decision = state.get("messages", [])[-10:] if len(state.get("messages", [])) > 10 else state.get("messages", [])
        
        # Add current ai_msg and tool_results (they form a valid pair)
        if tool_results:
            decision_messages = recent_for_decision + [ai_msg] + tool_results
        else:
            decision_messages = recent_for_decision + [ai_msg]
        
        decision: AgentDecision = stream_llm.with_structured_output(AgentDecision).invoke(
            decision_messages
        )

        print("\n\n\n[AGENT TOOL NODE] Decision:", decision, "\n\n\n")

        if tool_results and decision.next_node == "RETRY":
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
                    "next_node_type": "agent",
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
                    "messages": state.get('messages', []) + [ai_msg] + tool_results,
                    "current_message": [ai_msg] + tool_results if tool_results else [ai_msg],
                    "reason": ai_msg.content,
                    "provider_id": state.get("provider_id"),
                    "next_node": parent_node,
                    "node_type": "agent",
                    "next_node_type": "supervisor",
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