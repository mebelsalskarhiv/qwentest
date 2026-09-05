from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.inventory import InventoryItemType


class InventoryItemBase(BaseModel):
    sku: str = Field(..., max_length=100)
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    item_type: InventoryItemType
    unit_of_measure: str = Field(..., max_length=50)
    min_stock_level: float = 0
    max_stock_level: Optional[float] = None
    reorder_point: Optional[float] = None
    reorder_quantity: Optional[float] = None
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    location: Optional[str] = None
    barcode: Optional[str] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    item_type: Optional[InventoryItemType] = None
    unit_of_measure: Optional[str] = None
    min_stock_level: Optional[float] = None
    max_stock_level: Optional[float] = None
    current_stock: Optional[float] = None
    reserved_stock: Optional[float] = None
    available_stock: Optional[float] = None
    reorder_point: Optional[float] = None
    reorder_quantity: Optional[float] = None
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    location: Optional[str] = None
    barcode: Optional[str] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    is_active: Optional[bool] = None


class InventoryItemResponse(InventoryItemBase):
    id: int
    current_stock: float = 0
    reserved_stock: float = 0
    available_stock: float = 0
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StockMovementBase(BaseModel):
    movement_type: str
    quantity: float
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    notes: Optional[str] = None


class StockMovementCreate(StockMovementBase):
    item_id: int


class StockMovementResponse(StockMovementBase):
    id: int
    item_id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class InventoryCategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None


class InventoryCategoryCreate(InventoryCategoryBase):
    pass


class InventoryCategoryResponse(InventoryCategoryBase):
    id: int
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


class SupplierBase(BaseModel):
    name: str = Field(..., max_length=255)
    code: str = Field(..., max_length=50)
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_id: Optional[str] = None
    payment_terms: Optional[str] = None
    lead_time_days: Optional[int] = None
    rating: Optional[float] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_id: Optional[str] = None
    payment_terms: Optional[str] = None
    lead_time_days: Optional[int] = None
    rating: Optional[float] = None
    is_active: Optional[bool] = None


class SupplierResponse(SupplierBase):
    id: int
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True
