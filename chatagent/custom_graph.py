import os
from dotenv import load_dotenv
from rich.console import Console

from langchain_openai import OpenAIEmbeddings
from langgraph.graph import StateGraph, START, END

from chatagent.utils import State
from chatagent.model.chat_agent_model import StreamChunk

# Import system agents
from chatagent.system.supervisor_agent import make_supervisor_node
from chatagent.system.planner_agent import make_planner_node
from chatagent.system.final_node import final_answer_node
from chatagent.system.task_selection import task_selection_node
from chatagent.system.task_dispatcher import task_dispatcher
from chatagent.system.inputer_agent import inputer
from chatagent.system.agent_search_node import search_agent_node

# Import agents from unified location
from chatagent.agents.gmail import gmail_agent_node
from chatagent.agents.instagram import instagram_agent_node
from chatagent.agents.youtube import youtube_agent_node
from chatagent.agents.research import research_agent_node
from chatagent.agents.sheets import sheets_agent_node
from chatagent.agents.gdoc import gdoc_agent_node
from chatagent.agents.forms import forms_agent_node

from chatagent.node_registry import NodeRegistry
from chatagent.db.database import Database
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import ChatPromptTemplate
from langgraph.types import Command
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from typing import Literal, Optional
from pydantic import BaseModel, Field
from config import BaseConfig
from chatagent.db.database_manager import DatabaseManager

# Import centralized agent configuration
from chatagent.agents.agents_config import AGENTS_CONFIG



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

# Dynamically add agents from centralized configuration
for agent_config in AGENTS_CONFIG:
    agent_name = agent_config["name"]
    agent_prompt = agent_config["prompt"]
    
    # Import the agent node
    if agent_name == "gmail_agent_node":
        main_register.add(agent_name, gmail_agent_node, "agent", agent_prompt)
    elif agent_name == "instagram_agent_node":
        main_register.add(agent_name, instagram_agent_node, "agent", agent_prompt)
    elif agent_name == "youtube_agent_node":
        main_register.add(agent_name, youtube_agent_node, "agent", agent_prompt)
    elif agent_name == "research_agent_node":
        main_register.add(agent_name, research_agent_node, "agent", agent_prompt)
    elif agent_name == "sheets_agent_node":
        main_register.add(agent_name, sheets_agent_node, "agent", agent_prompt)
    elif agent_name == "gdoc_agent_node":
        main_register.add(agent_name, gdoc_agent_node, "agent", agent_prompt)
    elif agent_name == "forms_agent_node":
        main_register.add(agent_name, forms_agent_node, "agent", agent_prompt)

task_dispatcher_node = task_dispatcher(
    registry=main_register
)

graph_builder = StateGraph(State)

graph_builder.add_node("inputer_node", inputer)
graph_builder.add_node("search_agent_node", search_agent)
graph_builder.add_node("planner_node", planner_node)
graph_builder.add_node("task_selection_node", selection_node)
graph_builder.add_node("final_answer_node", final_answer_node)
graph_builder.add_node("task_dispatcher_node", task_dispatcher_node)

#agents
graph_builder.add_node("gmail_agent_node", gmail_agent_node)
graph_builder.add_node("instagram_agent_node",instagram_agent_node)
graph_builder.add_node("research_agent_node", research_agent_node)
graph_builder.add_node("youtube_agent_node", youtube_agent_node)
graph_builder.add_node("sheets_agent_node", sheets_agent_node)
graph_builder.add_node("gdoc_agent_node", gdoc_agent_node)
graph_builder.add_node("forms_agent_node", forms_agent_node)


graph_builder.add_edge(START, "inputer_node")