from langchain.prompts import PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.types import Command
from pydantic import BaseModel, Field
from typing import Literal, Optional
from chatagent.utils import State, usages, sanitize_messages
from chatagent.config.init import non_stream_llm, stream_llm
from langchain_community.callbacks import get_openai_callback
from chatagent.system.inputer_models import Router


class InputRouter:
    """Routes user input to either agent search or direct answer."""

    def __init__(self):
        pass

        self.router_prompt = PromptTemplate.from_template(
            """
                You are Chatverse AI routing assistant.
                Decide if the user query is **actionable** (needs agents/tools) or **simple** (answer directly).

                Rules:
                - Use `search_agent_node` for tasks needing actions, planning, search, automation, or workflows
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

    async def route(self, state: State) -> Command[Literal["search_agent_node", "final_answer_node"]]:
        """Pick next node: actionable -> search_agent_node, simple -> finish."""
        recent_messages = state["messages"][-state.get("max_message", 20):]
        recent_messages.append(HumanMessage(content=state["input"]))

        # Sanitize messages to ensure proper format
        sanitized_messages = sanitize_messages(recent_messages)
            
        # First LLM call: Decide routing
        system = SystemMessage(content=self.router_prompt.format(input=state["input"]))
        messages = [system, *sanitized_messages]

        with get_openai_callback() as cb:
            decision = await non_stream_llm.with_structured_output(Router).ainvoke(messages)

        routing_usages = usages(cb)

        # Use the reason from the router decision
        ai_message = AIMessage(content=decision.reason)

        common_update = {
            "input": state["input"],
            "messages": [ai_message],
            "current_message": [ai_message],
            "provider_id": state.get("provider_id"),
            "status": "success",
            "type": "thinker",
            "plans": state.get("plans", []),
            "current_task": state.get("current_task", "NO TASK"),
            "usages": routing_usages,
            "tool_output": state.get("tool_output"),
            "max_message": state.get("max_message", 10),
        }

        if decision.next.lower() == "finish":
            common_update.update({"next_node": "final_answer_node", "next_type": "thinker"})
            return Command(update=common_update, goto="final_answer_node")

        common_update.update({"next_node": "search_agent_node", "next_type": "agent_searcher"})
        return Command(update=common_update, goto="search_agent_node")


# Callable router
inputer = InputRouter().route