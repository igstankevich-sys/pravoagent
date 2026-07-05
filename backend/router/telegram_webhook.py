"""
Telegram Webhook — обработка входящих сообщений от Telegram.
Часть ADR-006: отдельный микросервис с Webhook.
"""
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Request

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/telegram", tags=["telegram_webhook"])


@router.post("/webhook")
async def telegram_webhook(request: Request) -> dict[str, Any]:
    """Webhook для приёма входящих сообщений от Telegram.

    В демо-режиме логирует полученные сообщения.
    В production здесь будет обработка команд:
    - /start — регистрация chat_id
    - /my_cases — список дел
    - /approve — approve документа
    """
    try:
        body = await request.json()
        message = body.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")

        logger.info(
            "Telegram webhook: chat_id=%s text='%s'",
            chat_id,
            text[:100] if text else "",
        )
        # В production здесь: обработка команд, поиск TelegramConnection
        return {"status": "ok", "mode": "demo"}
    except Exception as exc:
        logger.warning("Telegram webhook error: %s", exc)
        return {"status": "error", "detail": str(exc)}
