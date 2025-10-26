from typing import List
from typing_extensions import Literal
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command
from langchain_community.callbacks import get_openai_callback

from chatagent.config.init import non_stream_llm
from chatagent.utils import State, usages
from chatagent.system.planner_models import Plan


def make_planner_node(node_name: str = "planner_node"):
    """
    Factory function creating a planner node that generates step-by-step plans.
    Uses available agents from state to create context-aware plans.
    """

    def planner(state: State) -> Command[Literal["task_selection_node"]]:
        """Generate a structured plan based on user input and available agents."""
        available_agents = state.get("agents", [])

        # Build agent descriptions for prompt
        if not available_agents:
            agents_desc = ["- No specific agents found for this query."]
        else:
            agents_desc = [
                f"- {agent['name']}: {agent['description']}"
                for agent in available_agents
            ]

        # Build concise planning prompt
        planner_prompt = (
            "You are a planning agent. Create a clear, step-by-step plan for the user's request.\n\n"
            f"Available agents & tools:\n{chr(10).join(agents_desc)}\n\n"
            "Rules:\n"
            "- do not include for any login or authentication steps in the plan.\n because it can be automatically handled by the Agents"
            "- Use ONLY the exact agent names listed above.\n"
            "- Do NOT add actions not explicitly requested by the user.\n"
            "- Keep the plan concise with only essential steps.\n"
            "- If information is missing, include a step to ask the user.\n"
            "- one step can accommodate two actions if query is simple keep it one step.\n"
            "- do not ask for unnecessary clarifications. because agent can handle it"
            "- Only include approval steps if explicitly requested.\n"
        )

        with get_openai_callback() as cb:
            message_content = f"{planner_prompt}\n\nUser Query: {state.get('messages')}"


            result: Plan = non_stream_llm.with_structured_output(Plan).invoke(
                [HumanMessage(content=message_content)]
            )

        print(f"📝 Planner generated plan: {result} ")

        usages_data = usages(cb)

        # Format plan for display
        plan_text = "\n".join(
            [f"Step {i+1}: {step}" for i, step in enumerate(result.steps)]
        )

        return Command(
            goto="task_selection_node",
            update={
                "input": state["input"],
                "messages": [AIMessage(content=plan_text)],
                "current_message": [AIMessage(content=plan_text)],
                "provider_id": state.get("provider_id"),
                "node": node_name,
                "next_node": "task_selection_node",
                "type": "planner",
                "next_type": "thinker",
                "usages": usages_data,
                "status": "success",
                "plans": result.steps,
                "current_task": state.get("current_task", "NO TASK"),
                "tool_output": state.get("tool_output"),
                "max_message": state.get("max_message", 10),
            },
        )

    planner.__name__ = node_name
    return planner
