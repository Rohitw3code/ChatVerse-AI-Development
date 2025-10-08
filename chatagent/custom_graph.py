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
from chatagent.agents.social_media_manager.instagram.instagram_agent import instagram_agent_node
# Import the new youtube agent
from chatagent.agents.social_media_manager.youtube.youtube_agent import youtube_agent_node
from chatagent.agents.research.research_agent import research_agent_node
from chatagent.agents.final_node import final_answer_node
from chatagent.node_registry import NodeRegistry
from chatagent.db.database import Database
from chatagent.prompt.node_prompt import PROMPTS
from chatagent.agents.task_selection import task_selection_node
from chatagent.agents.task_dispatcher import task_dispatcher
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import ChatPromptTemplate
from langgraph.types import Command
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from typing import Literal, Optional
from pydantic import BaseModel, Field
from config import BaseConfig
from chatagent.db.database_manager import DatabaseManager
from chatagent.agents.inputer_agent import inputer
from chatagent.agents.agent_search_node import search_agent_node


db = Database()
load_dotenv()
rich = Console()

embedding_model = OpenAIEmbeddings(
    api_key=BaseConfig.OPENAI_API_KEY, model="text-embedding-3-small"
)


search_agent = search_agent_node()
planner_node = make_planner_node()
selection_node = task_selection_node()

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

# Create a new YouTube manager
youtube_register = NodeRegistry()
youtube_register.add("youtube_agent_node", youtube_agent_node, "agent", "Handles all tasks related to YouTube.")

youtube_manager_node = make_supervisor_node(
    llm=llm,
    registry=youtube_register,
    node_name="youtube_manager_node",
    goto_end_symbol="social_media_manager_node",
    prompt=PROMPTS.youtube_manager_node,
)


social_media_manager_registry = NodeRegistry()
social_media_manager_registry.add(
    "instagram_manager_node",
    instagram_manager_node,
    "supervisor",
    PROMPTS.instagram_manager_node,
)
# Add the new YouTube manager to the social media supervisor
social_media_manager_registry.add(
    "youtube_manager_node",
    youtube_manager_node,
    "supervisor",
    PROMPTS.youtube_manager_node,
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
graph_builder.add_node("search_agent_node", search_agent)
graph_builder.add_node("planner_node", planner_node)
graph_builder.add_node("task_selection_node", selection_node)
graph_builder.add_node("final_answer_node", final_answer_node)
graph_builder.add_node("task_dispatcher_node", task_dispatcher_node)
graph_builder.add_node("gmail_agent_node", gmail_agent_node)
graph_builder.add_node("social_media_manager_node", social_media_manager_node)
graph_builder.add_node("instagram_manager_node", instagram_manager_node)
graph_builder.add_node("instagram_agent_node", instagram_agent_node)
graph_builder.add_node("youtube_manager_node", youtube_manager_node)
graph_builder.add_node("youtube_agent_node", youtube_agent_node)
graph_builder.add_node("research_agent_node", research_agent_node)
graph_builder.add_edge(START, "inputer_node")