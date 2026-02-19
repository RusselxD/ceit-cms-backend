from .base import CRUDBase
from sqlalchemy import select
from app.models import User, Role
from sqlalchemy.orm import selectinload
from uuid import UUID

class CRUDUser(CRUDBase[User, None, None]):

    async def get_by_email(self, db, email: str) -> User:
        result = await db.execute(
            select(self.model).filter(User.email == email)
            .options(
                selectinload(User.role).selectinload(Role.permissions) # eager load
            )
            .execution_options(populate_existing=False) # disable tracking
        )
        return result.scalars().first()

    async def get_by_id(self, db, user_id: UUID) -> User:
        result = await db.execute(
            select(self.model).filter(User.id == user_id)
            .options(
                selectinload(User.role).selectinload(Role.permissions)
            )
            .execution_options(populate_existing=False)
        )
        return result.scalars().first()


user_crud = CRUDUser(User)