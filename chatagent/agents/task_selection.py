from typing_extensions import Literal
from langchain_core.messages import AIMessage
from langgraph.types import Command

from chatagent.utils import State


def task_selection_node(node_name: str = "task_selection_node"):
    """
    Factory function creating a task selection node.
    Pops the first task from plans and sets it as the current task.
    """

    def task_selection(state: State) -> Command[Literal["task_dispatcher_node"]]:
        """Select the next task from remaining plans."""
        plans = state.get('plans', []) or []

        if plans:
            current_task = plans[0]
            new_plan = plans[1:]
        else:
            current_task = "No tasks left — all plans completed"
            new_plan = []

        ai_msg = AIMessage(content=f"Current Task: {current_task}")

        return Command(
            goto="task_dispatcher_node",
            update={
                "input": state["input"],
                "messages": [ai_msg],
                "current_message": [ai_msg],
                "reason": current_task,
                "provider_id": state.get("provider_id"),
                "node": node_name,
                "next_node": "task_dispatcher_node",
                "type": "planner",
                "next_type": "thinker",
                "usages": {},
                "status": "success",
                "plans": new_plan,
                "current_task": current_task,
                "tool_output": state.get("tool_output"),
                "max_message": state.get("max_message", 10),
            },
        )

    task_selection.__name__ = node_name
    return task_selection