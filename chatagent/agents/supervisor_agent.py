from typing import Literal, List
from pydantic import BaseModel, Field, field_validator
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.types import Command
from langchain_community.callbacks import get_openai_callback

from chatagent.utils import State, usages
from chatagent.node_registry import NodeRegistry

def make_supervisor_node(
    registry: NodeRegistry,
    node_name: str,
    goto_end_symbol: str,
    prompt: str = ""
):
    """
    Factory function creating a supervisor node that routes tasks within a specific domain.
    Handles escalation (BACK), task completion (NEXT_TASK), and proper retry logic.
    """
    special_commands = ['BACK', 'NEXT_TASK']
    members = registry.members() + special_commands
    router_members = registry.members()

    system_prompt = f"""<prompt>
    <role>You are {node_name}, a supervisor that decides the next step in the workflow.</role>
    <supervisor_instructions>{prompt}</supervisor_instructions>
    <output_format>Respond with ONLY a valid JSON object: {{"next": "<node_name | 'BACK' | 'NEXT_TASK'>", "reason": "<brief_justification>"}}</output_format>
    <instructions>
        <rule id="1">Analyze the current task and route to the most appropriate node from `<available_nodes>`.</rule>
        <rule id="2">Select 'BACK' if the task is incomplete and a previous supervisor can help.</rule>
        <rule id="3">Select 'NEXT_TASK' if the current task is fully completed.</rule>
        <rule id="4">Select 'BACK' if no available node can handle the request.</rule>
        <rule id="5">Keep reason brief and user-friendly without revealing internal node names.</rule>
    </instructions>
    <available_nodes>{registry.prompt_block("Supervisor")}</available_nodes>
    <allowed_choices>{members}</allowed_choices>
</prompt>"""

    class Router(BaseModel):
        """Response model for supervisor routing decisions."""
        next: str = Field(..., description="Exact node name to call next, or 'BACK', or 'NEXT_TASK'.")
        reason: str = Field(..., description="Brief human-readable explanation without revealing internal node names.")

        @field_validator("next")
        @classmethod
        def validate_next(cls, v: str) -> str:
            """Validate and sanitize the next node selection."""
            if not v or not v.strip():
                raise ValueError("'next' must not be empty")
            v = v.strip()
            if v not in members:
                print(f"[WARN] Invalid next='{v}', falling back to BACK")
                return "BACK"
            return v

    def _create_command(goto: str, state: State, reason: str, usages_data: dict, next_type: str = "thinker", back_count: int = 0, reset_task_status: bool = False) -> Command:
        """Helper to create consistent Command objects with all required state."""
        return Command(
            goto=goto,
            update={
                "input": state["input"],
                "messages": [AIMessage(content=f"Supervisor: {reason}")],
                "current_message": [AIMessage(content=reason)],
                "reason": reason,
                "provider_id": state.get("provider_id"),
                "node": node_name,
                "next_node": goto,
                "type": "thinker",
                "next_type": next_type,
                "usages": usages_data,
                "status": "success",
                "plans": state.get("plans", []),
                "current_task": state.get("current_task", "NO TASK"),
                "tool_output": state.get("tool_output"),
                "max_message": state.get("max_message", 10),
                "back_count": back_count,
                "task_status": "" if reset_task_status else state.get("task_status", ""),
            },
        )

    def supervisor_node(state: State) -> Command:
        """Main supervisor logic that routes within domain and handles escalation."""
        back_count = state.get("back_count", 0)
        max_back = state.get("max_back", 2)

        # Handle task completion deterministically
        if state.get("task_status") == "completed":
            done_msg = AIMessage(content="Task completed. Advancing to the next task.")
            return _create_command(
                goto="task_selection_node",
                state=state,
                reason=done_msg.content,
                usages_data={},
                next_type="planner",
                reset_task_status=True
            )

        # Build messages for LLM
        messages = [SystemMessage(content=system_prompt)]
        if state.get("messages"):
            messages += state["messages"]

        # Import non_stream_llm for structured output
        from chatagent.config.init import non_stream_llm
        
        with get_openai_callback() as cb:
            try:
                response: Router = non_stream_llm.with_structured_output(Router).invoke(messages)
            except Exception as e:
                print(f"[ERROR] LLM failed to produce valid Router output: {e}")
                response = Router(next="BACK", reason="LLM invocation failed, escalating back safely.")

        usages_data = usages(cb)

        # Handle NEXT_TASK command
        if response.next.upper() == "NEXT_TASK":
            return _create_command(
                goto="task_selection_node",
                state=state,
                reason=response.reason,
                usages_data=usages_data,
                next_type="planner",
                reset_task_status=True
            )

        # Handle BACK command with retry limit
        if response.next.upper() == "BACK":
            new_back_count = back_count + 1

            # End gracefully after too many BACKs
            if new_back_count >= max_back:
                end_msg = AIMessage(
                    content="Cannot complete this request with available agents. Ending to avoid infinite loop."
                )
                return Command(
                    goto="final_answer_node",
                    update={
                        "input": state["input"],
                        "messages": [end_msg],
                        "current_message": [end_msg],
                        "reason": end_msg.content,
                        "provider_id": state.get("provider_id"),
                        "node": node_name,
                        "next_node": "final_answer_node",
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

            return _create_command(
                goto=goto_end_symbol,
                state=state,
                reason=response.reason,
                usages_data=usages_data,
                next_type="thinker",
                back_count=new_back_count
            )

        # Route to selected node
        spec = registry.get(response.next)
        resolved_type = spec.type if spec else "unknown"
        next_type = "thinker" if resolved_type == "supervisor" else "executor"

        return _create_command(
            goto=response.next,
            state=state,
            reason=response.reason,
            usages_data=usages_data,
            next_type=next_type
        )

    supervisor_node.__name__ = node_name
    return supervisor_node