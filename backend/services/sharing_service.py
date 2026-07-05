"""
Sharing Service - расшаривание документов между пользователями внутри организации.
"""
import datetime
from typing import Optional
from sqlalchemy.orm import Session
from backend.models.base import Document, DocumentACL, AuditLog, User


class SharingService:
    """Сервис расшаривания документов."""

    ACCESS_LEVELS = ["read", "edit", "comment"]

    def share_document(
        self,
        db: Session,
        doc_id: int,
        owner_id: int,
        target_user_id: int,
        access_level: str = "read",
        expires_in_days: Optional[int] = 30,
    ) -> dict:
        """Расшарить документ коллеге."""
        if access_level not in self.ACCESS_LEVELS:
            raise ValueError(
                f"Уровень доступа должен быть: {', '.join(self.ACCESS_LEVELS)}"
            )

        # Проверяем, что пользователи существуют и принадлежат одному тенанту
        owner = db.query(User).filter(User.id == owner_id).first()
        target = db.query(User).filter(User.id == target_user_id).first()
        if not owner or not target:
            raise ValueError("Пользователь не найден")
        if owner.tenant_id != target.tenant_id:
            raise ValueError("Нельзя расшарить документ пользователю из другой организации")

        # Создаём ACL-запись
        expires = None
        if expires_in_days:
            expires = datetime.datetime.utcnow() + datetime.timedelta(days=expires_in_days)

        acl = DocumentACL(
            doc_id=doc_id,
            user_id=target_user_id,
            access_level=access_level,
            expires_at=expires,
            created_by=owner_id,
        )
        db.add(acl)

        # Логируем шаринг
        log = AuditLog(
            user_id=owner_id,
            action="share_document",
            entity_type="document",
            entity_id=str(doc_id),
            details=f"Shared with user {target_user_id}, access={access_level}",
            timestamp=datetime.datetime.utcnow(),
        )
        db.add(log)
        db.commit()

        return {
            "doc_id": doc_id,
            "shared_with": target_user_id,
            "access_level": access_level,
            "expires_at": str(expires) if expires else None,
            "status": "shared",
        }
