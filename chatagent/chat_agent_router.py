from fastapi import APIRouter, Request, Query
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from rich.console import Console
import uuid
import asyncio

from langchain_core.messages import HumanMessage
from langgraph.types import Command

from chatagent.utils import print_stream_debug
from chatagent.db.database import Database
from chatagent.db.serialization import Serialization
from chatagent.model.chat_agent_model import StreamChunk
from chatagent.custom_graph import embedding_model
from chatagent.model.tool_output import ToolOutput
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

rich = Console()
db = Database()

chat_agent_router = APIRouter(
    prefix="/chatagent/chat",
    tags=["Chat Agent"]
)

class SendMessagePayload(BaseModel):
    message: str
    provider_id: str


class UpdateDataPayload(BaseModel):
    id: int
    thread_id: str
    query_id: str
    data: dict
    merge: bool = False

@chat_agent_router.get("/threads")
async def get_threads(
    provider_id: str = Query(..., description="Provider ID"),
    error: str = Query(None, description="Optional error parameter")
):   
    clean_provider_id = provider_id.split('?')[0].strip()
    
    threads = await db.fetch_threads_by_provider(clean_provider_id)
    return JSONResponse(content=threads)


@chat_agent_router.patch("/update-data")
async def update_message_data(payload: UpdateDataPayload):
    """Update the data JSON for a chat_agent row by id, thread_id and query_id.

    - If merge is False (default), replaces the data entirely.
    - If merge is True, merges the provided JSON into existing data.
    """
    try:
        updated = await db.update_data_by_identifiers(
            row_id=payload.id,
            thread_id=payload.thread_id,
            query_id=payload.query_id,
            data=payload.data,
            merge=payload.merge,
        )
        if not updated:
            return JSONResponse(
                content={"error": "Row not found for given identifiers"}, status_code=404
            )
        return JSONResponse(content={"message": "Data updated", **updated})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@chat_agent_router.delete("/threads/{thread_id}")
async def delete_thread(thread_id: str, request: Request):
    """
    Deletes all checkpoints for a given thread_id.
    """
    try:
        pool = await db.db_manager.get_pool()
        async with pool.connection() as conn:
            checkpointer = AsyncPostgresSaver(conn=conn)
            await checkpointer.adelete_thread(thread_id)
                # 2. Delete all messages from the chat_agent table
            await conn.execute(
                "DELETE FROM chat_agent WHERE thread_id = %s",
                (thread_id,)
            )
            
            # 3. Delete the thread entry from the chat_thread table
            await conn.execute(
                "DELETE FROM chat_thread WHERE thread_id = %s",
                (thread_id,)
            )
            return JSONResponse(content={"message": f"Thread '{thread_id}' deleted successfully."})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@chat_agent_router.get("/history")
async def get_chat_history(
        provider_id: str,
        thread_id: str,
        page: int = 1,
        limit: int = 20):
    offset = (page - 1) * limit
    history = await db.get_chat_history(provider_id, thread_id, limit, offset)
    # print("History : ",history," provider_id : ", provider_id)
    history_dicts = [dict(row) for row in history]
    encoded_history = jsonable_encoder(history_dicts)
    return JSONResponse(content=encoded_history)

async def get_credits(provider_id: str):
    pool = await db.db_manager.get_pool()
    async with pool.connection() as conn:
        result = await conn.execute(
            "SELECT current_credits FROM billing_usage WHERE provider_id = %s",
            (provider_id,)
        )
        row = await result.fetchone()
        print("\n\n\n CREDIT QUERY RESULT: ", row, "\n\n\n")
        if row:
            return row['current_credits']
        return 0

@chat_agent_router.get("/send-message-stream")
async def send_message_stream(
        message: str,
        provider_id: str,
        chat_id: str,
        request: Request,
        human_response: bool = False):
    print("message : ", message, " human : ", human_response)

    query_id = uuid.uuid4()
    print("chatid : ",chat_id)

    graph = request.app.state.graph
    thread_cfg = {
        "configurable": {"thread_id": chat_id, "user_id": provider_id,"query_id":query_id},
        "recursion_limit": 250,
    }

    async def event_gen():
        # Check credits before processing
        current_credits = await get_credits(provider_id)
        print("Current credits:", current_credits," Provider ID:", provider_id)
        if current_credits <= 0:
            error_payload = {
                "error": "Insufficient credits",
                "message": "Your current credits are below zero. Please add credits to continue.",
                "current_credits": current_credits
            }
            yield f"event: error\ndata: {Serialization.safe_json_dumps(error_payload)}\n\n"
            return
        
        
        pool = await db.db_manager.get_pool()

        async with pool.connection() as conn:

            result = await conn.execute(
                "SELECT 1 FROM chat_thread WHERE thread_id = %s AND provider_id = %s",
                (chat_id, provider_id)
            )
            thread_exists = await result.fetchone()

            if not thread_exists:
                words = message.split()
                default_thread_name = " ".join(words[:5])
                if len(words) > 5:
                    default_thread_name += "..."

                await conn.execute(
                    """
                    INSERT INTO chat_thread (thread_id, provider_id, name)
                    VALUES (%s, %s, %s)
                    """,
                    (chat_id, provider_id, default_thread_name)
                )

            message_embedding = None
            try:
                if isinstance(message, str) and message.strip():
                    vecs = await asyncio.to_thread(embedding_model.embed_documents, [message])
                    message_embedding = vecs[0] if vecs else None
            except Exception:
                message_embedding = None

            try:
                _initial_insert_id = await db.add_message(
                    stream_type="updates",
                    provider_id=provider_id,
                    thread_id=chat_id,
                    query_id=query_id,
                    role="human_message",
                    node="input_node",
                    next_node="starter_node",
                    type_="human",
                    next_type="starter",
                    message=message,
                    reason="User Input",
                    current_messages=[{"role": "user", "content": message}],
                    params={},
                    embedding_vector=message_embedding,
                    tool_output=ToolOutput().to_dict(),
                    usage={},
                    status="success",
                    total_token=0,
                    total_cost=0.0,
                    data={}
                )
            except Exception as e:
                print("⚠️ Failed to save initial user message:", e)

            print("message => ", message, human_response)

            state = {
                "messages": [HumanMessage(content=message)],
                "provider_id": provider_id,
                "input": message,
                "max_message": 25,
                "back_count": 0,
                "max_back": 3,
                "dispatch_retries": 0,
                "max_dispatch_retries": 4,
                "task_status": "",
            }

        if human_response:
            state = Command(resume=message)

        print("state input => ", state)
        
        # Session tracking variables
        session_total_cost = 0.0
        session_total_tokens = 0
        session_llm_calls = 0
        
        async for chunk in graph.astream(state, thread_cfg, stream_mode=["messages", "updates", "custom"]):
            if await request.is_disconnected():
                break

            stream_type, stream_data = chunk

            if stream_type == "messages":
                message_chunk = stream_data[0]
                # print("\n\n\n")
                # print("---- ","--start---","-----")

                # print("message chunk : ",message_chunk)
                metadata = stream_data[1]
                if metadata.get("tags",["nonstream"]) == ["nonstream"]:
                    continue
                # print("meta data : ",metadata)

                # print("---- ","--end---","-----")
                # print("\n\n\n")
                node_name = metadata.get('langgraph_node')

                if node_name and message_chunk.content:
                    sc = StreamChunk(
                        stream_type="messages",
                        provider_id=provider_id,
                        thread_id=chat_id,
                        query_id=str(query_id),
                        role="ai_message",
                        node=node_name,
                        message=message_chunk.content,
                        status="streaming"
                    )
                    # print("message ---> : ",sc.message)
                    payload = Serialization.safe_json_dumps(sc.model_dump(mode="python"))
                    yield f"event: delta\ndata: {payload}\n\n"
                continue

            sc = StreamChunk.from_chunk(
                stream_type=stream_type,
                stream_data=stream_data,
                provider_id=provider_id,
                thread_id=chat_id,
                db_current_message=None
            )

            try:
                # print("\n\n","=="*20)
                node_name = next(iter(stream_data.keys()))
                # print("AGENTIC : messagesss ==> ",stream_data[node_name]['messages'])
                # print("=="*20,"\n\n")
            except:
                print("\n\n","=ERROR="*20)
                node_name = next(iter(stream_data.keys()))
                print("node name : ",node_name)
                print("data : ",stream_data)
                print("=="*20,"\n\n")                

            try:
                print_stream_debug(stream_data)
            except BaseException:
                pass

            
            try:
                message_embedding = embedding_model.embed_documents([sc.message])[0]
            except Exception as e:
                print("Embedding Error:", str(e))
            
            try:
                inserted_id = await db.add_message(
                    stream_type=sc.stream_type,
                    provider_id=sc.provider_id,
                    thread_id=sc.thread_id,
                    query_id=query_id,
                    role=sc.role or "unknown",
                    message=sc.message,
                    node=sc.node,
                    reason=sc.reason or "",
                    current_messages=sc.current_messages or [],
                    tool_output=sc.tool_output,
                    next_node=sc.next_node,
                    type_=sc.type_ or "unknown",
                    params=sc.params,
                    next_type=sc.next_type,
                    embedding_vector=message_embedding,
                    usage=sc.usage,
                    status=sc.status or "started",
                    total_token=sc.total_token,
                    total_cost=sc.total_cost,
                    data=sc.data
                )
            except Exception as e:
                print("⚠️ => Failed to save stream chunk:", e)

            # Track session totals for meaningful usage
            if sc.total_token > 0 or sc.total_cost > 0:
                session_total_cost += sc.total_cost
                session_total_tokens += sc.total_token
                session_llm_calls += 1

            # Only show cost tracking for nodes that actually used tokens
            if sc.total_token > 0 or sc.total_cost > 0:
                print(f"\n💰 [TOKEN USAGE] {sc.node}:")
                print(f"   • Cost: ${sc.total_cost:.6f}")
                print(f"   • Tokens: {sc.total_token} (prompt: {sc.usage.get('prompt_tokens', 0)}, completion: {sc.usage.get('completion_tokens', 0)})")
                print(f"   • Action: {sc.reason or 'Processing'}")
                print()

            print("Inserted ID : ", inserted_id)

            await db.increment_billing_usage(
                provider_id=provider_id, chat_tokens=sc.total_token, chat_cost=sc.total_cost)

            # Attach the inserted DB row id to the payload for client correlation
            try:
                sc.id = inserted_id  # type: ignore[attr-defined]
                sc.query_id = str(query_id)
            except Exception:
                pass
            payload = Serialization.safe_json_dumps(sc.model_dump(mode="python"))

            yield f"event: delta\ndata: {payload}\n\n"
        
        # Session summary at the end
        if session_llm_calls > 0:
            print(f"\n🎯 [SESSION SUMMARY]")
            print(f"   • Total Cost: ${session_total_cost:.6f}")
            print(f"   • Total Tokens: {session_total_tokens}")
            print(f"   • LLM Calls: {session_llm_calls}")
            print(f"   • Provider: {provider_id}")
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "X-Accel-Buffering": "no",
        },
    )