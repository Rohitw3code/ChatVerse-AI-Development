from typing_extensions import Literal
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.types import Command
from chatagent.config.init import llm
from chatagent.utils import State, usages
from langchain_community.callbacks import get_openai_callback
from pydantic import BaseModel, Field
from typing import List, Optional


class Act(BaseModel):
    type: Literal["END", "PLAN"]
    steps: Optional[list[str]] = Field(None, description="If planning further")


def re_planner_node(
        available_agents: dict[str, str], node_name="replanner_node"):
    def replanner(state: State) -> Command[Literal["final_answer_node"]]:
        if not state.get('plans'):
            ai_message = AIMessage(content="All Task and Plans complete")
            return Command(
                update={
                    "input": state["input"],
                    "messages": [ai_message],
                    "current_message": [ai_message],
                    "reason": "Generated replan (final response).",
                    "provider_id": state.get("provider_id"),
                    "next_node": "__end__",
                    "node_type": state.get("node_type"),
                    "type": state.get("type"),
                    "next_type": state.get("next_type"),
                    "status": "success",
                    "plans": [],
                    "current_task": state.get("current_task", "NO TASK"),
                    "usages": state.get("usages", {}),
                    "tool_output": state.get("tool_output"),
                    "max_message": state.get("max_message", 10),
                },
                goto="final_answer_node",
            )

        agents_desc = [f"- {name}: {desc}" for name, desc in available_agents.items()]

        replanner_prompt = (
            f"""You are a replanning agent. Your task is to adjust the existing plan ONLY if necessary, 
            based strictly on the user's original request.

            Rules for replanning:
            - Do NOT add new steps that are not explicitly mentioned in the user's request or the original plan.
            - Only refine or reorder existing steps if it improves clarity or correctness.
            - Each step must map directly to one of the available agents/tools below.
            - Keep the plan concise. Do not over-break steps.
            - If all tasks are already complete, return type="END".

            Objective (from user):
            {state.get('input')}

            Available agents:
            {chr(10).join(agents_desc)}

            Current plan:
            {state.get('plans')}

            Return only the updated plan or END.
            """
        )

        with get_openai_callback() as cb:
            result: Act = llm.with_structured_output(Act).invoke(
                [SystemMessage(content=replanner_prompt)] + state['messages']
            )

        usages_data = usages(cb)

        

        if result.type.upper() == 'END' or not result.steps:
            ai_message = AIMessage(content="All Task and Plans complete")
            return Command(
                update={
                    "input": state["input"],
                    "messages": [ai_message],
                    "current_message": [ai_message],
                    "reason": "Generated replan (final response).",
                    "provider_id": state.get("provider_id"),
                    "next_node": "__end__",
                    "node_type": state.get("node_type"),
                    "type": state.get("type"),
                    "next_type": state.get("next_type"),
                    "status": "success",
                    "plans": [],
                    "current_task": state.get("current_task", "NO TASK"),
                    "usages": usages_data,
                    "tool_output": state.get("tool_output"),
                    "max_message": state.get("max_message", 10),
                },
                goto="final_answer_node",
            )

        # Plan branch
        plan_text = "\n".join([f"{i + 1}. {step}" for i, step in enumerate(result.steps)])
        ai_message = AIMessage(content=f"Plan:\n{plan_text}")

        return Command(
            update={
                "input": state["input"],
                "messages": [ai_message],
                "current_message": [ai_message],
                "reason": "Generated replan for execution.",
                "provider_id": state.get("provider_id"),
                "next_node": "task_dispatcher_node",
                "node_type": state.get("node_type"),
                "plans":result.steps,
                "type": state.get("type"),
                "next_type": state.get("next_type"),
                "status": "success",
                "current_task": state.get("current_task", "NO TASK"),
                "usages": usages_data,
                "tool_output": state.get("tool_output"),
            },
            goto="task_dispatcher_node",
        )

    replanner.__name__ = node_name
    return replanner