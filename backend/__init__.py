from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from pathlib import Path
import datetime
import platform

from backend.config import settings
from backend.database import SessionLocal
from jinja2 import Environment, FileSystemLoader, select_autoescape

router = APIRouter(tags=["ui"])
templates_dir = Path(__file__).parent.parent.parent / "templates"

env = Environment(
    loader=FileSystemLoader(str(templates_dir)),
    autoescape=select_autoescape(["html", "xml"]),
    cache_size=0,  # Disable cache to avoid compatibility issues
)


def render_template(name: str, **context):
    template = env.get_template(name)
    return HTMLResponse(template.render(**context))


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return render_template(
        "index.html",
        request=request,
        demo_mode=settings.demo_mode,
        app_name=settings.app_name,
        app_version=settings.app_version,
    )


@router.get("/health")
async def health():
    db_ok = False
    try:
        db = SessionLocal()
        db.execute(db.bind.text("SELECT 1"))
        db.close()
        db_ok = True
    except Exception:
        db_ok = False

    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "demo_mode": settings.demo_mode,
        "database": "connected" if db_ok else "error",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "python": platform.python_version(),
    }
