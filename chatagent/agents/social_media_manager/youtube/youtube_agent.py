from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from supabase_client import supabase
import httpx

router = APIRouter(
    prefix="/instagram/insight",
    tags=["Instagram insight"]
)


