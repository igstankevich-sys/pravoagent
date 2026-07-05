"""
Роутер ролевых workspace для ПравоАгент.
Каждый workspace — отдельная страница с кастомным набором панелей.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from pathlib import Path
import datetime

from backend.database import get_db
from backend.models.base import User, Case, Document, AuditLog, Tenant
from backend.services.auth_service import get_current_user, require_role
from backend.services.workspace_service import get_workspace_config, get_default_workspace, WORKSPACE_CONFIG
from backend.config import settings
from jinja2 import Environment, FileSystemLoader, select_autoescape

router = APIRouter(prefix="/app", tags=["workspace"])

templates_dir = Path(__file__).parent.parent.parent / "templates"
env = Environment(
    loader=FileSystemLoader(str(templates_dir)),
    autoescape=select_autoescape(["html", "xml"]),
    cache_size=0,
)


def render_workspace(name: str, **context):
    """Render a workspace template with common context."""
    ctx = {
        "demo_mode": settings.demo_mode,
        "app_name": settings.app_name,
        "app_version": settings.app_version,
    }
    ctx.update(context)
    template = env.get_template(name)
    return HTMLResponse(template.render(**ctx))


@router.get("/")
def workspace_redirect(
    current_user: User = Depends(get_current_user),
):
    """Редирект на workspace в зависимости от роли пользователя."""
    workspace_id = get_default_workspace(current_user.role)
    return RedirectResponse(url=f"/app/{workspace_id}")


# --- Litigation workspace ---

@router.get("/litigation")
def litigation_workspace(
    current_user: User = Depends(require_role("litigation", "head_legal", "admin")),
    db: Session = Depends(get_db),
):
    """Workspace судебного юриста."""
    cases = (
        db.query(Case)
        .filter(Case.tenant_id == current_user.tenant_id)
        .all()
    )
    documents = (
        db.query(Document)
        .filter(Document.tenant_id == current_user.tenant_id)
        .count()
    )
    config = get_workspace_config("litigation")

    return render_workspace(
        "workspaces/litigation.html",
        request={},
        user=current_user,
        workspace_id="litigation",
        workspace_config=config,
        cases=cases,
        documents_count=documents,
        demo_mode=True,
        now=datetime.datetime.utcnow(),
    )


# --- Contracts workspace ---

@router.get("/contracts")
def contracts_workspace(
    current_user: User = Depends(require_role("contracts", "head_legal", "admin")),
    db: Session = Depends(get_db),
):
    """Workspace договорника."""
    cases = (
        db.query(Case)
        .filter(
            Case.tenant_id == current_user.tenant_id,
            Case.case_type == "contracts",
        )
        .all()
    )
    documents = (
        db.query(Document)
        .filter(Document.tenant_id == current_user.tenant_id)
        .count()
    )
    config = get_workspace_config("contracts")

    return render_workspace(
        "workspaces/contracts.html",
        request={},
        user=current_user,
        workspace_id="contracts",
        workspace_config=config,
        cases=cases,
        documents_count=documents,
        demo_mode=True,
        now=datetime.datetime.utcnow(),
    )


# --- General workspace ---

@router.get("/general")
def general_workspace(
    current_user: User = Depends(require_role("general", "head_legal", "admin")),
    db: Session = Depends(get_db),
):
    """Workspace общего отдела."""
    documents = (
        db.query(Document)
        .filter(Document.tenant_id == current_user.tenant_id)
        .all()
    )
    config = get_workspace_config("general")

    return render_workspace(
        "workspaces/general.html",
        request={},
        user=current_user,
        workspace_id="general",
        workspace_config=config,
        documents=documents,
        demo_mode=True,
        now=datetime.datetime.utcnow(),
    )


# --- Head of Legal workspace ---

@router.get("/head-legal")
def head_legal_workspace(
    current_user: User = Depends(require_role("head_legal", "admin")),
    db: Session = Depends(get_db),
):
    """Workspace Head of Legal (дашборд)."""
    tenant_id = current_user.tenant_id

    total_cases = db.query(Case).filter(Case.tenant_id == tenant_id).count()
    open_cases = db.query(Case).filter(Case.tenant_id == tenant_id, Case.status == "open").count()
    closed_cases = db.query(Case).filter(Case.tenant_id == tenant_id, Case.status == "closed").count()
    in_progress_cases = db.query(Case).filter(Case.tenant_id == tenant_id, Case.status == "in_progress").count()

    total_documents = db.query(Document).filter(Document.tenant_id == tenant_id).count()
    total_users = db.query(User).filter(User.tenant_id == tenant_id).count()

    team_members = (
        db.query(User)
        .filter(User.tenant_id == tenant_id, User.is_active == True)
        .all()
    )

    # Efficiency rate
    efficiency = 0
    if total_cases > 0:
        efficiency = round((closed_cases / total_cases) * 100)

    # Average case duration (mock)
    avg_duration_days = 45

    config = get_workspace_config("head_legal")

    return render_workspace(
        "workspaces/head_legal.html",
        request={},
        user=current_user,
        workspace_id="head_legal",
        workspace_config=config,
        total_cases=total_cases,
        open_cases=open_cases,
        closed_cases=closed_cases,
        in_progress_cases=in_progress_cases,
        total_documents=total_documents,
        total_users=total_users,
        team_members=team_members,
        efficiency=efficiency,
        avg_duration_days=avg_duration_days,
        demo_mode=True,
        now=datetime.datetime.utcnow(),
    )


# --- Admin workspace ---

@router.get("/admin")
def admin_workspace(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Админ-панель."""
    users = db.query(User).all()
    tenants = db.query(Tenant).all()
    audit_logs = (
        db.query(AuditLog)
        .order_by(AuditLog.timestamp.desc())
        .limit(50)
        .all()
    )

    config = get_workspace_config("admin")

    return render_workspace(
        "workspaces/admin.html",
        request={},
        user=current_user,
        workspace_id="admin",
        workspace_config=config,
        users=users,
        tenants=tenants,
        audit_logs=audit_logs,
        demo_mode=True,
        now=datetime.datetime.utcnow(),
    )


# --- Legal Opinions workspace ---

@router.get("/legal-opinions")
def legal_opinions_workspace(
    current_user: User = Depends(require_role("admin", "head_legal", "general")),
    db: Session = Depends(get_db),
):
    """Workspace юридических заключений."""
    opinions = (
        db.query(Document)
        .filter(
            Document.tenant_id == current_user.tenant_id,
            Document.doc_type == "opinion",
        )
        .all()
    )
    config = get_workspace_config("legal_opinions")

    return render_workspace(
        "workspaces/legal_opinions.html",
        request={},
        user=current_user,
        workspace_id="legal_opinions",
        workspace_config=config,
        opinions=opinions,
        demo_mode=True,
        now=datetime.datetime.utcnow(),
    )
