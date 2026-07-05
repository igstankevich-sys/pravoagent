"""
Сервис email-верификации для ПравоАгент.

Генерация кодов подтверждения, проверка кодов, expiry.
В демо-режиме код всегда "000000".
"""

import datetime
import random
from typing import Optional

from sqlalchemy.orm import Session

from backend.config import settings
from backend.models.base import EmailVerification


def generate_code() -> str:
    """Генерирует 6-значный код подтверждения.

    В демо-режиме всегда возвращает "000000",
    в production — случайные цифры.

    Returns:
        str: 6-значный код подтверждения.
    """
    if settings.demo_mode:
        return "000000"
    return "".join(str(random.randint(0, 9)) for _ in range(6))


def create_verification(db: Session, email: str) -> EmailVerification:
    """Создаёт запись верификации email с 6-значным кодом.

    Деактивирует предыдущие неподтверждённые коды для этого email
    и создаёт новую запись с кодом, срок действия — 15 минут.

    Args:
        db: Сессия SQLAlchemy.
        email: Email для верификации.

    Returns:
        EmailVerification: Созданная запись верификации.
    """
    existing = (
        db.query(EmailVerification)
        .filter(EmailVerification.email == email, EmailVerification.is_verified == False)
        .all()
    )
    for record in existing:
        record.is_verified = True

    code = generate_code()
    now = datetime.datetime.utcnow()
    expires_at = now + datetime.timedelta(minutes=15)

    verification = EmailVerification(
        email=email,
        code=code,
        is_verified=False,
        created_at=now,
        expires_at=expires_at,
    )
    db.add(verification)
    db.commit()
    db.refresh(verification)
    return verification


def verify_code(db: Session, email: str, code: str) -> bool:
    """Проверяет код подтверждения для указанного email.

    В демо-режиме принимает любой код.

    Args:
        db: Сессия SQLAlchemy.
        email: Email для верификации.
        code: 6-значный код подтверждения.

    Returns:
        bool: True если код верный и не истёк, иначе False.
    """
    if settings.demo_mode:
        return True

    now = datetime.datetime.utcnow()
    verification = (
        db.query(EmailVerification)
        .filter(
            EmailVerification.email == email,
            EmailVerification.is_verified == False,
            EmailVerification.code == code,
            EmailVerification.expires_at > now,
        )
        .first()
    )

    if verification is None:
        return False

    verification.is_verified = True
    db.commit()
    return True


def resend_code(db: Session, email: str) -> Optional[EmailVerification]:
    """Отправляет новый код подтверждения на email.

    Деактивирует старые коды, генерирует новый.
    В демо-режиме всегда возвращает код "000000".

    Args:
        db: Сессия SQLAlchemy.
        email: Email для повторной отправки.

    Returns:
        Optional[EmailVerification]: Новая запись верификации или None при ошибке.
    """
    return create_verification(db, email)
