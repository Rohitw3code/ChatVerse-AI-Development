# planner_agent.py

from typing_extensions import Literal
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.types import Command
from chatagent.config.init import llm
from chatagent.utils import State, usages
from langchain_community.callbacks import get_openai_callback
from pydantic import BaseModel, Field
from typing import List


class Plan(BaseModel):
    """Plan to follow in future"""

    steps: List[str] = Field(
        description="different steps to follow, should be in sorted order"
    )
    reason: str = Field(
        description="overall reason and explaination about the steps in short"
    )


def make_planner_node(
        available_agents: dict[str, str], node_name="planner_node"):
    """
    Factory to create a planner node that generates a structured step-by-step plan.

    Args:
        available_agents: Dict of {agent_name: description}.
        node_name: Name for the planner node.
    """

    # Build system prompt dynamically
    agents_desc = [
        f"- {name}: {desc}" for name,
        desc in available_agents.items()]
    planner_prompt = (
        "You are a planning agent. Your job is to analyze the user request and create a clear, step-by-step plan.\n\n"
        "Available agents & tools:\n"
        f"{chr(10).join(agents_desc)}\n\n"
        "Rules:\n"
        "- Use ONLY the exact agent/tool names listed above when relevant.\n"
        "- Do NOT add actions or tasks that the user did not explicitly request.\n"
        "- Do NOT over-divide tasks into unnecessary sub-steps.\n"
        "  • Example: If the user asks to draft an email → one step is enough.\n"
        "  • If the user asks to draft AND send an email → two or at most three steps are enough.\n"
        "- Keep the plan concise, with only the essential steps needed.\n"
        "- If information is missing or ambiguous, ask the user for clarification instead of assuming.\n"
        "- Only include approval or confirmation steps if the user explicitly asks for them.\n"
        "- The plan must strictly reflect the user’s query and nothing more.\n"
    )


    def planner(state: State) -> Command[Literal["task_selection_node"]]:

        with get_openai_callback() as cb:
            message_content = f"info : {planner_prompt} and User Query : {state['input']}"
            result: Plan = llm.with_structured_output(Plan).invoke([
                HumanMessage(content=message_content)
            ])
        
        print(f"📝 Planner generated plan: {result} ")

        usages_data = usages(cb)

        # Convert structured Plan → AIMessage for traceability
        plan_text = "\n".join(
            [
                f"Step {i+1}: {s}"
                for i, s in enumerate(result.steps)
            ]
        )

        return Command(
            update={
                "input": state["input"],
                "messages": [AIMessage(content=f"{plan_text}")],
                "current_message": [AIMessage(content=f"{plan_text}")],
                "reason": result.reason,
                "provider_id": state.get("provider_id"),
                "next_node": "task_dispatcher_node",
                "node_type": "planner",
                "next_node_type": "supervisor",
                "type": "planner",
                "next_type": "thinker",
                "usages": usages_data,
                "status": "success",
                "plans": result.steps,
                "current_task": state.get("current_task", "NO TASK"),
                "tool_output": state.get("tool_output"),
                "max_message": state.get("max_message", 10),
            },
            goto="task_selection_node",
        )

    planner.__name__ = node_name
    return planner