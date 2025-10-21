# agent_db.py
# This file serves as a registry for agents, containing their names and descriptions.
# It can be used for semantic search or dynamic agent selection in the multi-agent system.
# All configurations are now loaded from the centralized agents_config.py

from chatagent.agents.agents_config import get_agents_registry_for_db

# Load agents from centralized configuration
agents_registry = get_agents_registry_for_db()
