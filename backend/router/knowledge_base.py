"""
Router для работы с базой знаний.
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional

from backend.rag.kb_selector import KnowledgeBaseSelector
from backend.services.auth_service import get_current_user
from backend.models.base import User

router = APIRouter(prefix="/api/knowledge-base", tags=["knowledge_base"])
kb_selector = KnowledgeBaseSelector()


@router.get("/search")
async def search_knowledge_base(
    query: str = Query(..., description="Поисковый запрос"),
    sources: str = Query("own", description="Источники через запятую"),
    top_k: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
):
    """Поиск по базе знаний."""
    sources_list = [s.strip() for s in sources.split(",")]
    return await kb_selector.search(
        query=query, sources=sources_list, top_k=top_k
    )


@router.get("/sources")
async def list_sources(current_user: User = Depends(get_current_user)):
    """Список доступных источников."""
    return {
        "sources": [
            {
                "id": k,
                "name": v["name"],
                "type": v["type"],
                "real": v["real"],
            }
            for k, v in KnowledgeBaseSelector.SOURCES.items()
        ]
    }
