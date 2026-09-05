from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.schemas.production import (
    ProductionOrderCreate, ProductionOrderUpdate, ProductionOrderResponse,
    ProductCreate, ProductUpdate, ProductResponse,
    WorkCenterCreate, WorkCenterUpdate, WorkCenterResponse,
    ProductionOperationCreate, ProductionOperationUpdate, ProductionOperationResponse,
    BillOfMaterialCreate, BillOfMaterialResponse
)
from app.models.production import (
    ProductionOrder, Product, WorkCenter, 
    ProductionOperation, BillOfMaterial, MaterialConsumption,
    ProductionOrderStatus
)
from app.models.user import User
from app.services.auth import get_current_user

router = APIRouter(prefix="/production", tags=["Production"])


@router.get("/orders", response_model=List[ProductionOrderResponse])
async def get_production_orders(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all production orders."""
    query = select(ProductionOrder).where(ProductionOrder.is_active == True)
    
    if status_filter:
        query = query.where(ProductionOrder.status == status_filter)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/orders/{order_id}", response_model=ProductionOrderResponse)
async def get_production_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get production order by ID."""
    result = await db.execute(
        select(ProductionOrder).where(ProductionOrder.id == order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Production order not found"
        )
    
    return order


@router.post("/orders", response_model=ProductionOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_production_order(
    order_data: ProductionOrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new production order."""
    # Check if order number exists
    result = await db.execute(
        select(ProductionOrder).where(ProductionOrder.order_number == order_data.order_number)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order number already exists"
        )
    
    order = ProductionOrder(
        **order_data.model_dump(),
        created_by=current_user.id,
        status=ProductionOrderStatus.DRAFT
    )
    
    db.add(order)
    await db.flush()
    await db.refresh(order)
    
    return order


@router.put("/orders/{order_id}", response_model=ProductionOrderResponse)
async def update_production_order(
    order_id: int,
    order_data: ProductionOrderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update production order."""
    result = await db.execute(
        select(ProductionOrder).where(ProductionOrder.id == order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Production order not found"
        )
    
    update_data = order_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    
    await db.flush()
    await db.refresh(order)
    
    return order


@router.post("/orders/{order_id}/start", response_model=ProductionOrderResponse)
async def start_production_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start production order."""
    result = await db.execute(
        select(ProductionOrder).where(ProductionOrder.id == order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Production order not found"
        )
    
    order.status = ProductionOrderStatus.IN_PROGRESS
    order.actual_start = datetime.utcnow()
    
    await db.flush()
    await db.refresh(order)
    
    return order


@router.post("/orders/{order_id}/complete", response_model=ProductionOrderResponse)
async def complete_production_order(
    order_id: int,
    quantity_completed: float,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Complete production order."""
    result = await db.execute(
        select(ProductionOrder).where(ProductionOrder.id == order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Production order not found"
        )
    
    order.quantity_completed = quantity_completed
    order.status = ProductionOrderStatus.COMPLETED
    order.actual_end = datetime.utcnow()
    
    await db.flush()
    await db.refresh(order)
    
    return order


@router.get("/products", response_model=List[ProductResponse])
async def get_products(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all products."""
    result = await db.execute(select(Product).where(Product.is_active == True))
    return result.scalars().all()


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new product."""
    product = Product(**product_data.model_dump())
    db.add(product)
    await db.flush()
    await db.refresh(product)
    return product


@router.get("/work-centers", response_model=List[WorkCenterResponse])
async def get_work_centers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all work centers."""
    result = await db.execute(select(WorkCenter).where(WorkCenter.is_active == True))
    return result.scalars().all()


@router.post("/work-centers", response_model=WorkCenterResponse, status_code=status.HTTP_201_CREATED)
async def create_work_center(
    work_center_data: WorkCenterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new work center."""
    work_center = WorkCenter(**work_center_data.model_dump())
    db.add(work_center)
    await db.flush()
    await db.refresh(work_center)
    return work_center


@router.get("/orders/{order_id}/operations", response_model=List[ProductionOperationResponse])
async def get_production_operations(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get operations for production order."""
    result = await db.execute(
        select(ProductionOperation)
        .where(ProductionOperation.production_order_id == order_id)
        .order_by(ProductionOperation.operation_number)
    )
    return result.scalars().all()


@router.post("/orders/{order_id}/operations", response_model=ProductionOperationResponse)
async def create_production_operation(
    order_id: int,
    operation_data: ProductionOperationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create production operation."""
    operation = ProductionOperation(**operation_data.model_dump())
    db.add(operation)
    await db.flush()
    await db.refresh(operation)
    return operation


@router.get("/products/{product_id}/bom", response_model=List[BillOfMaterialResponse])
async def get_bill_of_materials(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get bill of materials for product."""
    result = await db.execute(
        select(BillOfMaterial)
        .where(BillOfMaterial.product_id == product_id)
        .where(BillOfMaterial.is_active == True)
    )
    return result.scalars().all()


@router.post("/products/{product_id}/bom", response_model=BillOfMaterialResponse)
async def add_bill_of_material(
    product_id: int,
    bom_data: BillOfMaterialCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add bill of material to product."""
    bom = BillOfMaterial(product_id=product_id, **bom_data.model_dump())
    db.add(bom)
    await db.flush()
    await db.refresh(bom)
    return bom
