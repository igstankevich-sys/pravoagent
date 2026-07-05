"""
Model Router — трёхуровневая маршрутизация: Flash / Balance / Pro.
Автоматический выбор модели по сложности запроса + fallback при недоступности.

Уровни:
- Flash — быстрые и дешёвые модели для черновиков и простых запросов
- Balance — баланс цены и качества для анализа и ревью
- Pro — максимальное качество для сложных юридических задач
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from backend.services.budget_controller import BudgetController


@dataclass
class TierConfig:
    """Конфигурация одного ценового уровня."""

    models: list[str]
    cost_per_1k: float
    suitable_for: list[str]


@dataclass
class RouterStats:
    """Статистика маршрутизации."""

    total_calls: int = 0
    flash_calls: int = 0
    balance_calls: int = 0
    pro_calls: int = 0
    fallbacks: int = 0
    total_cost: float = 0.0


class ModelRouter:
    """Маршрутизатор запросов к моделям по уровню сложности.

    Позволяет автоматически выбирать модель в зависимости от типа задачи:
    - simple/draft → Flash
    - review/analysis → Balance
    - complex/final → Pro

    Особенности:
    - Оценка стоимости до выполнения запроса
    - Fallback на уровень ниже при недоступности модели
    - Сбор статистики для мониторинга затрат
    """

    TIERS: dict[str, TierConfig] = {
        "flash": TierConfig(
            models=["deepseek-chat", "qwen2.5:7b"],
            cost_per_1k=0.001,
            suitable_for=["simple", "draft"],
        ),
        "balance": TierConfig(
            models=["deepseek-chat", "gpt-4o-mini"],
            cost_per_1k=0.005,
            suitable_for=["review", "analysis"],
        ),
        "pro": TierConfig(
            models=["deepseek-reasoner", "gpt-4o"],
            cost_per_1k=0.02,
            suitable_for=["complex", "legal_analysis", "final"],
        ),
    }

    COMPLEXITY_KEYWORDS: dict[str, str] = {
        "complex": "pro",
        "legal_analysis": "pro",
        "final": "pro",
        "review": "balance",
        "analysis": "balance",
        "draft": "balance",
        "simple": "flash",
    }

    def __init__(self, default_tier: str = "flash") -> None:
        if default_tier not in self.TIERS:
            raise ValueError(
                f"Недопустимый уровень: {default_tier}. "
                f"Допустимые: {', '.join(self.TIERS)}"
            )
        self.default_tier = default_tier
        self.stats = RouterStats()
        self.budget_controller = BudgetController()

    def select_tier(
        self,
        request: str,
        estimated_complexity: Optional[str] = None,
    ) -> str:
        """Выбор уровня модели по сложности запроса.

        Args:
            request: Текст запроса.
            estimated_complexity: Оценка сложности (simple, review, complex, ...).

        Returns:
            Название уровня: flash, balance или pro.
        """
        self.stats.total_calls += 1

        if estimated_complexity:
            tier = self.COMPLEXITY_KEYWORDS.get(estimated_complexity)
            if tier:
                self._increment_tier(tier)
                return tier

        # Авто-определение по ключевым словам в запросе
        request_lower = request.lower()
        pro_keywords = ["иск", "суд", "кассаци", "апелляци", "жалоба", "решение суда"]
        balance_keywords = [
            "анализ", "проверк", "ревью", "экспертиз", "заключен",
        ]

        if any(kw in request_lower for kw in pro_keywords):
            self._increment_tier("pro")
            return "pro"
        if any(kw in request_lower for kw in balance_keywords):
            self._increment_tier("balance")
            return "balance"

        self._increment_tier(self.default_tier)
        return self.default_tier

    def select_model(self, tier: str) -> str:
        """Выбор первой доступной модели для указанного уровня.

        Args:
            tier: Уровень (flash, balance, pro).

        Returns:
            Имя модели.
        """
        config = self.TIERS.get(tier, self.TIERS["flash"])
        return config.models[0] if config.models else "mock"

    def fallback_model(self, tier: str) -> str:
        """Fallback на уровень ниже при недоступности.

        Args:
            tier: Текущий уровень.

        Returns:
            Имя модели с уровнем ниже.
        """
        fallback_map = {"pro": "balance", "balance": "flash", "flash": "flash"}
        fallback_tier = fallback_map.get(tier, "flash")
        if fallback_tier != tier:
            self.stats.fallbacks += 1
        return self.select_model(fallback_tier)

    def can_process(self, db, tenant_id: int, estimated_tokens: int) -> dict:
        """Проверка, можно ли обработать запрос по бюджету."""
        return self.budget_controller.check_budget(db, tenant_id, float(estimated_tokens))

    def get_cost_estimate(self, tier: str, tokens: int) -> float:
        """Оценка стоимости запроса.

        Args:
            tier: Уровень модели.
            tokens: Оценочное количество токенов.

        Returns:
            Стоимость в USD.
        """
        config = self.TIERS.get(tier, self.TIERS["flash"])
        cost = (tokens / 1000) * config.cost_per_1k
        return round(cost, 6)

    def reset_stats(self) -> None:
        """Сброс статистики маршрутизации."""
        self.stats = RouterStats()

    def _increment_tier(self, tier: str) -> None:
        if tier == "flash":
            self.stats.flash_calls += 1
        elif tier == "balance":
            self.stats.balance_calls += 1
        elif tier == "pro":
            self.stats.pro_calls += 1
