from supabase import create_client, Client
from config import BaseConfig


if not BaseConfig.SUPABASE_URL or not BaseConfig.SUPABASE_KEY:
    raise Exception("Supabase environment variables are missing")

supabase: Client = create_client(BaseConfig.SUPABASE_URL, BaseConfig.SUPABASE_KEY)