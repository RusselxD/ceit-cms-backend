from fastapi import APIRouter, Depends
from app.core.database import get_db
from app.services import auth_service
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import Token, RefreshTokenRequest
from app.api.v1.dependencies import get_current_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(email: str, password: str, db: AsyncSession = Depends(get_db)) -> Token:
    return await auth_service.authenticate_user(db=db, email=email, password=password)


@router.post("/refresh", response_model=Token)
async def refresh_token(payload: RefreshTokenRequest, db: AsyncSession = Depends(get_db)) -> Token:
    return await auth_service.refresh_access_token(db=db, refresh_token=payload.refresh_token)


@router.post("/logout")
async def logout(
    payload: RefreshTokenRequest | None = None,
    access_token: str = Depends(get_current_token)
):
    refresh_token = payload.refresh_token if payload else None
    auth_service.logout(access_token=access_token, refresh_token=refresh_token)
    return {"message": "Logged out successfully"}