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
