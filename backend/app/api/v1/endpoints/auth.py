from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from app.core.database import get_db
from app.core.config import settings
from app.core.security import verify_password, get_password_hash
from app.schemas.user import UserCreate, UserResponse, LoginRequest, Token
from app.models.user import User
from app.services.auth import create_access_token, create_refresh_token
from sqlalchemy import select

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    # Check if user exists
    result = await db.execute(
        select(User).where(
            (User.email == user_data.email) | (User.username == user_data.username)
        )
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role=user_data.role,
    )
    
    db.add(user)
    await db.flush()
    await db.refresh(user)
    
    return user


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login and get access token."""
    # Find user by username or email
    result = await db.execute(
        select(User).where(
            (User.username == login_data.username) | (User.email == login_data.username)
        )
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role.value},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(lambda: None)):
    """Get current user information."""
    # This will be implemented with proper dependency
    return current_user
