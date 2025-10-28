"""
Instagram Profile Module
Handles Instagram profile insights and API interactions.
"""

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from supabase_client import supabase
import httpx

router = APIRouter(
    prefix="/instagram/insight",
    tags=["Instagram insight"]
)


INSTAGRAM_INSIGHT_URL = "https://graph.instagram.com/{ig_id}/insights"


async def get_access_token(platform_user_id: str) -> str:
    """Get access token for Instagram account from database."""
    try:
        response = supabase.table("connected_accounts").select("access_token").eq(
            "platform_user_id", platform_user_id).eq(
            "platform", "instagram").eq(
            "connected", True).limit(1).maybe_single().execute()

        if not response.data or not response.data.get("access_token"):
            raise ValueError("Connected account or access token not found.")

        return response.data["access_token"]
    except Exception as e:
        raise


async def getInstagramInsight(platform_user_id: str) -> dict:
    """
    Fetch Instagram Insights data for a given Instagram account (async).
    Returns a dictionary of metrics and their values.
    """
    try:
        access_token = await get_access_token(platform_user_id)

        if not platform_user_id or not access_token:
            raise ValueError("Missing ig_id or access_token")

        params = {
            "metric": "reach,website_clicks,profile_views,accounts_engaged,total_interactions,likes,comments,saves",
            "period": "days_28",
            "metric_type": "total_value",
            "access_token": access_token,
            "locale": "en_US"
        }

        url = INSTAGRAM_INSIGHT_URL.format(ig_id=platform_user_id)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)

        response.raise_for_status()  # Raise an exception for bad responses (4xx or 5xx)

        data = response.json().get("data", [])
        simplified = {
            item["name"]: item.get("total_value", {}).get("value", 0) 
            for item in data
        }

        return simplified

    except httpx.HTTPStatusError as e:
        # Handle HTTP errors specifically
        error_details = e.response.json()
        return f"Failed to fetch insights: {error_details}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


async def publishInstagramPost(platform_user_id: str, image_url: str, caption: str = None) -> dict:
    """
    Publish a post to Instagram using an image URL.
    This uses Instagram Graph API's two-step process:
    1. Create a media container with the image URL
    2. Publish the media container
    
    Args:
        platform_user_id: Instagram Business Account ID
        image_url: URL of the image to post (must be publicly accessible)
        caption: Optional caption for the post
        
    Returns:
        Dictionary with success status, post_id, and message
    """
    try:
        access_token = await get_access_token(platform_user_id)
        
        if not platform_user_id or not access_token:
            raise ValueError("Missing platform_user_id or access_token")
        
        if not image_url:
            raise ValueError("Missing image_url")
        
        # Step 1: Create media container
        container_url = f"https://graph.instagram.com/v21.0/{platform_user_id}/media"
        container_params = {
            "image_url": image_url,
            "access_token": access_token
        }
        
        if caption:
            container_params["caption"] = caption
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Create container
            container_response = await client.post(container_url, data=container_params)
            container_response.raise_for_status()
            container_data = container_response.json()
            
            if "id" not in container_data:
                return {
                    "success": False,
                    "message": "Failed to create media container",
                    "error": str(container_data)
                }
            
            creation_id = container_data["id"]
            
            # Step 2: Publish the container
            publish_url = f"https://graph.instagram.com/v21.0/{platform_user_id}/media_publish"
            publish_params = {
                "creation_id": creation_id,
                "access_token": access_token
            }
            
            publish_response = await client.post(publish_url, data=publish_params)
            publish_response.raise_for_status()
            publish_data = publish_response.json()
            
            if "id" in publish_data:
                return {
                    "success": True,
                    "post_id": publish_data["id"],
                    "message": "Post published successfully on Instagram"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to publish post",
                    "error": str(publish_data)
                }
                
    except httpx.HTTPStatusError as e:
        error_details = e.response.json() if e.response.content else str(e)
        return {
            "success": False,
            "message": f"HTTP error occurred: {e.response.status_code}",
            "error": str(error_details)
        }
    except Exception as e:
        return {
            "success": False,
            "message": "An unexpected error occurred",
            "error": str(e)
        }
