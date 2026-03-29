from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services import user_service
from app.schemas.user import (
    UserResponse,
    UserCreate,
    UserUpdate,
    ChangePasswordRequest,
    ResetPasswordRequest,
)
from app.api.v1.dependencies import require_auth, require_role, CurrentUser

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("super_admin")),
) -> list[UserResponse]:
    return await user_service.get_all_users(db)


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("super_admin")),
) -> UserResponse:
    return await user_service.create_user(db, payload)


@router.put("/me/password")
async def change_own_password(
    payload: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_auth),
):
    await user_service.change_password(
        db, current_user.user_id, payload.current_password, payload.new_password
    )
    return {"message": "Password changed successfully"}


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("super_admin")),
) -> UserResponse:
    return await user_service.update_user(db, user_id, payload, current_user.user_id)


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("super_admin")),
):
    await user_service.delete_user(db, user_id, current_user.user_id)


@router.put("/{user_id}/reset-password")
async def reset_password(
    user_id: UUID,
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("super_admin")),
):
    await user_service.reset_password(db, user_id, payload.new_password)
    return {"message": "Password reset successfully"}
