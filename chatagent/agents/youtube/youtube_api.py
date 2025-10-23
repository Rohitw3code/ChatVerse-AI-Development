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
