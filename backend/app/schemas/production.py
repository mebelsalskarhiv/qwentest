from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.production import (
    ProductionOrderStatus, ProductionOrderPriority,
    WorkOrderStatus, StageType, ProductionStageStatus
)


class ProductionOrderBase(BaseModel):
    order_number: str = Field(..., max_length=50)
    product_id: int
    quantity_planned: float
    priority: ProductionOrderPriority = ProductionOrderPriority.MEDIUM
    work_center_id: Optional[int] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    notes: Optional[str] = None


class ProductionOrderCreate(ProductionOrderBase):
    pass


class ProductionOrderUpdate(BaseModel):
    quantity_planned: Optional[float] = None
    status: Optional[ProductionOrderStatus] = None
    priority: Optional[ProductionOrderPriority] = None
    work_center_id: Optional[int] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ProductionOrderResponse(ProductionOrderBase):
    id: int
    quantity_completed: float = 0
    quantity_scrap: float = 0
    status: ProductionOrderStatus = ProductionOrderStatus.DRAFT
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    created_by: Optional[int] = None
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    sku: str = Field(..., max_length=100)
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    unit_of_measure: str = Field(..., max_length=50)
    standard_cost: Optional[float] = None
    selling_price: Optional[float] = None
    lead_time_days: Optional[int] = None
    reorder_point: Optional[float] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    unit_of_measure: Optional[str] = None
    standard_cost: Optional[float] = None
    selling_price: Optional[float] = None
    lead_time_days: Optional[int] = None
    reorder_point: Optional[float] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: int
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WorkCenterBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    capacity: Optional[float] = None
    efficiency: float = 1.0
    cost_per_hour: Optional[float] = None


class WorkCenterCreate(WorkCenterBase):
    pass


class WorkCenterUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    capacity: Optional[float] = None
    efficiency: Optional[float] = None
    cost_per_hour: Optional[float] = None
    is_active: Optional[bool] = None


class WorkCenterResponse(WorkCenterBase):
    id: int
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


class ProductionOperationBase(BaseModel):
    production_order_id: int
    operation_number: int
    work_center_id: Optional[int] = None
    description: Optional[str] = None
    planned_duration: Optional[float] = None
    setup_time: Optional[float] = None
    run_time: Optional[float] = None


class ProductionOperationCreate(ProductionOperationBase):
    pass


class ProductionOperationUpdate(BaseModel):
    work_center_id: Optional[int] = None
    description: Optional[str] = None
    planned_duration: Optional[float] = None
    actual_duration: Optional[float] = None
    setup_time: Optional[float] = None
    run_time: Optional[float] = None
    quantity_good: Optional[float] = None
    quantity_scrap: Optional[float] = None
    status: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    operator_id: Optional[int] = None
    notes: Optional[str] = None


class ProductionOperationResponse(ProductionOperationBase):
    id: int
    actual_duration: Optional[float] = None
    quantity_good: float = 0
    quantity_scrap: float = 0
    status: str = "pending"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    operator_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BillOfMaterialBase(BaseModel):
    product_id: int
    component_id: int
    quantity: float
    unit_of_measure: str = Field(..., max_length=50)
    scrap_percentage: float = 0


class BillOfMaterialCreate(BillOfMaterialBase):
    pass


class BillOfMaterialResponse(BillOfMaterialBase):
    id: int
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


# Work Order Schemas
class WorkOrderBase(BaseModel):
    production_order_id: int
    work_order_number: str = Field(..., max_length=50)
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    priority: ProductionOrderPriority = ProductionOrderPriority.MEDIUM
    work_center_id: Optional[int] = None
    assigned_to: Optional[int] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    quantity_planned: float
    notes: Optional[str] = None


class WorkOrderCreate(WorkOrderBase):
    pass


class WorkOrderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[WorkOrderStatus] = None
    priority: Optional[ProductionOrderPriority] = None
    work_center_id: Optional[int] = None
    assigned_to: Optional[int] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    quantity_completed: Optional[float] = None
    quantity_scrap: Optional[float] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class WorkOrderResponse(WorkOrderBase):
    id: int
    status: WorkOrderStatus = WorkOrderStatus.PENDING
    quantity_completed: float = 0
    quantity_scrap: float = 0
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Production Stage Schemas
class ProductionStageBase(BaseModel):
    work_order_id: int
    stage_type: StageType
    stage_number: int
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    work_center_id: Optional[int] = None
    planned_duration: Optional[float] = None
    setup_time: Optional[float] = None
    run_time_per_unit: Optional[float] = None
    dependencies: Optional[str] = None  # JSON array
    is_critical: bool = False
    notes: Optional[str] = None


class ProductionStageCreate(ProductionStageBase):
    pass


class ProductionStageUpdate(BaseModel):
    stage_type: Optional[StageType] = None
    name: Optional[str] = None
    description: Optional[str] = None
    work_center_id: Optional[int] = None
    planned_duration: Optional[float] = None
    actual_duration: Optional[float] = None
    setup_time: Optional[float] = None
    run_time_per_unit: Optional[float] = None
    quantity_good: Optional[float] = None
    quantity_scrap: Optional[float] = None
    status: Optional[ProductionStageStatus] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    operator_id: Optional[int] = None
    quality_checked: Optional[bool] = None
    quality_checked_by: Optional[int] = None
    quality_notes: Optional[str] = None
    dependencies: Optional[str] = None
    is_critical: Optional[bool] = None
    notes: Optional[str] = None


class ProductionStageResponse(ProductionStageBase):
    id: int
    status: ProductionStageStatus = ProductionStageStatus.NOT_STARTED
    actual_duration: Optional[float] = None
    quantity_good: float = 0
    quantity_scrap: float = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    operator_id: Optional[int] = None
    quality_checked: bool = False
    quality_checked_by: Optional[int] = None
    quality_checked_at: Optional[datetime] = None
    quality_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Stage Type Definition Schemas
class StageTypeDefinitionBase(BaseModel):
    stage_type: StageType
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    default_duration: Optional[float] = None
    requires_quality_check: bool = False


class StageTypeDefinitionCreate(StageTypeDefinitionBase):
    pass


class StageTypeDefinitionResponse(StageTypeDefinitionBase):
    id: int
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


# Work Order Comment Schemas
class WorkOrderCommentBase(BaseModel):
    work_order_id: int
    comment_text: str
    is_internal: bool = True


class WorkOrderCommentCreate(WorkOrderCommentBase):
    pass


class WorkOrderCommentResponse(WorkOrderCommentBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Stage Timeline Event Schemas
class StageTimelineEventBase(BaseModel):
    stage_id: int
    event_type: str = Field(..., max_length=50)
    event_data: Optional[str] = None  # JSON
    user_id: Optional[int] = None


class StageTimelineEventCreate(StageTimelineEventBase):
    pass


class StageTimelineEventResponse(StageTimelineEventBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
