import secrets
from functools import lru_cache
from typing import Literal

from pydantic.v1 import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = "Personal AI Assistant API"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    database_url: str = (
        "postgresql+psycopg://assistant:assistant@localhost:5432/assistant"
    )

    jwt_secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    jwt_access_token_expire_minutes: int = 30

    # Telemetry
    telemetry_enabled: bool = False

    # LLM Configuration

    llm_mode: Literal["local_llama", "http_tgi", "groq"] = "local_llama"
    tgi_endpoint: str = "http://localhost:8080/generate"
    llama_binary_path: str = "./llama-cli"
    llama_model_path: str = ""
    llm_timeout_seconds: float = Field(default=60.0, gt=0)
    llm_max_retries: int = Field(default=3, ge=1)
    llm_max_new_tokens: int = Field(default=256, gt=0)
    groq_api_key: str = ""

    # Document search configuration
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    milvus_uri: str = "http://localhost:19530"
    milvus_token: str = ""
    milvus_collection_name: str = "documents"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
