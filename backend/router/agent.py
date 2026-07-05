"""
Router: AI Agent API для ПравоАгент.

Устаревший симулятор (direct) заменён на вызов LangGraph-оркестратора.
Endpoint: POST /api/agent/chat
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.agents.orchestrator import Orchestrator
from backend.database import get_db
from backend.models.base import AuditLog
from backend.services.auth_service import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agent", tags=["agent"])
orchestrator = Orchestrator()


# ---------------------------------------------------------------------------
# Pydantic схемы
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000, description="Текст запроса")
    agent_type: str = Field(
        default="",
        description=(
            "Тип агента: litigation | contracts | general_dept | legal_opinion. "
            "Если не указан — определяется автоматически."
        ),
    )
    case_id: Optional[int] = Field(default=None, description="ID дела (опционально)")
    estimated_complexity: Optional[str] = Field(
        default=None,
        description="Оценка сложности: simple | review | complex | legal_analysis",
    )


class ChatResponse(BaseModel):
    response: str = Field(..., description="Ответ агента")
    agent_type: str = Field(..., description="Тип агента, обработавшего запрос")
    requires_human_approval: bool = Field(
        default=False,
        description="Требуется ли утверждение человеком",
    )
    approved: Optional[bool] = Field(
        default=None,
        description="Статус утверждения (null = ожидает)",
    )
    model_used: str = Field(default="mock", description="Модель LLM")
    model_tier: str = Field(default="flash", description="Уровень модели")
    tokens_used: int = Field(default=0, ge=0, description="Использовано токенов")
    error: Optional[str] = Field(default=None, description="Ошибка, если была")


# ---------------------------------------------------------------------------
# Agent Chat
# ---------------------------------------------------------------------------


@router.post("/chat", response_model=ChatResponse)
async def agent_chat(
    request: ChatRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Обработка запроса к AI-агенту через LangGraph-оркестратор.

    Оркестратор:
    1. Маршрутизирует запрос к нужному агенту (или авто-определение)
    2. Оценивает, нужно ли утверждение человека (HITL)
    3. Генерирует ответ через LLM (демо-режим / real LLM)
    4. Логирует в AuditLog
    """
    # Нормализация agent_type для совместимости со старыми клиентами
    agent_type = request.agent_type
    if agent_type == "litigation" or agent_type == "legal_opinion":
        # Передаём пустую строку для авто-определения оркестратором,
        # либо отображаем в правильный тип
        if agent_type == "legal_opinion":
            agent_type = "general_dept"

    try:
        result = await orchestrator.process_request(
            request=request.message,
            user_id=current_user.id,
            tenant_id=current_user.tenant_id,
            case_id=request.case_id,
            agent_type=agent_type if agent_type else None,
            db_session=db,
            estimated_complexity=request.estimated_complexity,
        )

        # Логирование вызова в AuditLog
        try:
            audit = AuditLog(
                user_id=current_user.id,
                user_name=getattr(current_user, "username", None),
                tenant_id=current_user.tenant_id,
                role=getattr(current_user, "role", None),
                action="agent_chat",
                entity_type="agent",
                entity_id=str(request.case_id) if request.case_id else None,
                details=(
                    f"agent_type={result['agent_type']}, "
                    f"tokens={result['tokens_used']}, "
                    f"model={result['model_used']}, "
                    f"hitl={result['requires_human_approval']}"
                ),
            )
            db.add(audit)
            db.commit()
        except Exception as exc:
            logger.warning("Agent chat: ошибка записи AuditLog: %s", exc)

        return ChatResponse(
            response=result["response"],
            agent_type=result["agent_type"],
            requires_human_approval=result["requires_human_approval"],
            approved=result["approved"],
            model_used=result["model_used"],
            model_tier=result["model_tier"],
            tokens_used=result["tokens_used"],
            error=result.get("error"),
        )

    except Exception as exc:
        logger.exception("Agent chat: необработанная ошибка")
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка сервера при обработке запроса агента: {exc}",
        )
