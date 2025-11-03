"""Configurações do backend via Pydantic Settings."""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="CLIPADOR_")

    app_env: str = "development"
    database_url: str
    twitch_client_id: Optional[str] = None
    twitch_client_secret: Optional[str] = None
    jwt_secret: str = "change-me"
    jwt_access_minutes: int = 60
    jwt_refresh_days: int = 14
    redis_url: str = "redis://localhost:6379/0"
    kirvano_token: Optional[str] = None
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
