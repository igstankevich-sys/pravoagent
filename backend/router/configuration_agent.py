"""
API для Configuration Agent — управление настройками KPI метрик.
Phase 10: KPI Dashboard + Configuration Agent.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from backend.database import get_db
from backend.models.base import User
from backend.services.auth_service import require_role
from backend.services.configuration_service import ConfigurationService

router = APIRouter(prefix="/api/kpi", tags=["kpi-config"])
config_service = ConfigurationService()


# --- Pydantic schemas ---


class KpiMetricSchema(BaseModel):
    """Схема метрики KPI для API."""
    metric_key: str
    metric_label: str
    metric_description: Optional[str] = ""
    target_value: Optional[float] = None
    comparison: Optional[str] = "gte"
    is_custom: Optional[bool] = False
    formula: Optional[str] = None
    is_enabled: Optional[bool] = True
    sort_order: Optional[int] = 0


class KpiConfigResponse(BaseModel):
    """Ответ с конфигурацией KPI."""
    id: int
    tenant_id: int
    metric_key: str
    metric_label: str
    metric_description: Optional[str] = ""
    target_value: Optional[float] = None
    comparison: str
    is_custom: bool
    formula: Optional[str] = None
    is_enabled: bool
    sort_order: int


class KpiConfigUpdateRequest(BaseModel):
    """Запрос на обновление всех метрик KPI."""
    metrics: List[KpiMetricSchema]


class KpiAddMetricRequest(BaseModel):
    """Запрос на добавление кастомной метрики."""
    metric_key: Optional[str] = None
    metric_label: str
    metric_description: Optional[str] = ""
    target_value: Optional[float] = None
    comparison: Optional[str] = "gte"
    formula: Optional[str] = None


class KpiToggleRequest(BaseModel):
    """Запрос на включение/выключение метрики."""
    is_enabled: bool


# --- Endpoints ---


@router.get("/config", response_model=List[KpiConfigResponse])
def get_kpi_config(
    current_user: User = Depends(require_role("head_legal", "admin")),
    db: Session = Depends(get_db),
) -> list:
    """Получение конфигурации KPI метрик для текущего тенанта.

    Если конфигурация ещё не создана — возвращает дефолтный набор метрик.
    """
    if current_user.tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь не привязан к тенанту",
        )
    return config_service.get_kpi_config(db, current_user.tenant_id)


@router.put("/config", response_model=List[KpiConfigResponse])
def update_kpi_config(
    request: KpiConfigUpdateRequest,
    current_user: User = Depends(require_role("head_legal", "admin")),
    db: Session = Depends(get_db),
) -> list:
    """Обновление конфигурации KPI метрик для текущего тенанта.

    Заменяет все метрики переданным списком.
    """
    if current_user.tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь не привязан к тенанту",
        )
    metrics_dict = [m.model_dump() for m in request.metrics]
    return config_service.update_kpi_config(db, current_user.tenant_id, metrics_dict)


@router.post("/config/metric", response_model=KpiConfigResponse)
def add_kpi_metric(
    request: KpiAddMetricRequest,
    current_user: User = Depends(require_role("head_legal", "admin")),
    db: Session = Depends(get_db),
) -> dict:
    """Добавление кастомной метрики KPI."""
    if current_user.tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь не привязан к тенанту",
        )
    data = request.model_dump(exclude_none=True)
    return config_service.add_custom_metric(db, current_user.tenant_id, data)


@router.delete("/config/metric/{config_id}")
def delete_kpi_metric(
    config_id: int,
    current_user: User = Depends(require_role("head_legal", "admin")),
    db: Session = Depends(get_db),
) -> dict:
    """Удаление кастомной метрики KPI.

    Встроенные (дефолтные) метрики удалить нельзя.
    """
    if current_user.tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь не привязан к тенанту",
        )

    deleted = config_service.delete_kpi_metric(db, current_user.tenant_id, config_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Метрика не найдена или не является кастомной",
        )
    return {"detail": "Метрика удалена"}


@router.patch("/config/metric/{config_id}/toggle", response_model=KpiConfigResponse)
def toggle_kpi_metric(
    config_id: int,
    request: KpiToggleRequest,
    current_user: User = Depends(require_role("head_legal", "admin")),
    db: Session = Depends(get_db),
) -> dict:
    """Включение/выключение метрики KPI."""
    if current_user.tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь не привязан к тенанту",
        )

    result = config_service.toggle_kpi_metric(db, current_user.tenant_id, config_id, request.is_enabled)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Метрика не найдена",
        )
    return result
