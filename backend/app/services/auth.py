from datetime import timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.schemas.user import TokenData
from app.models.user import User
from app.models.enums import Permission, UserRole
from sqlalchemy import select

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


ROLE_PERMISSIONS: dict[UserRole, set[Permission]] = {
    UserRole.SUPERADMIN: set(Permission),
    UserRole.ADMIN: set(Permission),
    UserRole.MANAGER: {
        Permission.USERS_READ,
        Permission.PRODUCTION_READ,
        Permission.PRODUCTION_CREATE,
        Permission.PRODUCTION_UPDATE,
        Permission.INVENTORY_READ,
        Permission.INVENTORY_CREATE,
        Permission.INVENTORY_UPDATE,
        Permission.REPORTS_READ,
        Permission.REPORTS_EXPORT,
    },
    UserRole.SUPERVISOR: {
        Permission.USERS_READ,
        Permission.PRODUCTION_READ,
        Permission.PRODUCTION_CREATE,
        Permission.PRODUCTION_UPDATE,
        Permission.INVENTORY_READ,
        Permission.REPORTS_READ,
    },
    UserRole.OPERATOR: {
        Permission.PRODUCTION_READ,
        Permission.PRODUCTION_UPDATE,
    },
    UserRole.QUALITY_INSPECTOR: {
        Permission.PRODUCTION_READ,
        Permission.QUALITY_READ,
        Permission.QUALITY_CREATE,
        Permission.QUALITY_UPDATE,
    },
    UserRole.MAINTENANCE_TECHNICIAN: {
        Permission.PRODUCTION_READ,
        Permission.MAINTENANCE_READ,
        Permission.MAINTENANCE_CREATE,
        Permission.MAINTENANCE_UPDATE,
    },
    UserRole.WAREHOUSE_KEEPER: {
        Permission.INVENTORY_READ,
        Permission.INVENTORY_CREATE,
        Permission.INVENTORY_UPDATE,
    },
    UserRole.ENGINEER: {
        Permission.PRODUCTION_READ,
        Permission.PRODUCTION_CREATE,
        Permission.PRODUCTION_UPDATE,
        Permission.INVENTORY_READ,
    },
    UserRole.GUEST: {
        Permission.PRODUCTION_READ,
        Permission.INVENTORY_READ,
        Permission.REPORTS_READ,
    },
}


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=int(user_id))
    except JWTError:
        raise credentials_exception
    
    result = await db.execute(select(User).where(User.id == token_data.user_id))
    user = result.scalar_one_or_none()
    
    if user is None or not user.is_active:
        raise credentials_exception
    
    return user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user


def require_permission(permission: Permission):
    """Build a dependency that enforces a permission for the current role."""
    async def permission_dependency(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.is_superuser:
            return current_user

        granted = ROLE_PERMISSIONS.get(current_user.role, set())
        if permission not in granted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission.value}",
            )
        return current_user

    return permission_dependency
