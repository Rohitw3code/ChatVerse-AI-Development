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


async def getProfileInfo(platform_user_id: str) -> dict:
    """
    Fetch Instagram profile information.
    Returns basic profile data like username, followers count, media count, etc.
    """
    try:
        access_token = await get_access_token(platform_user_id)
        
        if not platform_user_id or not access_token:
            raise ValueError("Missing platform_user_id or access_token")
        
        url = f"https://graph.instagram.com/v21.0/{platform_user_id}"
        params = {
            "fields": "id,username,name,profile_picture_url,followers_count,follows_count,media_count,biography,website",
            "access_token": access_token
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as e:
        error_details = e.response.json() if e.response.content else str(e)
        return f"Failed to fetch profile info: {error_details}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


async def getRecentMedia(platform_user_id: str, limit: int = 25) -> dict:
    """
    Fetch recent media posts from Instagram account.
    Returns list of recent posts with their details.
    """
    try:
        access_token = await get_access_token(platform_user_id)
        
        if not platform_user_id or not access_token:
            raise ValueError("Missing platform_user_id or access_token")
        
        url = f"https://graph.instagram.com/v21.0/{platform_user_id}/media"
        params = {
            "fields": "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp,like_count,comments_count",
            "limit": limit,
            "access_token": access_token
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as e:
        error_details = e.response.json() if e.response.content else str(e)
        return f"Failed to fetch recent media: {error_details}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


async def getTopPosts(platform_user_id: str, limit: int = 25) -> dict:
    """
    Fetch top performing posts based on engagement (likes + comments).
    Returns sorted list of posts by engagement.
    """
    try:
        # First get all recent media
        media_data = await getRecentMedia(platform_user_id, limit)
        
        if isinstance(media_data, str):  # Error message
            return media_data
        
        posts = media_data.get("data", [])
        
        # Calculate engagement and sort
        for post in posts:
            likes = post.get("like_count", 0) or 0
            comments = post.get("comments_count", 0) or 0
            post["engagement"] = likes + comments
        
        # Sort by engagement
        sorted_posts = sorted(posts, key=lambda x: x.get("engagement", 0), reverse=True)
        
        return {
            "data": sorted_posts,
            "count": len(sorted_posts)
        }
            
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


async def getMediaInsights(platform_user_id: str, media_id: str) -> dict:
    """
    Fetch insights for a specific media post.
    Returns engagement metrics like reach, impressions, saves, etc.
    """
    try:
        access_token = await get_access_token(platform_user_id)
        
        if not platform_user_id or not access_token:
            raise ValueError("Missing platform_user_id or access_token")
        
        url = f"https://graph.instagram.com/v21.0/{media_id}/insights"
        params = {
            "metric": "impressions,reach,engagement,saved,likes,comments,shares",
            "access_token": access_token
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json().get("data", [])
            simplified = {
                item["name"]: item.get("values", [{}])[0].get("value", 0)
                for item in data
            }
            return simplified
            
    except httpx.HTTPStatusError as e:
        error_details = e.response.json() if e.response.content else str(e)
        return f"Failed to fetch media insights: {error_details}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


async def getHashtagSearch(platform_user_id: str, hashtag: str) -> dict:
    """
    Search for Instagram hashtag and get its ID.
    Note: This requires Instagram Business Account and specific permissions.
    """
    try:
        access_token = await get_access_token(platform_user_id)
        
        if not platform_user_id or not access_token:
            raise ValueError("Missing platform_user_id or access_token")
        
        # Remove # if present
        hashtag = hashtag.lstrip('#')
        
        # Use the correct endpoint format
        url = f"https://graph.instagram.com/v21.0/ig_hashtag_search"
        params = {
            "user_id": platform_user_id,
            "q": hashtag,
            "access_token": access_token
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            
            # Check if we have permission issues
            if response.status_code == 400:
                return {
                    "error": "Hashtag search requires Instagram Business Account with proper permissions. "
                            "Please ensure your account is a Business or Creator account and has the required permissions.",
                    "hashtag": hashtag,
                    "status": "permission_required"
                }
            
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as e:
        error_details = e.response.json() if e.response.content else str(e)
        
        # Check for specific permission errors
        if isinstance(error_details, dict) and error_details.get('error', {}).get('code') == 100:
            return {
                "error": "Hashtag search is not available for this account. This feature requires an Instagram Business or Creator account with additional permissions.",
                "hashtag": hashtag,
                "status": "not_available",
                "details": error_details
            }
        
        return f"Failed to search hashtag: {error_details}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


async def getComments(platform_user_id: str, media_id: str) -> dict:
    """
    Fetch comments for a specific media post.
    """
    try:
        access_token = await get_access_token(platform_user_id)
        
        if not platform_user_id or not access_token:
            raise ValueError("Missing platform_user_id or access_token")
        
        url = f"https://graph.instagram.com/v21.0/{media_id}/comments"
        params = {
            "fields": "id,text,username,timestamp,like_count",
            "access_token": access_token
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as e:
        error_details = e.response.json() if e.response.content else str(e)
        return f"Failed to fetch comments: {error_details}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


async def analyzeHashtagsInPosts(platform_user_id: str, limit: int = 25) -> dict:
    """
    Analyze hashtags used in user's own posts.
    Returns hashtag usage statistics and frequency.
    This is an alternative to hashtag search for accounts without Business permissions.
    """
    try:
        # Get recent media
        media_data = await getRecentMedia(platform_user_id, limit)
        
        if isinstance(media_data, str):  # Error message
            return media_data
        
        posts = media_data.get("data", [])
        
        # Extract and count hashtags
        hashtag_count = {}
        hashtag_posts = {}
        
        for post in posts:
            caption = post.get("caption", "")
            if caption:
                # Find all hashtags in caption
                words = caption.split()
                for word in words:
                    if word.startswith("#") and len(word) > 1:
                        hashtag = word.lower()
                        hashtag_count[hashtag] = hashtag_count.get(hashtag, 0) + 1
                        
                        if hashtag not in hashtag_posts:
                            hashtag_posts[hashtag] = []
                        
                        hashtag_posts[hashtag].append({
                            "post_id": post.get("id"),
                            "likes": post.get("like_count", 0),
                            "comments": post.get("comments_count", 0)
                        })
        
        # Sort by frequency
        sorted_hashtags = sorted(hashtag_count.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "total_posts_analyzed": len(posts),
            "unique_hashtags": len(hashtag_count),
            "hashtag_frequency": dict(sorted_hashtags),
            "top_hashtags": sorted_hashtags[:10],
            "hashtag_details": hashtag_posts
        }
        
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
