"""
Supervisor Models Module
Contains all Pydantic models specific to supervisor agent operations.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List


class Router(BaseModel):
    """Response model for supervisor routing decisions."""
    next: str = Field(
        ..., 
        description="Exact node name to call next, or 'BACK', or 'NEXT_TASK'."
    )
    reason: str = Field(
        ..., 
        description="Brief human-readable explanation without revealing internal node names."
    )

    @field_validator("next")
    @classmethod
    def validate_next(cls, v: str, info) -> str:
        """Validate and sanitize the next node selection."""
        if not v or not v.strip():
            raise ValueError("'next' must not be empty")
        v = v.strip()
        # Note: Full validation against members list happens in the node logic
        # where we have access to the registry members
        return v
