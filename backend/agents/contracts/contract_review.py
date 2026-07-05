"""
Агент проверки договоров (ContractReviewAgent).

Анализирует текст договора на предмет рисков, несоответствий,
отсутствия существенных условий. В демо-режиме возвращает шаблон.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ContractReviewAgent:
    """Агент для анализа и ревью договоров.

    Проверяет:
    - Наличие существенных условий (предмет, цена, сроки)
    - Сбалансированность ответственности сторон
    - Соответствие законодательству РФ
    - Корпоративные требования (одобрение сделок)
    """

    async def review(self, contract_text: str) -> dict[str, Any]:
        """Анализ текста договора.

        Args:
            contract_text: Текст договора.

        Returns:
            Словарь с результатами анализа.
        """
        logger.info("ContractReviewAgent: review text_len=%s", len(contract_text))
        return {
            "risks": [
                "Не указан порядок изменения цены",
                "Отсутствует условие о конфиденциальности",
                "Неустойка ниже ключевой ставки ЦБ РФ",
            ],
            "recommendations": [
                "Добавить п. о пересмотре цены при изменении курса",
                "Включить NDA на 3 года после окончания договора",
                "Увеличить неустойку до 0.1% за каждый день просрочки",
            ],
            "missing_clauses": ["Форс-мажор", "Порядок разрешения споров"],
            "status": "demo",
            "overall_risk": "medium",
        }

    async def compare_versions(
        self,
        old_text: str,
        new_text: str,
    ) -> list[dict[str, Any]]:
        """Сравнение двух версий договора.

        Args:
            old_text: Предыдущая версия.
            new_text: Новая версия.

        Returns:
            Список изменений.
        """
        return [
            {
                "section": "Цена",
                "old": "100 000 руб.",
                "new": "120 000 руб.",
                "risk": "medium",
            },
            {
                "section": "Срок",
                "old": "12 месяцев",
                "new": "6 месяцев",
                "risk": "low",
            },
        ]
