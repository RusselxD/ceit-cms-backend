from typing import Optional
from .base import CRUDBase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Role
from sqlalchemy.orm import selectinload
from uuid import UUID

class CRUDUser(CRUDBase[User, None, None]):

    async def get_by_id(self, db: AsyncSession, user_id: UUID) -> Optional[User]:
        result = await db.execute(
            select(self.model).filter(User.id == user_id)
            .options(
                selectinload(User.role).selectinload(Role.permissions)
            )
            .execution_options(populate_existing=False)
        )
        return result.scalars().first()

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(
            select(self.model).filter(User.email == email)
            .options(
                selectinload(User.role).selectinload(Role.permissions) # eager load
            )
            .execution_options(populate_existing=False) # disable tracking
        )
        return result.scalars().first()


user_crud = CRUDUser(User)
user_repo = user_crud