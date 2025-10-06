from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.types import Command
from pydantic import BaseModel, Field
from typing import Literal, Optional
from chatagent.utils import State
from chatagent.config.init import llm


class InputRouter:
    """
    Decides whether the user query should go to planner or finish.
    """

    class Router(BaseModel):
        next: Literal["planner_node", "finish"]
        reason: str = Field(
            description="Why this choice was made, referencing the user query and context."
        )
        final_answer: Optional[str] = Field(
            None, description="If `finish`, provide the final assistant answer."
        )

    def __init__(self, llm):
        self.llm = llm

    async def route(
        self, state: State
    ) -> Command[Literal["planner_node", "__end__"]]:
        """ 
        Determines the next node based on the user's input.
        """

        recent_messages = state['messages'][-state.get('max_message',20):]
        recent_messages.append(HumanMessage(content=state["input"]))

        sanitized_messages = []
        for i, msg in enumerate(recent_messages):
            if isinstance(msg, ToolMessage):
                if i > 0 and isinstance(recent_messages[i-1], AIMessage) and getattr(recent_messages[i-1], "tool_calls", None):
                    sanitized_messages.append(msg)
                else:
                    continue 
            else:
                sanitized_messages.append(msg)


        messages = [
            SystemMessage(
                content=(
                    "You are Chatverse AI, an intelligent assistant for the platform Chatverse (chatverse.io). "
                    "Your purpose is to make any task complete with just the user’s query.\n\n"
                    "You have the capability to perform many tasks like Gmail and Instagram related tasks only, "
                    "but for any other actionable or agentic queries, you should still route to the planner node.\n\n"

                    "Routing Rules:\n"
                    "- If the query is an **actionable or agentic task** "
                    "(e.g., planning, executing, performing a task, searching, or retrieving external information), "
                    "route to `planner_node`.\n"
                    "  - Examples:\n"
                    "    - 'Send an email to my manager.'\n"
                    "    - 'Schedule a post on Instagram.'\n"
                    "    - 'Plan my daily tasks.'\n"
                    "    - 'Look for the AI ML job in India.'\n"
                    "    - 'Find trending hashtags for Instagram.'\n\n"

                    "- If the query is a simple, generic, or casual question that does not involve any actionable task, "
                    "route to `finish`.\n"
                    "  - Examples:\n"
                    "    - 'Hi'\n"
                    "    - 'How are you?'\n"
                    "    - 'What is Chatverse?'\n\n"

                    "If the user’s query is ambiguous or unclear, default to `planner_node`.\n\n"

                    "Respond with only one choice: `planner_node` or `finish`."
                )
            ),
            *sanitized_messages
        ]


        decision: self.Router = self.llm.with_structured_output(self.Router).invoke(
            messages
        )
        ai_message = AIMessage(content=decision.final_answer or decision.reason)

        print("\n", "=="*8)
        print("Decision : ", decision)
        print("="*8, "\n")

        if decision.next.lower() == "finish":
            return Command(
                update={
                        "input": state['input'],
                        "messages": [ai_message],
                        "current_message": [ai_message],
                        "reason": decision.reason,
                        "provider_id": state.get("provider_id"),
                        "next_node": "__end__",
                        "node_type": "starter",
                        "next_node_type": "end",
                        "status": "success",
                        "type": "thinker",
                        "next_type": "thinker",
                        "plans": state.get("plans", []),
                        "current_task": state.get("current_task", "NO TASK"),
                        "usages": state.get("usages", {}),
                        "tool_output": state.get("tool_output"),
                        "max_message": state.get("max_message", 10),
                },
                goto="__end__",
            )

        # UPDATED SECTION: Changed planner_node to search_agent_node
        return Command(
            update={
                    "input": state['input'],
                    "messages": [ai_message],
                    "current_message": [ai_message],
                    "reason": decision.reason,
                    "provider_id": state.get("provider_id"),
                    "next_node": "search_agent_node",
                    "node_type": "starter",
                    "next_node_type": "agent_searcher",
                    "next_type": "agent_searcher",
                    "status": "success",
                    "type": "thinker",
                    "plans": state.get("plans", []),
                    "current_task": state.get("current_task", "NO TASK"),
                    "usages": state.get("usages", {}),
                    "tool_output": state.get("tool_output"),
                    "max_message": state.get("max_message", 10),
            },
            goto="search_agent_node",
        )


# Instantiate the router with the language model
inputer = InputRouter(llm).route