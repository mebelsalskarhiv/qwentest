"""
Multitenancy core module for Virtuoso MES
Handles tenant isolation, subdomain routing, and SSL configuration
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .base import Base


class TenantStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"
    TRIAL = "trial"


class BillingPlan(str, enum.Enum):
    FREE = "free"
    STARTUP = "startup"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class Tenant(Base):
    """Tenant model for multitenancy support"""
    __tablename__ = "tenants"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    subdomain = Column(String(100), unique=True, nullable=False, index=True)
    custom_domain = Column(String(255), unique=True, nullable=True)
    status = Column(SQLEnum(TenantStatus), default=TenantStatus.PENDING)
    billing_plan = Column(SQLEnum(BillingPlan), default=BillingPlan.FREE)
    
    # SSL Configuration
    ssl_enabled = Column(Boolean, default=False)
    ssl_cert_path = Column(String(500), nullable=True)
    ssl_key_path = Column(String(500), nullable=True)
    letsencrypt_email = Column(String(255), nullable=True)
    
    # Admin & Billing
    admin_user_id = Column(String(36), ForeignKey("users.id", use_alter=True, name="fk_tenants_admin_user_id"), nullable=True)
    admin_email = Column(String(255), nullable=True)
    
    # Trial & Expiration
    trial_ends_at = Column(DateTime, nullable=True)
    subscription_expires_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    admin_user = relationship("User", foreign_keys=[admin_user_id])
    users = relationship("User", back_populates="tenant", foreign_keys="User.tenant_id", cascade="all, delete-orphan")
    
    # Cascade delete for related data through users
    audit_logs = relationship("AuditLog", secondary="users", primaryjoin="Tenant.id == User.tenant_id", secondaryjoin="User.id == AuditLog.user_id", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Tenant {self.name} ({self.subdomain})>"
    
    @property
    def primary_domain(self) -> str:
        """Returns the primary domain (subdomain or custom)"""
        return self.custom_domain if self.custom_domain else f"{self.subdomain}.{self.base_domain}"
    
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
    
    @property
    def is_active(self) -> bool:
        return (
            self.status == TenantStatus.ACTIVE and
            not self.is_trial_expired and
            not self.is_subscription_expired
        )
