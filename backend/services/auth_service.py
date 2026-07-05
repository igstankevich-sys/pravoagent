"""
Сервис аутентификации и RBAC для ПравоАгент.
JWT access/refresh токены, хеширование паролей, ролевой контроль доступа.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.models.base import User

security = HTTPBearer(auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Password ---

def hash_password(password: str) -> str:
    """Хеширование пароля через bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля против хеша."""
    return pwd_context.verify(plain_password, hashed_password)


# --- JWT Tokens ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создание access_token (короткоживущий JWT)."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire, "type": "access", "jti": str(uuid.uuid4())})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создание refresh_token (долгоживущий JWT)."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=settings.refresh_token_expire_days)
    )
    to_encode.update({"exp": expire, "type": "refresh", "jti": str(uuid.uuid4())})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    """Декодирование и проверка JWT токена."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен истёк",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
        )


# --- User helpers ---

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Аутентификация пользователя по email + password."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def register_user(
    db: Session,
    email: str,
    username: str,
    password: str,
    role: str = "general",
    tenant_id: Optional[int] = None,
    company_name: Optional[str] = None,
    phone: Optional[str] = None,
) -> User:
    """Регистрация нового пользователя.

    Args:
        db: Сессия SQLAlchemy.
        email: Email пользователя.
        username: Имя пользователя.
        password: Пароль.
        role: Роль в системе.
        tenant_id: ID тенанта (опционально).
        company_name: Название компании (опционально).
        phone: Телефон пользователя (опционально).

    Returns:
        User: Созданный пользователь.

    Raises:
        HTTPException 409: Если email уже зарегистрирован.
        HTTPException 400: Если роль недопустима.
    """
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует",
        )

    valid_roles = {"litigation", "contracts", "general", "head_legal", "admin", "legal_opinions"}
    if role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимая роль: {role}. Допустимые: {', '.join(sorted(valid_roles))}",
        )

    user = User(
        email=email,
        username=username,
        hashed_password=hash_password(password),
        role=role,
        tenant_id=tenant_id,
        is_active=True,
        company_name=company_name,
        phone=phone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def user_to_dict(user: User) -> dict:
    """Сериализация пользователя в словарь (без пароля)."""
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "role": user.role,
        "tenant_id": user.tenant_id,
        "is_active": user.is_active,
        "telegram_chat_id": user.telegram_chat_id,
        "company_name": user.company_name,
        "phone": user.phone,
        "email_verified": user.email_verified,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


# --- FastAPI Dependencies ---

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency: получение текущего пользователя из JWT."""
    if credentials is None:
        if settings.demo_mode:
            user = db.query(User).first()
            if user:
                return user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не предоставлен токен авторизации",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(credentials.credentials)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен: отсутствует идентификатор пользователя",
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Учётная запись заблокирована",
        )

    return user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """FastAPI dependency: опциональное получение пользователя (не блокирует)."""
    if credentials is None:
        return None
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None


class DemoUser:
    """Демо-пользователь для анонимного доступа в demo_mode.

    Позволяет просматривать workspace без аутентификации.
    """
    def __init__(self):
        self.id = 0
        self.email = "demo@pravoagent.ru"
        self.username = "Демо-пользователь"
        self.role = "demo"
        self.tenant_id = 1
        self.is_active = True
        self.is_demo = True
        self.company_name = "Демо-Компания"
        self.phone = None
        self.telegram_chat_id = None
        self.email_verified = False
        self.created_at = None


def get_current_user_or_demo(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency: получение пользователя или демо-пользователя.

    В demo_mode при отсутствии токена возвращает DemoUser.
    При наличии токена — стандартная аутентификация.
    """
    if credentials is None and settings.demo_mode:
        return DemoUser()
    return get_current_user(credentials, db)


def require_role(*roles: str):
    """FastAPI dependency: проверка роли пользователя.

    Использование:
        @router.get("/admin")
        def admin_panel(user: User = Depends(require_role("admin"))):
            ...

    В demo_mode демо-пользователи пропускают проверку роли.
    """
    async def role_checker(
        current_user: User = Depends(get_current_user_or_demo),
    ) -> User:
        # Демо-пользователи пропускают проверку роли в demo_mode
        if getattr(current_user, 'is_demo', False) and settings.demo_mode:
            return current_user
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Доступ запрещён. Требуется роль: {', '.join(roles)}",
            )
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Учётная запись заблокирована",
            )
        return current_user

    return role_checker
