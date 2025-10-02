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
    try:
        response = supabase.table("connected_accounts").select("access_token").eq(
            "platform_user_id", platform_user_id).eq(
            "platform", "instagram").eq(
            "connected", True).limit(1).maybe_single().execute()

        if not response.data or not response.data.get("access_token"):
            raise "Connected account or access token not found."

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
            # For internal errors, raising an exception is often better
            raise ValueError("Missing ig_id or access_token")

        params = {
            "metric": "reach,website_clicks,profile_views,accounts_engaged,total_interactions,likes,comments,saves",
            "period": "days_28",
            "metric_type": "total_value",
            "access_token": access_token,
            "locale": "en_US"}

        url = INSTAGRAM_INSIGHT_URL.format(ig_id=platform_user_id)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)

        response.raise_for_status()  # Raise an exception for bad responses (4xx or 5xx)

        data = response.json().get("data", [])
        simplified = {
            item["name"]: item.get(
                "total_value",
                {}).get(
                "value",
                0) for item in data}

        # FIX: Return the dictionary directly
        return simplified

    except httpx.HTTPStatusError as e:
        # Handle HTTP errors specifically
        error_details = e.response.json()
        # Log the error or handle it as needed
        return f"Failed to fetch insights: {error_details}"
    except Exception as e:
        # Re-raise other exceptions to be caught by the tool
        return f"An unexpected error occurred: {str(e)}"


