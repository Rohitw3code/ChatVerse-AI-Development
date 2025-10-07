from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.types import Command
from pydantic import BaseModel, Field
from typing import Literal, Optional
from chatagent.utils import State, usages
from chatagent.config.init import llm
from langchain_community.callbacks import get_openai_callback


class InputRouter:
    """Decide whether a user query is actionable (route to planner) or simple (finish)."""

    class Router(BaseModel):
        next: Literal["search_agent_node", "finish"]
        final_answer: Optional[str] = Field(
            None,
            description=(
                "Assistant reply to the user. "
                "If the query is actionable, this MUST begin exactly with: "
                "'I will help you do this: {task}'. "
                "Do NOT include routing justification or the reason for choosing the next node."
            ),
        )
        meta: Optional[str] = Field(
            None, description="Short machine-readable tag (optional)."
        )

    def __init__(self, llm):
        self.llm = llm

    async def route(self, state: State) -> Command[Literal["search_agent_node", "__end__"]]:
        """Pick next node: actionable -> search_agent_node, simple -> finish."""

        recent_messages = state["messages"][-state.get("max_message", 20) :]
        recent_messages.append(HumanMessage(content=state["input"]))

        sanitized_messages = []
        for i, msg in enumerate(recent_messages):
            if isinstance(msg, ToolMessage):
                if i > 0 and isinstance(recent_messages[i - 1], AIMessage) and getattr(
                    recent_messages[i - 1], "tool_calls", None
                ):
                    sanitized_messages.append(msg)
                else:
                    continue
            else:
                sanitized_messages.append(msg)

        # Short, precise system prompt
        system = SystemMessage(
            content=(
                "You are Chatverse AI. Choose between `search_agent_node` (actionable/agentic) "
                "or `finish` (simple Q/A).\n\n"
                "Rules:\n"
                "- Actionable/agentic tasks (planning, executing, scheduling, searching, sending, etc.) -> "
                "`search_agent_node`. For these, set `final_answer` and it MUST start with:\n"
                "  I will help you do this: {short task summary}\n"
                "  (No routing explanation — do not explain why you chose the node.)\n"
                "- Non-actionable (greetings, factual queries, quick answers) -> `finish`. "
                "Provide `final_answer` as the assistant reply.\n"
                "- If unclear, prefer `search_agent_node`.\n\n"
                "Return output that conforms to the Router schema only."
            )
        )

        messages = [system, *sanitized_messages]

        with get_openai_callback() as cb:
            decision: self.Router = await self.llm.with_structured_output(self.Router).ainvoke(
                messages
            )

        usages_data = usages(cb)

        # The user-facing message MUST be `final_answer` (or fallback to meta)
        ai_message = AIMessage(content=decision.final_answer or decision.meta or "")

        # Minimal debug (keeps logs readable)
        print("\n", "==" * 8)
        print("Decision : ", decision)
        print("=" * 8, "\n")

        common_update = {
            "input": state["input"],
            "messages": [ai_message],
            "current_message": [ai_message],
            "reason": decision.meta,
            "provider_id": state.get("provider_id"),
            "status": "success",
            "type": "thinker",
            "plans": state.get("plans", []),
            "current_task": state.get("current_task", "NO TASK"),
            "usages": usages_data,
            "tool_output": state.get("tool_output"),
            "max_message": state.get("max_message", 10),
        }

        if decision.next.lower() == "finish":
            common_update.update(
                {
                    "next_node": "__end__",
                    "next_type": "thinker",
                }
            )
            return Command(update=common_update, goto="__end__")

        # actionable path
        common_update.update(
            {
                "next_node": "search_agent_node",
                "next_type": "agent_searcher",
            }
        )
        return Command(update=common_update, goto="search_agent_node")


# Instantiate router method (callable)
inputer = InputRouter(llm).route
