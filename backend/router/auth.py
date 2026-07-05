"""
Роутер аутентификации ПравоАгент.
Регистрация, логин, refresh токенов, профиль.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from backend.database import get_db
from backend.models.base import User
from backend.services.auth_service import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    register_user,
    user_to_dict,
)
from backend.services.email_verification import create_verification, verify_code, resend_code as resend_verification_code

router = APIRouter(prefix="/api/auth", tags=["auth"])


# --- Pydantic Schemas ---

class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str
    role: str = "general"
    tenant_id: Optional[int] = None
    company_name: Optional[str] = None
    phone: Optional[str] = None


class VerifyEmailRequest(BaseModel):
    email: str
    code: str


class ResendCodeRequest(BaseModel):
    email: str


class VerifyEmailResponse(BaseModel):
    verified: bool
    message: str


class ResendCodeResponse(BaseModel):
    sent: bool
    message: str


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    role: str
    tenant_id: Optional[int] = None
    is_active: bool
    telegram_chat_id: Optional[str] = None
    company_name: Optional[str] = None
    phone: Optional[str] = None
    email_verified: bool = False
    created_at: Optional[str] = None


# --- Endpoints ---

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Регистрация нового пользователя.

    Создаёт пользователя с указанными данными и инициирует
    email-верификацию (создаёт код подтверждения).
    """
    user = register_user(
        db=db,
        email=request.email,
        username=request.username,
        password=request.password,
        role=request.role,
        tenant_id=request.tenant_id,
        company_name=request.company_name,
        phone=request.phone,
    )

    # Создаём код верификации email
    create_verification(db, user.email)

    return UserResponse(**user_to_dict(user))


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Аутентификация и получение JWT токенов."""
    user = authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )

    token_data = {"sub": str(user.id), "role": user.role, "email": user.email}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(request: RefreshRequest):
    """Обновление access_token по refresh_token."""
    payload = decode_token(request.refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный тип токена. Ожидается refresh_token.",
        )

    token_data = {
        "sub": payload["sub"],
        "role": payload.get("role", ""),
        "email": payload.get("email", ""),
    }
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Получение профиля текущего пользователя."""
    return UserResponse(**user_to_dict(current_user))


@router.get("/verify")
def verify_token(current_user: User = Depends(get_current_user)):
    """Проверка валидности access_token."""
    return {
        "valid": True,
        "user": user_to_dict(current_user),
    }


@router.post("/verify-email", response_model=VerifyEmailResponse)
def verify_email(request: VerifyEmailRequest, db: Session = Depends(get_db)):
    """Подтверждение email по коду верификации.

    Проверяет 6-значный код для указанного email.
    В демо-режиме принимает любой код.

    Args:
        request: Email и код подтверждения.
        db: Сессия БД.

    Returns:
        VerifyEmailResponse: Результат верификации.
    """
    success = verify_code(db, request.email, request.code)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный или истёкший код подтверждения",
        )

    # Отмечаем email пользователя как подтверждённый
    user = db.query(User).filter(User.email == request.email).first()
    if user:
        user.email_verified = True
        db.commit()

    return VerifyEmailResponse(
        verified=True,
        message="Email успешно подтверждён",
    )


@router.post("/resend-code", response_model=ResendCodeResponse)
def resend_code(request: ResendCodeRequest, db: Session = Depends(get_db)):
    """Повторная отправка кода подтверждения.

    Генерирует новый 6-значный код для указанного email.
    В демо-режиме возвращает код "000000".

    Args:
        request: Email для повторной отправки.
        db: Сессия БД.

    Returns:
        ResendCodeResponse: Результат отправки.
    """
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь с таким email не найден",
        )

    if user.email_verified:
        return ResendCodeResponse(
            sent=True,
            message="Email уже подтверждён",
        )

    resend_verification_code(db, request.email)

    return ResendCodeResponse(
        sent=True,
        message=f"Код подтверждения отправлен на {request.email}",
    )


# --- HTML Pages ---

_templates_dir = Path(__file__).parent.parent.parent / "templates"
_auth_env = Environment(
    loader=FileSystemLoader(str(_templates_dir / "auth")),
    autoescape=True,
)


@router.get("/login", response_class=HTMLResponse, include_in_schema=False)
def login_page(request: Request):
    """Страница логина."""
    template = _auth_env.get_template("login.html")
    return HTMLResponse(template.render(request=request))


@router.get("/register", response_class=HTMLResponse, include_in_schema=False)
def register_page(request: Request):
    """Страница регистрации."""
    template = _auth_env.get_template("register.html")
    return HTMLResponse(template.render(request=request))
