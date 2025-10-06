from typing_extensions import Literal
from langchain_core.messages import AIMessage
from langgraph.types import Command
from chatagent.config.init import llm
from chatagent.utils import State


def task_selection_node(node_name="task_selection_node"):
    """
    This Node is for the selection of the task
    """

    def task_selection(
            state: State) -> Command[Literal["task_dispatcher_node"]]:
        # defensive: make sure plans is always a list
        plans = state.get('plans', []) or []

        if plans:
            current_task = plans[0]
            new_plan = plans[1:]
        else:
            current_task = "No tasks left — all plans completed"
            new_plan = []

        ai_msg = AIMessage(content=f"Current Task : {current_task}")

        return Command(
            update={
                "input": state["input"],
                "messages": [ai_msg],
                "current_message": [ai_msg],
                "reason": f"{current_task}",
                "provider_id": state.get("provider_id"),
                "next_node": "task_dispatcher_node",
                "node_type": "selection",
                "type": "planner",
                "next_type": "thinker",
                "usages": {},
                "status": "success",
                "plans": new_plan,
                "current_task": current_task,
                "tool_output": state.get("tool_output"),
                "max_message": state.get("max_message", 10),
            },
            goto="task_dispatcher_node",
        )

    task_selection.__name__ = node_name
    return task_selection