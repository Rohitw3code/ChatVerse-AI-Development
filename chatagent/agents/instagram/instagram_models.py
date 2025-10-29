"""
Instagram Models Module
Contains all Pydantic models specific to Instagram agent operations.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class InstagramProfileInsight(BaseModel):
    """Schema for Instagram profile insights."""
    followers_count: Optional[int] = Field(None, description="Number of followers")
    following_count: Optional[int] = Field(None, description="Number of following")
    posts_count: Optional[int] = Field(None, description="Number of posts")
    engagement_rate: Optional[float] = Field(None, description="Engagement rate percentage")
    profile_data: Optional[Dict[str, Any]] = Field(None, description="Additional profile data")


class InstagramAuthVerification(BaseModel):
    """Schema for Instagram authentication verification."""
    is_connected: bool = Field(..., description="Whether Instagram account is connected")
    platform_user_id: Optional[str] = Field(None, description="Platform user ID if connected")
    message: str = Field(..., description="Status message")


class InstagramPostPublish(BaseModel):
    """Schema for Instagram post publishing."""
    image_url: str = Field(..., description="URL of the image to post")
    caption: Optional[str] = Field(None, description="Caption for the post")
    
    
class InstagramPostResponse(BaseModel):
    """Schema for Instagram post publishing response."""
    success: bool = Field(..., description="Whether the post was published successfully")
    post_id: Optional[str] = Field(None, description="Instagram post ID if successful")
    message: str = Field(..., description="Status message")
    error: Optional[str] = Field(None, description="Error message if failed")


class InstagramProfileInfo(BaseModel):
    """Schema for Instagram profile information."""
    id: Optional[str] = Field(None, description="Instagram account ID")
    username: Optional[str] = Field(None, description="Instagram username")
    name: Optional[str] = Field(None, description="Display name")
    profile_picture_url: Optional[str] = Field(None, description="Profile picture URL")
    followers_count: Optional[int] = Field(None, description="Number of followers")
    follows_count: Optional[int] = Field(None, description="Number of accounts following")
    media_count: Optional[int] = Field(None, description="Number of media posts")
    biography: Optional[str] = Field(None, description="Account biography")
    website: Optional[str] = Field(None, description="Website URL")


class InstagramMediaItem(BaseModel):
    """Schema for Instagram media/post item."""
    id: str = Field(..., description="Media ID")
    caption: Optional[str] = Field(None, description="Post caption")
    media_type: Optional[str] = Field(None, description="Media type (IMAGE, VIDEO, CAROUSEL_ALBUM)")
    media_url: Optional[str] = Field(None, description="Media URL")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL for videos")
    permalink: Optional[str] = Field(None, description="Post permalink")
    timestamp: Optional[str] = Field(None, description="Post timestamp")
    like_count: Optional[int] = Field(None, description="Number of likes")
    comments_count: Optional[int] = Field(None, description="Number of comments")
    engagement: Optional[int] = Field(None, description="Total engagement (likes + comments)")


class InstagramMediaInsights(BaseModel):
    """Schema for Instagram media insights."""
    impressions: Optional[int] = Field(None, description="Number of impressions")
    reach: Optional[int] = Field(None, description="Number of unique accounts reached")
    engagement: Optional[int] = Field(None, description="Total engagement")
    saved: Optional[int] = Field(None, description="Number of saves")
    likes: Optional[int] = Field(None, description="Number of likes")
    comments: Optional[int] = Field(None, description="Number of comments")
    shares: Optional[int] = Field(None, description="Number of shares")


class InstagramComment(BaseModel):
    """Schema for Instagram comment."""
    id: str = Field(..., description="Comment ID")
    text: str = Field(..., description="Comment text")
    username: str = Field(..., description="Username of commenter")
    timestamp: str = Field(..., description="Comment timestamp")
    like_count: Optional[int] = Field(None, description="Number of likes on comment")
