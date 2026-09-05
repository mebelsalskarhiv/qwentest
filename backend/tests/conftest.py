"""
Pytest configuration and fixtures for async tests
"""
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
from app.core.database import get_db
from app.main import app

# Import all models FIRST to ensure they're registered with Base metadata
from app.models.user import User, Role, AuditLog
from app.models.inventory import InventoryItem, InventoryCategory, StockMovement, Supplier
from app.models.production import (
    ProductionOrder, Product, WorkCenter,
    ProductionOperation, BillOfMaterial, MaterialConsumption
)
from app.models.hr import Employee, Department, Customer, Station
from app.models.tenant import Tenant
from app.core.database import Base

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/virtuoso_mes_test"

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)

# Create async session maker for tests
test_async_session_maker = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="function", autouse=True)
async def setup_test_database():
    """Setup test database before each test function."""
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Drop all tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db() -> AsyncSession:
    """Override get_db dependency for testing."""
    async with test_async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest.fixture(scope="function")
async def client(setup_test_database) -> AsyncGenerator[AsyncClient, None]:
    """Test client with fresh database for each test function."""
    # Override database dependency
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    # Remove override
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Direct database session fixture for tests that need DB access."""
    async with test_async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
