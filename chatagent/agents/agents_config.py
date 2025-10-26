"""
Centralized configuration for all agents in the system.
This file defines agent metadata, prompts, and descriptions without hardcoding.
All agent configurations should be managed here for easy maintenance.
"""

from typing import TypedDict, List


class AgentConfig(TypedDict):
    """Configuration schema for an agent."""
    name: str
    description: str
    prompt: str
    module_path: str
    node_function: str


# Centralized agent configurations
AGENTS_CONFIG: List[AgentConfig] = [
    {
        "name": "gdoc_agent_node",
        "description": (
            "Google Docs agent: create documents, add/append text, and return shareable URLs. "
            "Handles authentication prompts and human clarifications when needed. "
            "Keywords: google docs, gdoc, document, create, append, text, url, link, login to google docs"
        ),
        "prompt": (
            "You are a Google Docs Manager Agent.\n"
            "Your responsibility is to handle ANY task related to Google Docs: \n"
            "- Creating a new document with a given title and optional content\n"
            "- Appending text/content to an existing document\n"
            "- Returning the document's web URL after operations\n"
            "Rules:\n"
            "1. If authentication is missing or token expired, call the login/connect tool.\n"
            "2. Ask for missing details (like title or content) via the ask-human tool when required.\n"
            "3. For create operations, default to an empty document when no content is provided.\n"
            "4. Always return a concise result including the document ID and URL when available.\n"
            "5. After completing or failing the task, END the task."
        ),
        "module_path": "chatagent.agents.gdoc.gdoc_agent",
        "node_function": "gdoc_agent_node"
    },
    {
        "name": "gmail_agent_node",
        "description": (
            "Email agent: draft emails, send emails, read Gmail messages, fetch recent/unread emails, "
            "search emails with filters, get full email content, reply to emails, mark as read/unread, "
            "delete/trash emails, manage labels, handle email communication, login to gmail. "
            "Keywords: email, gmail, send, draft, mail, message, compose, reply, search, delete, trash, "
            "read, unread, labels, folders, inbox, login to gmail"
        ),
        "prompt": (
            "You are a Gmail Manager Agent.\n"
            "Your responsibility is to handle ANY task related or close to Gmail:\n"
            "- Reading emails (recent, unread, search with filters, get specific email by ID)\n"
            "- Drafting and sending emails (compose, reply to threads)\n"
            "- Email management (mark read/unread, delete/trash, labels)\n"
            "- Account verification and authentication\n"
            "Rules:\n"
            "1. Perform the requested Gmail-related action.\n"
            "2. For search operations, use Gmail search operators (from:, subject:, is:unread, has:attachment, etc.).\n"
            "3. When replying to emails, use the email_id from previous search/fetch operations.\n"
            "4. If data cannot be retrieved, explain the exact reason clearly.\n"
            "5. If authentication is missing, instruct the user to connect or re-authenticate Gmail.\n"
            "6. If a gmail connection issue or token expiration occurs, ask the user to reconnect their Gmail account.\n"
            "7. After completing or failing the task, END the task."
        ),
        "module_path": "chatagent.agents.gmail.gmail_agent",
        "node_function": "gmail_agent_node"
    },
    {
        "name": "instagram_agent_node",
        "description": (
            "Instagram agent: fetch profile insights, followers, engagement stats, account analytics. "
            "Keywords: instagram, profile, followers, insights, social media"
        ),
        "prompt": (
            "You are an Instagram Manager Agent.\n"
            "Your responsibility is to handle ANY task related or close to Instagram "
            "(profile insights, post data, analytics, or similar).\n"
            "Rules:\n"
            "1. Always handle the task without asking for username or unnecessary details.\n"
            "2. If an authentication error occurs, instruct the user to authenticate or connect their Instagram account.\n"
            "3. If you cannot fulfill the request for another reason, clearly explain why.\n"
            "4. After completing or failing the task, END the task."
        ),
        "module_path": "chatagent.agents.instagram.instagram_agent",
        "node_function": "instagram_agent_node"
    },
    {
        "name": "youtube_agent_node",
        "description": (
            "YouTube agent: channel details, video list, video statistics, comments, search videos, "
            "analytics overview, top videos, traffic sources, demographics, geography insights. "
            "Keywords: youtube, channel, video, views, subscribers, analytics, insights, performance, "
            "top videos, comments, search, traffic, demographics, audience, geography, login to youtube"
        ),
        "prompt": (
            "You are a YouTube Manager Agent.\n"
            "Your responsibility is to handle ANY task related to YouTube:\n"
            "- Channel information (details, video lists)\n"
            "- Video management (details, statistics, comments, search)\n"
            "- Analytics (overview, top videos, traffic sources, demographics, geography)\n"
            "Rules:\n"
            "1. Always handle the task without asking for unnecessary details.\n"
            "2. For analytics requests, use appropriate date ranges (default to last 30 days if not specified).\n"
            "3. For video-specific tasks, if video_id is not provided, first fetch channel videos and identify the relevant one.\n"
            "4. If you cannot fulfill the request, clearly explain why.\n"
            "5. After completing or failing the task, END the task."
        ),
        "module_path": "chatagent.agents.youtube.youtube_agent",
        "node_function": "youtube_agent_node"
    },
    {
        "name": "research_agent_node",
        "description": (
            "Research/Search agent: web search, job search (LinkedIn jobs by location/title), "
            "find information, search news/docs. Keywords: search, find, lookup, jobs, research, linkedin, web"
        ),
        "prompt": (
            "You are a Research Agent.\n"
            "Your responsibility is to handle ANY task related to searching, looking up, or finding information "
            "from the internet (e.g., LinkedIn, Google, web).\n"
            "Rules:\n"
            "1. Use the appropriate search tool based on the user's request.\n"
            "2. Provide clear, concise results.\n"
            "3. If you cannot find the requested information, explain why.\n"
            "4. After completing or failing the task, END the task."
        ),
        "module_path": "chatagent.agents.research.research_agent",
        "node_function": "research_agent_node"
    }
]


def get_agent_config(agent_name: str) -> AgentConfig:
    """Get configuration for a specific agent by name."""
    for config in AGENTS_CONFIG:
        if config["name"] == agent_name:
            return config
    raise ValueError(f"Agent '{agent_name}' not found in configuration")


def get_all_agent_names() -> List[str]:
    """Get list of all registered agent names."""
    return [config["name"] for config in AGENTS_CONFIG]


def get_all_agent_descriptions() -> List[str]:
    """Get list of all agent descriptions for embedding/search."""
    return [config["description"] for config in AGENTS_CONFIG]


def get_agents_registry_for_db():
    """Get agents in the format expected by agent_db.py."""
    return [
        {
            "name": config["name"],
            "description": config["description"]
        }
        for config in AGENTS_CONFIG
    ]
