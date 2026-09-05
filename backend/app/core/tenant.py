"""
Multitenancy dependency injection and tenant resolution
Handles subdomain-based tenant routing and isolation
"""
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional
import re

from app.core.database import get_db
from app.models.tenant import Tenant, TenantStatus
from app.models.user import User


class TenantResolver:
    """Resolves tenant from subdomain or custom domain"""
    
    @staticmethod
    async def resolve_tenant_from_request(request: Request, db: Session) -> Optional[Tenant]:
        """
        Resolve tenant from request host header.
        Supports:
        - Subdomain: tenant1.example.com -> tenant1
        - Custom domain: custom-domain.com -> lookup by custom_domain
        - Root domain: example.com -> demo/public tenant
        """
        host = request.headers.get("host", "")
        
        # Extract domain parts
        domain_pattern = r'^([a-z0-9-]+)\.(.+)$'
        match = re.match(domain_pattern, host.lower())
        
        if not match:
            # Root domain or localhost - return None (public/demo)
            return None
        
        subdomain = match.group(1)
        full_domain = host.lower()
        
        # Try to find tenant by subdomain
        tenant = db.query(Tenant).filter(
            (Tenant.subdomain == subdomain) | 
            (Tenant.custom_domain == full_domain)
        ).first()
        
        if tenant and not tenant.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Tenant '{tenant.name}' is not active. Status: {tenant.status}"
            )
        
        return tenant


async def get_current_tenant(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[Tenant]:
    """Dependency to get current tenant from request"""
    return await TenantResolver.resolve_tenant_from_request(request, db)


async def get_required_tenant(
    tenant: Optional[Tenant] = Depends(get_current_tenant)
) -> Tenant:
    """Dependency that requires a valid tenant"""
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found. Please access via your tenant subdomain."
        )
    return tenant


def get_tenant_id_from_token(token_data: dict) -> Optional[str]:
    """Extract tenant ID from JWT token payload"""
    return token_data.get("tenant_id")


class TenantIsolationMiddleware:
    """
    Middleware to enforce tenant isolation on database queries.
    Automatically filters queries by tenant_id for multitenant models.
    """
    
    TENANT_ISOLATED_MODELS = [
        "InventoryItem",
        "ProductionOrder",
        "Employee",
        # Add other models that need isolation
    ]
    
    @staticmethod
    def apply_isolation(query, model_class, tenant_id: str):
        """Apply tenant filter to query if model requires isolation"""
        if model_class.__name__ in TenantIsolationMiddleware.TENANT_ISOLATED_MODELS:
            if hasattr(model_class, 'tenant_id'):
                return query.filter(model_class.tenant_id == tenant_id)
        return query
