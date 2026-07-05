from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.base import Case, Document

router = APIRouter(prefix="/api/cases", tags=["cases"])


@router.get("")
def list_cases(
    skip: int = 0,
    limit: int = 20,
    status: str = None,
    db: Session = Depends(get_db),
):
    query = db.query(Case)
    if status:
        query = query.filter(Case.status == status)
    total = query.count()
    cases = query.order_by(Case.updated_at.desc()).offset(skip).limit(limit).all()
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [
            {
                "id": c.id,
                "title": c.title,
                "description": c.description,
                "status": c.status,
                "case_type": c.case_type,
                "case_number": c.case_number,
                "priority": c.priority,
                "court": c.court,
                "plaintiff": c.plaintiff,
                "defendant": c.defendant,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "updated_at": c.updated_at.isoformat() if c.updated_at else None,
            }
            for c in cases
        ],
    }


@router.get("/{case_id}")
def get_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    documents = db.query(Document).filter(Document.case_id == case_id).all()
    return {
        "id": case.id,
        "title": case.title,
        "description": case.description,
        "status": case.status,
        "case_type": case.case_type,
        "case_number": case.case_number,
        "priority": case.priority,
        "court": case.court,
        "judge": case.judge,
        "plaintiff": case.plaintiff,
        "defendant": case.defendant,
        "user_id": case.user_id,
        "tenant_id": case.tenant_id,
        "created_at": case.created_at.isoformat() if case.created_at else None,
        "updated_at": case.updated_at.isoformat() if case.updated_at else None,
        "documents": [
            {
                "id": d.id,
                "title": d.title,
                "doc_type": d.doc_type,
                "status": d.status,
                "created_at": d.created_at.isoformat() if d.created_at else None,
            }
            for d in documents
        ],
    }
