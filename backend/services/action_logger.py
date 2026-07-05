"""
Action Logger - логирование всех действий пользователей (Audit Log).
"""
from typing import Optional
from sqlalchemy.orm import Session
from backend.models.base import AuditLog
import datetime


class ActionLogger:
    """Логирование действий пользователей."""

    def log(
        self,
        db: Session,
        user_id: int,
        action: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        details: Optional[str] = None,
        tenant_id: Optional[int] = None,
        user_name: Optional[str] = None,
        role: Optional[str] = None,
        ip_address: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> AuditLog:
        """Запись действия в лог аудита.

        Args:
            db: Сессия SQLAlchemy.
            user_id: ID пользователя.
            action: Тип действия (user.login, case.create, ...).
            entity_type: Тип сущности (user, case, document, ...).
            entity_id: ID сущности.
            details: Детали действия.
            tenant_id: ID тенанта.
            user_name: Имя пользователя.
            role: Роль пользователя.
            ip_address: IP-адрес.
            session_id: ID сессии.

        Returns:
            AuditLog: Созданная запись лога.
        """
        log = AuditLog(
            user_id=user_id,
            user_name=user_name,
            role=role,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            tenant_id=tenant_id,
            ip_address=ip_address,
            session_id=session_id,
            timestamp=datetime.datetime.utcnow(),
        )
        db.add(log)
        db.commit()
        return log
