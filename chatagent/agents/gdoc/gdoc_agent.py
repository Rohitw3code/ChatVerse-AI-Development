"""
Google Docs Agent Module
Handles all Google Docs-related operations without hardcoded prompts.
All prompts are managed through agents_config.py
"""

from chatagent.agents.create_agent_tool import make_agent_tool_node
from chatagent.agents.gdoc.gdoc_tools import get_gdoc_tool_registry


def create_gdoc_agent_node(prompt: str = None):
    """
    Factory function to create Google Docs agent node with dynamic prompt.
    
    Args:
        prompt (str, optional): Custom prompt for the agent. 
                               If None, loads from agents_config.py
    
    Returns:
        Agent node configured with Google Docs tools
    """
    if prompt is None:
        from chatagent.agents.agents_config import get_agent_config
        config = get_agent_config("gdoc_agent_node")
        prompt = config["prompt"]
    
    return make_agent_tool_node(
        members=get_gdoc_tool_registry(),
        prompt=prompt,
        node_name="gdoc_agent_node",
        parent_node="task_dispatcher_node",
    )


# Default instance for backward compatibility
gdoc_agent_node = create_gdoc_agent_node()
