from pydantic import BaseModel
from uuid import UUID


class TokenData(BaseModel):
    sub: UUID
    first_name: str
    last_name: str
    role_name: str
    permissions: list[str]


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str | None = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str