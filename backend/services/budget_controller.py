"""
Budget Controller - контроль лимитов токенов на тенанта.
"""
from sqlalchemy.orm import Session
from backend.models.base import Tenant


class BudgetController:
    """Контроль расходов на LLM-токены."""

    def check_budget(
        self, db: Session, tenant_id: int, estimated_tokens: float
    ) -> dict:
        """Проверка, не превышен ли бюджет тенанта."""
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            return {"allowed": True, "reason": "no_tenant"}

        budget_limit = tenant.monthly_token_limit or 10_000_000
        used = tenant.tokens_used_this_month or 0
        remaining = budget_limit - used
        usage_pct = (used / budget_limit) * 100 if budget_limit > 0 else 0

        if used >= budget_limit:
            return {
                "allowed": False,
                "budget_limit": budget_limit,
                "used": used,
                "remaining": 0,
                "usage_pct": 100.0,
                "alerts": ["blocked"],
                "reason": "Месячный лимит токенов исчерпан",
            }

        alerts = []
        if usage_pct >= 90:
            alerts.append("critical")
        elif usage_pct >= 80:
            alerts.append("warning")

        return {
            "allowed": remaining > estimated_tokens,
            "budget_limit": budget_limit,
            "used": used,
            "remaining": remaining,
            "usage_pct": round(usage_pct, 1),
            "alerts": alerts,
        }
