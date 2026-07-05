"""
Агент для подготовки исковых заявлений (LawsuitAgent).

Формирует проекты исковых заявлений для арбитражных судов и судов общей
юрисдикции. В демо-режиме возвращает шаблонный ответ.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class LawsuitAgent:
    """Агент для подготовки исковых заявлений.

    Учитывает подсудность, размер госпошлины, обеспечительные меры.
    """

    async def draft_lawsuit(self, case_data: dict[str, Any]) -> str:
        """Формирование проекта искового заявления.

        Args:
            case_data: Данные дела (стороны, сумма, основание, суд).

        Returns:
            Текст искового заявления.
        """
        logger.info("LawsuitAgent: draft_lawsuit with data keys=%s", list(case_data.keys()))
        return (
            "[ДЕМО] Проект искового заявления сформирован.\n\n"
            f"Данные дела: {case_data.get('title', 'без названия')}\n"
            f"Стороны: {case_data.get('plaintiff', '?')} vs {case_data.get('defendant', '?')}\n\n"
            "В production будет сгенерирован полный текст искового заявления "
            "с расчётом госпошлины, ссылками на нормы права, расчётом "
            "цены иска и перечнем приложений."
        )

    async def calculate_state_fee(self, claim_amount: float) -> dict[str, Any]:
        """Расчёт госпошлины (ст. 333.19, 333.21 НК РФ).

        Args:
            claim_amount: Цена иска в рублях.

        Returns:
            Словарь с размером госпошлины и правилами расчёта.
        """
        if claim_amount <= 0:
            return {"amount": 0, "rule": "без оценки", "status": "demo"}

        return {
            "amount": round(min(claim_amount * 0.04, 200_000), 2),
            "rule": "4% от цены иска, но не более 200 000 руб.",
            "status": "demo",
        }
