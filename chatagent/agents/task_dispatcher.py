from typing import List, Literal
from pydantic import BaseModel, Field, field_validator
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langgraph.types import Command
from langchain_community.callbacks import get_openai_callback

from chatagent.utils import State, usages
from chatagent.node_registry import NodeRegistry


def task_dispatcher(registry: NodeRegistry):
    """
    Factory function creating a task dispatcher node that routes tasks to appropriate agents.
    Handles task completion, retry logic, and fallback to replanner when needed.
    """
    node_name = "task_dispatcher"
    members = registry.members() + ['final_answer_node']
    special_commands = ['END', 'NEXT_TASK']
    allowed_choices = members + special_commands

    def _build_system_prompt(available_agents: List[dict]) -> str:
        """Build dynamic system prompt using agents from state or registry fallback."""
        if available_agents:
            agent_lines = [f"- {agent['name']}: {agent['description']}" for agent in available_agents]
            available_nodes_block = "\n".join(agent_lines)
            # Build allowed choices from identified agents only
            agent_names = [agent['name'] for agent in available_agents]
            dynamic_allowed_choices = agent_names + special_commands
        else:
            available_nodes_block = registry.prompt_block("Supervisor")
            # Fallback to all registry members if no agents identified
            dynamic_allowed_choices = allowed_choices
        
        return f"""<prompt>
                <role>You are {node_name}, an orchestrator supervisor that routes tasks to appropriate nodes based on current task requirements.</role>
                <output_format>
                    Respond with ONLY a valid JSON object:
                    {{"next": "<exact_node_name | 'END' | 'NEXT_TASK'>", "reason": "<brief_justification>"}}
                </output_format>
                <instructions>
                    <rule id="1">Analyze `current_task` and `remaining_plans` to decide the next step.</rule>
                    <rule id="2">Route to the most appropriate node from `<available_nodes>` for the current task.</rule>
                    <rule id="3">Select 'NEXT_TASK' only when the current task is fully complete.</rule>
                    <rule id="4">Select 'END' ONLY when `remaining_plans` is empty.</rule>
                    <rule id="5">If repeated failures occur (agent reports no capabilities), select 'END' to prevent infinite loops.</rule>
                    <rule id="6">Keep reason brief and user-friendly without revealing internal node names.</rule>
                </instructions>
                <available_nodes>
            {available_nodes_block}
                </available_nodes>
                <allowed_choices>{dynamic_allowed_choices}</allowed_choices>
            </prompt>"""

    class Router(BaseModel):
        """Response model for task routing decisions."""
        next: str = Field(..., description="Exact node name to call next, or 'END' or 'NEXT_TASK'.")
        reason: str = Field(..., description="Brief human-readable explanation without revealing internal node names.")

        @field_validator("next")
        @classmethod
        def validate_next(cls, v: str) -> str:
            """Validate and sanitize the next node selection."""
            if not v or not v.strip():
                raise ValueError("'next' must not be empty")
            v = v.strip()
            # Note: Validation against dynamic allowed_choices happens in the node logic
            # Here we just ensure it's not empty and trimmed
            return v

    def _create_command(goto: str, state: State, reason: str, usages_data: dict, next_type: str = "thinker", dispatch_retries: int = 0, reset_task_status: bool = False) -> Command:
        """Helper to create consistent Command objects with all required state."""
        return Command(
            goto=goto,
            update={
                "input": state["input"],
                "messages": [AIMessage(content=f"Dispatcher: {reason}")],
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
                "dispatch_retries": dispatch_retries,
                "task_status": "" if reset_task_status else state.get("task_status", ""),
            },
        )

    def task_dispatcher_node(state: State) -> Command:
        """Main dispatcher logic that routes tasks and handles completion/retry scenarios."""
        remaining_plans = state.get('plans', [])
        current_task = state.get('current_task', '')
        available_agents = state.get('agents', [])

        print("\n\nAVAILABLE AGENTS IN DISPATCHER:", available_agents, "\n\n")

        # Handle task completion deterministically
        if state.get('task_status') == 'completed':
            done_msg = AIMessage(content="Task completed. Moving to the next task.")
            return _create_command(
                goto="task_selection_node",
                state=state,
                reason=done_msg.content,
                usages_data={},
                next_type="planner",
                dispatch_retries=0,
                reset_task_status=True
            )

        # Retry logic with guardrails
        dispatch_retries = state.get('dispatch_retries', 0)
        max_dispatch_retries = state.get('max_dispatch_retries', 3)
        new_dispatch_retries = dispatch_retries + 1

        # Escalate to replanner after max retries
        if new_dispatch_retries >= max_dispatch_retries:
            replan_msg = AIMessage(
                content="Multiple routing attempts failed. Sending to replanner to adjust the plan."
            )
            return Command(
                goto="replanner_node",
                update={
                    "input": state["input"],
                    "messages": [replan_msg],
                    "current_message": [replan_msg],
                    "reason": replan_msg.content,
                    "provider_id": state.get("provider_id"),
                    "node": node_name,
                    "next_node": "replanner_node",
                    "type": "thinker",
                    "next_type": "thinker",
                    "usages": {},
                    "status": "replan",
                    "plans": state.get("plans", []),
                    "current_task": current_task or "NO TASK",
                    "tool_output": state.get("tool_output"),
                    "max_message": state.get("max_message", 10),
                    "dispatch_retries": 0,
                },
            )

        # Build prompt context
        prompt_context = HumanMessage(
            content=f"""Current workflow state:
            <current_task>{current_task}</current_task>
            <remaining_plans>{remaining_plans}</remaining_plans>
            <attempt_info>dispatch_retries: {new_dispatch_retries} / {max_dispatch_retries}</attempt_info>

            Decide the next step. Do NOT choose 'END' unless remaining_plans is empty
            """
        )

        # Build dynamic allowed choices based on available agents
        if available_agents:
            agent_names = [agent['name'] for agent in available_agents]
            dynamic_allowed_choices = agent_names + special_commands
        else:
            dynamic_allowed_choices = allowed_choices

        # Import non_stream_llm for structured output
        from chatagent.config.init import non_stream_llm
        
        # Invoke LLM with structured output
        system_prompt = _build_system_prompt(available_agents)
        messages = [SystemMessage(content=system_prompt), prompt_context] + state['messages']

        with get_openai_callback() as cb:
            try:
                response: Router = non_stream_llm.with_structured_output(Router).invoke(messages)
            except Exception as e:
                print(f"[ERROR] LLM failed to produce valid Router output: {e}")
                response = Router(next="END", reason="LLM invocation failed, ending safely.")

        usages_data = usages(cb)

        # Validate response against dynamic allowed choices
        if response.next not in dynamic_allowed_choices:
            print(f"[WARN] LLM selected invalid node '{response.next}' not in available agents. Falling back to END")
            response.next = "END"
            response.reason = f"Selected agent not available for this query. {response.reason}"

        # Handle NEXT_TASK command
        if response.next.upper() == "NEXT_TASK":
            return _create_command(
                goto="task_selection_node",
                state=state,
                reason=response.reason,
                usages_data=usages_data,
                next_type="planner",
                dispatch_retries=0
            )

        # Handle END/FINISH command
        if response.next.upper() in {"END", "FINISH"}:
            return _create_command(
                goto="final_answer_node",
                state=state,
                reason=f"{response.reason}",
                usages_data=usages_data,
                next_type="END",
                dispatch_retries=new_dispatch_retries
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
            next_type=next_type,
            dispatch_retries=new_dispatch_retries
        )

    task_dispatcher_node.__name__ = node_name
    return task_dispatcher_node