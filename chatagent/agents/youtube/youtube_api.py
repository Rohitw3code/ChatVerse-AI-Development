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
