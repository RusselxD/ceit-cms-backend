from sqlalchemy import Column, DateTime, String, Text, Integer, UUID, func
from .base import Base
import uuid


class Newsletter(Base):
    __tablename__ = "newsletters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(255), nullable=False)
    volume = Column(String(50), nullable=False)
    issue = Column(String(50), nullable=False)
    month_year = Column(String(50), nullable=False)
    summary = Column(Text, nullable=True)
    highlights = Column(Text, nullable=True)
    tags = Column(String(500), nullable=True)
    pages = Column(Integer, nullable=False, default=0)
    cover_url = Column(String(500), nullable=True)
    pdf_url = Column(String(500), nullable=True)
    flipbook_url = Column(String(500), nullable=True)
    is_latest = Column(Integer, nullable=False, default=0, server_default="0")
    created_at = Column(DateTime(timezone=True), server_default=func.timezone('UTC', func.now()), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.timezone('UTC', func.now()), onupdate=func.timezone('UTC', func.now()), nullable=False)
