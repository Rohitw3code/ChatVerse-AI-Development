"""
Planner Models Module
Contains all Pydantic models specific to planner agent operations.
"""

from pydantic import BaseModel, Field
from typing import List


class Plan(BaseModel):
    """Structured plan with ordered steps for task execution."""
    steps: List[str] = Field(
        description="Ordered list of steps to follow for completing the user's request."
    )
