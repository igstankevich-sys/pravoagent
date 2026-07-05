"""
ПравоАгент — Multi-Agent AI Platform для юридических департаментов.
Точка входа FastAPI.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from backend.config import settings
from backend.database import init_db
from backend.router import router as main_router
from backend.router.cases import router as cases_router
from backend.router.documents import router as documents_router
from backend.router.agent import router as agent_router
from backend.router.auth import router as auth_router
from backend.router.workspace import router as workspace_router
from backend.router.knowledge_base import router as kb_router
from backend.router.integrations import router as integrations_router
from backend.router.settings_api_keys import router as settings_api_keys_router
from backend.router.observability import router as observability_router
from backend.router.kpi import router as kpi_router
from backend.router.admin import router as admin_api_router
from backend.router.landing import router as landing_router
from backend.router.telegram_webhook import router as telegram_webhook_router
from backend.router.configuration_agent import router as config_agent_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.export_dir, exist_ok=True)
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

# Static files
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Routers
app.include_router(main_router)
app.include_router(cases_router)
app.include_router(documents_router)
app.include_router(agent_router)
app.include_router(auth_router)
app.include_router(workspace_router)
app.include_router(kb_router)
app.include_router(integrations_router)
app.include_router(settings_api_keys_router)
app.include_router(observability_router)
app.include_router(kpi_router)
app.include_router(admin_api_router)
app.include_router(landing_router)
app.include_router(telegram_webhook_router)
app.include_router(config_agent_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
