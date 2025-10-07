# agent_db.py
# This file serves as a registry for agents, containing their names and descriptions.
# It can be used for semantic search or dynamic agent selection in the multi-agent system.

agents_registry = [
    {
        "name": "gmail_agent",
        "description": "Handles Gmail-related operations including verifying Gmail connections, drafting professional emails with subject and body, sending emails after user approval, fetching recent Gmail messages with sender, subject, and snippet, fetching unread Gmail messages, asking the user for clarifications or missing information, and handling Gmail connection errors by prompting the user to connect their account."
    },
    {
        "name": "instagram_agent",
        "description": "Manages Instagram tasks such as verifying Instagram authentication and connection status, fetching profile insights including followers, following, engagement rate, bio, and other account statistics, asking the user for additional input or confirmation when needed, and handling Instagram errors like authentication issues by prompting the user to connect their account. It ensures tasks are only performed after proper verification and does not assume unavailable details."
    },
    {
        "name": "youtube_agent",
        "description": "Handles YouTube-related operations, primarily fetching details for a specified YouTube channel including channel statistics and information."
    },
    {
        "name":"reaserch_agent",
        "description":        
        "You are a Research/Search Agent with access to these tools:\n"
        "- tavily_search: Search the web for fresh information (news/jobs/docs).\n"
        "- linkedin_job_search: Search LinkedIn job listings by title and location.\n"
        "- linkedin_person_search: Search any person takes search keyword"
    }
]