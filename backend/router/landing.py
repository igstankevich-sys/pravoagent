"""
Роутер лэндинга ПравоАгент.
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

from backend.config import settings

router = APIRouter(tags=["landing"])
templates_dir = Path(__file__).parent.parent.parent / "templates"

env = Environment(
    loader=FileSystemLoader(str(templates_dir)),
    autoescape=select_autoescape(["html", "xml"]),
    cache_size=0,
)


@router.get("/landing", response_class=HTMLResponse)
def landing_page(request: Request):
    template = env.get_template("landing.html")
    return HTMLResponse(
        template.render(
            request=request,
            app_name=settings.app_name,
            app_version=settings.app_version,
        )
    )


@router.get("/onboarding", response_class=HTMLResponse)
def onboarding_page(request: Request):
    template = env.get_template("onboarding.html")
    return HTMLResponse(template.render(request=request))
