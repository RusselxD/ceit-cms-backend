from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from uuid import UUID

from app.core.config import settings
from app.core.authz import get_department_from_role, ensure_same_department_or_superadmin
from app.schemas.auth import TokenData
from app.services import auth_service


security = HTTPBearer()


class CurrentUser:
    """Wrapper for current user data from JWT token"""
    def __init__(self, token_data: TokenData):
        self.user_id = token_data.sub
        self.sub = token_data.sub
        self.first_name = token_data.first_name
        self.last_name = token_data.last_name
        self.role_name = token_data.role_name
        self.permissions = token_data.permissions
        self._token_data = token_data
    
    def __getattr__(self, name):
        # Fallback to TokenData attributes
        return getattr(self._token_data, name)


async def get_current_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    token = credentials.credentials
    if auth_service.is_access_token_revoked(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


async def get_current_user(
    token: str = Depends(get_current_token),
) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
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


async def require_auth(
    token_data: TokenData = Depends(get_current_user),
) -> CurrentUser:
    """Dependency that returns CurrentUser wrapper"""
    return CurrentUser(token_data)


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


def require_permission(required_permission: str):
    """Dependency to check if user has required permission (returns CurrentUser)"""
    async def permission_checker(current_user: CurrentUser = Depends(require_auth)):
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


def require_role(required_role: str):
    """Dependency to check if user has required role (returns CurrentUser)"""
    async def role_checker(current_user: CurrentUser = Depends(require_auth)):
        if current_user.role_name != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required"
            )
        return current_user
    return role_checker
