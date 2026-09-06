"""
Tests for SuperAdmin API endpoints in Virtuoso MES
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.main import app
from app.models.base import Base
from app.models.tenant import Tenant, TenantStatus, BillingPlan
from app.models.user import User, UserRole
from app.core.database import get_db
from app.core.security import create_access_token

# Test database URL (SQLite for testing)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_superadmin.db"

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


@pytest.fixture
def superadmin_user(db_session):
    """Create a superadmin user."""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    user = User(
        email="superadmin@virtuoso.com",
        username="superadmin",
        hashed_password=pwd_context.hash("admin123"),
        full_name="Super Admin",
        is_active=True,
        is_superuser=True,
        role=UserRole.SUPERADMIN
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def tenant_admin_user(db_session):
    """Create a tenant admin user."""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # Create tenant first
    tenant = Tenant(
        id="tenant-001",
        name="Test Company",
        subdomain="testcompany",
        status=TenantStatus.ACTIVE,
        billing_plan=BillingPlan.STARTUP
    )
    db_session.add(tenant)
    db_session.commit()
    
    user = User(
        email="admin@testcompany.com",
        username="tenantadmin",
        hashed_password=pwd_context.hash("admin123"),
        full_name="Tenant Admin",
        tenant_id=tenant.id,
        is_active=True,
        role=UserRole.ADMIN
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


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


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override."""
    with TestClient(app=app) as c:
        yield c


@pytest.fixture
def superadmin_token(superadmin_user):
    """Create access token for superadmin."""
    return create_access_token(
        data={"sub": str(superadmin_user.id), "role": UserRole.SUPERADMIN.value}
    )


@pytest.fixture
def auth_headers(superadmin_token):
    """Create authorization headers."""
    return {"Authorization": f"Bearer {superadmin_token}"}


class TestSuperAdminTenants:
    """Test SuperAdmin tenant management endpoints."""
    
    def test_list_all_tenants(self, client, superadmin_user, test_tenant, auth_headers):
        """Test listing all tenants (SuperAdmin only)."""
        response = client.get("/api/v1/superadmin/tenants", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "tenants" in data
        assert len(data["tenants"]) >= 1
        
        tenant_ids = [t["id"] for t in data["tenants"]]
        assert test_tenant.id in tenant_ids
    
    def test_create_tenant(self, client, superadmin_user, auth_headers):
        """Test creating a new tenant (SuperAdmin only)."""
        tenant_data = {
            "name": "New Company",
            "subdomain": "newcompany",
            "billing_plan": "startup",
            "admin_email": "admin@newcompany.com",
            "ssl_enabled": True
        }
        
        response = client.post(
            "/api/v1/superadmin/tenants",
            json=tenant_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Company"
        assert data["subdomain"] == "newcompany"
        assert data["billing_plan"] == "startup"
        assert data["ssl_enabled"] is True
    
    def test_create_tenant_duplicate_subdomain(self, client, superadmin_user, test_tenant, auth_headers):
        """Test creating tenant with duplicate subdomain fails."""
        tenant_data = {
            "name": "Duplicate Company",
            "subdomain": test_tenant.subdomain,  # Same subdomain
            "billing_plan": "free",
            "admin_email": "admin@duplicate.com"
        }
        
        response = client.post(
            "/api/v1/superadmin/tenants",
            json=tenant_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
    
    def test_get_tenant_by_id(self, client, superadmin_user, test_tenant, auth_headers):
        """Test getting a specific tenant by ID."""
        response = client.get(
            f"/api/v1/superadmin/tenants/{test_tenant.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_tenant.id
        assert data["name"] == test_tenant.name
    
    def test_update_tenant(self, client, superadmin_user, test_tenant, auth_headers):
        """Test updating a tenant."""
        update_data = {
            "name": "Updated Company Name",
            "billing_plan": "professional",
            "status": "active"
        }
        
        response = client.put(
            f"/api/v1/superadmin/tenants/{test_tenant.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Company Name"
        assert data["billing_plan"] == "professional"
    
    def test_delete_tenant(self, client, superadmin_user, test_tenant, db_session, auth_headers):
        """Test deleting a tenant."""
        response = client.delete(
            f"/api/v1/superadmin/tenants/{test_tenant.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Verify tenant is deleted
        deleted_tenant = db_session.query(Tenant).filter(Tenant.id == test_tenant.id).first()
        assert deleted_tenant is None
    
    def test_suspend_tenant(self, client, superadmin_user, test_tenant, db_session, auth_headers):
        """Test suspending a tenant."""
        response = client.post(
            f"/api/v1/superadmin/tenants/{test_tenant.id}/suspend",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        db_session.refresh(test_tenant)
        assert test_tenant.status == TenantStatus.SUSPENDED
    
    def test_activate_tenant(self, client, superadmin_user, db_session, auth_headers):
        """Test activating a suspended tenant."""
        # Create suspended tenant
        tenant = Tenant(
            id="suspended-tenant-001",
            name="Suspended Company",
            subdomain="suspendedcompany",
            status=TenantStatus.SUSPENDED,
            billing_plan=BillingPlan.FREE
        )
        db_session.add(tenant)
        db_session.commit()
        
        response = client.post(
            f"/api/v1/superadmin/tenants/{tenant.id}/activate",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        db_session.refresh(tenant)
        assert tenant.status == TenantStatus.ACTIVE
    
    def test_enable_ssl_for_tenant(self, client, superadmin_user, test_tenant, db_session, auth_headers):
        """Test enabling SSL for a tenant."""
        ssl_data = {
            "letsencrypt_email": "admin@testcompany.com",
            "custom_domain": "custom.testcompany.com"
        }
        
        response = client.post(
            f"/api/v1/superadmin/tenants/{test_tenant.id}/enable-ssl",
            json=ssl_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        db_session.refresh(test_tenant)
        assert test_tenant.ssl_enabled is True
        assert test_tenant.letsencrypt_email == "admin@testcompany.com"
    
    def test_get_tenant_statistics(self, client, superadmin_user, test_tenant, auth_headers):
        """Test getting statistics for all tenants."""
        response = client.get(
            "/api/v1/superadmin/tenants/statistics",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_tenants" in data
        assert "active_tenants" in data
        assert "total_users" in data
        assert "mrr" in data


class TestSuperAdminAuthorization:
    """Test SuperAdmin authorization."""
    
    def test_non_superadmin_cannot_access_tenants(self, client, tenant_admin_user, test_tenant):
        """Test that non-superadmin cannot access tenant management."""
        token = create_access_token(
            data={"sub": str(tenant_admin_user.id), "role": UserRole.ADMIN.value}
        )
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/superadmin/tenants", headers=headers)
        
        assert response.status_code == 403
    
    def test_unauthorized_access_to_tenants(self, client):
        """Test unauthorized access to tenant management."""
        response = client.get("/api/v1/superadmin/tenants")
        
        assert response.status_code == 401


class TestSuperAdminStatistics:
    """Test SuperAdmin statistics endpoints."""
    
    def test_mrr_calculation(self, client, superadmin_user, db_session, auth_headers):
        """Test MRR (Monthly Recurring Revenue) calculation."""
        # Create tenants with different plans
        plans_mrr = {
            BillingPlan.FREE: 0,
            BillingPlan.STARTUP: 49,
            BillingPlan.PROFESSIONAL: 149,
            BillingPlan.ENTERPRISE: 499
        }
        
        for i, (plan, mrr) in enumerate(plans_mrr.items()):
            tenant = Tenant(
                id=f"tenant-mrr-{i}",
                name=f"MRR Test Company {i}",
                subdomain=f"mrrtest{i}",
                status=TenantStatus.ACTIVE,
                billing_plan=plan
            )
            db_session.add(tenant)
        
        db_session.commit()
        
        response = client.get(
            "/api/v1/superadmin/tenants/statistics",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "mrr" in data
        expected_mrr = sum(plans_mrr.values())
        assert data["mrr"] == expected_mrr
    
    def test_tenant_count_by_status(self, client, superadmin_user, db_session, auth_headers):
        """Test counting tenants by status."""
        statuses = [TenantStatus.ACTIVE, TenantStatus.ACTIVE, TenantStatus.SUSPENDED, TenantStatus.PENDING]
        
        for i, status in enumerate(statuses):
            tenant = Tenant(
                id=f"tenant-status-{i}",
                name=f"Status Test Company {i}",
                subdomain=f"statustest{i}",
                status=status,
                billing_plan=BillingPlan.FREE
            )
            db_session.add(tenant)
        
        db_session.commit()
        
        response = client.get(
            "/api/v1/superadmin/tenants/statistics",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_tenants"] == 4
        assert data["active_tenants"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
