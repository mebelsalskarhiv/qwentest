"""
SuperAdmin API endpoints for multitenancy management
Manage tenants, SSL configuration, billing, and tenant admins
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from app.core.database import get_db
from app.core.security import get_current_superuser
from app.models.tenant import Tenant, TenantStatus, BillingPlan
from app.models.user import User
from app.schemas.tenant import (
    TenantCreate,
    TenantUpdate,
    TenantResponse,
    TenantListResponse,
    BillingUpdate,
    SSLConfigUpdate,
    TenantStats
)

router = APIRouter(prefix="/tenants", tags=["superadmin-tenants"])


@router.get("/stats", response_model=TenantStats)
async def get_tenant_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Get overall tenant statistics (SuperAdmin only)"""
    total_tenants = db.query(Tenant).count()
    active_tenants = db.query(Tenant).filter(Tenant.status == TenantStatus.ACTIVE).count()
    pending_tenants = db.query(Tenant).filter(Tenant.status == TenantStatus.PENDING).count()
    suspended_tenants = db.query(Tenant).filter(Tenant.status == TenantStatus.SUSPENDED).count()
    trial_tenants = db.query(Tenant).filter(Tenant.status == TenantStatus.TRIAL).count()
    
    # Count users across all tenants
    total_users = db.query(User).count()
    
    # Calculate MRR (simplified - would integrate with payment provider in production)
    plan_prices = {
        BillingPlan.FREE: 0,
        BillingPlan.STARTUP: 29.0,
        BillingPlan.PROFESSIONAL: 99.0,
        BillingPlan.ENTERPRISE: 299.0
    }
    
    revenue_mrr = sum(
        plan_prices.get(t.billing_plan, 0) 
        for t in db.query(Tenant).filter(Tenant.status == TenantStatus.ACTIVE).all()
    )
    
    return TenantStats(
        total_tenants=total_tenants,
        active_tenants=active_tenants,
        pending_tenants=pending_tenants,
        suspended_tenants=suspended_tenants,
        trial_tenants=trial_tenants,
        total_users=total_users,
        revenue_mrr=revenue_mrr
    )


@router.post("/validate-domain")
async def validate_domain_for_ssl(request: Request, db: Session = Depends(get_db)):
    """
    Validate domain for on-demand TLS (used by Caddy)
    Returns 200 if domain is allowed, 403 otherwise
    """
    host = request.headers.get("host", "")
    query_params = dict(request.query_params)
    domain = query_params.get("domain", host)
    
    # Check if domain belongs to an active tenant
    tenant = db.query(Tenant).filter(
        (Tenant.subdomain + ".virtuoso-mes.local" == domain) |
        (Tenant.custom_domain == domain) |
        (Tenant.subdomain == domain.split('.')[0])
    ).first()
    
    if tenant and tenant.is_active and tenant.ssl_enabled:
        return {"valid": True, "tenant_id": tenant.id}
    
    # Allow main domain
    if domain in ["virtuoso-mes.local", "www.virtuoso-mes.local", "localhost"]:
        return {"valid": True, "tenant_id": None}
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Domain not authorized for SSL"
    )


@router.get("/", response_model=TenantListResponse)
async def list_tenants(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[TenantStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """List all tenants (SuperAdmin only)"""
    query = db.query(Tenant)
    
    if status_filter:
        query = query.filter(Tenant.status == status_filter)
    
    total = query.count()
    tenants = query.offset(skip).limit(limit).all()
    
    return TenantListResponse(
        tenants=[TenantResponse.from_orm(t) for t in tenants],
        total=total,
        skip=skip,
        limit=limit
    )


@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant_data: TenantCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Create a new tenant (SuperAdmin only)"""
    # Check if subdomain already exists
    existing = db.query(Tenant).filter(
        (Tenant.subdomain == tenant_data.subdomain) |
        (Tenant.custom_domain == tenant_data.custom_domain)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subdomain or custom domain already exists"
        )
    
    # Create tenant
    tenant = Tenant(
        id=str(uuid.uuid4()),
        name=tenant_data.name,
        subdomain=tenant_data.subdomain,
        custom_domain=tenant_data.custom_domain,
        status=TenantStatus.ACTIVE if tenant_data.auto_activate else TenantStatus.PENDING,
        billing_plan=tenant_data.billing_plan or BillingPlan.FREE,
        ssl_enabled=tenant_data.ssl_enabled,
        letsencrypt_email=tenant_data.letsencrypt_email,
        admin_email=tenant_data.admin_email,
        trial_ends_at=datetime.utcnow() + timedelta(days=tenant_data.trial_days) if tenant_data.trial_days else None,
    )
    
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    
    # Create admin user if provided
    if tenant_data.admin_email and tenant_data.admin_password:
        from app.core.security import get_password_hash
        admin_user = User(
            email=tenant_data.admin_email,
            username=tenant_data.admin_email.split('@')[0],
            hashed_password=get_password_hash(tenant_data.admin_password),
            full_name=tenant_data.admin_name or "Tenant Admin",
            is_active=True,
            is_superuser=False,
            tenant_id=tenant.id,
            role="TENANT_ADMIN"
        )
        tenant.admin_user_id = admin_user.id
        db.add(admin_user)
        db.commit()
        db.refresh(tenant)
    
    return TenantResponse.from_orm(tenant)


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Get tenant details (SuperAdmin only)"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    return TenantResponse.from_orm(tenant)


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: str,
    tenant_data: TenantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Update tenant details (SuperAdmin only)"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    update_data = tenant_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tenant, field, value)
    
    db.commit()
    db.refresh(tenant)
    return TenantResponse.from_orm(tenant)


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(
    tenant_id: str,
    soft_delete: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Delete a tenant (SuperAdmin only) - CASCADE deletes all tenant data"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    if soft_delete:
        tenant.status = TenantStatus.SUSPENDED
        db.commit()
    else:
        # Hard delete - cascade will handle related records
        db.delete(tenant)
        db.commit()
    
    return None


@router.put("/{tenant_id}/billing", response_model=TenantResponse)
async def update_tenant_billing(
    tenant_id: str,
    billing_data: BillingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Update tenant billing plan and subscription (SuperAdmin only)"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    if billing_data.billing_plan:
        tenant.billing_plan = billing_data.billing_plan
    
    if billing_data.subscription_expires_at:
        tenant.subscription_expires_at = billing_data.subscription_expires_at
    
    if billing_data.extend_trial_days:
        tenant.trial_ends_at = datetime.utcnow() + timedelta(days=billing_data.extend_trial_days)
    
    db.commit()
    db.refresh(tenant)
    return TenantResponse.from_orm(tenant)


@router.put("/{tenant_id}/ssl", response_model=TenantResponse)
async def configure_tenant_ssl(
    tenant_id: str,
    ssl_data: SSLConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Configure SSL/Let's Encrypt for tenant (SuperAdmin only)"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    tenant.ssl_enabled = ssl_data.enabled
    tenant.letsencrypt_email = ssl_data.letsencrypt_email or tenant.letsencrypt_email
    
    # Note: Actual certificate generation happens via Caddy automation
    # This just updates the database flags
    
    db.commit()
    db.refresh(tenant)
    return TenantResponse.from_orm(tenant)


@router.post("/{tenant_id}/activate", response_model=TenantResponse)
async def activate_tenant(
    tenant_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Activate a pending tenant (SuperAdmin only)"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    tenant.status = TenantStatus.ACTIVE
    db.commit()
    db.refresh(tenant)
    return TenantResponse.from_orm(tenant)


@router.post("/{tenant_id}/suspend", response_model=TenantResponse)
async def suspend_tenant(
    tenant_id: str,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Suspend a tenant (SuperAdmin only)"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    tenant.status = TenantStatus.SUSPENDED
    # Could store reason in a separate field or audit log
    db.commit()
    db.refresh(tenant)
    return TenantResponse.from_orm(tenant)
