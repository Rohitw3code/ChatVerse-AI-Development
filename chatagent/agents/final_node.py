from typing import Literal, Optional
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.types import Command
from pydantic import BaseModel, Field
from chatagent.config.init import llm
from chatagent.utils import State, usages
from langchain_community.callbacks import get_openai_callback
from langchain_community.callbacks.openai_info import OpenAICallbackHandler


class FinalAnswerAgent:
    """
    give final answer
    """

    def __init__(self, llm):
        self.llm = llm
        self.callback_handler = OpenAICallbackHandler()

    def start(self, state: State) -> Command[Literal["__end__"]]:
        messages = [
            SystemMessage(
                content=(
                    "You are a professional task summarizer. After completing any task or analysis, "
                    "you must provide a comprehensive, well-structured summary that includes:\n\n"
                )
            ),
            *state["messages"],
        ]

        with get_openai_callback() as cb:
            final_answer = self.llm.invoke(messages)

        usages_data = usages(cb)

        # Ensure 'reason' is a string (some downstream code / pydantic expects a string)
        if hasattr(final_answer, "content"):
            reason_text = final_answer.content
        else:
            reason_text = str(final_answer)

        return Command(
            update={
                "input": state["input"],
                "messages": [final_answer],
                "current_message": [final_answer],
                "reason": reason_text,
                "provider_id": state.get("provider_id"),
                "next_node": "end",
                "node_type": "end",
                "type": "thinker",
                "next_type": "end",
                "usages": usages_data,
                "status": "success",
                "plans": state.get("plans", []),
                "current_task": state.get("current_task", "NO TASK"),
                "tool_output": state.get("tool_output"),
                "max_message": state.get("max_message", 10),
            },
            goto="__end__",
        )


final_answer_node = FinalAnswerAgent(llm).start