"""
Inputer Agent Models Module
Contains all Pydantic models specific to inputer (input router) agent operations.
"""

from pydantic import BaseModel, Field
from typing import Literal


class Router(BaseModel):
    """Routes user input to either agent search or direct answer."""
    next: Literal["search_agent_node", "finish"] = Field(
        ..., 
        description="Next node to route to based on query type"
    )
    reason: str = Field(
        ...,
        description="Short message to the user as if you're starting to work on their request (max 15 words). Examples: 'I'll help you with this task.', 'Let me answer that for you.' "
    )
