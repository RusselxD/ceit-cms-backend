from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class NewsletterBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    volume: str = Field(..., min_length=1, max_length=50)
    issue: str = Field(..., min_length=1, max_length=50)
    month_year: str = Field(..., min_length=1, max_length=50)
    summary: Optional[str] = None
    highlights: Optional[str] = None
    tags: Optional[str] = Field(None, max_length=500)
    pages: int = 0
    cover_url: Optional[str] = Field(None, max_length=500)
    pdf_url: Optional[str] = Field(None, max_length=500)
    flipbook_url: Optional[str] = Field(None, max_length=500)
    is_latest: int = 0


class NewsletterCreate(NewsletterBase):
    pass


class NewsletterUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    volume: Optional[str] = Field(None, min_length=1, max_length=50)
    issue: Optional[str] = Field(None, min_length=1, max_length=50)
    month_year: Optional[str] = Field(None, min_length=1, max_length=50)
    summary: Optional[str] = None
    highlights: Optional[str] = None
    tags: Optional[str] = Field(None, max_length=500)
    pages: Optional[int] = None
    cover_url: Optional[str] = Field(None, max_length=500)
    pdf_url: Optional[str] = Field(None, max_length=500)
    flipbook_url: Optional[str] = Field(None, max_length=500)
    is_latest: Optional[int] = None


class NewsletterResponse(NewsletterBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
