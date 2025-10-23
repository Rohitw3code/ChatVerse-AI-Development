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


class YouTubeVideoListInput(BaseModel):
    """Input schema for fetching channel videos."""
    max_results: Optional[int] = Field(10, description="Maximum number of videos to fetch (1-50)")
    order: Optional[str] = Field("date", description="Sort order: date, rating, relevance, title, videoCount, viewCount")


class YouTubeVideoDetailsInput(BaseModel):
    """Input schema for fetching video details."""
    video_id: str = Field(..., description="YouTube video ID")


class YouTubeVideoStatsItem(BaseModel):
    """Stats for a single video."""
    video_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    published_at: Optional[str] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    duration: Optional[str] = None
    thumbnail_url: Optional[str] = None


class YouTubeCommentsInput(BaseModel):
    """Input schema for fetching video comments."""
    video_id: str = Field(..., description="YouTube video ID")
    max_results: Optional[int] = Field(20, description="Maximum number of comments to fetch")


class YouTubeCommentItem(BaseModel):
    """Single comment item."""
    author: Optional[str] = None
    text: Optional[str] = None
    like_count: Optional[int] = None
    published_at: Optional[str] = None


class YouTubeSearchInput(BaseModel):
    """Input schema for searching channel content."""
    query: str = Field(..., description="Search query string")
    max_results: Optional[int] = Field(10, description="Maximum number of results")


class YouTubeTrafficSourcesInput(BaseModel):
    """Input schema for traffic sources analytics."""
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")
    max_results: Optional[int] = Field(10, description="Max results to return")


class YouTubeDemographicsInput(BaseModel):
    """Input schema for demographics analytics."""
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")


class YouTubeGeographyInput(BaseModel):
    """Input schema for geography analytics."""
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")
    max_results: Optional[int] = Field(10, description="Max results to return")
