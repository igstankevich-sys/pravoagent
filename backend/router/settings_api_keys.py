"""
Router для настроек API-ключей.
"""
from fastapi import APIRouter, Depends
from backend.services.settings_api_keys import APIKeySettings
from backend.services.auth_service import require_role
from backend.models.base import User

router = APIRouter(prefix="/api/settings", tags=["settings"])
api_key_settings = APIKeySettings()


@router.get("/api-keys")
def get_api_keys(current_user: User = Depends(require_role("admin", "head_legal"))):
    return api_key_settings.get_status()
