from typing import List
from typing_extensions import Literal
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command
from langchain_community.callbacks import get_openai_callback

from chatagent.config.init import llm
from chatagent.utils import State, usages


class Plan(BaseModel):
    """Structured plan with ordered steps for task execution."""
    steps: List[str] = Field(description="Ordered list of steps to follow for completing the user's request.")


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
            agents_desc = [f"- {agent['name']}: {agent['description']}" for agent in available_agents]

        # Build concise planning prompt
        planner_prompt = (
            "You are a planning agent. Create a clear, step-by-step plan for the user's request.\n\n"
            f"Available agents & tools:\n{chr(10).join(agents_desc)}\n\n"
            "Rules:\n"
            "- Use ONLY the exact agent names listed above.\n"
            "- Do NOT add actions not explicitly requested by the user.\n"
            "- Keep the plan concise with only essential steps.\n"
            "- Don't over-divide tasks into unnecessary sub-steps.\n"
            "- If information is missing, include a step to ask the user.\n"
            "- Only include approval steps if explicitly requested.\n"
        )

        with get_openai_callback() as cb:
            message_content = f"{planner_prompt}\n\nUser Query: {state['input']}"
            
            print("\n\n", "=" * 20, " Planner Node Invoked ", "=" * 20)
            print("Generating plan for:", state['input'])

            result: Plan = llm.with_structured_output(Plan).invoke([
                HumanMessage(content=message_content)
            ])
        
        print(f"📝 Generated plan: {result.steps}\n")


def make_planner_node(node_name="planner_node"):
    """
    Factory to create a planner node that generates a structured step-by-step plan
    based on the agents found in the state.
    """

    def planner(state: State) -> Command[Literal["task_selection_node"]]:
        
        # Dynamically get available agents from the state, put there by the search_agent_node
        available_agents = state.get("agents", [])
        
        if not available_agents:
             agents_desc = ["- No specific agents were found for this query."]
        else:
            agents_desc = [
                f"- {agent['name']}: {agent['description']}" for agent in available_agents
            ]

        # Build system prompt dynamically using agents from the state
        planner_prompt = (
            "You are a planning agent. Your job is to analyze the user request and create a clear, step-by-step plan.\n\n"
            "Available agents & tools for this query:\n"
            f"{chr(10).join(agents_desc)}\n\n"
            "Rules:\n"
            "- Use ONLY the exact agent names listed above when creating plan steps.\n"
            "- Do NOT add actions or tasks that the user did not explicitly request.\n"
            "- Do NOT over-divide tasks into unnecessary sub-steps.\n"
            "  • Example: If the user asks to draft an email → one step is enough.\n"
            "  • If the user asks to draft AND send an email → two or at most three steps are enough.\n"
            "- Keep the plan concise, with only the essential steps needed.\n"
            "- If information is missing or ambiguous, a step should be to ask the user for clarification.\n"
            "- Only include approval or confirmation steps if the user explicitly asks for them.\n"
            "- The plan must strictly reflect the user’s query and nothing more.\n"
        )

        with get_openai_callback() as cb:
            message_content = f"info : {planner_prompt} and User Query : {state['input']}"

            print("\n\n", "=" * 20, " Planner Node Invoked ", "=" * 20)
            print("message_content:", message_content)
            print("\n\n ")

            result: Plan = llm.with_structured_output(Plan).invoke([
                HumanMessage(content=message_content)
            ])
        
        print(f"📝 Planner generated plan: {result} ")

        usages_data = usages(cb)

        # Format plan for display
        plan_text = "\n".join([f"Step {i+1}: {step}" for i, step in enumerate(result.steps)])

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