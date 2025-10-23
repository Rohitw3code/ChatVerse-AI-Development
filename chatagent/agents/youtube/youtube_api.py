"""
YouTube API Module
Handles YouTube API interactions and channel details.
"""

import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from supabase_client import supabase

# Load YouTube credentials from youtube.json
youtube_json_path = os.path.join(os.path.dirname(__file__), "youtube.json")
with open(youtube_json_path, 'r') as f:
    youtube_config = json.load(f)
    google_client_id = youtube_config["web"]["client_id"]
    google_client_secret = youtube_config["web"]["client_secret"]


async def get_youtube_service(user_id: str):
    """
    Creates and returns an authenticated YouTube service object for the given user.
    """
    account_query = (
        supabase.table("connected_accounts")
        .select("*")
        .eq("provider_id", user_id)
        .eq("platform", "youtube")
        .execute()
    )

    if not account_query.data:
        raise Exception("YouTube account not connected for this user.")

    account_data = account_query.data[0]
    
    creds_info = {
        "token": account_data.get("access_token"),
        "refresh_token": account_data.get("refresh_token"),
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": google_client_id,
        "client_secret": google_client_secret,
        "scopes": account_data.get("scopes"),
    }

    creds = Credentials.from_authorized_user_info(creds_info)

    return build("youtube", "v3", credentials=creds)


async def get_channel_details(user_id: str) -> dict:
    """
    Fetches basic details (snippet, statistics) for the user's authenticated YouTube channel.
    """
    try:
        service = await get_youtube_service(user_id)
        response = service.channels().list(
            part="snippet,statistics",
            mine=True
        ).execute()
        
        if not response.get('items'):
            return {"error": "No YouTube channel found for this account."}
            
        return response['items'][0]
    except Exception as e:
        return {"error": f"Failed to fetch YouTube channel details: {str(e)}"}


async def get_analytics_service(user_id: str):
    """
    Creates and returns an authenticated YouTube Analytics service object for the given user.
    """
    account_query = (
        supabase.table("connected_accounts")
        .select("*")
        .eq("provider_id", user_id)
        .eq("platform", "youtube")
        .execute()
    )

    if not account_query.data:
        raise Exception("YouTube account not connected for this user.")

    account_data = account_query.data[0]
    creds_info = {
        "token": account_data.get("access_token"),
        "refresh_token": account_data.get("refresh_token"),
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": google_client_id,
        "client_secret": google_client_secret,
        "scopes": account_data.get("scopes"),
    }

    creds = Credentials.from_authorized_user_info(creds_info)

    return build("youtubeAnalytics", "v2", credentials=creds)


async def get_analytics_overview(user_id: str, start_date: str, end_date: str, metrics: str = "views,estimatedMinutesWatched") -> dict:
    """
    Fetches aggregated analytics metrics for the authenticated user's channel.
    Returns a dict mapping metric names to values (or an error dict).
    """
    try:
        service = await get_analytics_service(user_id)
        response = service.reports().query(
            ids="channel==MINE",
            startDate=start_date,
            endDate=end_date,
            metrics=metrics,
        ).execute()

        # Parse response. Expected shape: columnHeaders + rows
        headers = [h.get("name") for h in response.get("columnHeaders", [])]
        rows = response.get("rows", [])
        if not rows:
            return {"error": "No analytics rows returned for given range."}

        row = rows[0]
        parsed = {}
        for i, h in enumerate(headers):
            try:
                # try to coerce to int when reasonable
                parsed[h] = int(row[i]) if row[i] is not None and str(row[i]).isdigit() else row[i]
            except Exception:
                parsed[h] = row[i]

        return {"headers": headers, "values": parsed, "raw": response}
    except Exception as e:
        return {"error": f"Failed to fetch analytics overview: {str(e)}"}


async def get_top_videos(user_id: str, start_date: str, end_date: str, max_results: int = 5) -> dict:
    """
    Fetches top videos by views for the authenticated user's channel over a date range.
    Returns a list of items with video id and metrics. Title may be None (Data API lookup can be added later).
    """
    try:
        service = await get_analytics_service(user_id)
        response = service.reports().query(
            ids="channel==MINE",
            startDate=start_date,
            endDate=end_date,
            metrics="views,estimatedMinutesWatched",
            dimensions="video",
            sort="-views",
            maxResults=max_results,
        ).execute()

        headers = [h.get("name") for h in response.get("columnHeaders", [])]
        rows = response.get("rows", [])
        items = []
        for r in rows:
            # expected row shape: [videoId, views, estimatedMinutesWatched]
            video_id = r[0] if len(r) > 0 else None
            views = int(r[1]) if len(r) > 1 and r[1] is not None and str(r[1]).isdigit() else None
            emw = int(r[2]) if len(r) > 2 and r[2] is not None and str(r[2]).isdigit() else None
            items.append({"video_id": video_id, "views": views, "estimated_minutes_watched": emw})

        return {"headers": headers, "items": items, "raw": response}
    except Exception as e:
        return {"error": f"Failed to fetch top videos: {str(e)}"}


async def get_channel_videos(user_id: str, max_results: int = 10, order: str = "date") -> dict:
    """
    Fetches a list of videos from the authenticated user's channel.
    """
    try:
        service = await get_youtube_service(user_id)
        
        # First, get the uploads playlist ID
        channels_response = service.channels().list(
            part="contentDetails",
            mine=True
        ).execute()
        
        if not channels_response.get('items'):
            return {"error": "No channel found for this account."}
        
        uploads_playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # Now fetch videos from the uploads playlist
        playlist_response = service.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=uploads_playlist_id,
            maxResults=min(max_results, 50)
        ).execute()
        
        videos = []
        for item in playlist_response.get('items', []):
            video_data = {
                "video_id": item['contentDetails']['videoId'],
                "title": item['snippet']['title'],
                "description": item['snippet']['description'],
                "published_at": item['snippet']['publishedAt'],
                "thumbnail_url": item['snippet']['thumbnails'].get('high', {}).get('url')
            }
            videos.append(video_data)
        
        return {"items": videos, "count": len(videos)}
    except Exception as e:
        return {"error": f"Failed to fetch channel videos: {str(e)}"}


async def get_video_details(user_id: str, video_id: str) -> dict:
    """
    Fetches detailed statistics and info for a specific video.
    """
    try:
        service = await get_youtube_service(user_id)
        response = service.videos().list(
            part="snippet,statistics,contentDetails",
            id=video_id
        ).execute()
        
        if not response.get('items'):
            return {"error": f"Video with ID {video_id} not found."}
        
        video = response['items'][0]
        stats = video.get('statistics', {})
        snippet = video.get('snippet', {})
        content = video.get('contentDetails', {})
        
        return {
            "video_id": video_id,
            "title": snippet.get('title'),
            "description": snippet.get('description'),
            "published_at": snippet.get('publishedAt'),
            "view_count": int(stats.get('viewCount', 0)),
            "like_count": int(stats.get('likeCount', 0)),
            "comment_count": int(stats.get('commentCount', 0)),
            "duration": content.get('duration'),
            "thumbnail_url": snippet.get('thumbnails', {}).get('high', {}).get('url'),
            "tags": snippet.get('tags', []),
            "category_id": snippet.get('categoryId')
        }
    except Exception as e:
        return {"error": f"Failed to fetch video details: {str(e)}"}


async def get_video_comments(user_id: str, video_id: str, max_results: int = 20) -> dict:
    """
    Fetches comments for a specific video.
    """
    try:
        service = await get_youtube_service(user_id)
        response = service.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=min(max_results, 100),
            order="relevance"
        ).execute()
        
        comments = []
        for item in response.get('items', []):
            comment = item['snippet']['topLevelComment']['snippet']
            comments.append({
                "author": comment.get('authorDisplayName'),
                "text": comment.get('textDisplay'),
                "like_count": comment.get('likeCount', 0),
                "published_at": comment.get('publishedAt')
            })
        
        return {"comments": comments, "count": len(comments)}
    except Exception as e:
        return {"error": f"Failed to fetch video comments: {str(e)}"}


async def search_channel_content(user_id: str, query: str, max_results: int = 10) -> dict:
    """
    Searches for videos in the authenticated user's channel.
    """
    try:
        service = await get_youtube_service(user_id)
        
        # First get channel ID
        channels_response = service.channels().list(
            part="id",
            mine=True
        ).execute()
        
        if not channels_response.get('items'):
            return {"error": "No channel found for this account."}
        
        channel_id = channels_response['items'][0]['id']
        
        # Search within channel
        search_response = service.search().list(
            part="snippet",
            channelId=channel_id,
            q=query,
            maxResults=min(max_results, 50),
            type="video"
        ).execute()
        
        results = []
        for item in search_response.get('items', []):
            results.append({
                "video_id": item['id']['videoId'],
                "title": item['snippet']['title'],
                "description": item['snippet']['description'],
                "published_at": item['snippet']['publishedAt'],
                "thumbnail_url": item['snippet']['thumbnails'].get('high', {}).get('url')
            })
        
        return {"results": results, "count": len(results), "query": query}
    except Exception as e:
        return {"error": f"Failed to search channel content: {str(e)}"}


async def get_traffic_sources(user_id: str, start_date: str, end_date: str, max_results: int = 10) -> dict:
    """
    Fetches traffic source analytics (where views are coming from).
    """
    try:
        service = await get_analytics_service(user_id)
        response = service.reports().query(
            ids="channel==MINE",
            startDate=start_date,
            endDate=end_date,
            metrics="views,estimatedMinutesWatched",
            dimensions="insightTrafficSourceType",
            sort="-views",
            maxResults=max_results
        ).execute()
        
        headers = [h.get("name") for h in response.get("columnHeaders", [])]
        rows = response.get("rows", [])
        sources = []
        
        for r in rows:
            source_type = r[0] if len(r) > 0 else None
            views = int(r[1]) if len(r) > 1 and str(r[1]).isdigit() else 0
            watch_time = int(r[2]) if len(r) > 2 and str(r[2]).isdigit() else 0
            sources.append({
                "source_type": source_type,
                "views": views,
                "estimated_minutes_watched": watch_time
            })
        
        return {"traffic_sources": sources, "count": len(sources)}
    except Exception as e:
        return {"error": f"Failed to fetch traffic sources: {str(e)}"}


async def get_demographics(user_id: str, start_date: str, end_date: str) -> dict:
    """
    Fetches audience demographics (age groups and gender).
    """
    try:
        service = await get_analytics_service(user_id)
        response = service.reports().query(
            ids="channel==MINE",
            startDate=start_date,
            endDate=end_date,
            metrics="viewerPercentage",
            dimensions="ageGroup,gender",
            sort="-viewerPercentage"
        ).execute()
        
        headers = [h.get("name") for h in response.get("columnHeaders", [])]
        rows = response.get("rows", [])
        demographics = []
        
        for r in rows:
            age_group = r[0] if len(r) > 0 else None
            gender = r[1] if len(r) > 1 else None
            percentage = float(r[2]) if len(r) > 2 else 0.0
            demographics.append({
                "age_group": age_group,
                "gender": gender,
                "viewer_percentage": percentage
            })
        
        return {"demographics": demographics, "count": len(demographics)}
    except Exception as e:
        return {"error": f"Failed to fetch demographics: {str(e)}"}


async def get_geography_analytics(user_id: str, start_date: str, end_date: str, max_results: int = 10) -> dict:
    """
    Fetches geographic analytics (views by country).
    """
    try:
        service = await get_analytics_service(user_id)
        response = service.reports().query(
            ids="channel==MINE",
            startDate=start_date,
            endDate=end_date,
            metrics="views,estimatedMinutesWatched",
            dimensions="country",
            sort="-views",
            maxResults=max_results
        ).execute()
        
        headers = [h.get("name") for h in response.get("columnHeaders", [])]
        rows = response.get("rows", [])
        geography = []
        
        for r in rows:
            country = r[0] if len(r) > 0 else None
            views = int(r[1]) if len(r) > 1 and str(r[1]).isdigit() else 0
            watch_time = int(r[2]) if len(r) > 2 and str(r[2]).isdigit() else 0
            geography.append({
                "country": country,
                "views": views,
                "estimated_minutes_watched": watch_time
            })
        
        return {"geography": geography, "count": len(geography)}
    except Exception as e:
        return {"error": f"Failed to fetch geography analytics: {str(e)}"}
