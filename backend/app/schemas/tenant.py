"""
Pydantic schemas for multitenancy
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

from app.models.tenant import TenantStatus, BillingPlan


# Enums for API
class TenantStatusEnum(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"
    TRIAL = "trial"


class BillingPlanEnum(str, Enum):
    FREE = "free"
    STARTUP = "startup"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


# Request Schemas
class TenantCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    subdomain: str = Field(..., min_length=3, max_length=100, pattern="^[a-z0-9-]+$")
    custom_domain: Optional[str] = Field(None, max_length=255)
    billing_plan: Optional[BillingPlanEnum] = BillingPlanEnum.FREE
    ssl_enabled: bool = False
    letsencrypt_email: Optional[str] = None
    admin_email: Optional[str] = None
    admin_password: Optional[str] = None
    admin_name: Optional[str] = None
    auto_activate: bool = False
    trial_days: int = 14
    
    @validator('subdomain')
    def validate_subdomain(cls, v):
        if v in ['www', 'api', 'app', 'admin', 'superadmin', 'demo']:
            raise ValueError('Subdomain is reserved')
        return v


class TenantUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    custom_domain: Optional[str] = Field(None, max_length=255)
    status: Optional[TenantStatusEnum] = None
    billing_plan: Optional[BillingPlanEnum] = None
    ssl_enabled: Optional[bool] = None
    letsencrypt_email: Optional[str] = None
    admin_email: Optional[str] = None


class BillingUpdate(BaseModel):
    billing_plan: Optional[BillingPlanEnum] = None
    subscription_expires_at: Optional[datetime] = None
    extend_trial_days: Optional[int] = None


class SSLConfigUpdate(BaseModel):
    enabled: bool = True
    letsencrypt_email: Optional[str] = None


# Response Schemas
class TenantResponse(BaseModel):
    id: str
    name: str
    subdomain: str
    custom_domain: Optional[str]
    status: TenantStatus
    billing_plan: BillingPlan
    ssl_enabled: bool
    letsencrypt_email: Optional[str]
    admin_user_id: Optional[str]
    admin_email: Optional[str]
    trial_ends_at: Optional[datetime]
    subscription_expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
    
    @property
    def primary_domain(self) -> str:
        return self.custom_domain if self.custom_domain else f"{self.subdomain}.virtuoso-mes.local"
    
    @property
    def is_active(self) -> bool:
        return (
            self.status == TenantStatus.ACTIVE and
            not self.is_trial_expired and
            not self.is_subscription_expired
        )
    
    @property
    def is_trial_expired(self) -> bool:
        if not self.trial_ends_at:
            return False
        return datetime.utcnow() > self.trial_ends_at
    
    @property
    def is_subscription_expired(self) -> bool:
        if not self.subscription_expires_at:
            return False
        return datetime.utcnow() > self.subscription_expires_at


class TenantListResponse(BaseModel):
    tenants: List[TenantResponse]
    total: int
    skip: int
    limit: int


class TenantStats(BaseModel):
    total_tenants: int
    active_tenants: int
    pending_tenants: int
    suspended_tenants: int
    trial_tenants: int
    total_users: int
    revenue_mrr: float  # Monthly Recurring Revenue
