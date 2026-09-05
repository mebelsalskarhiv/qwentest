"""
Tests for Authentication module
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture(scope="function")
async def client():
    """Test client with fresh database"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_register_user(client):
    """Test user registration"""
    response = await client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123!",
        "full_name": "Test User"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_user(client):
    """Test user login"""
    # First register a user
    await client.post("/api/v1/auth/register", json={
        "username": "loginuser",
        "email": "login@example.com",
        "password": "TestPass123!",
        "full_name": "Login User"
    })
    
    # Then login
    response = await client.post("/api/v1/auth/login", data={
        "username": "loginuser",
        "password": "TestPass123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

@pytest.mark.asyncio
async def test_get_current_user(client):
    """Test getting current user"""
    # Register and get token
    reg_response = await client.post("/api/v1/auth/register", json={
        "username": "meuser",
        "email": "me@example.com",
        "password": "TestPass123!",
        "full_name": "Me User"
    })
    token = reg_response.json()["access_token"]
    
    # Get current user
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "meuser"
    assert data["email"] == "me@example.com"

@pytest.mark.asyncio
async def test_invalid_login(client):
    """Test invalid login credentials"""
    response = await client.post("/api/v1/auth/login", data={
        "username": "nonexistent",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
