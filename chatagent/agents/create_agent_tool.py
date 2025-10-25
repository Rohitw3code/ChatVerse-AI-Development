from chatagent.utils import State, usages, sanitize_messages
from langchain_core.messages import AIMessage, ToolMessage, SystemMessage, HumanMessage
from langgraph.types import Command
from langchain_community.callbacks.openai_info import OpenAICallbackHandler
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
        description=(
            "Decide whether to RETRY or END based on these rules:\n"
            "- RETRY: If agent has sufficient tools available AND (data is insufficient/incomplete OR error occurred OR authentication needed) AND retry attempts < 2 AND current task is NOT completed\n"
            "- END: If no suitable tools available OR current task completed successfully OR max retries reached OR repeated failures OR task cannot be completed with available tools\n"
            "Consider: Does agent have right tools for the CURRENT TASK? Did tool fail or return incomplete data FOR THE CURRENT TASK? Can retrying help complete the CURRENT TASK? Have we already retried?\n"
            "IMPORTANT: Always consider the current task context. Only RETRY if it directly helps complete the current task.\n"
            "Be conservative - only RETRY if there's a clear path to success for the current task."
        )
    )
    reason: str = Field(
        description="Explanation of why the agent decided to transition to the specified next node, specifically referencing the current task status."
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
        "never call any tool related to login auth or connection issues. if there is no error or token expire or without user query "
        "login tool should be called when there is an auth issue or token expire or connection issue only or user asked to do it"
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
                    "current_message": [AIMessage(content=f"Using {node_name} Node to get information")],
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
        sanitized_messages = sanitize_messages(recent_messages)

        messages = [SystemMessage(content=system_prompt)] + sanitized_messages

        # print("\n\ncurrent task : ",state.get("current_task","NO TASK"))

        # print("\n\n\n[BIND TOOL ] ",members.runs(), "\n\n\n")
        
        ai_msg: AIMessage = await stream_llm.bind_tools(members.runs()).ainvoke(
            messages, config={"callbacks": [callback_handler]}
        )

        # print("\n\n\n[AGENT TOOL NODE] LLM Message:", ai_msg, "\n\n\n")

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
        recent_for_decision = state.get("messages", [])[-10:] if len(state.get("messages", [])) > 10 else state.get("messages", [])
        
        # Sanitize recent messages to remove orphaned tool calls/messages
        sanitized_recent = sanitize_messages(recent_for_decision)
        
        # Add current ai_msg and tool_results (they form a valid pair)
        if tool_results:
            decision_messages = sanitized_recent + [ai_msg] + tool_results
        else:
            decision_messages = sanitized_recent + [ai_msg]
        
        # Add current task context to help decision making
        current_task = state.get("current_task", "NO TASK")
        task_context_message = SystemMessage(
            content=f"CURRENT TASK CONTEXT: {current_task}\n\n"
                    f"Evaluate if the current task '{current_task}' has been completed or needs retry based on the tool execution results. "
                    f"Only RETRY if the tools can help complete THIS SPECIFIC TASK. "
                    f"If the task is complete or cannot be completed with available tools, choose END."
        )
        decision_messages = [task_context_message] + decision_messages
        
        decision: AgentDecision = stream_llm.with_structured_output(AgentDecision).invoke(
            decision_messages
        )

        print("\n\n\n[AGENT TOOL NODE] Decision:", decision, "\n\n\n")

        if tool_output and decision.next_node == "RETRY":
            return Command(
                goto=node_name,
                update={
                    "input": state["input"],
                    "messages": [ai_msg] + tool_results,
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
                    "messages": [ai_msg] + tool_results if tool_results else [ai_msg],
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