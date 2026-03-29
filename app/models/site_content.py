from sqlalchemy import Column, DateTime, String, UUID, func
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base
import uuid


class SiteContent(Base):
    __tablename__ = "site_content"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    page = Column(String(100), nullable=False, unique=True, index=True)
    content = Column(JSONB, nullable=False, default=dict)
    updated_at = Column(DateTime(timezone=True), server_default=func.timezone('UTC', func.now()), onupdate=func.timezone('UTC', func.now()), nullable=False)
