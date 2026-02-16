from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from pydantic import ValidationError

from app.repositories import user_repo
from app.core.config import settings
from app.core.database import get_db
from app.schemas.auth import TokenData

security = HTTPBearer()


class CurrentUser:

    """Holds the authenticated user's data from the token"""
    def __init__(self, token_data: TokenData):
        self.user_id = token_data.sub
        self.first_name = token_data.first_name
        self.last_name = token_data.last_name
        self.role_name = token_data.role_name
        self.permissions = token_data.permissions


async def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> CurrentUser:

    unauthorized_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = TokenData.model_validate(payload)
        
    except (JWTError, ValidationError):
        raise unauthorized_exception
    
    user_in_db = await user_repo.get_by_id(db, token_data.sub)
    if user_in_db is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return CurrentUser(token_data)


def require_permission(required_permission: str):

    async def _check(
        current_user: CurrentUser = Depends(require_auth)
    ):
        if required_permission not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{required_permission}' required"
            )
        return current_user
    
    return _check


def require_role(required_role: str):

    async def _check(
        current_user: CurrentUser = Depends(require_auth)
    ):
        if current_user.role_name != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required"
            )
        return current_user
    
    return _check
