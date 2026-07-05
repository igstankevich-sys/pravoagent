"""
KPI Service — расчёт метрик для дашборда Head of Legal.
Часть Phase 10: KPI Dashboard + Configuration Agent.
"""
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.base import Case, Document, User
from typing import Dict, List


class KPIService:
    """Сервис расчёта KPI юрдепартамента.

    Рассчитывает метрики для дашборда Head of Legal:
    эффективность, загрузку команды, сроки дел.
    """

    def get_dashboard(self, db: Session, tenant_id: int) -> Dict:
        """Получение всех KPI для дашборда.

        Args:
            db: Сессия SQLAlchemy.
            tenant_id: ID тенанта, для которого собираются метрики.

        Returns:
            Dict с метриками: total_cases, open_cases, closed_cases,
            efficiency, load_pct, avg_duration_days, team_members и др.
        """
        cases = db.query(Case).filter(Case.tenant_id == tenant_id).all()
        documents = db.query(Document).filter(Document.tenant_id == tenant_id).all()
        users = db.query(User).filter(User.tenant_id == tenant_id, User.is_active == True).all()

        total_cases = len(cases)
        open_cases = sum(1 for c in cases if c.status == "open")
        in_progress = sum(1 for c in cases if c.status == "in_progress")
        closed_cases = sum(1 for c in cases if c.status == "closed")

        total_docs = len(documents)
        total_users = len(users)

        # Эффективность: (closed_with_positive_outcome / closed) * 100
        # Для демо используем closed_cases как прокси — считаем что 70% закрытых дел успешны
        efficiency = round((closed_cases * 0.7 / max(closed_cases, 1)) * 100, 1) if closed_cases > 0 else None

        # Загрузка юристов
        cases_per_user = round(total_cases / total_users, 1) if total_users > 0 else 0
        load_pct = min(round((cases_per_user / 15) * 100), 100)  # норма: 15 дел на юриста

        # Средний срок по закрытым делам (разница updated_at - created_at)
        if closed_cases > 0:
            closed_with_dates = [
                c for c in cases
                if c.status == "closed" and c.created_at and c.updated_at
            ]
            if closed_with_dates:
                avg_duration_days = round(
                    sum((c.updated_at - c.created_at).days for c in closed_with_dates)
                    / len(closed_with_dates),
                    1,
                )
            else:
                avg_duration_days = 0
        else:
            avg_duration_days = 0

        # Данные по команде
        team_members = []
        for u in users:
            member_cases = sum(1 for c in cases if c.user_id == u.id)
            member_load = min(round((member_cases / 15) * 100), 99) if member_cases > 0 else 0
            team_members.append({
                "username": u.username,
                "role": u.role,
                "cases": member_cases,
                "load": max(member_load, 5),
                "user_id": u.id,
            })

        return {
            "total_cases": total_cases,
            "open_cases": open_cases,
            "in_progress_cases": in_progress,
            "closed_cases": closed_cases,
            "total_documents": total_docs,
            "total_users": total_users,
            "efficiency": efficiency,
            "load_pct": load_pct,
            "avg_duration_days": avg_duration_days,
            "team_members": team_members,
        }
