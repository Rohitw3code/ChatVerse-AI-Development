from langchain_core.messages import SystemMessage, HumanMessage, AIMessage,ToolMessage
from langgraph.types import Command
from pydantic import BaseModel, Field
from typing import Literal, Optional
from chatagent.utils import State
from chatagent.config.init import llm
from chatagent.db.database import Database
from langchain_core.runnables import RunnableConfig


db = Database()


class MemoryLoaderRouter:
    """
    Decides whether the user query should go to planner or finish.
    """

    def __init__(self, llm):
        self.llm = llm

    async def route(
        self, state: State, config: RunnableConfig
    ) -> Command[Literal["inputer_node"]]:
        """
        Determines the next node based on the user's input.
        """
        messages = state.get("messages")
        provider_id = config.get("configurable", {}).get("user_id")
        thread_id = config.get("configurable", {}).get("thread_id")

        if len(messages) < 2:
            # pool = await db.db_manager.get_pool()
            # async with pool.connection() as conn:
            #     messages = await db.get_memory_messages(
            #         provider_id=provider_id, thread_id=thread_id, limit=20
            #     )
            print("fetched messages : ", messages)
        else:
            print("state already active : ", messages)

        return Command(
            update={
                "input": state["input"],
                "messages": messages,
                "current_message": state.get("current_message"),
                "reason": state.get("reason"),
                "provider_id": state.get("provider_id"),
                "next_node":"inputer",
                "node_type":"inputer",
                "type":"inputer",
                "next_type":"inputer",
                "plans": state.get("plans", []),
                "current_task": state.get("current_task", "NO TASK"),
                "usages": state.get("usages", {}),
                "tool_output": state.get("tool_output"),
                "max_message": state.get("max_message", 10),
            },
            goto="inputer_node",
        )


memory_loader_node = MemoryLoaderRouter(llm).route