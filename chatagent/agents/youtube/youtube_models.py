"""
YouTube Models Module
Contains all Pydantic models specific to YouTube agent operations.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class YouTubeChannelDetailsInput(BaseModel):
    """Input schema for fetching YouTube channel details."""
    channel_name: str = Field(
        ..., description="The name of the YouTube channel to fetch details for."
    )


class YouTubeChannelDetails(BaseModel):
    """Schema for YouTube channel details."""
    channel_id: Optional[str] = Field(None, description="YouTube channel ID")
    channel_name: Optional[str] = Field(None, description="Channel name")
    subscriber_count: Optional[int] = Field(None, description="Number of subscribers")
    video_count: Optional[int] = Field(None, description="Total number of videos")
    view_count: Optional[int] = Field(None, description="Total view count")
    description: Optional[str] = Field(None, description="Channel description")
    custom_url: Optional[str] = Field(None, description="Custom channel URL")
    thumbnail_url: Optional[str] = Field(None, description="Channel thumbnail URL")
