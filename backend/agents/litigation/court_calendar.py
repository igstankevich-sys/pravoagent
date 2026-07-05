"""
Агент календаря судебных заседаний (CourtCalendar).

Управление расписанием судебных заседаний, напоминания, контроль сроков.
В демо-режиме возвращает шаблонные данные.
"""
from __future__ import annotations

import datetime
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class CourtCalendar:
    """Агент для управления календарём судебных заседаний.

    Отслеживает:
    - Даты заседаний
    - Процессуальные сроки (апелляция, кассация)
    - Напоминания для юриста
    """

    async def get_upcoming_hearings(
        self,
        user_id: int,
        days_ahead: int = 14,
    ) -> list[dict[str, Any]]:
        """Получение предстоящих заседаний.

        Args:
            user_id: ID пользователя.
            days_ahead: Горизонт планирования (дней).

        Returns:
            Список заседаний.
        """
        logger.info("CourtCalendar: get_upcoming_hearings user=%s days=%s", user_id, days_ahead)
        return [
            {
                "id": 1,
                "case": "Пример дела",
                "court": "Арбитражный суд г. Москвы",
                "date": (datetime.datetime.utcnow() + datetime.timedelta(days=3)).isoformat(),
                "type": "предварительное",
                "status": "demo",
            }
        ]

    async def check_procedural_deadlines(self, case_id: int) -> dict[str, Any]:
        """Проверка процессуальных сроков по делу.

        Args:
            case_id: ID дела.

        Returns:
            Словарь со статусом сроков по делу.
        """
        return {
            "appeal_deadline": None,
            "cassation_deadline": None,
            "has_overdue": False,
            "status": "demo",
        }
