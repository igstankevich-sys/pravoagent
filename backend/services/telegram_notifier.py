"""
Telegram Notifier — уведомления о статусах дел.
Часть Part 12.11 плана.
"""
from typing import Optional
from backend.services.telegram_bot import TelegramBot


class TelegramNotifier:
    """Отправка уведомлений в Telegram."""

    def __init__(self):
        self.bot = TelegramBot()

    async def notify_case_update(self, chat_id: str, case_title: str, update: str) -> dict:
        """Уведомление об изменении по делу."""
        message = f"🔔 Обновление по делу: {update}"
        return await self.bot.send_notification(chat_id, case_title, message)

    async def notify_deadline(self, chat_id: str, case_title: str, days_left: int) -> dict:
        """Уведомление об истекающем сроке."""
        message = f"⏰ Истекает срок через {days_left} дн."
        return await self.bot.send_notification(chat_id, case_title, message)

    async def notify_approval(self, chat_id: str, doc_title: str) -> dict:
        """Запрос утверждения документа."""
        message = f"✅ Требуется утверждение: {doc_title}"
        return await self.bot.send_notification(chat_id, doc_title, message)
