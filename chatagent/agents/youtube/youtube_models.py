"""
YouTube Models Module
Contains all Pydantic models specific to YouTube agent operations.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


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


class YouTubeAnalyticsRequest(BaseModel):
    """Request schema for YouTube Analytics queries."""
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")
    metrics: Optional[str] = Field(
        "views,estimatedMinutesWatched",
        description="Comma-separated metrics to request from YouTube Analytics",
    )
    max_results: Optional[int] = Field(5, description="Max results for ranked lists (e.g. top videos)")


class YouTubeAnalyticsOverview(BaseModel):
    """Aggregated overview metrics returned by the Analytics tool."""
    views: Optional[int] = None
    estimated_minutes_watched: Optional[int] = None
    average_view_duration: Optional[float] = None
    subscribers_gained: Optional[int] = None
    raw: Optional[Dict[str, Any]] = None


class YouTubeTopVideosItem(BaseModel):
    video_id: Optional[str] = None
    title: Optional[str] = None
    views: Optional[int] = None
    estimated_minutes_watched: Optional[int] = None


class YouTubeTopVideosResponse(BaseModel):
    items: List[YouTubeTopVideosItem] = []
