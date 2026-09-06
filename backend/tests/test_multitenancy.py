"""
Tests for multitenancy functionality in Virtuoso MES
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.models.base import Base
from app.models.tenant import Tenant, TenantStatus, BillingPlan
from app.models.user import User
from app.core.database import get_db

# Test database URL (SQLite for testing)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_virtuoso_mes.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override."""
    with TestClient(app=app) as c:
        yield c


@pytest.fixture
def test_tenant(db_session):
    """Create a test tenant."""
    tenant = Tenant(
        id="test-tenant-001",
        name="Test Company",
        subdomain="testcompany",
        status=TenantStatus.ACTIVE,
        billing_plan=BillingPlan.STARTUP,
        ssl_enabled=True,
        admin_email="admin@testcompany.com"
    )
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def test_user(db_session, test_tenant):
    """Create a test user."""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    user = User(
        email="user@testcompany.com",
        username="testuser",
        hashed_password=pwd_context.hash("password123"),
        full_name="Test User",
        tenant_id=test_tenant.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestTenantCreation:
    """Test tenant creation and management."""
    
    def test_create_tenant(self, db_session):
        """Test creating a new tenant."""
        tenant = Tenant(
            id="new-tenant-001",
            name="New Company",
            subdomain="newcompany",
            status=TenantStatus.PENDING,
            billing_plan=BillingPlan.FREE
        )
        db_session.add(tenant)
        db_session.commit()
        
        assert tenant.id == "new-tenant-001"
        assert tenant.name == "New Company"
        assert tenant.subdomain == "newcompany"
        assert tenant.status == TenantStatus.PENDING
    
    def test_tenant_subdomain_unique(self, db_session, test_tenant):
        """Test that subdomain must be unique."""
        from sqlalchemy.exc import IntegrityError
        
        duplicate_tenant = Tenant(
            id="duplicate-tenant-001",
            name="Duplicate Company",
            subdomain=test_tenant.subdomain,  # Same subdomain
            status=TenantStatus.ACTIVE
        )
        db_session.add(duplicate_tenant)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_tenant_primary_domain(self, test_tenant):
        """Test primary domain property."""
        # Without custom domain
        assert test_tenant.primary_domain == f"{test_tenant.subdomain}.{test_tenant.base_domain}"
        
        # With custom domain
        test_tenant.custom_domain = "custom.example.com"
        assert test_tenant.primary_domain == "custom.example.com"


class TestTenantIsolation:
    """Test data isolation between tenants."""
    
    def test_users_isolated_by_tenant(self, db_session, test_tenant, test_user):
        """Test that users are isolated by tenant_id."""
        # Create another tenant
        tenant2 = Tenant(
            id="tenant-002",
            name="Another Company",
            subdomain="anothercompany",
            status=TenantStatus.ACTIVE
        )
        db_session.add(tenant2)
        db_session.commit()
        
        # Create user in second tenant
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        user2 = User(
            email="user@anothercompany.com",
            username="user2",
            hashed_password=pwd_context.hash("password123"),
            tenant_id=tenant2.id,
            is_active=True
        )
        db_session.add(user2)
        db_session.commit()
        
        # Verify isolation
        tenant1_users = db_session.query(User).filter(User.tenant_id == test_tenant.id).all()
        tenant2_users = db_session.query(User).filter(User.tenant_id == tenant2.id).all()
        
        assert len(tenant1_users) == 1
        assert len(tenant2_users) == 1
        assert tenant1_users[0].id == test_user.id
        assert tenant2_users[0].id == user2.id


class TestTenantLifecycle:
    """Test tenant lifecycle operations."""
    
    def test_trial_expiration(self, db_session):
        """Test trial expiration logic."""
        from datetime import datetime, timedelta
        
        # Tenant with active trial
        trial_tenant = Tenant(
            id="trial-tenant-001",
            name="Trial Company",
            subdomain="trialcompany",
            status=TenantStatus.TRIAL,
            trial_ends_at=datetime.utcnow() + timedelta(days=7)
        )
        db_session.add(trial_tenant)
        db_session.commit()
        
        assert not trial_tenant.is_trial_expired
        assert trial_tenant.is_active
        
        # Expired trial
        expired_tenant = Tenant(
            id="expired-tenant-001",
            name="Expired Company",
            subdomain="expiredcompany",
            status=TenantStatus.TRIAL,
            trial_ends_at=datetime.utcnow() - timedelta(days=1)
        )
        db_session.add(expired_tenant)
        db_session.commit()
        
        assert expired_tenant.is_trial_expired
        assert not expired_tenant.is_active
    
    def test_subscription_expiration(self, db_session):
        """Test subscription expiration logic."""
        from datetime import datetime, timedelta
        
        # Active subscription
        active_tenant = Tenant(
            id="active-sub-001",
            name="Active Subscription Co",
            subdomain="activesub",
            status=TenantStatus.ACTIVE,
            subscription_expires_at=datetime.utcnow() + timedelta(days=30)
        )
        db_session.add(active_tenant)
        db_session.commit()
        
        assert not active_tenant.is_subscription_expired
        assert active_tenant.is_active
        
        # Expired subscription
        expired_tenant = Tenant(
            id="expired-sub-001",
            name="Expired Subscription Co",
            subdomain="expiredsub",
            status=TenantStatus.ACTIVE,
            subscription_expires_at=datetime.utcnow() - timedelta(days=1)
        )
        db_session.add(expired_tenant)
        db_session.commit()
        
        assert expired_tenant.is_subscription_expired
        assert not expired_tenant.is_active
    
    def test_suspend_tenant(self, db_session, test_tenant):
        """Test suspending a tenant."""
        assert test_tenant.status == TenantStatus.ACTIVE
        assert test_tenant.is_active
        
        test_tenant.status = TenantStatus.SUSPENDED
        db_session.commit()
        
        assert test_tenant.status == TenantStatus.SUSPENDED
        assert not test_tenant.is_active


class TestCascadeDelete:
    """Test cascade delete functionality."""
    
    def test_delete_tenant_cascades_to_users(self, db_session, test_tenant, test_user):
        """Test that deleting a tenant cascades to its users."""
        tenant_id = test_tenant.id
        
        # Verify user exists
        users_before = db_session.query(User).filter(User.tenant_id == tenant_id).count()
        assert users_before == 1
        
        # Delete tenant
        db_session.delete(test_tenant)
        db_session.commit()
        
        # Verify users are also deleted
        users_after = db_session.query(User).filter(User.tenant_id == tenant_id).count()
        assert users_after == 0
        
        # Verify tenant is deleted
        tenant = db_session.query(Tenant).filter(Tenant.id == tenant_id).first()
        assert tenant is None


class TestBillingPlans:
    """Test billing plan functionality."""
    
    def test_billing_plan_enum(self, db_session):
        """Test billing plan enum values."""
        plans = [BillingPlan.FREE, BillingPlan.STARTUP, BillingPlan.PROFESSIONAL, BillingPlan.ENTERPRISE]
        assert len(plans) == 4
        assert BillingPlan.FREE.value == "free"
        assert BillingPlan.STARTUP.value == "startup"
        assert BillingPlan.PROFESSIONAL.value == "professional"
        assert BillingPlan.ENTERPRISE.value == "enterprise"
    
    def test_tenant_billing_plan_upgrade(self, db_session, test_tenant):
        """Test upgrading tenant billing plan."""
        assert test_tenant.billing_plan == BillingPlan.STARTUP
        
        # Upgrade to Professional
        test_tenant.billing_plan = BillingPlan.PROFESSIONAL
        db_session.commit()
        
        assert test_tenant.billing_plan == BillingPlan.PROFESSIONAL
        
        # Upgrade to Enterprise
        test_tenant.billing_plan = BillingPlan.ENTERPRISE
        db_session.commit()
        
        assert test_tenant.billing_plan == BillingPlan.ENTERPRISE


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
