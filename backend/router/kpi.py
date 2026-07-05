"""
API для KPI Dashboard Head of Legal.
Phase 10: KPI Dashboard + Configuration Agent.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.base import User
from backend.services.auth_service import require_role
from backend.services.kpi_service import KPIService

router = APIRouter(prefix="/api/kpi", tags=["kpi"])
kpi_service = KPIService()


@router.get("/dashboard")
def kpi_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("head_legal", "admin")),
) -> dict:
    """Получение всех KPI метрик для дашборда Head of Legal."""
    if current_user.tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь не привязан к тенанту",
        )
    return kpi_service.get_dashboard(db, current_user.tenant_id)
