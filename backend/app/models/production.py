from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from enum import Enum


class ProductionOrderStatus(str, Enum):
    DRAFT = "draft"
    PLANNED = "planned"
    RELEASED = "released"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProductionOrderPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ProductionOrder(Base):
    """Production order model."""
    __tablename__ = "production_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity_planned = Column(Float, nullable=False)
    quantity_completed = Column(Float, default=0)
    quantity_scrap = Column(Float, default=0)
    status = Column(SQLEnum(ProductionOrderStatus), default=ProductionOrderStatus.DRAFT, nullable=False)
    priority = Column(SQLEnum(ProductionOrderPriority), default=ProductionOrderPriority.MEDIUM)
    work_center_id = Column(Integer, ForeignKey("work_centers.id"))
    scheduled_start = Column(DateTime(timezone=True))
    scheduled_end = Column(DateTime(timezone=True))
    actual_start = Column(DateTime(timezone=True))
    actual_end = Column(DateTime(timezone=True))
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    product = relationship("Product", back_populates="production_orders")
    work_center = relationship("WorkCenter", back_populates="production_orders")
    created_by_user = relationship("User", back_populates="production_orders")
    operations = relationship("ProductionOperation", back_populates="production_order")
    material_consumptions = relationship("MaterialConsumption", back_populates="production_order")


class Product(Base):
    """Product model for manufactured items."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    unit_of_measure = Column(String(50), nullable=False)
    standard_cost = Column(Float)
    selling_price = Column(Float)
    lead_time_days = Column(Integer)
    reorder_point = Column(Float)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    production_orders = relationship("ProductionOrder", back_populates="product")
    bill_of_materials = relationship("BillOfMaterial", back_populates="product")


class WorkCenter(Base):
    """Work center model for production resources."""
    __tablename__ = "work_centers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    capacity = Column(Float)  # Hours per day
    efficiency = Column(Float, default=1.0)
    cost_per_hour = Column(Float)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    production_orders = relationship("ProductionOrder", back_populates="work_center")
    operations = relationship("ProductionOperation", back_populates="work_center")


class ProductionOperation(Base):
    """Production operation model."""
    __tablename__ = "production_operations"

    id = Column(Integer, primary_key=True, index=True)
    production_order_id = Column(Integer, ForeignKey("production_orders.id"), nullable=False)
    operation_number = Column(Integer, nullable=False)
    work_center_id = Column(Integer, ForeignKey("work_centers.id"))
    description = Column(Text)
    planned_duration = Column(Float)  # Hours
    actual_duration = Column(Float)
    setup_time = Column(Float)  # Hours
    run_time = Column(Float)  # Hours per unit
    quantity_good = Column(Float, default=0)
    quantity_scrap = Column(Float, default=0)
    status = Column(String(50), default="pending")
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    operator_id = Column(Integer, ForeignKey("users.id"))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    production_order = relationship("ProductionOrder", back_populates="operations")
    work_center = relationship("WorkCenter", back_populates="operations")


class BillOfMaterial(Base):
    """Bill of Material model."""
    __tablename__ = "bill_of_materials"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    component_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_of_measure = Column(String(50), nullable=False)
    scrap_percentage = Column(Float, default=0)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    product = relationship("Product", back_populates="bill_of_materials")


class MaterialConsumption(Base):
    """Material consumption tracking."""
    __tablename__ = "material_consumptions"

    id = Column(Integer, primary_key=True, index=True)
    production_order_id = Column(Integer, ForeignKey("production_orders.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    quantity_planned = Column(Float, nullable=False)
    quantity_consumed = Column(Float, default=0)
    quantity_returned = Column(Float, default=0)
    unit_of_measure = Column(String(50), nullable=False)
    notes = Column(Text)
    consumed_by = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    production_order = relationship("ProductionOrder", back_populates="material_consumptions")
