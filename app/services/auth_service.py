from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.core.security import verify_password, create_access_token
from datetime import timedelta, datetime, timezone
from app.core.config import settings
from app.models import User
from app.schemas import Token, TokenData
from app.repositories import user_repo
from jose import jwt, JWTError
from uuid import UUID

class AuthService:

    def __init__(self):
        self.revoked_access_tokens: set[str] = set()
        self.revoked_refresh_tokens: set[str] = set()
        self.valid_refresh_tokens: dict[str, str] = {}
    
    async def authenticate_user(self, db: AsyncSession, email: str, password: str) -> Token:
        
        user_in_db = await user_repo.get_by_email(db=db, email=email)
        
        if not user_in_db or not verify_password(plain_password=password, hashed_password=user_in_db.hashed_password):
            raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid credentials",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
        
        return await self._create_token_pair(user_in_db)


    async def _create_access_token(self, user: User) -> str:
        claims = TokenData(
            sub=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            role_name=user.role.name,
            permissions=[perm.name for perm in user.role.permissions]
        )

        access_token_expires = timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
        return create_access_token(data=claims, expires_delta=access_token_expires)

    def _create_refresh_token(self, user: User) -> str:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {
            "sub": str(user.id),
            "type": "refresh",
            "exp": int(expire.timestamp())
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        self.valid_refresh_tokens[token] = str(user.id)
        return token

    async def _create_token_pair(self, user: User) -> Token:
        access_token = await self._create_access_token(user)
        refresh_token = self._create_refresh_token(user)
        return Token(access_token=access_token, token_type="bearer", refresh_token=refresh_token)

    async def refresh_access_token(self, db: AsyncSession, refresh_token: str) -> Token:
        if refresh_token in self.revoked_refresh_tokens:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked")

        if refresh_token not in self.valid_refresh_tokens:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        user = await user_repo.get_by_id(db=db, user_id=UUID(user_id))
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        self.valid_refresh_tokens.pop(refresh_token, None)
        self.revoked_refresh_tokens.add(refresh_token)

        return await self._create_token_pair(user)

    def revoke_access_token(self, access_token: str) -> None:
        self.revoked_access_tokens.add(access_token)

    def logout(self, access_token: str, refresh_token: str | None = None) -> None:
        self.revoke_access_token(access_token)
        if refresh_token:
            self.valid_refresh_tokens.pop(refresh_token, None)
            self.revoked_refresh_tokens.add(refresh_token)

    def is_access_token_revoked(self, token: str) -> bool:
        return token in self.revoked_access_tokens


auth_service = AuthService()