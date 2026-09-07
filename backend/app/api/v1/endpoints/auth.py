from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import uuid
from app.core.database import get_db
from app.core.config import settings
from app.core.security import verify_password, get_password_hash
from app.schemas.user import UserCreate, UserResponse, LoginRequest, Token, TenantRegistration, RegistrationResponse
from app.models.user import User
from app.models.tenant import Tenant, TenantStatus, BillingPlan
from app.models.enums import UserRole
from app.services.auth import create_access_token, create_refresh_token, get_current_user
from sqlalchemy import select

router = APIRouter(prefix="/auth", tags=["Authentication"])


async def _authenticate_user(login_data: LoginRequest, db: AsyncSession) -> User:
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
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    return user


def _create_tokens(user: User) -> Token:
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "username": user.username,
            "role": user.role.value,
            "tenant_id": user.tenant_id,
        },
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "tenant_id": user.tenant_id}
    )
    return Token(access_token=access_token, refresh_token=refresh_token)


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


@router.post("/register-tenant", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_tenant(registration: TenantRegistration, db: AsyncSession = Depends(get_db)):
    """Create a tenant and its first administrator from the public landing page."""
    existing_user = (await db.execute(
        select(User).where((User.email == registration.email) | (User.username == registration.username))
    )).scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email or username already registered")

    existing_tenant = (await db.execute(
        select(Tenant).where(Tenant.subdomain == registration.subdomain)
    )).scalar_one_or_none()
    if existing_tenant:
        raise HTTPException(status_code=400, detail="Subdomain already registered")

    tenant = Tenant(
        id=str(uuid.uuid4()),
        name=registration.tenant_name,
        subdomain=registration.subdomain,
        status=TenantStatus.TRIAL,
        billing_plan=BillingPlan.FREE,
        admin_email=registration.email,
        trial_ends_at=datetime.utcnow() + timedelta(days=14),
    )
    db.add(tenant)
    await db.flush()

    user = User(
        email=registration.email,
        username=registration.username,
        full_name=registration.full_name,
        hashed_password=get_password_hash(registration.password),
        role=UserRole.ADMIN,
        tenant_id=tenant.id,
    )
    db.add(user)
    await db.flush()
    tenant.admin_user_id = user.id
    await db.commit()
    await db.refresh(user)

    return RegistrationResponse(
        access_token=create_access_token(data={"sub": str(user.id), "username": user.username, "role": user.role.value, "tenant_id": tenant.id}),
        refresh_token=create_refresh_token(data={"sub": str(user.id), "tenant_id": tenant.id}),
        user=user,
        tenant_id=tenant.id,
    )


@router.post("/demo", response_model=Token)
async def demo_login(db: AsyncSession = Depends(get_db)):
    """Issue a session for the dedicated demo tenant."""
    tenant = (await db.execute(
        select(Tenant).where(Tenant.subdomain == "demo", Tenant.status.in_([TenantStatus.ACTIVE, TenantStatus.TRIAL]))
    )).scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=503, detail="Demo tenant is not configured")

    user = (await db.execute(
        select(User).where(User.tenant_id == tenant.id, User.is_active.is_(True)).order_by(User.id)
    )).scalars().first()
    if not user:
        raise HTTPException(status_code=503, detail="Demo user is not configured")

    return Token(
        access_token=create_access_token(data={"sub": str(user.id), "username": user.username, "role": user.role.value, "tenant_id": tenant.id}),
        refresh_token=create_refresh_token(data={"sub": str(user.id), "tenant_id": tenant.id}),
    )


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login and get access token."""
    user = await _authenticate_user(login_data, db)
    if user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Use the dedicated superadmin login",
        )
    return _create_tokens(user)


@router.post("/superadmin/login", response_model=Token)
async def superadmin_login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login for the isolated superadmin area."""
    user = await _authenticate_user(login_data, db)
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superadmin privileges are required",
        )
    return _create_tokens(user)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user
