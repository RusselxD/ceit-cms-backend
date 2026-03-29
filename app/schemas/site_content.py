from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Any


class SiteContentResponse(BaseModel):
    id: UUID
    page: str
    content: dict[str, Any]
    updated_at: datetime

    class Config:
        from_attributes = True


class SiteContentUpdate(BaseModel):
    content: dict[str, Any] = Field(...)
