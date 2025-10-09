from langchain.prompts import PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.types import Command
from pydantic import BaseModel, Field
from typing import Literal, Optional
from chatagent.utils import State, usages
from chatagent.config.init import llm
from langchain_community.callbacks import get_openai_callback


class InputRouter:
    """Routes user input to either agent search or direct answer."""

    class Router(BaseModel):
        next: Literal["search_agent_node", "finish"]
        final_answer: Optional[str] = Field(
            None, description="Reply to the user. For actionable tasks, start with I will help you do this {task} and describe the plan. first step if final answer then just answer the question in propery format."
        )

    def __init__(self, llm):
        self.llm = llm

        self.router_prompt = PromptTemplate.from_template(
            """
                You are Chatverse AI.
                Decide if the user query is **actionable** (needs agents/tools) or **simple** (answer directly).

                Rules:
                - Use `search_agent_node` for tasks needing actions, planning, search, automation, or workflows.
                - Use `finish` for normal chat, factual Q&A, code help, or anything you can handle directly.
                - Prefer `finish` if unclear, unsafe, or self-referential.
                - If actionable, reply must start with: "I will help you do this: ..."

                Return valid JSON:
                {{"next": "search_agent_node" | "finish", "final_answer": "...", "meta": "<optional>"}}

                User Input:
                {{input}}
            """
        )

    async def route(self, state: State) -> Command[Literal["search_agent_node", "__end__"]]:
        """Pick next node: actionable -> search_agent_node, simple -> finish."""
        recent_messages = state["messages"][-state.get("max_message", 20):]
        recent_messages.append(HumanMessage(content=state["input"]))

        sanitized_messages = []
        for i, msg in enumerate(recent_messages):
            if isinstance(msg, ToolMessage):
                if i > 0 and isinstance(recent_messages[i - 1], AIMessage) and getattr(
                    recent_messages[i - 1], "tool_calls", None
                ):
                    sanitized_messages.append(msg)
            else:
                sanitized_messages.append(msg)
            
        print(">>> ",self.router_prompt.format(input=state["input"]))

        system = SystemMessage(content=self.router_prompt.format(input=state["input"]))
        messages = [system, *sanitized_messages]

        with get_openai_callback() as cb:
            decision: self.Router = await self.llm.with_structured_output(self.Router).ainvoke(messages)

        usages_data = usages(cb)
        ai_message = AIMessage(content=decision.final_answer or decision.meta or "")

        print("\n======== Decision ========")
        print(decision)
        print("==========================\n")

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
            common_update.update({"next_node": "__end__", "next_type": "thinker"})
            return Command(update=common_update, goto="__end__")

        common_update.update({"next_node": "search_agent_node", "next_type": "agent_searcher"})
        return Command(update=common_update, goto="search_agent_node")


# Callable router
inputer = InputRouter(llm).route