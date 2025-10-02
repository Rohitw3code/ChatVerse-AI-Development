from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: str
    TAVILY_API_KEY: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    RAPID_API_KEY: str

    # Database
    PSQL_USERNAME: str
    PSQL_PASSWORD: str
    PSQL_HOST: str
    PSQL_PORT: int
    PSQL_DATABASE: str
    PSQL_SSLMODE: str

    # CORS Origins
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "https://chatverses.web.app",
    ]

    # Use model_config to allow extra env vars and specify env file (pydantic v2)
    model_config = {
        "env_file": ".env",
        "extra": "ignore",  # ignore unknown env variables instead of raising
    }

settings = Settings()
