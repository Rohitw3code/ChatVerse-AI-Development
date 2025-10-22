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
from langchain_community.callbacks import get_openai_callback
from pydantic import BaseModel, Field
from chatagent.config.init import stream_llm
from typing import Literal



callback_handler = OpenAICallbackHandler()
import json


class AgentDecision(BaseModel):
    """Decision model for determining agent's next action after tool execution."""
    
    next_action: Literal["continue", "complete"] = Field(
        description=(
            "'continue' - Need to call another tool or retry with different parameters. "
            "Use when: authentication failed, no results found (can retry max 2 times), "
            "tool returned empty/null data, or multi-step task requires next action. "
            "'complete' - Current task is done, return to dispatcher. "
            "Use when: tool succeeded with data, max retries reached, or task accomplished."
        )
    )
    
    reason: str = Field(
        description=(
            "Brief explanation for the decision. "
            "If continuing: explain what action/retry is needed. "
            "If completing: summarize result or why stopping."
        )
    )

def make_agent_tool_node(
    members: NodeRegistry,
    prompt: str | None = None,
    node_name: str = "agent_tool_node",
    parent_node: str = "task_dispatcher"
):

    print("agent ===> ", members.prompt_block('agent'))

    system_prompt = (
        "You are a strict tool-selection agent. Your ONLY job is to choose the single most appropriate tool "
        "for the CURRENT user task based on the provided tool descriptions.\n\n"
        "CRITICAL: You execute ONE tool call for the current task, then IMMEDIATELY exit. "
        "Do NOT call the same tool again. Do NOT process next tasks. "
        "The task dispatcher will handle what comes next.\n\n"
        "Focus only on the CURRENT task — do not plan, anticipate, or think about future or other tasks.\n"
        "If no tool is needed, respond directly without calling any tool.\n\n"
        "Tool Selection Rules:\n"
        "- Call EXACTLY ONE tool for the current task, then stop.\n"
        "- Do NOT call the same tool repeatedly.\n"
        "- Do NOT attempt to process multiple tasks or plan ahead.\n"
        "- After tool execution, your job is DONE — let the dispatcher decide what's next.\n\n"
        "Available tools (name [type]: description):\n"
        f"{members.prompt_block('agent')}\n"
    )


    async def agent_tool_node(state: State) -> Command[Literal["task_dispatcher_node",node_name]]:   
        agent_call_count = state.get("agent_call_count", 0) + 1
        max_agent_calls = 3  # Maximum consecutive calls before forcing completion
        
        # Track retry attempts for tools that return no results
        tool_retry_count = state.get("tool_retry_count", 0)
        max_tool_retries = 2  # Maximum retries for tools returning no results
        
        print(f"\n🔄 Agent call count: {agent_call_count}/{max_agent_calls}")
        print(f"🔁 Tool retry count: {tool_retry_count}/{max_tool_retries}\n")
        
        # Force completion if max calls reached
        if agent_call_count > max_agent_calls:
            print(f"⚠️ Max agent calls ({max_agent_calls}) reached. Forcing task completion.\n")
            return Command(
                goto=parent_node,
                update={
                    "input": state["input"],
                    "messages": state.get('messages', []) + [
                        AIMessage(content=f"Task completed after {max_agent_calls} attempts.")
                    ],
                    "current_message": [AIMessage(content="Max attempts reached, moving to next task")],
                    "reason": f"Maximum agent calls reached ({max_agent_calls}), task considered complete",
                    "provider_id": state.get("provider_id"),
                    "next_node": parent_node,
                    "type": "executor",
                    "next_type": "supervisor",
                    "tool_output": state.get("tool_output", ToolOutput().to_dict()),
                    "usages": {},
                    "plans": state.get("plans", []),
                    "current_task": state.get("current_task", "NO TASK"),
                    "max_message": state.get("max_message", 10),
                    "task_status": "completed",
                    "agent_call_count": 0,  # Reset counter
                    "tool_retry_count": 0,  # Reset retry counter
                },
            )
        
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

        # If tools were executed, use decision model to determine next action
        if tool_results:
            # Use Pydantic model to decide next action based on task completion
            from chatagent.config.init import non_stream_llm
            
            # Check if tool returned no/empty results (for retry logic)
            has_empty_results = False
            for tool_info in tools_info:
                output = tool_info.get("output", {})
                # Check for empty, null, or no-data indicators
                if output in [None, "", [], {}]:
                    has_empty_results = True
                elif isinstance(output, dict):
                    if output.get("error") or output.get("data") in [None, [], {}]:
                        has_empty_results = True
                elif isinstance(output, str):
                    lower_output = output.lower()
                    if any(indicator in lower_output for indicator in 
                           ["no results", "not found", "no data", "empty", "no items", "none found"]):
                        has_empty_results = True
            
            decision_prompt = (
                "You are an intelligent task completion evaluator. "
                "Analyze the current task, tool execution results, and retry count "
                "to decide if the task is complete or needs more work.\n\n"
                "IMPORTANT Guidelines:\n"
                "- If tool returned NO RESULTS/EMPTY DATA:\n"
                f"  • Current retry count: {tool_retry_count}/{max_tool_retries}\n"
                "  • If retry count < 2: choose 'continue' to retry with DIFFERENT parameters\n"
                "  • If retry count >= 2: choose 'complete' (max retries reached)\n"
                "- If tool returned SUCCESSFUL DATA: choose 'complete'\n"
                "- If authentication/connection failed: choose 'continue' to retry\n"
                "- If multi-step task needs next action: choose 'continue'\n"
                "- Do NOT continue just to 'verify' or 'confirm' success\n"
                "- Do NOT continue to process next tasks (dispatcher's job)\n\n"
                f"Current Task: {state.get('current_task', 'NO TASK')}\n"
                f"Tool Results: {json.dumps(tools_info, indent=2)}\n"
                f"Has Empty Results: {has_empty_results}\n"
                f"Retry Count: {tool_retry_count}/{max_tool_retries}\n"
                f"Conversation History: {len(state.get('messages', []))} messages\n"
            )

            decision_messages = [
                SystemMessage(content=decision_prompt),
                HumanMessage(content="Evaluate if the current task is complete or needs continuation/retry.")
            ]

            with get_openai_callback() as cb_decision:
                decision: AgentDecision = non_stream_llm.with_structured_output(AgentDecision).invoke(
                    decision_messages
                )
            
            print(f"\n\n🤔 Agent Decision: {decision.next_action} - {decision.reason}\n")
            
            # Determine if this is a retry scenario
            should_increment_retry = has_empty_results and decision.next_action == "continue"
            new_tool_retry_count = (tool_retry_count + 1) if should_increment_retry else tool_retry_count
            
            # Force complete if max retries reached
            if should_increment_retry and new_tool_retry_count > max_tool_retries:
                print(f"⚠️ Max tool retries ({max_tool_retries}) reached. Forcing completion.\n")
                decision.next_action = "complete"
                decision.reason = f"No results found after {max_tool_retries} retry attempts"
                new_tool_retry_count = 0
            
            # Determine routing based on decision
            if decision.next_action == "continue":
                # Agent needs to continue working - return to self
                return Command(
                    goto=node_name,
                    update={
                        "input": state["input"],
                        "messages": state.get('messages', []) + [ai_msg] + tool_results,
                        "current_message": tool_results,
                        "reason": decision.reason,
                        "provider_id": state.get("provider_id"),
                        "next_node": node_name,
                        "type": "executor",
                        "next_type": "agent",
                        "tool_output": tool_output,
                        "usages": {**usages_data, **usages(cb_decision)},
                        "plans": state.get("plans", []),
                        "current_task": state.get("current_task", "NO TASK"),
                        "max_message": state.get("max_message", 10),
                        "task_status": "in_progress",
                        "agent_call_count": agent_call_count,  # Increment counter
                        "tool_retry_count": new_tool_retry_count,  # Update retry counter
                    },
                )
            else:
                # Task complete - return to parent dispatcher
                return Command(
                    goto=parent_node,
                    update={
                        "input": state["input"],
                        "messages": state.get('messages', []) + [ai_msg] + tool_results,
                        "current_message": tool_results,
                        "reason": decision.reason,
                        "provider_id": state.get("provider_id"),
                        "next_node": parent_node,
                        "type": "executor",
                        "next_type": "supervisor",
                        "tool_output": tool_output,
                        "usages": {**usages_data, **usages(cb_decision)},
                        "plans": state.get("plans", []),
                        "current_task": state.get("current_task", "NO TASK"),
                        "max_message": state.get("max_message", 10),
                        "task_status": "completed",
                        "agent_call_count": 0,  # Reset counter when returning to dispatcher
                        "tool_retry_count": 0,  # Reset retry counter
                    },
                )
        else:
            # No tools were called - return to parent with completion status
            return Command(
                goto=parent_node,
                update={
                    "input": state["input"],
                    "messages": state.get('messages', []) + [ai_msg],
                    "current_message": [ai_msg],
                    "reason": ai_msg.content or "Task completed without tool usage",
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
                    "agent_call_count": 0,  # Reset counter
                    "tool_retry_count": 0,  # Reset retry counter
                },
            )

    if prompt:
        agent_tool_node.__doc__ = prompt

    agent_tool_node.__name__ = node_name
    return agent_tool_node