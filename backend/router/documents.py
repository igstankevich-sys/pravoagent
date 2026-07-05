from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from backend.database import get_db
from backend.models.base import Document
from backend.services.auth_service import get_current_user
from backend.services.document_service import DocumentService
from backend.services.export_service import DocumentExporter
from backend.services.sharing_service import SharingService
from backend.models.base import User

router = APIRouter(prefix="/api/documents", tags=["documents"])

# --- Service instances ---
document_service = DocumentService()
export_service = DocumentExporter()
sharing_service = SharingService()


# --- Pydantic schemas ---

class CreateFromTemplateRequest(BaseModel):
    template_name: str
    case_id: int
    context: dict


class ShareRequest(BaseModel):
    target_user_id: int
    access_level: str = "read"
    expires_in_days: Optional[int] = 30


# --- Existing endpoints ---

@router.get("")
def list_documents(
    skip: int = 0,
    limit: int = 20,
    case_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Document).filter(Document.tenant_id == current_user.tenant_id)
    if case_id:
        query = query.filter(Document.case_id == case_id)
    total = query.count()
    docs = query.order_by(Document.updated_at.desc()).offset(skip).limit(limit).all()
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [
            {
                "id": d.id,
                "title": d.title,
                "doc_type": d.doc_type,
                "status": d.status,
                "case_id": d.case_id,
                "created_at": d.created_at.isoformat() if d.created_at else None,
                "updated_at": d.updated_at.isoformat() if d.updated_at else None,
            }
            for d in docs
        ],
    }


@router.get("/{doc_id}")
def get_document(doc_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == doc_id, Document.tenant_id == current_user.tenant_id).first()
    if not doc:
        return {"error": "Document not found"}
    return {
        "id": doc.id,
        "title": doc.title,
        "content": doc.content,
        "doc_type": doc.doc_type,
        "status": doc.status,
        "case_id": doc.case_id,
        "author_id": doc.author_id,
        "created_at": doc.created_at.isoformat() if doc.created_at else None,
        "updated_at": doc.updated_at.isoformat() if doc.updated_at else None,
    }


# --- New Phase 5 endpoints ---

@router.post("/from-template")
def create_from_template(
    req: CreateFromTemplateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Создать документ из шаблона."""
    try:
        doc = document_service.create_from_template(
            db=db,
            template_name=req.template_name,
            context=req.context,
            case_id=req.case_id,
            author_id=current_user.id,
            tenant_id=current_user.tenant_id,
        )
        return {
            "id": doc.id,
            "title": doc.title,
            "doc_type": doc.doc_type,
            "status": doc.status,
            "case_id": doc.case_id,
            "content": doc.content,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{doc_id}/export")
def export_document(
    doc_id: int,
    format: str = Query("docx", pattern="^(docx|pdf|txt|md)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Экспорт документа в указанный формат."""
    doc = db.query(Document).filter(Document.id == doc_id, Document.tenant_id == current_user.tenant_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")

    try:
        result = export_service.export(
            doc_id=doc.id,
            content=doc.content,
            title=doc.title,
            format=format,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{doc_id}/share")
def share_document(
    doc_id: int,
    req: ShareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Расшарить документ коллеге."""
    doc = db.query(Document).filter(Document.id == doc_id, Document.tenant_id == current_user.tenant_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")

    try:
        result = sharing_service.share_document(
            db=db,
            doc_id=doc_id,
            owner_id=current_user.id,
            target_user_id=req.target_user_id,
            access_level=req.access_level,
            expires_in_days=req.expires_in_days,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{doc_id}/graph")
def get_document_graph(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Граф связей документов для дела, к которому относится документ."""
    doc = db.query(Document).filter(Document.id == doc_id, Document.tenant_id == current_user.tenant_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")
    if not doc.case_id:
        return {
            "case_id": None,
            "documents": [],
            "links": [],
            "message": "Документ не привязан к делу",
        }
    return document_service.get_document_graph(db=db, case_id=doc.case_id)
