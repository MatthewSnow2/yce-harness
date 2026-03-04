"""Configuration settings for the VoiceAgent QA Platform"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""

    app_name: str = "VoiceAgent QA Platform"
    debug: bool = True
    database_url: str = "sqlite:///./voiceqa.db"

    # CORS settings
    cors_origins: list = ["*"]

    # Test configuration
    max_conversation_length: int = 50
    default_response_timeout_ms: int = 2000

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    """Get cached settings instance"""
    return Settings()
