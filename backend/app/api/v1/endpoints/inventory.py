from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from app.core.database import get_db
from app.schemas.inventory import (
    InventoryItemCreate, InventoryItemUpdate, InventoryItemResponse,
    StockMovementCreate, StockMovementResponse,
    InventoryCategoryCreate, InventoryCategoryResponse,
    SupplierCreate, SupplierUpdate, SupplierResponse
)
from app.models.inventory import InventoryItem, StockMovement, InventoryCategory, Supplier
from app.models.user import User
from app.models.enums import Permission
from app.services.auth import require_permission

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("/items", response_model=List[InventoryItemResponse])
async def get_inventory_items(
    skip: int = 0,
    limit: int = 100,
    category_id: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.INVENTORY_READ))
):
    """Get all inventory items."""
    query = select(InventoryItem).where(
        InventoryItem.is_active == True,
        InventoryItem.tenant_id == current_user.tenant_id,
    )
    
    if category_id:
        query = query.where(InventoryItem.category_id == category_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()
    return items


@router.get("/items/{item_id}", response_model=InventoryItemResponse)
async def get_inventory_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.INVENTORY_READ))
):
    """Get inventory item by ID."""
    result = await db.execute(
        select(InventoryItem).where(
            InventoryItem.id == item_id,
            InventoryItem.tenant_id == current_user.tenant_id,
        )
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    return item


@router.post("/items", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_item(
    item_data: InventoryItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.INVENTORY_CREATE))
):
    """Create new inventory item."""
    # Check if SKU exists
    result = await db.execute(
        select(InventoryItem).where(
            InventoryItem.sku == item_data.sku,
            InventoryItem.tenant_id == current_user.tenant_id,
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SKU already exists"
        )
    
    item = InventoryItem(**item_data.model_dump(), tenant_id=current_user.tenant_id)
    item.available_stock = item.current_stock - item.reserved_stock
    
    db.add(item)
    await db.flush()
    await db.refresh(item)
    
    return item


@router.put("/items/{item_id}", response_model=InventoryItemResponse)
async def update_inventory_item(
    item_id: int,
    item_data: InventoryItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.INVENTORY_UPDATE))
):
    """Update inventory item."""
    result = await db.execute(
        select(InventoryItem).where(
            InventoryItem.id == item_id,
            InventoryItem.tenant_id == current_user.tenant_id,
        )
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    update_data = item_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    if item.current_stock is not None and item.reserved_stock is not None:
        item.available_stock = item.current_stock - item.reserved_stock
    
    await db.flush()
    await db.refresh(item)
    
    return item


@router.post("/items/{item_id}/movements", response_model=StockMovementResponse)
async def create_stock_movement(
    item_id: int,
    movement_data: StockMovementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.INVENTORY_UPDATE))
):
    """Create stock movement."""
    # Verify item exists
    result = await db.execute(
        select(InventoryItem).where(
            InventoryItem.id == item_id,
            InventoryItem.tenant_id == current_user.tenant_id,
        )
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    # Create movement
    movement = StockMovement(
        **movement_data.model_dump(),
        tenant_id=current_user.tenant_id,
        performed_by=current_user.id
    )
    
    # Update stock
    if movement_data.movement_type == "IN":
        item.current_stock += movement_data.quantity
    elif movement_data.movement_type == "OUT":
        item.current_stock -= movement_data.quantity
    
    item.available_stock = item.current_stock - item.reserved_stock
    
    db.add(movement)
    await db.flush()
    await db.refresh(movement)
    
    return movement


@router.get("/categories", response_model=List[InventoryCategoryResponse])
async def get_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.INVENTORY_READ))
):
    """Get all inventory categories."""
    result = await db.execute(
        select(InventoryCategory).where(
            InventoryCategory.tenant_id == current_user.tenant_id
        )
    )
    return result.scalars().all()


@router.post("/categories", response_model=InventoryCategoryResponse)
async def create_category(
    category_data: InventoryCategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.INVENTORY_CREATE))
):
    """Create inventory category."""
    category = InventoryCategory(
        **category_data.model_dump(), tenant_id=current_user.tenant_id
    )
    db.add(category)
    await db.flush()
    await db.refresh(category)
    return category


@router.get("/suppliers", response_model=List[SupplierResponse])
async def get_suppliers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.INVENTORY_READ))
):
    """Get all suppliers."""
    result = await db.execute(
        select(Supplier).where(
            Supplier.is_active == True,
            Supplier.tenant_id == current_user.tenant_id,
        )
    )
    return result.scalars().all()


@router.post("/suppliers", response_model=SupplierResponse)
async def create_supplier(
    supplier_data: SupplierCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.INVENTORY_CREATE))
):
    """Create supplier."""
    supplier = Supplier(**supplier_data.model_dump(), tenant_id=current_user.tenant_id)
    db.add(supplier)
    await db.flush()
    await db.refresh(supplier)
    return supplier
