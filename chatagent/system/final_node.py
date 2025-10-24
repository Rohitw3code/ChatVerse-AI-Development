from typing import Literal, Optional
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.types import Command
from pydantic import BaseModel, Field
from chatagent.config.init import stream_llm
from chatagent.utils import State, usages
from langchain_community.callbacks import get_openai_callback
from langchain_community.callbacks.openai_info import OpenAICallbackHandler


class FinalAnswerAgent:

    def __init__(self):
        self.callback_handler = OpenAICallbackHandler()

    def _sanitize_messages(self, messages):
        """Remove AIMessages with tool_calls that don't have corresponding ToolMessage responses."""
        sanitized = []
        i = 0
        while i < len(messages):
            msg = messages[i]
            
            # If it's an AIMessage with tool_calls, check if next message is a ToolMessage
            if isinstance(msg, AIMessage) and hasattr(msg, "tool_calls") and msg.tool_calls:
                # Check if the next message(s) are ToolMessages responding to these tool_calls
                has_tool_response = False
                if i + 1 < len(messages):
                    next_msg = messages[i + 1]
                    if isinstance(next_msg, ToolMessage):
                        has_tool_response = True
                
                if has_tool_response:
                    # Include the AIMessage with tool_calls and the ToolMessage(s)
                    sanitized.append(msg)
                    # Skip ahead to include tool messages
                    i += 1
                    while i < len(messages) and isinstance(messages[i], ToolMessage):
                        sanitized.append(messages[i])
                        i += 1
                    continue
                else:
                    # Skip this AIMessage with orphaned tool_calls
                    # Or create a copy without tool_calls
                    msg_copy = AIMessage(content=msg.content)
                    sanitized.append(msg_copy)
            else:
                # Regular message, keep it
                sanitized.append(msg)
            
            i += 1
        
        return sanitized

    def start(self, state: State) -> Command[Literal["__end__"]]:
        # Sanitize messages to remove orphaned tool_calls
        sanitized_state_messages = self._sanitize_messages(state["messages"])
        
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
            },
            goto="__end__",
        )


final_answer_node = FinalAnswerAgent().start