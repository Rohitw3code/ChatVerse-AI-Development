from typing import Literal, Optional
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.types import Command
from pydantic import BaseModel, Field
from chatagent.config.init import stream_llm
from chatagent.utils import State, usages, sanitize_messages
from langchain_community.callbacks import get_openai_callback
from langchain_community.callbacks.openai_info import OpenAICallbackHandler


class FinalAnswerAgent:

    def __init__(self):
        self.callback_handler = OpenAICallbackHandler()

    def start(self, state: State) -> Command[Literal["__end__"]]:
        # Sanitize messages to remove orphaned tool_calls
        sanitized_state_messages = sanitize_messages(state["messages"])
        
        messages = [
            SystemMessage(
                content=(
                    "You are a professional task summarizer. After completing any task or analysis, "
                    "you must provide a comprehensive, well-structured summary that includes:\n\n"
                )
            ),
            *sanitized_state_messages,
        ]

        with get_openai_callback() as cb:
            final_answer = stream_llm.invoke(messages)

        usages_data = usages(cb)

        # Ensure 'reason' is a string (some downstream code / pydantic expects a string)
        if hasattr(final_answer, "content"):
            reason_text = final_answer.content
        else:
            reason_text = str(final_answer)

        trace_entry = {
            "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
            "node": "final_answer_node",
            "event": "routing_decision",
            "decision": {"goto": "__end__", "reason": reason_text},
        }
        prev_trace = state.get("automation_trace", [])
        return Command(
            update={
                "input": state["input"],
                "messages": [final_answer],
                "current_message": [final_answer],
                "reason": reason_text,
                "provider_id": state.get("provider_id"),
                "next_node": "__end__",
                "type": "thinker",
                "next_type": "end",
                "usages": usages_data,
                "status": "success",
                "plans": state.get("plans", []),
                "current_task": state.get("current_task", "NO TASK"),
                "tool_output": state.get("tool_output"),
                "max_message": state.get("max_message", 10),
                "automation_trace": prev_trace + [trace_entry],
            },
            goto="__end__",
        )


final_answer_node = FinalAnswerAgent().start