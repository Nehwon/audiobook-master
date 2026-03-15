"""Configuration settings for FastAPI application."""

from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:audiobook123@localhost:5432/audiobook_v3"
    
    # Security
    JWT_SECRET_KEY: str = "votre-secret-key-tres-securise-pour-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Application
    APP_NAME: str = "Audiobook Master v3 API"
    APP_VERSION: str = "3.0.0-alpha.1"
    DEBUG: bool = False
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS: int = 100
    
    # PostgreSQL Events
    PG_NOTIFY_CHANNEL: str = "audiobook_events"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
