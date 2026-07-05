"""
Observability Router — метрики, логи, eval результаты.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from backend.database import get_db
from backend.models.base import AuditLog, User
from backend.services.auth_service import require_role, get_current_user
from backend.services.action_logger import ActionLogger
from backend.eval.eval_suite import EvalSuite

router = APIRouter(prefix="/api/observability", tags=["observability"])
action_logger = ActionLogger()


class ActionLogCreateRequest(BaseModel):
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    details: Optional[str] = None
    tenant_id: Optional[int] = None


@router.post("/action-logs")
def create_action_log(
    req: ActionLogCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Запись действия пользователя в лог (фронтенд -> бэкенд)."""
    try:
        log = action_logger.log(
            db=db,
            user_id=current_user.id,
            user_name=current_user.username,
            role=current_user.role,
            action=req.action,
            entity_type=req.entity_type,
            entity_id=req.entity_id,
            details=req.details,
            tenant_id=current_user.tenant_id,
        )
        return {"id": log.id, "status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit-logs")
def get_audit_logs(
    skip: int = 0,
    limit: int = 50,
    action: Optional[str] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "head_legal")),
):
    query = db.query(AuditLog)
    if current_user.role == "head_legal" and current_user.tenant_id is not None:
        query = query.filter(AuditLog.tenant_id == current_user.tenant_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    total = query.count()
    logs = query.order_by(AuditLog.id.desc()).offset(skip).limit(limit).all()
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [
            {
                "id": l.id,
                "timestamp": str(l.timestamp) if l.timestamp else None,
                "user_id": l.user_id,
                "user_name": l.user_name,
                "role": l.role,
                "tenant_id": l.tenant_id,
                "action": l.action,
                "entity_type": l.entity_type,
                "entity_id": l.entity_id,
                "details": l.details,
                "ip_address": l.ip_address,
                "session_id": l.session_id,
            }
            for l in logs
        ],
    }


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "head_legal")),
) -> dict:
    from sqlalchemy import func

    query = db.query(AuditLog)
    if current_user.role == "head_legal" and current_user.tenant_id is not None:
        query = query.filter(AuditLog.tenant_id == current_user.tenant_id)

    total_logs = query.with_entities(func.count(AuditLog.id)).scalar()
    unique_users = query.with_entities(func.count(func.distinct(AuditLog.user_id))).scalar()
    action_counts = (
        query.with_entities(AuditLog.action, func.count(AuditLog.id))
        .group_by(AuditLog.action)
        .all()
    )
    return {
        "total_logs": total_logs,
        "unique_users": unique_users,
        "actions": {action: count for action, count in action_counts},
    }


@router.post("/evals/run")
def run_evals(current_user: User = Depends(require_role("admin"))):
    """Запуск eval-тестов (с тестовыми данными)."""
    suite = EvalSuite()
    test_data = {
        "litigation": {
            "accuracy": [
                {"expected": "исковое заявление", "actual": "подготовлено исковое заявление"},
                {"expected": "претензия", "actual": "претензия"},
            ],
            "completeness": [
                {"fields_filled": 5, "required_fields": 5},
                {"fields_filled": 3, "required_fields": 5},
            ],
            "harmlessness": [
                {"has_harmful_content": False},
                {"has_harmful_content": False},
            ],
        },
    }
    return suite.run_all(test_data)
