"""
Instagram Agent Module
Handles all Instagram-related operations without hardcoded prompts.
All prompts are managed through agents_config.py
"""

from chatagent.agents.create_agent_tool import make_agent_tool_node
from chatagent.agents.instagram.instagram_tools import get_instagram_tool_registry


def create_instagram_agent_node(prompt: str = None):
    """
    Factory function to create Instagram agent node with dynamic prompt.
    
    Args:
        prompt (str, optional): Custom prompt for the agent. 
                               If None, loads from agents_config.py
    
    Returns:
        Agent node configured with Instagram tools
    """
    if prompt is None:
        from chatagent.agents.agents_config import get_agent_config
        config = get_agent_config("instagram_agent_node")
        prompt = config["prompt"]
    
    return make_agent_tool_node(
        members=get_instagram_tool_registry(),
        prompt=prompt,
        node_name="instagram_agent_node",
        parent_node="task_dispatcher_node",
    )


# Default instance for backward compatibility
instagram_agent_node = create_instagram_agent_node()
