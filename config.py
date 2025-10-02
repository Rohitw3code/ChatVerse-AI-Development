import os
from dotenv import load_dotenv

load_dotenv()

class BaseConfig:
    # Instagram API Credentials
    INSTAGRAM_CLIENT_ID = os.getenv("INSTAGRAM_CLIENT_ID")
    INSTAGRAM_CLIENT_SECRET = os.getenv("INSTAGRAM_CLIENT_SECRET")
    INSTAGRAM_REDIRECT_URI = os.getenv("INSTAGRAM_REDIRECT_URI")

    # Frontend URL
    FRONTEND_PLATFORM_URL = os.getenv(
        "FRONTEND_PLATFORM_URL", "http://localhost:5173/platforms"
    )

    # Supabase Credentials
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    # Vector Database & Storage Config
    PINECONE_CHAT_INDEX = "autmeta"
    CHAT_BUCKET_NAME = "chatrag"

    # OpenAI and Tavily API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")