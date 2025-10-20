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

    def __init__(self, llm):
        self.llm = llm

        self.router_prompt = PromptTemplate.from_template(
            """
                You are Chatverse AI routing assistant.
                Decide if the user query is **actionable** (needs agents/tools) or **simple** (answer directly).

                Rules:
                - Use `search_agent_node` for tasks needing actions, planning, search, automation, or workflows.
                - Use `finish` for normal chat, factual Q&A, code help, or anything you can handle directly.
                - Prefer `finish` if unclear, unsafe, or self-referential.
                
                Only decide the routing - don't generate answers yet.
            """
        )

        self.answer_prompt = PromptTemplate.from_template(
            """
                You are Chatverse AI.
                The routing decision is: {decision}
                
                Generate an appropriate response:
                - If decision is 'search_agent_node' (actionable): Start with "I will help you do this:" and outline the plan briefly (max 50 words).
                - If decision is 'finish' (direct answer): Answer the question clearly and properly formatted.
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
            
        # First LLM call: Decide routing
        system = SystemMessage(content=self.router_prompt.format(input=state["input"]))
        messages = [system, *sanitized_messages]

        with get_openai_callback() as cb:
            decision = await self.llm.with_structured_output(self.Router).ainvoke(messages)

        routing_usages = usages(cb)

        # Second LLM call: Generate appropriate answer based on routing decision (simple text)
        answer_system = SystemMessage(content=self.answer_prompt.format(decision=decision.next))
        answer_messages = [answer_system, *sanitized_messages]

        with get_openai_callback() as cb:
            answer_result = await self.llm.ainvoke(answer_messages)

        answer_usages = usages(cb)

        # Combine usages from both calls
        combined_usages = {
            "total_tokens": routing_usages.get("total_tokens", 0) + answer_usages.get("total_tokens", 0),
            "prompt_tokens": routing_usages.get("prompt_tokens", 0) + answer_usages.get("prompt_tokens", 0),
            "completion_tokens": routing_usages.get("completion_tokens", 0) + answer_usages.get("completion_tokens", 0),
            "total_cost": routing_usages.get("total_cost", 0.0) + answer_usages.get("total_cost", 0.0),
        }

        ai_message = AIMessage(content=answer_result.content)

        common_update = {
            "input": state["input"],
            "messages": [ai_message],
            "current_message": [ai_message],
            "provider_id": state.get("provider_id"),
            "status": "success",
            "type": "thinker",
            "plans": state.get("plans", []),
            "current_task": state.get("current_task", "NO TASK"),
            "usages": combined_usages,
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