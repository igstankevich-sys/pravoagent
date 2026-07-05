import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from backend.database import Base


class TelegramConnection(Base):
    """Привязка Telegram-чата к пользователю ПравоАгент."""

    __tablename__ = "telegram_connections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chat_id = Column(String, nullable=False)
    username = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )
