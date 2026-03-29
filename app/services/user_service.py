from uuid import UUID
from typing import List

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import get_password_hash, verify_password
from app.models import User, Role
from app.schemas.user import UserCreate, UserUpdate, UserResponse


async def _get_role_by_name(db: AsyncSession, role_name: str) -> Role:
    result = await db.execute(
        select(Role).filter(Role.name == role_name)
    )
    role = result.scalars().first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role '{role_name}' not found",
        )
    return role


def _user_to_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role_name=user.role.name if user.role else "",
        created_at=user.created_at,
    )


async def get_all_users(db: AsyncSession) -> List[UserResponse]:
    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .execution_options(populate_existing=False)
    )
    users = result.scalars().unique().all()
    return [_user_to_response(u) for u in users]


async def get_user(db: AsyncSession, user_id: UUID) -> UserResponse:
    user = await _get_user_or_404(db, user_id)
    return _user_to_response(user)


async def create_user(db: AsyncSession, data: UserCreate) -> UserResponse:
    # Check for duplicate email
    existing = await db.execute(
        select(User).filter(User.email == data.email)
    )
    if existing.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )

    role = await _get_role_by_name(db, data.role_name)

    user = User(
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name,
        hashed_password=get_password_hash(data.password),
        role_id=role.id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user, attribute_names=["role"])
    return _user_to_response(user)


async def update_user(db: AsyncSession, user_id: UUID, data: UserUpdate, current_user_id: UUID) -> UserResponse:
    user = await _get_user_or_404(db, user_id)

    update_data = data.model_dump(exclude_unset=True)

    # Prevent changing your own role
    if "role_name" in update_data and user_id == current_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot change your own role",
        )

    # Check for duplicate email when email is being changed
    if "email" in update_data and update_data["email"] != user.email:
        existing = await db.execute(
            select(User).filter(User.email == update_data["email"])
        )
        if existing.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists",
            )

    if "role_name" in update_data:
        role = await _get_role_by_name(db, update_data.pop("role_name"))
        user.role_id = role.id

    for field, value in update_data.items():
        setattr(user, field, value)

    db.add(user)
    await db.commit()
    await db.refresh(user, attribute_names=["role"])
    return _user_to_response(user)


async def delete_user(db: AsyncSession, user_id: UUID, current_user_id: UUID) -> None:
    # Prevent deleting yourself
    if user_id == current_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account",
        )

    user = await _get_user_or_404(db, user_id)

    # Prevent deleting the last super_admin
    if user.role and user.role.name == "super_admin":
        result = await db.execute(
            select(func.count(User.id))
            .join(Role, User.role_id == Role.id)
            .filter(Role.name == "super_admin")
        )
        super_admin_count = result.scalar()
        if super_admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the last super_admin",
            )

    await db.delete(user)
    await db.commit()


async def change_password(
    db: AsyncSession, user_id: UUID, current_password: str, new_password: str
) -> None:
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters long",
        )
    user = await _get_user_or_404(db, user_id)
    if not verify_password(current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    user.hashed_password = get_password_hash(new_password)
    db.add(user)
    await db.commit()


async def reset_password(db: AsyncSession, user_id: UUID, new_password: str) -> None:
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters long",
        )
    user = await _get_user_or_404(db, user_id)
    user.hashed_password = get_password_hash(new_password)
    db.add(user)
    await db.commit()


async def _get_user_or_404(db: AsyncSession, user_id: UUID) -> User:
    result = await db.execute(
        select(User)
        .filter(User.id == user_id)
        .options(selectinload(User.role))
        .execution_options(populate_existing=False)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
