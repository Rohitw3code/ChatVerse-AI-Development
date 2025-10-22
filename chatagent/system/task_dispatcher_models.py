"""
Task Dispatcher Models Module
Contains all Pydantic models specific to task dispatcher operations.
"""

from pydantic import BaseModel, Field, field_validator


class Router(BaseModel):
    """Response model for task routing decisions."""
    next: str = Field(
        ..., 
        description="Exact node name to call next, or 'END' or 'NEXT_TASK'."
    )
    reason: str = Field(
        ..., 
        description="Brief human-readable explanation without revealing internal node names."
    )

    @field_validator("next")
    @classmethod
    def validate_next(cls, v: str) -> str:
        """Validate and sanitize the next node selection."""
        if not v or not v.strip():
            raise ValueError("'next' must not be empty")
        v = v.strip()
        # Note: Validation against dynamic allowed_choices happens in the node logic
        # Here we just ensure it's not empty and trimmed
        return v
