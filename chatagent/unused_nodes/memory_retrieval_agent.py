from chatagent.utils import State
from langchain_core.runnables import RunnableConfig
from config import BaseConfig
from chatagent.db.database import Database
from langchain_openai import OpenAIEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.types import Command
from pydantic import BaseModel
from langgraph.graph import END
from typing import Literal
from chatagent.config.init import llm
from pydantic import BaseModel, Field, field_validator


class MemoryRetrievalAgent:
    """
    Performs semantic search to retrieve long-term memories
    and adds them to the state in a clean, formatted way.
    """

    class Router(BaseModel):
        next: Literal["planner_node", "finish"] = Field(
            ...,
            description="The next step to take. Use 'planner_node' if the query requires an action based on memories, "
                        "or 'finish' if the query can be directly answered from the retrieved memories."
        )
        reason: str = Field(..., description="Why this next step was chosen.")
        final_answer: str = Field(
            description="If `finish`, provide the final assistant answer strictly based on the retrieved memories and the user query."
        )

    def __init__(self, db, embedding_model, llm):
        self.db = db
        self.embedding_model = embedding_model
        self.llm = llm

    async def retrieve(self, state: State, config: RunnableConfig) -> Command[Literal["planner_node","__end__"]]:
        print("---MEMORY RETRIEVAL NODE---")
        user_input = state.get("input", "")
        if not user_input:
             return Command(
                update={
                    "input": state["input"],
                    "messages": state.get("messages"),
                    "current_message": state.get("current_message"),
                    "reason": state.get("reason"),
                    "provider_id": state.get("provider_id"),
                    "next_node": state.get("next_node"),
                    "node_type": state.get("node_type"),
                    "type": state.get("type"),
                    "next_type": state.get("next_type"),
                    "plans": state.get("plans", []),
                    "current_task": state.get("current_task", "NO TASK"),
                    "usages": state.get("usages", {}),
                    "tool_output": state.get("tool_output"),
                    "max_message": state.get("max_message", 10),
                },
             )

        # 1. Create an embedding for the user's current input
        input_embedding = self.embedding_model.embed_query(user_input)

        provider_id = config.get("configurable", {}).get("user_id")
        thread_id = config.get("configurable", {}).get("thread_id")

        # 2. Query the database for similar messages
        similar_messages = await self.db.search_messages(
            embedding_vector=input_embedding,
            provider_id=provider_id,
            thread_id=thread_id,
        )

        # 3. Format retrieved messages
        if not similar_messages:
            return Command(
                update={
                    "input": state["input"],
                    "messages": state.get("messages"),
                    "current_message": state.get("current_message"),
                    "reason": state.get("reason"),
                    "provider_id": state.get("provider_id"),
                    "next_node": state.get("next_node"),
                    "node_type": state.get("node_type"),
                    "type": state.get("type"),
                    "next_type": state.get("next_type"),
                    "plans": state.get("plans", []),
                    "current_task": state.get("current_task", "NO TASK"),
                    "usages": state.get("usages", {}),
                    "tool_output": state.get("tool_output"),
                    "max_message": state.get("max_message", 10),
                },
             )

        print("***" * 10)
        print("similar =>", similar_messages)
        print("***" * 10)

        formatted_chunks = []
        messages = []
        for idx, msg in enumerate(similar_messages, 1):
            formatted = (
                f"Memory {idx}:\n"
                f"Role: {msg.get('role', 'unknown')}\n"
                f"Message: {msg.get('message', '').strip()}\n"
                f"tool output : {msg.get('tool_output','')}"
                # f"Similarity: {msg.get('cosine_similarity', 0):.3f}\n"
                f"Time: {msg.get('execution_time')}\n"
                f"{'-'*40}"
            )
            messages.append(AIMessage(content=formatted))
            formatted_chunks.append(formatted)

        memory_chunks = "\n".join(formatted_chunks)

        print("START=" * 10)
        print(f"Found relevant memories:\n{memory_chunks}")
        print("END=" * 10)

        messages = [
            SystemMessage(
                content=(
                    "You are Chatverse AI, an intelligent assistant for the platform Chatverse (chatverse.io).\n"
                    "Your purpose is to complete any task with just the user’s query.\n\n"
                    "Capabilities:\n"
                    "- You can perform Gmail-related tasks.\n"
                    "- You can perform Instagram-related tasks.\n"
                    "- For any other domains, You should route to `planner_node`"
                    "Routing Rules:\n"
                    "1. If the user query is a simple greeting, small-talk, or can be answered directly "
                    "using the retrieved memories, choose `finish` and provide the complete answer in `final_answer`.\n"
                    "   - Example: 'Hi', 'What did I say earlier?', 'Summarize our last chat.'\n\n"
                    "2. If no relevant memories are found, always route to `planner_node`.\n\n"
                    "3. If the query requires performing an action or planning a task (for example: 'Send an email', "
                    "'Check my Instagram insights'), route to `planner_node`.\n\n"
                    "Respond strictly with a JSON object matching the Router schema:\n"
                    "{ 'next': 'planner_node'|'finish', 'reason': str, 'final_answer': str }.\n"
                    "- If you choose `finish`, the `final_answer` must come directly from the retrieved memory chunks and the query.\n"
                    "- If you choose `planner_node`, leave `final_answer` empty.\n"
                )
            ),
            HumanMessage(content=f"User query: {user_input}"),
            AIMessage(
                content=(
                    "Use the following pieces of retrieved context (past messages with their role and timestamp) "
                    "to answer the question. If you don't know the answer, just say that you don't know. "
                    "Use three sentences maximum and keep the answer concise.\n\n"
                    f"{memory_chunks}"
                )
            )
        ]

        print("**"*10)
        print("\n\nmemory :: ",messages)
        print("**"*10)

        decision: self.Router = self.llm.with_structured_output(self.Router).invoke(
            messages
        )

        print("\n\ndecision => ",decision,"\n\n")

        if decision.next == "planner_node":
            return Command(
                update={
                    "input": state["input"],
                    "messages": [
                        AIMessage(
                            content=f"Memory retrieved. The plan is to {decision.reason}"
                        )
                    ],
                    "current_message":[
                        AIMessage(content=decision.reason)
                    ],
                    "reason": decision.reason,
                    "provider_id": state.get("provider_id"),
                    "next_node": "planner_node",
                    "node_type":"planner",
                    "type":"memory",
                    "next_type":"planner",
                    "plans": state.get("plans", []),
                    "past_steps": state.get("past_steps", []),
                    "current_task": state.get("current_task", "NO TASK"),
                    "usages": state.get("usages", {}),
                    "tool_output": state.get("tool_output"),
                    "chunks": memory_chunks,
                    "max_message": state.get("max_message", 10),
                    "recall_memories": state.get("recall_memories", []),
                },
                goto="planner_node",
            )
        else:
            return Command(
                update={
                    "input": state["input"],
                    "messages": [
                        AIMessage(
                            content=decision.reason+"\n"+decision.final_answer
                        )
                    ],
                    "current_message": [
                        AIMessage(
                            content=decision.final_answer
                        )
                    ],
                    "reason": decision.reason,
                    "provider_id": state.get("provider_id"),
                    "next_node":"end",
                    "node_type":"end",
                    "type":"end",
                    "next_type":'end',
                    "plans": state.get("plans", []),
                    "past_steps": state.get("past_steps", []),
                    "current_task": state.get("current_task", "NO TASK"),
                    "usages": state.get("usages", {}),
                    "tool_output": state.get("tool_output"),
                    "chunks": memory_chunks,
                    "max_message": state.get("max_message", 10),
                    "recall_memories": state.get("recall_memories", []),
                },
                goto=END,
            )

# Instantiate the agent
db = Database()
embedding_model = OpenAIEmbeddings(
    api_key=BaseConfig.OPENAI_API_KEY, model="text-embedding-3-small"
)

memory_retrieval_node = MemoryRetrievalAgent(db, embedding_model, llm).retrieve