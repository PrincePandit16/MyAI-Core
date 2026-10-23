import secrets
from functools import lru_cache
from typing import Literal

from pydantic.v1 import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = "Personal AI Assistant API"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    database_url: str = "postgresql+psycopg://assistant:assistant@localhost:5432/assistant"

    jwt_secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    jwt_access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
