import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="lawyer")  # litigation | contracts | general | head_legal | admin | legal_opinions
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    telegram_chat_id = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    tenant = relationship("Tenant", back_populates="users")
    cases = relationship("Case", back_populates="user")


class EmailVerification(Base):
    """Подтверждение email пользователя."""
    __tablename__ = "email_verifications"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    code = Column(String, nullable=False)  # 6-значный код
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)  # +15 минут от created_at


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    monthly_token_limit = Column(Integer, default=10_000_000)
    tokens_used_this_month = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    users = relationship("User", back_populates="tenant")


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, default="")
    status = Column(String, default="open")  # open | in_progress | closed
    case_type = Column(String, default="litigation")  # litigation | contracts | general
    court = Column(String, nullable=True)
    judge = Column(String, nullable=True)
    plaintiff = Column(String, nullable=True)
    defendant = Column(String, nullable=True)
    case_number = Column(String, nullable=True)
    priority = Column(String, default="normal")  # low | normal | high | urgent
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="cases")
    documents = relationship("Document", back_populates="case")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, default="")
    doc_type = Column(String, default="other")  # claim | complaint | contract | opinion | other
    status = Column(String, default="draft")  # draft | review | approved | rejected
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    case = relationship("Case", back_populates="documents")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, nullable=True)
    user_name = Column(String, nullable=True)
    tenant_id = Column(Integer, nullable=True)
    role = Column(String, nullable=True)
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=True)
    entity_id = Column(String, nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)
    session_id = Column(String, nullable=True)


class LegalRequest(Base):
    """Заявки/поручения для юристов."""
    __tablename__ = "legal_requests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, default="")
    status = Column(String, default="open")  # open | in_progress | completed | cancelled
    request_type = Column(String, default="other")  # document | advice | approval | registration | other
    priority = Column(String, default="normal")  # low | normal | high | urgent
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User")


class KpiEntry(Base):
    """История KPI по тенантам (временные ряды)."""
    __tablename__ = "kpi_entries"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    date = Column(DateTime, nullable=False)
    metric_name = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    tenant = relationship("Tenant")


class LegalOpinion(Base):
    """Юридические заключения."""
    __tablename__ = "legal_opinions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    question = Column(Text, nullable=False)
    short_answer = Column(Text, default="")
    full_answer = Column(Text, default="")
    opinion_type = Column(String, default="other")  # tax | contract | corporate | litigation | regulatory | other
    status = Column(String, default="draft")  # draft | review | approved | archived
    tags = Column(String, nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    author = relationship("User")
    case = relationship("Case")


class KpiMetricConfig(Base):
    """Конфигурация метрик KPI для тенанта.

    Хранит настройки отображения, целевые значения и кастомные метрики.
    Часть Configuration Agent (Phase 10).
    """
    __tablename__ = "kpi_metric_configs"
    __table_args__ = (
        UniqueConstraint("tenant_id", "metric_key", name="uq_tenant_metric_key"),
    )

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    metric_key = Column(String, nullable=False)
    metric_label = Column(String, nullable=False)
    metric_description = Column(String, default="")
    target_value = Column(Float, nullable=True)
    comparison = Column(String, default="gte")  # gte (>=), lte (<=), eq (=)
    is_custom = Column(Boolean, default=False)
    formula = Column(Text, nullable=True)
    is_enabled = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    tenant = relationship("Tenant")


class DocumentACL(Base):
    """ACL для расшаренных документов."""
    __tablename__ = "document_acls"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    access_level = Column(String, default="read")  # read | edit | comment
    expires_at = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
