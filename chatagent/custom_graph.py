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
from chatagent.agents.social_media_manager.instagram.instagram_agent import instagram_agent_node
from chatagent.agents.social_media_manager.youtube.youtube_agent import youtube_agent_node



db = Database()
load_dotenv()
rich = Console()

embedding_model = OpenAIEmbeddings(
    api_key=BaseConfig.OPENAI_API_KEY, model="text-embedding-3-small"
)


search_agent = search_agent_node()
planner_node = make_planner_node()
selection_node = task_selection_node()


main_register = NodeRegistry()
main_register.add(
    "instagram_agent_node",
    instagram_agent_node,
    "agent",
    PROMPTS.social_media_manager_node,
)
main_register.add(
    "gmail_agent_node", gmail_agent_node, "agent",
    "Handle all tasks related to Gmail or Email (reading, drafting, sending, replying, searching, or managing). Always trigger if the query is Gmail/Email-related."
)
main_register.add(
    "research_agent_node", research_agent_node, "agent",
    "Handle all tasks related to searching, looking up, or finding information from the internet (e.g., LinkedIn, Google, web). Always trigger if the query implies search or research."
)

main_register.add(
    "youtube_agent_node", research_agent_node, "agent",
    "Youtube agent to handle all tasks related to YouTube such as fetching channel details, video management, comments, and analytics. Always trigger if the query is YouTube-related."
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
graph_builder.add_node("instagram_agent_node",instagram_agent_node)
graph_builder.add_node("research_agent_node", research_agent_node)
graph_builder.add_node("youtube_agent_node", youtube_agent_node)


graph_builder.add_edge(START, "inputer_node")