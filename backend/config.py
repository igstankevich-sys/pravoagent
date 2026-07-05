import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    app_name: str = "ПравоАгент"
    app_version: str = "0.2.0"
    debug: bool = True
    secret_key: str = "demo-secret-key-change-in-production"

    # Database
    database_url: str = "sqlite:///./data/pravoagent.db"

    # LLM API Keys (demo mode uses mock)
    deepseek_api_key: Optional[str] = None
    deepseek_model: str = "deepseek-chat"
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"
    yandex_api_key: Optional[str] = None
    yandex_catalog: Optional[str] = None
    gigachat_client_id: Optional[str] = None
    gigachat_secret: Optional[str] = None
    ollama_endpoint: str = "http://localhost:11434"

    # Model routing defaults
    default_model_tier: str = "flash"  # flash | balance | pro
    max_tokens_per_month: int = 10_000_000

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Telegram
    telegram_bot_token: Optional[str] = None

    # JWT
    jwt_secret_key: str = "demo-jwt-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Storage
    upload_dir: str = "./data/uploads"
    export_dir: str = "./data/exports"

    # Demo mode
    demo_mode: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
