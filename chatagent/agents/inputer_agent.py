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


        system = SystemMessage(
            content=(
                "You are Chatverse AI — a hybrid assistant that decides whether to use agents or directly answer.\n\n"
                "### Your Goals\n"
                "- If the user query clearly requires multi-step or external action (planning, searching, sending, automation, data fetching, workflow creation, etc.), choose `search_agent_node`.\n"
                "- If the query is conversational, code-related, analytical, random text, or something you can answer directly, choose `finish`.\n"
                "- If the query looks unsafe, looping, self-referential, or likely to break the agentic system (e.g. recursive prompts or infinite agent chaining), choose `finish` and provide a safe natural response.\n\n"
                "### Decision Rules\n"
                "- `search_agent_node`: actionable/agentic requests — tasks that require calling tools, agents, or generating structured plans.\n"
                "  - Example: 'Fetch top AI jobs from LinkedIn', 'Send this email', 'Summarize 5 PDFs'.\n"
                "  - Response must start with: 'I will help you do this: {short summary}'.\n"
                "- `finish`: general conversation, factual questions, random code/text, or system-risk prompts.\n"
                "  - Example: greetings, explanations, debugging code, factual answers, or any query that doesn't require multi-agent work.\n"
                "  - Response should directly answer the user in natural language.\n\n"
                "### Safety & Robustness\n"
                "- Detect and stop any loop-inducing or recursive agent prompts.\n"
                "- Do NOT trigger agent search for random, unclear, or passive text.\n"
                "- If the input looks like code or instructions (e.g. Python, JSON, JS), analyze or explain it directly instead of routing to agents.\n"
                "- Always prefer `finish` if unsure, unsafe, or non-actionable.\n\n"
                "Return only a valid JSON matching the Router schema with keys: `next`, `final_answer`, and optionally `meta`."
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
