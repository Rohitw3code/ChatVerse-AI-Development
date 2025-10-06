from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langgraph.graph import END
from langgraph.types import Command
from chatagent.utils import State, usages
from typing import List, Optional
from chatagent.node_registry import NodeRegistry
from langchain_community.callbacks.openai_info import OpenAICallbackHandler
from langchain_core.runnables import RunnableConfig

callback_handler = OpenAICallbackHandler()


def make_supervisor_node(
    llm: BaseChatModel,
    registry: NodeRegistry,
    node_name: str,
    goto_end_symbol: str,
    prompt: str = ""
):
    
    special_commands = ['BACK', 'NEXT_TASK']
    members = registry.members() + special_commands
    router_members = registry.members()

    system_prompt = f"""<prompt>
        <role>You are {node_name}, a supervisor. Decide the next best step in the workflow.</role>
        <supervisor_instructions>{prompt}</supervisor_instructions>
        <output_format>
            Your response MUST be a single, valid JSON object with keys "next" and "reason".
        </output_format>
        <instructions>
            <rule id="1">Analyze the current task and route to the node from `<available_nodes>` that is best equipped to handle it.</rule>
            <rule id="2">If the task is incomplete and a previous supervisor can help, select 'BACK' to escalate.</rule>
            <rule id="3">If the current task is fully completed, select 'NEXT_TASK' to get the next plan from the replanner.</rule>
            <rule id="4">If no available node can handle the request, you must select 'BACK'.</rule>
        </instructions>
        <available_nodes>{registry.prompt_block("Supervisor")}</available_nodes>
        <allowed_choices>The "next" value must be one of the following exact strings: {members}</allowed_choices>
    </prompt>"""

    class Router(BaseModel):
        
        next: str = Field(
            ...,
            description="Exact node name to call next, or 'BACK', or 'NEXT_TASK' to handle special commands.")
        reason: str = Field(..., description="Why this next step was chosen.")

        @field_validator("next")
        @classmethod
        def validate_next(cls, v: str) -> str:
            if not v or not v.strip():
                raise ValueError("'next' must not be empty")
            v = v.strip()
            if v not in members:
                print(f"[WARN] Invalid next='{v}', falling back to BACK")
                return "BACK"
            return v

    def supervisor_node(state: State) -> Command[Literal[*router_members]]:
        
        # Guardrail counters
        back_count = state.get("back_count", 0)
        max_back = state.get("max_back", 2)

        # If the current task was marked completed by an agent, auto-advance
        if state.get("task_status") == "completed":
            done_msg = AIMessage(content="Task completed. Advancing to the next task.")
            return Command(
                goto="task_selection_node",
                update={
                    "input": state["input"],
                    "messages": [done_msg],
                    "current_message": [done_msg],
                    "reason": done_msg.content,
                    "provider_id": state.get("provider_id"),
                    "node": node_name,
                    "node_type": "supervisor",
                    "next_node": "task_selection_node",
                    "type": "thinker",
                    "next_type": "planner",
                    "usages": state.get("usages", {}),
                    "status": "success",
                    "plans": state.get("plans", []),
                    "current_task": state.get("current_task", "NO TASK"),
                    "tool_output": state.get("tool_output"),
                    "max_message": state.get("max_message", 10),
                    "dispatch_retries": 0,
                    "task_status": "",
                },
            )

        messages = [
            SystemMessage(content=system_prompt),
        ]

        if state.get("messages"):
            messages += state["messages"]

        # try:
        response: Router = llm.with_structured_output(Router).invoke(
            messages, config={"callbacks": [callback_handler]}
        )
        # except Exception as e:
        #     print(f"[ERROR] LLM failed to produce valid Router output: {e}")
        #     response = Router(
        #         next="BACK",
        #         reason="LLM failed, escalating back safely.")

        usages_data = usages(callback_handler)
        past_step = (state.get('current_task', 'N/A'), response.reason)

        if response.next.upper() == "NEXT_TASK":
            return Command(
                goto="task_selection_node",
                update={
                    "input": state["input"],
                    "messages": [AIMessage(content=f"Supervisor: {response.reason}")],
                    "current_message": [AIMessage(content=response.reason)],
                    "reason": response.reason,
                    "provider_id": state.get("provider_id"),
                    "node": node_name,
                    "node_type": "supervisor",
                    "next_node": "task_selection_node",
                    "type": "thinker",
                    "next_type": "planner",
                    "usages": usages_data,
                    "status": "success",
                    "plans": state.get("plans", []),
                    "current_task": state.get("current_task", "NO TASK"),
                    "tool_output": state.get("tool_output"),
                    "max_message": state.get("max_message", 10),
                    # Reset retries when moving to next task
                    "dispatch_retries": 0,
                    "task_status": "",
                },
            )

        if response.next.upper() == "BACK":
            new_back_count = back_count + 1

            # If too many BACKs, end gracefully to avoid infinite loops
            if new_back_count >= max_back:
                end_msg = AIMessage(content=(
                    "I cannot complete this request with the currently available agents. "
                    "Ending now to avoid an infinite loop."
                ))
                return Command(
                    goto="final_answer_node",
                    update={
                        "input": state["input"],
                        "messages": [end_msg],
                        "current_message": [end_msg],
                        "reason": end_msg.content,
                        "provider_id": state.get("provider_id"),
                        "node": node_name,
                        "node_type": "supervisor",
                        "next_node": "END",
                        "type": "thinker",
                        "next_type": "END",
                        "usages": usages_data,
                        "status": "ended_backoff",
                        "plans": state.get("plans", []),
                        "current_task": state.get("current_task", "NO TASK"),
                        "tool_output": state.get("tool_output"),
                        "max_message": state.get("max_message", 10),
                        "back_count": new_back_count,
                    },
                )

            return Command(
                goto=goto_end_symbol,
                update={
                    "input": state["input"],
                    "messages": [AIMessage(content=f"Supervisor escalating back: {response.reason}")],
                    "current_message": [AIMessage(content=f"{response.reason}")],
                    "reason": response.reason,
                    "provider_id": state.get("provider_id"),
                    "node": node_name,
                    "node_type": "supervisor",
                    "next_node": goto_end_symbol,
                    "type": "thinker",
                    "next_type": "thinker",
                    "usages": usages_data,
                    "status": "success",
                    "plans": state.get("plans", []),
                    "current_task": state.get("current_task", "NO TASK"),
                    "tool_output": state.get("tool_output"),
                    "max_message": state.get("max_message", 10),
                    "back_count": new_back_count,
                },
            )

        spec = registry.get(response.next)
        resolved_type = spec.type if spec else "unknown"

        return Command(
            goto=response.next,
            update={
                "input": state["input"],
                "messages": [AIMessage(content=f"Supervisor: {response.reason}")],
                "current_message": [AIMessage(content=f"Routing to {response.next} because {response.reason}")],
                "reason": response.reason,
                "provider_id": state.get("provider_id"),
                "node": node_name,
                "node_type": "supervisor",
                "next_node": response.next,            
                "type": "thinker",
                "next_type": "thinker" if resolved_type == "supervisor" else "executor",
                "usages": usages_data,
                "status": "success",
                "plans": state.get("plans", []),
                "current_task": state.get("current_task", "NO TASK"),
                "tool_output": state.get("tool_output"),
                "max_message": state.get("max_message", 10),
            },
        )

    supervisor_node.__name__ = node_name
    return supervisor_node