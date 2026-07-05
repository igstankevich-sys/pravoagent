"""
Admin API endpoints для ПравоАгент.
Пользователи, тенанты, аудит, health check, бюджет.
"""
import datetime
import platform
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.database import get_db
from backend.models.base import User, Tenant, AuditLog
from backend.services.action_logger import ActionLogger
from backend.services.auth_service import require_role

action_logger = ActionLogger()

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users")
def admin_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict:
    """Список всех пользователей."""
    users = db.query(User).offset(skip).limit(limit).all()
    total = db.query(User).count()
    return {
        "total": total,
        "items": [
            {
                "id": u.id,
                "email": u.email,
                "username": u.username,
                "role": u.role,
                "tenant_id": u.tenant_id,
                "is_active": u.is_active,
            }
            for u in users
        ],
    }


@router.get("/tenants")
def admin_tenants(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict:
    """Список всех тенантов с информацией о лимитах."""
    tenants = db.query(Tenant).all()
    return {
        "items": [
            {
                "id": t.id,
                "name": t.name,
                "monthly_token_limit": t.monthly_token_limit,
                "tokens_used_this_month": t.tokens_used_this_month,
                "is_active": t.is_active,
            }
            for t in tenants
        ]
    }


@router.get("/audit-logs")
def admin_audit_logs(
    skip: int = 0,
    limit: int = 50,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict:
    """Логи аудита с фильтрацией."""
    q = db.query(AuditLog)
    if user_id is not None:
        q = q.filter(AuditLog.user_id == user_id)
    if action:
        q = q.filter(AuditLog.action == action)
    if entity_type:
        q = q.filter(AuditLog.entity_type == entity_type)
    logs = q.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    total = q.count()
    return {
        "total": total,
        "items": [
            {
                "id": l.id,
                "timestamp": str(l.timestamp) if l.timestamp else None,
                "user_id": l.user_id,
                "user_name": l.user_name,
                "action": l.action,
                "entity_type": l.entity_type,
                "entity_id": l.entity_id,
                "details": l.details,
            }
            for l in logs
        ],
    }


@router.get("/health")
def admin_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict:
    """Health check всех сервисов."""
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    qdrant_ok = False
    try:
        from backend.config import settings

        import http.client

        conn = http.client.HTTPConnection(
            settings.qdrant_host, settings.qdrant_port, timeout=3
        )
        conn.request("GET", "/")
        resp = conn.getresponse()
        qdrant_ok = resp.status == 200
        conn.close()
    except Exception:
        qdrant_ok = False

    return {
        "status": "ok" if db_ok else "degraded",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "python": platform.python_version(),
        "services": {
            "api": {"status": "healthy", "uptime": None},
            "database": {
                "status": "connected" if db_ok else "error",
                "type": "SQLite" if db_ok else None,
            },
            "qdrant": {
                "status": "connected" if qdrant_ok else "disconnected",
                "host": None,
            },
        },
    }


@router.get("/llm-usage")
def admin_llm_usage(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict:
    """Статистика использования LLM по тенантам."""
    tenants = db.query(Tenant).all()
    items = []
    for t in tenants:
        usage_pct = 0
        if t.monthly_token_limit and t.monthly_token_limit > 0:
            usage_pct = round(
                (t.tokens_used_this_month / t.monthly_token_limit) * 100, 1
            )
        items.append(
            {
                "tenant_id": t.id,
                "tenant_name": t.name,
                "monthly_limit": t.monthly_token_limit,
                "tokens_used": t.tokens_used_this_month,
                "usage_pct": usage_pct,
                "remaining": (t.monthly_token_limit or 0)
                - (t.tokens_used_this_month or 0),
            }
        )
    return {"items": items}


@router.post("/tenants/{tenant_id}/budget")
def update_budget(
    tenant_id: int,
    monthly_limit: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict:
    """Обновление месячного лимита токенов для тенанта."""
    if monthly_limit < 0:
        raise HTTPException(status_code=400, detail="Лимит не может быть отрицательным")
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant.monthly_token_limit = monthly_limit
    action_logger.log(
        db=db,
        user_id=current_user.id,
        action="admin_update_budget",
        entity_type="admin",
        entity_id=str(tenant_id),
        details="Admin action: update_budget",
        tenant_id=current_user.tenant_id,
    )
    db.commit()
    return {
        "status": "updated",
        "tenant_id": tenant_id,
        "monthly_limit": monthly_limit,
    }


@router.post("/tenants/{tenant_id}/toggle")
def toggle_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict:
    """Включение/отключение тенанта."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant.is_active = not tenant.is_active
    action_logger.log(
        db=db,
        user_id=current_user.id,
        action="admin_toggle_tenant",
        entity_type="admin",
        entity_id=str(tenant_id),
        details="Admin action: toggle_tenant",
        tenant_id=current_user.tenant_id,
    )
    db.commit()
    return {
        "status": "toggled",
        "tenant_id": tenant_id,
        "is_active": tenant.is_active,
    }


@router.post("/users/{user_id}/toggle")
def toggle_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict:
    """Блокировка/разблокировка пользователя."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Нельзя заблокировать себя")
    user.is_active = not user.is_active
    action_logger.log(
        db=db,
        user_id=current_user.id,
        action="admin_toggle_user",
        entity_type="admin",
        entity_id=str(user_id),
        details="Admin action: toggle_user",
        tenant_id=current_user.tenant_id,
    )
    db.commit()
    return {
        "status": "toggled",
        "user_id": user_id,
        "is_active": user.is_active,
    }
