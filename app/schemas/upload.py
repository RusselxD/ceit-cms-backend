from __future__ import annotations

from pydantic import BaseModel


class UploadResponse(BaseModel):
    public_id: str
    secure_url: str
    url: str
    resource_type: str
    format: str | None = None
    bytes: int | None = None
    width: int | None = None
    height: int | None = None
    original_filename: str | None = None
