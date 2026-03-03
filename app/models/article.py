from sqlalchemy import Column, DateTime, Enum, String, ForeignKey, Text, UUID, func, Integer
from sqlalchemy.orm import relationship
from .base import Base
import enum
import uuid


class ArticleStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    ARCHIVED = "archived"


class ArticleCategory(str, enum.Enum):
    ANNOUNCEMENTS = "announcements"
    ACHIEVEMENTS = "achievements"
    EVENTS = "events"
    PARTNERSHIPS = "partnerships"


class Article(Base):
    __tablename__ = "articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    author_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    image_path = Column(String(255), nullable=True)
    image_alt_text = Column(String(255), nullable=True)
    category = Column(Enum(ArticleCategory), nullable=False, default=ArticleCategory.ANNOUNCEMENTS)
    like_count = Column(Integer, nullable=False, default=0, server_default="0")
    status = Column(Enum(ArticleStatus), nullable=False, default=ArticleStatus.DRAFT)
    created_at = Column(DateTime(timezone=True), server_default=func.timezone('UTC', func.now()), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.timezone('UTC', func.now()), onupdate=func.timezone('UTC', func.now()), nullable=False)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    author = relationship("User", back_populates="articles")
