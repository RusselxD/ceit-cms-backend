from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from uuid import UUID

from app.core.config import settings
from app.core.database import get_db
from app.schemas.auth import TokenData


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        user_id: str = payload.get("sub")
        first_name: str = payload.get("first_name")
        last_name: str = payload.get("last_name")
        role_name: str = payload.get("role_name")
        permissions: list = payload.get("permissions", [])
        
        if user_id is None:
            raise credentials_exception
        
        token_data = TokenData(
            sub=UUID(user_id),
            first_name=first_name,
            last_name=last_name,
            role_name=role_name,
            permissions=permissions
        )
        
    except JWTError:
        raise credentials_exception
    
    return token_data


def check_permission(required_permission: str):
    """Dependency to check if user has required permission"""
    async def permission_checker(current_user: TokenData = Depends(get_current_user)):
        if required_permission not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{required_permission}' required"
            )
        return current_user
    return permission_checker


def check_role(required_role: str):
    """Dependency to check if user has required role"""
    async def role_checker(current_user: TokenData = Depends(get_current_user)):
        if current_user.role_name != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required"
            )
        return current_user
    return role_checker
