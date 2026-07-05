"""
Агент создания договоров (ContractDraftAgent).

Формирует проекты договоров на основе шаблонов и параметров,
указанных пользователем. В демо-режиме возвращает шаблонный ответ.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ContractDraftAgent:
    """Агент для создания проектов договоров.

    Поддерживаемые типы:
    - Договор поставки
    - Договор подряда
    - Договор возмездного оказания услуг
    - Договор аренды
    - Лицензионный договор
    - NDA
    """

    AVAILABLE_TEMPLATES: dict[str, str] = {
        "supply": "Договор поставки",
        "contract": "Договор подряда",
        "services": "Договор возмездного оказания услуг",
        "rent": "Договор аренды",
        "license": "Лицензионный договор",
        "nda": "Соглашение о конфиденциальности (NDA)",
    }

    async def draft_contract(
        self,
        contract_type: str,
        params: dict[str, Any],
    ) -> str:
        """Формирование проекта договора.

        Args:
            contract_type: Тип договора (supply, services, nda, ...).
            params: Параметры договора (стороны, сумма, сроки).

        Returns:
            Текст проекта договора.
        """
        template_name = self.AVAILABLE_TEMPLATES.get(
            contract_type,
            f"Шаблон {contract_type}",
        )
        logger.info(
            "ContractDraftAgent: draft_contract type=%s params_keys=%s",
            contract_type,
            list(params.keys()),
        )
        return (
            "[ДЕМО] Проект договора сформирован.\n\n"
            f"Тип: {template_name}\n"
            f"Параметры: {params}\n\n"
            "В production будет сгенерирован полный текст договора "
            "с учетом всех существенных условий и требований законодательства."
        )
