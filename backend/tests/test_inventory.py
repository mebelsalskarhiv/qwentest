"""
Tests for Inventory module
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db

# Test database setup - use sync SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_inventory.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def authenticated_client(db_session):
    """Test client with authenticated user"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Register and login to get token
    with TestClient(app) as client:
        reg_response = client.post("/api/v1/auth/register", json={
            "username": "inventoryuser",
            "email": "inventory@example.com",
            "password": "TestPass123!",
            "full_name": "Inventory User"
        })
        token = reg_response.json()["access_token"]
        client.headers["Authorization"] = f"Bearer {token}"
        yield client
    
    app.dependency_overrides.clear()

def test_create_inventory_item(authenticated_client, db_session):
    """Test creating an inventory item"""
    response = authenticated_client.post("/api/v1/inventory/items", json={
        "sku": "TEST-001",
        "name": "Test Item",
        "description": "A test inventory item",
        "category_id": None,
        "unit_of_measure": "pcs",
        "quantity_on_hand": 100,
        "reorder_point": 10,
        "unit_cost": 25.50
    })
    assert response.status_code == 200
    data = response.json()
    assert data["sku"] == "TEST-001"
    assert data["name"] == "Test Item"
    assert data["quantity_on_hand"] == 100

def test_get_inventory_items(authenticated_client, db_session):
    """Test getting all inventory items"""
    # Create an item first
    authenticated_client.post("/api/v1/inventory/items", json={
        "sku": "TEST-002",
        "name": "Test Item 2",
        "description": "Another test item",
        "category_id": None,
        "unit_of_measure": "pcs",
        "quantity_on_hand": 50,
        "reorder_point": 5,
        "unit_cost": 15.00
    })
    
    response = authenticated_client.get("/api/v1/inventory/items")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1

def test_update_inventory_item(authenticated_client, db_session):
    """Test updating an inventory item"""
    # Create an item first
    create_response = authenticated_client.post("/api/v1/inventory/items", json={
        "sku": "TEST-003",
        "name": "Test Item 3",
        "description": "Item to update",
        "category_id": None,
        "unit_of_measure": "pcs",
        "quantity_on_hand": 30,
        "reorder_point": 3,
        "unit_cost": 10.00
    })
    item_id = create_response.json()["id"]
    
    # Update the item
    response = authenticated_client.put(f"/api/v1/inventory/items/{item_id}", json={
        "sku": "TEST-003-UPDATED",
        "name": "Updated Test Item 3",
        "description": "Updated description",
        "category_id": None,
        "unit_of_measure": "pcs",
        "quantity_on_hand": 60,
        "reorder_point": 6,
        "unit_cost": 12.00
    })
    assert response.status_code == 200
    data = response.json()
    assert data["sku"] == "TEST-003-UPDATED"
    assert data["quantity_on_hand"] == 60

def test_delete_inventory_item(authenticated_client, db_session):
    """Test deleting an inventory item"""
    # Create an item first
    create_response = authenticated_client.post("/api/v1/inventory/items", json={
        "sku": "TEST-004",
        "name": "Test Item 4",
        "description": "Item to delete",
        "category_id": None,
        "unit_of_measure": "pcs",
        "quantity_on_hand": 20,
        "reorder_point": 2,
        "unit_cost": 8.00
    })
    item_id = create_response.json()["id"]
    
    # Delete the item
    response = authenticated_client.delete(f"/api/v1/inventory/items/{item_id}")
    assert response.status_code == 200
    
    # Verify it's deleted
    get_response = authenticated_client.get(f"/api/v1/inventory/items/{item_id}")
    assert get_response.status_code == 404

def test_create_stock_movement(authenticated_client, db_session):
    """Test creating a stock movement"""
    # Create an item first
    item_response = authenticated_client.post("/api/v1/inventory/items", json={
        "sku": "TEST-005",
        "name": "Test Item 5",
        "description": "Item for movement",
        "category_id": None,
        "unit_of_measure": "pcs",
        "quantity_on_hand": 100,
        "reorder_point": 10,
        "unit_cost": 5.00
    })
    item_id = item_response.json()["id"]
    
    # Create a stock movement
    response = authenticated_client.post("/api/v1/inventory/movements", json={
        "item_id": item_id,
        "movement_type": "in",
        "quantity": 50,
        "reference": "PO-001",
        "notes": "Initial stock receipt"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["movement_type"] == "in"
    assert data["quantity"] == 50
