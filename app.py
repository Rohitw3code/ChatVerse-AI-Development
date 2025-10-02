from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from chatagent.chat_agent_router import chat_agent_router
from chatagent.custom_graph import graph_builder
from chatagent.db.database_manager import DatabaseManager
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool = await DatabaseManager.get_pool()
    app.state.pool = pool  # Store the pool in the app state
    conn = await pool.getconn()
    try:
        memory = AsyncPostgresSaver(conn=conn)
        await memory.setup()

        app.state.graph = graph_builder.compile(checkpointer=memory)

        # Try to visualize the graph; don't fail startup if unsupported
        try:
            png_data = None
            g_obj = None
            # Prefer the builder's graph if available (works across LangGraph versions)
            if hasattr(graph_builder, "get_graph"):
                g_obj = graph_builder.get_graph()
            # Otherwise try the compiled graph
            if g_obj is None and hasattr(app.state.graph, "get_graph"):
                g_obj = app.state.graph.get_graph()
            # If we managed to get a graph object, try to render PNG
            if g_obj and hasattr(g_obj, "draw_mermaid_png"):
                png_data = g_obj.draw_mermaid_png()
            # Some versions expose draw_mermaid_png directly on the compiled graph
            if png_data is None and hasattr(app.state.graph, "draw_mermaid_png"):
                png_data = app.state.graph.draw_mermaid_png()
            if png_data:
                with open("graph.png", "wb") as f:
                    f.write(png_data)
                print("Graph saved to graph.png")
            else:
                print("Visualization skipped: Mermaid PNG not supported by this LangGraph version.")
                
        except Exception as viz_err:
            print(f"Visualization skipped: {viz_err}")

        print("🚀 Graph compiled with Postgres memory saver.")

        yield

    finally:
        await pool.putconn(conn)
        print("🔌 Database connection returned to pool.")


app = FastAPI(lifespan=lifespan)


origins = [
    "http://localhost:5173",
    "https://chatverses.web.app",
    "https://chatverse.io",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "https://7rsfnd7q-8000.inc1.devtunnels.ms",
    "https://7rsfnd7q-5173.inc1.devtunnels.ms",
    "https://chatverse-eegsdnaqe7e9gjeb.centralindia-01.azurewebsites.net",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_agent_router)

@app.get("/")
async def root():
    return {"message": "Welcome to ChatVerse AI"}