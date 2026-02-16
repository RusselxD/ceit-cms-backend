from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.core.security import verify_password, create_access_token
from datetime import timedelta
from app.core.config import settings
from app.models import User
from app.schemas import Token, TokenData
from app.repositories import user_repo

class AuthService:
    
    async def authenticate_user(self, db: AsyncSession, email: str, password: str) -> Token:
        
        user_in_db = await user_repo.get_by_email(db=db, email=email)
        
        if not user_in_db or not verify_password(plain_password=password, hashed_password=user_in_db.hashed_password):
            raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid credentials",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
        
        access_token = await self._create_token(user_in_db)
        return Token(access_token=access_token, token_type="bearer")


    async def _create_token(self, user: User) -> str:
        claims = TokenData(
            sub=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            role_name=user.role.name,
            permissions=[perm.name for perm in user.role.permissions]
        )

        access_token_expires = timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
        return create_access_token(data=claims, expires_delta=access_token_expires)


auth_service = AuthService()