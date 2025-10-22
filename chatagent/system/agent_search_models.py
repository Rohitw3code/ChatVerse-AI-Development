"""
Agent Search Models Module
Contains all Pydantic models specific to agent search operations.
"""

from pydantic import BaseModel, Field
from typing import List


class AgentSelection(BaseModel):
    """Model for selecting specific agents needed for the query."""
    selected_agent_names: List[str] = Field(
        description="List of exact agent names (from the provided list) that are required to handle the user query. Only include agents that are explicitly needed. Return empty list if no suitable agents found."
    )
    sufficient: bool = Field(
        description="True if the selected agents can fully handle the user query. False if no suitable agents were found or if the available agents cannot handle the request."
    )
    reason: str = Field(
        description="Brief explanation of why these agents were selected and whether they are sufficient to handle the query"
    )
