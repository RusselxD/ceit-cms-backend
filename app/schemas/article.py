from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.models.article import ArticleStatus, ArticleCategory


class ArticleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    body: str = Field(..., min_length=1)
    category: ArticleCategory = ArticleCategory.ANNOUNCEMENTS
    image_path: Optional[str] = Field(None, max_length=255)
    image_alt_text: Optional[str] = Field(None, max_length=255)


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    body: Optional[str] = Field(None, min_length=1)
    category: Optional[ArticleCategory] = None
    image_path: Optional[str] = Field(None, max_length=255)
    image_alt_text: Optional[str] = Field(None, max_length=255)
    status: Optional[ArticleStatus] = None


class ArticleResponse(ArticleBase):
    id: UUID
    author_id: UUID
    category: ArticleCategory
    like_count: int = 0
    status: ArticleStatus
    created_at: datetime
    updated_at: datetime
    approved_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ArticleWithAuthor(ArticleResponse):
    author_first_name: str
    author_last_name: str
    author_email: str

    class Config:
        from_attributes = True
