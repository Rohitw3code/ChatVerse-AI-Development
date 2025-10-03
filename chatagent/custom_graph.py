import os
from dotenv import load_dotenv
from rich.console import Console

from langchain_openai import OpenAIEmbeddings
from langgraph.graph import StateGraph, START, END

from chatagent.config.init import llm

from chatagent.utils import State
from chatagent.model.chat_agent_model import StreamChunk

from chatagent.agents.supervisor_agent import make_supervisor_node
from chatagent.agents.planner_agent import make_planner_node
from chatagent.agents.social_media_manager.gmail.email_agent import gmail_agent_node
from chatagent.agents.social_media_manager.youtube.youtube_agent import youtube_agent_node
from chatagent.agents.social_media_manager.instagram.instagram_agent import instagram_agent_node
from chatagent.agents.research.research_agent import research_agent_node
from chatagent.agents.final_node import final_answer_node
from chatagent.node_registry import NodeRegistry
from chatagent.db.database import Database
from chatagent.prompt.node_prompt import PROMPTS
from chatagent.agents.replanner import re_planner_node
from chatagent.agents.task_selection import task_selection_node
from chatagent.agents.task_dispatcher import task_dispatcher
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from typing import Literal, Optional
from pydantic import BaseModel, Field
from config import BaseConfig
from chatagent.db.database_manager import DatabaseManager
from chatagent.agents.inputer_agent import inputer
from chatagent.unused_nodes.memory_loader import memory_loader_node
from chatagent.unused_nodes.memory_retrieval_agent import memory_retrieval_node


db = Database()
load_dotenv()
rich = Console()

embedding_model = OpenAIEmbeddings(
    api_key=BaseConfig.OPENAI_API_KEY, model="text-embedding-3-small"
)

available_agents = {
    "gmail_agent_node": (
        "Handles ALL tasks related to Gmail or Email. "
    ),
    "social_media_manager_node": (
        "Handles ONLY Instagram-related tasks (posts, reels, insights, analytics, followers, profile, or messages). "
        "It can handle youtube channel or youtube related tasks too"
        "Tasks for Twitter/X, Facebook, WhatsApp, YouTube, and others are currently unsupported and must end with a clear explanation."
    ),
    "research_agent_node": (
        "Handles ALL tasks related to searching or finding information from the internet. "
    )
}


planner_node = make_planner_node(available_agents)
selection_node = task_selection_node()
replanner_node = re_planner_node(available_agents)

instagram_register = NodeRegistry()
instagram_register.add(
    "instagram_agent_node",
    instagram_agent_node,
    "agent",
    "Handle all tasks related to Instagram (posts, reels, insights, analytics, followers, profile, or messages). Always trigger if the query is Instagram-related."
)

instagram_manager_node = make_supervisor_node(
    llm=llm,
    registry=instagram_register,
    node_name="instagram_manager_node",
    goto_end_symbol="social_media_manager_node",
    prompt=PROMPTS.instagram_manager_node
)


social_media_manager_registry = NodeRegistry()
social_media_manager_registry.add(
    "instagram_manager_node",
    instagram_manager_node,
    "supervisor",
    PROMPTS.instagram_manager_node,
)

social_media_manager_registry.add(
    "youtube_agent_node",
    youtube_agent_node, 
    "agent",
    "Handle all tasks related to fetching YouTube OR YOUTUBE Channels"
)


social_media_manager_node = make_supervisor_node(
    llm=llm,
    registry=social_media_manager_registry,
    node_name="social_media_manager_node",
    goto_end_symbol="task_dispatcher_node",
)

main_register = NodeRegistry()
main_register.add(
    "social_media_manager_node",
    social_media_manager_node,
    "supervisor",
    PROMPTS.social_media_manager_node,
)

main_register.add(
    "gmail_agent_node",
    gmail_agent_node,
    "agent",
    "Handle all tasks related to Gmail or Email (reading, drafting, sending, replying, searching, or managing). Always trigger if the query is Gmail/Email-related."
)
main_register.add(
    "research_agent_node", research_agent_node, "agent",
    "Handle all tasks related to searching, looking up, or finding information from the internet (e.g., LinkedIn, Google, web). Always trigger if the query implies search or research."
)

task_dispatcher_node = task_dispatcher(
    llm=llm,
    registry=main_register
)

graph_builder = StateGraph(State)

graph_builder.add_node("inputer_node", inputer)
graph_builder.add_node("planner_node", planner_node)
graph_builder.add_node("task_selection_node", selection_node)
graph_builder.add_node("final_answer_node", final_answer_node)
graph_builder.add_node("task_dispatcher_node", task_dispatcher_node)
graph_builder.add_node("replanner_node", replanner_node)
graph_builder.add_node("gmail_agent_node", gmail_agent_node)
graph_builder.add_node("social_media_manager_node", social_media_manager_node)
graph_builder.add_node("instagram_manager_node", instagram_manager_node)
graph_builder.add_node("instagram_agent_node", instagram_agent_node)
graph_builder.add_node("research_agent_node", research_agent_node)
graph_builder.add_node("youtube_agent_node", youtube_agent_node) 
graph_builder.add_edge(START, "inputer_node")


# png_data = graph_builder.get_graph().draw_mermaid_png()
# with open("graph.png", "wb") as f:
#     f.write(png_data)
# print("Graph saved to graph1.png")
