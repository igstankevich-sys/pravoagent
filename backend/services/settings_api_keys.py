"""
Settings API Keys — управление API-ключами LLM.
Часть Part 12.5 плана.
"""
from backend.config import settings


class APIKeySettings:
    """Управление API-ключами в настройках."""

    PROVIDERS = {
        "deepseek": {
            "name": "DeepSeek",
            "fields": ["api_key", "model"],
            "default_model": "deepseek-chat",
        },
        "openai": {
            "name": "OpenAI",
            "fields": ["api_key", "model"],
            "default_model": "gpt-4o",
        },
        "yandex": {
            "name": "YandexGPT",
            "fields": ["api_key", "catalog"],
            "default_model": None,
        },
        "gigachat": {
            "name": "GigaChat",
            "fields": ["client_id", "secret"],
            "default_model": None,
        },
        "ollama": {
            "name": "Локальная (Ollama)",
            "fields": ["endpoint"],
            "default_model": "qwen2.5:7b",
        },
    }

    def get_status(self) -> dict:
        """Статус всех подключений."""
        return {
            "deepseek": {
                "connected": bool(settings.deepseek_api_key),
                "model": settings.deepseek_model,
            },
            "openai": {
                "connected": bool(settings.openai_api_key),
                "model": settings.openai_model,
            },
            "yandex": {"connected": bool(settings.yandex_api_key)},
            "gigachat": {"connected": bool(settings.gigachat_client_id)},
            "ollama": {"connected": True, "endpoint": settings.ollama_endpoint},
            "demo_mode": settings.demo_mode,
        }
