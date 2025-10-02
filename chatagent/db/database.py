from chatagent.db.database_manager import DatabaseManager
from chatagent.db.serialization import Serialization
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage,ToolMessage
import json
from typing import List, Union
import hashlib
import uuid

class Database:
    """A class to manage all database operations."""

    def __init__(self):
        self.db_manager = DatabaseManager()

    async def initialize(self):
        """Initialize the database and create necessary tables."""
        pool = await self.db_manager.get_pool()
        async with pool.connection() as conn:
            try:
                await conn.execute(
                    "ALTER TABLE chat_agent DROP CONSTRAINT IF EXISTS chat_agent_type_check"
                )
            except Exception:
                pass

            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_agent (
                    id BIGSERIAL PRIMARY KEY,
                    stream_type TEXT,
                    provider_id TEXT,
                    thread_id TEXT,
                    query_id TEXT,
                    role TEXT,
                    node TEXT,
                    next_node TEXT,
                    node_type TEXT,
                    next_node_type TEXT,
                    type TEXT,
                    next_type TEXT,
                    message TEXT,
                    reason TEXT,
                    current_messages JSONB,
                    params JSONB,
                    embedding VECTOR(1536),
                    tool_output JSONB,
                    usage JSONB,
                    status TEXT CHECK (status IN ('success','failed','started')),
                    total_token BIGINT,
                    total_cost FLOAT,
                    data JSONB,
                    execution_time TIMESTAMPTZ DEFAULT NOW()
                );
                """
            )

            try:
                await conn.execute(
                    """
                    ALTER TABLE chat_agent DROP CONSTRAINT IF EXISTS chat_agent_type_check;
                    ALTER TABLE chat_agent ADD CONSTRAINT chat_agent_type_check
                    CHECK (type IN ('tool_agent','thinker','executor','planner','starter','supervisor','end','unknown'));
                    """
                )
            except Exception as e:
                print(f"Warning: Could not update type constraint: {e}")

    async def add_message(self, **kwargs):
        """Add a new message to the chat history."""
        pool = await self.db_manager.get_pool()
        async with pool.connection() as conn:
            await self._add_message_to_chat(conn, **kwargs)

    async def _add_message_to_chat(self, conn, **kwargs):
        """Helper method to insert a message into the database."""
        validated_role = Serialization.validate_and_map_role(kwargs.get("role"))
        current_messages_json = Serialization.safe_json_dumps(kwargs.get("current_messages"))
        params_json = Serialization.safe_json_dumps(kwargs.get("params"))
        usage_json = Serialization.safe_json_dumps(kwargs.get("usage"))
        data_json = Serialization.safe_json_dumps(kwargs.get("data"))
        tool_output_json = Serialization.safe_json_dumps(kwargs.get("tool_output"))

        await conn.execute(
            """
            INSERT INTO chat_agent (
                stream_type, provider_id, thread_id, query_id, role, message, node, next_node,
                node_type, next_node_type, type, next_type, reason,
                current_messages, params, embedding, tool_output, usage,
                status, total_token, total_cost, data
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
            """,
            (
                kwargs.get("stream_type"),
                kwargs.get("provider_id"),
                kwargs.get("thread_id"),
                kwargs.get("query_id"),
                validated_role,
                kwargs.get("message"),
                kwargs.get("node"),
                kwargs.get("next_node"),
                kwargs.get("node_type"),
                kwargs.get("next_node_type"),
                kwargs.get("type_"),
                kwargs.get("next_type"),
                kwargs.get("reason"),
                current_messages_json,
                params_json,
                kwargs.get("embedding_vector"),
                tool_output_json,
                usage_json,
                kwargs.get("status"),
                kwargs.get("total_token"),
                kwargs.get("total_cost"),
                data_json,
            ),
        )

    async def search_messages(self, embedding_vector, provider_id=None, thread_id=None):
        """Search for similar messages in the chat history."""
        pool = await self.db_manager.get_pool()
        async with pool.connection() as conn:
            return await self._search_similar_messages(conn, embedding_vector, provider_id, thread_id)

    async def _search_similar_messages(self, conn, embedding_vector, provider_id=None, thread_id=None):
        """Helper method to search for similar messages."""
        conditions = ["embedding IS NOT NULL"] 
        params = [embedding_vector, embedding_vector]

        if provider_id:
            conditions.append("provider_id = %s")
            params.append(provider_id)

        if thread_id:
            conditions.append("thread_id = %s")
            params.append(thread_id)

        where_clause = " AND ".join(conditions)

        similarity_search = await conn.execute(
            f"""
            WITH ranked_messages AS (
                SELECT
                    role,
                    message,
                    params,
                    tool_output,
                    execution_time,
                    1 - (embedding <=> %s::vector) AS cosine_similarity,
                    ROW_NUMBER() OVER (
                        PARTITION BY message
                        ORDER BY 1 - (embedding <=> %s::vector) DESC
                    ) as rn
                FROM chat_agent
                WHERE {where_clause}
            )
            SELECT role, message, params, tool_output, execution_time, cosine_similarity
            FROM ranked_messages
            WHERE rn = 1
            ORDER BY execution_time DESC
            LIMIT 5;
            """,
            tuple(params),
        )
        return await similarity_search.fetchall()

    async def fetch_threads_by_provider(self, provider_id: str):
        """Fetch all threads for a given provider."""
        pool = await self.db_manager.get_pool()
        async with pool.connection() as conn:
            result = await conn.execute(
                "SELECT * FROM chat_thread WHERE provider_id = %s ORDER BY id DESC;",
                (provider_id,)
            )
            return await result.fetchall()

    async def get_chat_history(self, provider_id: str, thread_id: str, limit: int, offset: int):
        """Fetch the chat history for a given thread."""
        pool = await self.db_manager.get_pool()
        async with pool.connection() as conn:
            result = await conn.execute(
                """
                SELECT
                    id, stream_type, provider_id, thread_id, role, node, next_node,
                    node_type, next_node_type, type, next_type, message, reason,
                    current_messages, params, tool_output, usage, status,
                    total_token, total_cost, data, execution_time
                FROM chat_agent
                WHERE provider_id = %s AND thread_id = %s
                ORDER BY execution_time DESC
                LIMIT %s OFFSET %s
                """,
                (provider_id, thread_id, limit, offset)
            )
            return await result.fetchall()

    async def increment_billing_usage(self, provider_id: str, chat_tokens: int = 0, chat_cost: float = 0.0):
        """Increment the billing usage for a provider."""
        pool = await self.db_manager.get_pool()
        async with pool.connection() as conn:
            await conn.execute(
                """
                INSERT INTO billing_usage (provider_id, chat_token, chat_cost)
                VALUES (%s, %s, %s)
                ON CONFLICT (provider_id) DO UPDATE
                SET chat_token = billing_usage.chat_token + EXCLUDED.chat_token,
                    chat_cost = billing_usage.chat_cost + EXCLUDED.chat_cost,
                    current_credits = billing_usage.current_credits - EXCLUDED.chat_token,
                    updated_at = timezone('utc'::text, now());
                """,
                (provider_id, chat_tokens, chat_cost),
            )



    async def get_memory_messages(
        self, provider_id: str, thread_id: str, limit: int = 20, offset: int = 0
    ) -> List[Union[AIMessage, HumanMessage, ToolMessage]]:
        """
        Reconstruct messages from the `current_messages` JSONB column (preserves metadata).
        Returns a list ordered oldest -> newest.
        """
        pool = await self.db_manager.get_pool()
        async with pool.connection() as conn:
            result = await conn.execute(
                """
                SELECT current_messages
                FROM chat_agent
                WHERE provider_id = %s AND thread_id = %s
                ORDER BY execution_time ASC
                LIMIT %s OFFSET %s
                """,
                (provider_id, thread_id, limit, offset),
            )
            rows = await result.fetchall()

        messages: List[Union[AIMessage, HumanMessage, ToolMessage]] = []


        return messages