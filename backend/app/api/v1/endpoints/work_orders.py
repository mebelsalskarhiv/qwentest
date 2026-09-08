from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime
import json
from app.core.database import get_db
from app.schemas.production import (
    WorkOrderCreate, WorkOrderUpdate, WorkOrderResponse,
    ProductionStageCreate, ProductionStageUpdate, ProductionStageResponse,
    StageTypeDefinitionCreate, StageTypeDefinitionResponse,
    WorkOrderCommentCreate, WorkOrderCommentResponse,
    StageTimelineEventCreate, StageTimelineEventResponse
)
from app.models.production import (
    WorkOrder, ProductionStage, StageTypeDefinition,
    WorkOrderComment, StageTimelineEvent, ProductionOrder,
    WorkOrderStatus, ProductionStageStatus, StageType
)
from app.models.user import User
from app.models.enums import Permission
from app.services.auth import require_permission

router = APIRouter(prefix="/work-orders", tags=["Work Orders"])


@router.get("", response_model=List[WorkOrderResponse])
async def get_work_orders(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    production_order_id: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.PRODUCTION_READ))
):
    """Get all work orders."""
    query = select(WorkOrder).where(
        WorkOrder.is_active == True,
        WorkOrder.tenant_id == current_user.tenant_id,
    )
    
    if status_filter:
        query = query.where(WorkOrder.status == status_filter)
    
    if production_order_id:
        query = query.where(WorkOrder.production_order_id == production_order_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{order_id}", response_model=WorkOrderResponse)
async def get_work_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.PRODUCTION_READ))
):
    """Get work order by ID."""
    result = await db.execute(
        select(WorkOrder).where(
            WorkOrder.id == order_id,
            WorkOrder.tenant_id == current_user.tenant_id,
        )
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work order not found"
        )
    
    return order


@router.post("", response_model=WorkOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_work_order(
    order_data: WorkOrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.PRODUCTION_CREATE))
):
    """Create new work order."""
    # Check if work order number exists
    result = await db.execute(
        select(WorkOrder).where(
            WorkOrder.work_order_number == order_data.work_order_number,
            WorkOrder.tenant_id == current_user.tenant_id,
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Work order number already exists"
        )
    
    # Verify production order exists
    prod_result = await db.execute(
        select(ProductionOrder).where(
            ProductionOrder.id == order_data.production_order_id,
            ProductionOrder.tenant_id == current_user.tenant_id,
        )
    )
    prod_order = prod_result.scalar_one_or_none()
    
    if not prod_order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Production order not found"
        )
    
    order = WorkOrder(
        **order_data.model_dump(),
        tenant_id=current_user.tenant_id,
    )
    
    db.add(order)
    await db.flush()
    await db.refresh(order)
    
    return order


@router.put("/{order_id}", response_model=WorkOrderResponse)
async def update_work_order(
    order_id: int,
    order_data: WorkOrderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.PRODUCTION_UPDATE))
):
    """Update work order."""
    result = await db.execute(
        select(WorkOrder).where(
            WorkOrder.id == order_id,
            WorkOrder.tenant_id == current_user.tenant_id,
        )
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work order not found"
        )
    
    update_data = order_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    
    await db.flush()
    await db.refresh(order)
    
    return order


@router.post("/{order_id}/start", response_model=WorkOrderResponse)
async def start_work_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.PRODUCTION_UPDATE))
):
    """Start work order."""
    result = await db.execute(
        select(WorkOrder).where(
            WorkOrder.id == order_id,
            WorkOrder.tenant_id == current_user.tenant_id,
        )
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work order not found"
        )
    
    order.status = WorkOrderStatus.IN_PROGRESS
    order.actual_start = datetime.utcnow()
    
    await db.flush()
    await db.refresh(order)
    
    return order


@router.post("/{order_id}/complete", response_model=WorkOrderResponse)
async def complete_work_order(
    order_id: int,
    quantity_completed: float,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.PRODUCTION_UPDATE))
):
    """Complete work order."""
    result = await db.execute(
        select(WorkOrder).where(
            WorkOrder.id == order_id,
            WorkOrder.tenant_id == current_user.tenant_id,
        )
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work order not found"
        )
    
    order.quantity_completed = quantity_completed
    order.status = WorkOrderStatus.COMPLETED
    order.actual_end = datetime.utcnow()
    
    await db.flush()
    await db.refresh(order)
    
    return order


# Production Stages endpoints
@router.get("/{order_id}/stages", response_model=List[ProductionStageResponse])
async def get_work_order_stages(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.PRODUCTION_READ))
):
    """Get stages for work order."""
    result = await db.execute(
        select(ProductionStage)
        .where(
            ProductionStage.work_order_id == order_id,
            ProductionStage.tenant_id == current_user.tenant_id,
        )
        .order_by(ProductionStage.stage_number)
    )
    return result.scalars().all()


@router.post("/{order_id}/stages", response_model=ProductionStageResponse)
async def create_work_order_stage(
    order_id: int,
    stage_data: ProductionStageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.PRODUCTION_CREATE))
):
    """Create production stage for work order."""
    # Verify work order exists
    wo_result = await db.execute(
        select(WorkOrder).where(
            WorkOrder.id == order_id,
            WorkOrder.tenant_id == current_user.tenant_id,
        )
    )
    work_order = wo_result.scalar_one_or_none()
    
    if not work_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work order not found"
        )
    
    stage = ProductionStage(
        **stage_data.model_dump(),
        tenant_id=current_user.tenant_id,
    )
    
    db.add(stage)
    await db.flush()
    await db.refresh(stage)
    
    return stage


@router.put("/stages/{stage_id}", response_model=ProductionStageResponse)
async def update_production_stage(
    stage_id: int,
    stage_data: ProductionStageUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.PRODUCTION_UPDATE))
):
    """Update production stage."""
    result = await db.execute(
        select(ProductionStage).where(
            ProductionStage.id == stage_id,
            ProductionStage.tenant_id == current_user.tenant_id,
        )
    )
    stage = result.scalar_one_or_none()
    
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Production stage not found"
        )
    
    update_data = stage_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(stage, field, value)
    
    await db.flush()
    await db.refresh(stage)
    
    return stage


@router.post("/stages/{stage_id}/start", response_model=ProductionStageResponse)
async def start_production_stage(
    stage_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.PRODUCTION_UPDATE))
):
    """Start production stage."""
    result = await db.execute(
        select(ProductionStage).where(
            ProductionStage.id == stage_id,
            ProductionStage.tenant_id == current_user.tenant_id,
        )
    )
    stage = result.scalar_one_or_none()
    
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Production stage not found"
        )
    
    stage.status = ProductionStageStatus.IN_PROGRESS
    stage.started_at = datetime.utcnow()
    
    # Add timeline event
    timeline_event = StageTimelineEvent(
        stage_id=stage_id,
        event_type="started",
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
    )
    db.add(timeline_event)
    
    await db.flush()
    await db.refresh(stage)
    
    return stage


@router.post("/stages/{stage_id}/complete", response_model=ProductionStageResponse)
async def complete_production_stage(
    stage_id: int,
    quantity_good: float = 0,
    quantity_scrap: float = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.PRODUCTION_UPDATE))
):
    """Complete production stage."""
    result = await db.execute(
        select(ProductionStage).where(
            ProductionStage.id == stage_id,
            ProductionStage.tenant_id == current_user.tenant_id,
        )
    )
    stage = result.scalar_one_or_none()
    
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Production stage not found"
        )
    
    stage.quantity_good = quantity_good
    stage.quantity_scrap = quantity_scrap
    stage.completed_at = datetime.utcnow()
    
    if stage.quality_checked:
        stage.status = ProductionStageStatus.QUALITY_PASSED
    else:
        stage.status = ProductionStageStatus.COMPLETED
    
    # Add timeline event
    timeline_event = StageTimelineEvent(
        stage_id=stage_id,
        event_type="completed",
        event_data=json.dumps({"quantity_good": quantity_good, "quantity_scrap": quantity_scrap}),
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
    )
    db.add(timeline_event)
    
    await db.flush()
    await db.refresh(stage)
    
    return stage


@router.post("/stages/{stage_id}/quality-check", response_model=ProductionStageResponse)
async def quality_check_stage(
    stage_id: int,
    passed: bool,
    notes: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.QUALITY_UPDATE))
):
    """Perform quality check on production stage."""
    result = await db.execute(
        select(ProductionStage).where(
            ProductionStage.id == stage_id,
            ProductionStage.tenant_id == current_user.tenant_id,
        )
    )
    stage = result.scalar_one_or_none()
    
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Production stage not found"
        )
    
    stage.quality_checked = True
    stage.quality_checked_by = current_user.id
    stage.quality_checked_at = datetime.utcnow()
    stage.quality_notes = notes
    
    if passed:
        stage.status = ProductionStageStatus.QUALITY_PASSED
    else:
        stage.status = ProductionStageStatus.QUALITY_FAILED
    
    # Add timeline event
    timeline_event = StageTimelineEvent(
        stage_id=stage_id,
        event_type="quality_check",
        event_data=json.dumps({"passed": passed, "notes": notes}),
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
    )
    db.add(timeline_event)
    
    await db.flush()
    await db.refresh(stage)
    
    return stage


# Stage Type Definitions endpoints
@router.get("/stage-types", response_model=List[StageTypeDefinitionResponse])
async def get_stage_types(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.PRODUCTION_READ))
):
    """Get all stage type definitions."""
    result = await db.execute(
        select(StageTypeDefinition).where(
            StageTypeDefinition.is_active == True,
            StageTypeDefinition.tenant_id == current_user.tenant_id,
        )
    )
    return result.scalars().all()


@router.post("/stage-types", response_model=StageTypeDefinitionResponse)
async def create_stage_type(
    stage_type_data: StageTypeDefinitionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.PRODUCTION_CREATE))
):
    """Create stage type definition."""
    stage_type = StageTypeDefinition(
        **stage_type_data.model_dump(),
        tenant_id=current_user.tenant_id,
    )
    db.add(stage_type)
    await db.flush()
    await db.refresh(stage_type)
    return stage_type


# Work Order Comments endpoints
@router.get("/{order_id}/comments", response_model=List[WorkOrderCommentResponse])
async def get_work_order_comments(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.PRODUCTION_READ))
):
    """Get comments for work order."""
    result = await db.execute(
        select(WorkOrderComment)
        .where(
            WorkOrderComment.work_order_id == order_id,
            WorkOrderComment.tenant_id == current_user.tenant_id,
        )
        .order_by(WorkOrderComment.created_at)
    )
    return result.scalars().all()


@router.post("/{order_id}/comments", response_model=WorkOrderCommentResponse)
async def add_work_order_comment(
    order_id: int,
    comment_data: WorkOrderCommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.PRODUCTION_UPDATE))
):
    """Add comment to work order."""
    comment = WorkOrderComment(
        **comment_data.model_dump(),
        author_id=current_user.id,
        tenant_id=current_user.tenant_id,
    )
    db.add(comment)
    await db.flush()
    await db.refresh(comment)
    return comment


# Stage Timeline endpoints
@router.get("/stages/{stage_id}/timeline", response_model=List[StageTimelineEventResponse])
async def get_stage_timeline(
    stage_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.PRODUCTION_READ))
):
    """Get timeline events for production stage."""
    result = await db.execute(
        select(StageTimelineEvent)
        .where(
            StageTimelineEvent.stage_id == stage_id,
            StageTimelineEvent.tenant_id == current_user.tenant_id,
        )
        .order_by(StageTimelineEvent.timestamp)
    )
    return result.scalars().all()
