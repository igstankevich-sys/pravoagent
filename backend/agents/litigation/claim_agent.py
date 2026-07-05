"""
Агент для подготовки претензий (ClaimAgent).

Формирует проекты досудебных претензий на основе данных дела.
В демо-режиме возвращает шаблонный ответ.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ClaimAgent:
    """Агент для подготовки досудебных претензий.

    Анализирует фактические обстоятельства и формирует текст претензии
    в соответствии с требованиями ГК РФ (ст. 15, 393, 395 и др.).
    """

    async def draft_claim(self, case_data: dict[str, Any]) -> str:
        """Формирование проекта претензии.

        Args:
            case_data: Данные дела (стороны, сумма, основание, документы).

        Returns:
            Текст претензии.
        """
        logger.info("ClaimAgent: draft_claim with data keys=%s", list(case_data.keys()))
        return (
            "[ДЕМО] Проект претензии сформирован.\n\n"
            f"Данные дела: {case_data.get('title', 'без названия')}\n\n"
            "В production будет сгенерирован полный текст претензии "
            "с расчётом суммы, ссылками на нормы права и приложениями."
        )

    async def analyze_claim(self, claim_text: str) -> dict[str, Any]:
        """Анализ существующей претензии.

        Args:
            claim_text: Текст претензии для анализа.

        Returns:
            Словарь с оценкой: риски, сильные стороны, рекомендации.
        """
        return {
            "risks": ["риск неполучения ответа", "пропуск срока"],
            "strengths": ["обоснованный расчёт"],
            "recommendations": ["направить заказным письмом с описью"],
            "status": "demo",
        }
