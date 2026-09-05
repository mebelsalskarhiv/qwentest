from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.production import ProductionOrderStatus, ProductionOrderPriority


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
