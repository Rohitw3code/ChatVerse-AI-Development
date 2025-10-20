# agent_db.py
# This file serves as a registry for agents, containing their names and descriptions.
# It can be used for semantic search or dynamic agent selection in the multi-agent system.

agents_registry = [
    {
        "name": "gmail_agent_node",
        "description": "Email agent: draft emails, send emails, read Gmail messages, handle email communication. Keywords: email, gmail, send, draft, mail, message, compose"
    },
    {
        "name": "instagram_agent_node",
        "description": "Instagram agent: fetch profile insights, followers, engagement stats, account analytics. Keywords: instagram, profile, followers, insights, social media"
    },
    {
        "name": "youtube_agent_node",
        "description": "YouTube agent: channel details, video statistics, channel information. Keywords: youtube, channel, video, views, subscribers"
    },
    {
        "name": "research_agent_node",
        "description": "Research/Search agent: web search, job search (LinkedIn jobs by location/title), find information, search news/docs. Keywords: search, find, lookup, jobs, research, linkedin, web"
    }
]