"""
Router для интеграций: КАД, Telegram, Почта России.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend.services.kad_mock import KADMock
from backend.services.russian_post_mock import RussianPostMock
from backend.services.telegram_bot import TelegramBot
from backend.services.auth_service import get_current_user
from backend.models.base import User


class ShipmentRequest(BaseModel):
    recipient: str
    address: str
    documents: List[str] = []


router = APIRouter(prefix="/api/integrations", tags=["integrations"])
kad = KADMock()
post = RussianPostMock()
telegram = TelegramBot()


@router.get("/kad/search")
def kad_search(query: str, current_user: User = Depends(get_current_user)):
    return {"results": kad.search_cases(query), "mode": "demo"}


@router.get("/kad/case/{case_number}")
async def kad_case(
    case_number: str,
    current_user: User = Depends(get_current_user),
):
    result = kad.get_case(case_number)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/kad/submit")
def kad_submit(
    case_number: str, document_text: str, current_user: User = Depends(get_current_user)
):
    return kad.submit_document(case_number, document_text)


@router.post("/post/shipment")
async def post_shipment(
    req: ShipmentRequest,
    current_user: User = Depends(get_current_user),
):
    return post.create_shipment(req.recipient, req.address, req.documents)


@router.get("/post/status/{tracking}")
def post_status(tracking: str, current_user: User = Depends(get_current_user)):
    return post.get_status(tracking)


@router.post("/telegram/send")
async def telegram_send(
    chat_id: str, text: str, current_user: User = Depends(get_current_user)
):
    return await telegram.send_message(chat_id, text)
