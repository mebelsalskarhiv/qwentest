from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
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


class WorkOrderStatus(str, Enum):
    """Work order status for detailed tracking."""
    PENDING = "pending"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class StageType(str, Enum):
    """Predefined stage types for manufacturing processes."""
    CUTTING = "cutting"
    BENDING = "bending"
    WELDING = "welding"
    ASSEMBLY = "assembly"
    PAINTING = "painting"
    QUALITY_CONTROL = "quality_control"
    PACKAGING = "packaging"
    CUSTOM = "custom"


class ProductionStageStatus(str, Enum):
    """Status for individual production stages."""
    NOT_STARTED = "not_started"
    SETUP = "setup"
    IN_PROGRESS = "in_progress"
    WAITING_QUALITY = "waiting_quality"
    QUALITY_PASSED = "quality_passed"
    QUALITY_FAILED = "quality_failed"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class ProductionOrder(Base):
    """Production order model."""
    __tablename__ = "production_orders"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
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
    work_orders = relationship("WorkOrder", back_populates="production_order", cascade="all, delete-orphan")


class WorkOrder(Base):
    """Work order model - executable unit of work derived from a production order."""
    __tablename__ = "work_orders"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
    production_order_id = Column(Integer, ForeignKey("production_orders.id"), nullable=False)
    work_order_number = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(WorkOrderStatus), default=WorkOrderStatus.PENDING, nullable=False)
    priority = Column(SQLEnum(ProductionOrderPriority), default=ProductionOrderPriority.MEDIUM)
    work_center_id = Column(Integer, ForeignKey("work_centers.id"))
    assigned_to = Column(Integer, ForeignKey("users.id"))  # Operator assigned
    scheduled_start = Column(DateTime(timezone=True))
    scheduled_end = Column(DateTime(timezone=True))
    actual_start = Column(DateTime(timezone=True))
    actual_end = Column(DateTime(timezone=True))
    quantity_planned = Column(Float, nullable=False)
    quantity_completed = Column(Float, default=0)
    quantity_scrap = Column(Float, default=0)
    notes = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    production_order = relationship("ProductionOrder", back_populates="work_orders")
    work_center = relationship("WorkCenter", back_populates="work_orders")
    assigned_user = relationship("User", back_populates="work_orders")
    stages = relationship("ProductionStage", back_populates="work_order", cascade="all, delete-orphan")
    comments = relationship("WorkOrderComment", back_populates="work_order", cascade="all, delete-orphan")


class ProductionStage(Base):
    """Production stage model - individual step within a work order with tracking."""
    __tablename__ = "production_stages"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)
    stage_type = Column(SQLEnum(StageType), nullable=False)
    stage_number = Column(Integer, nullable=False)  # Sequence number
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(ProductionStageStatus), default=ProductionStageStatus.NOT_STARTED, nullable=False)
    work_center_id = Column(Integer, ForeignKey("work_centers.id"))
    planned_duration = Column(Float)  # Hours
    actual_duration = Column(Float)  # Hours
    setup_time = Column(Float)  # Hours
    run_time_per_unit = Column(Float)  # Hours per unit
    quantity_good = Column(Float, default=0)
    quantity_scrap = Column(Float, default=0)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    operator_id = Column(Integer, ForeignKey("users.id"))
    quality_checked = Column(Boolean, default=False)
    quality_checked_by = Column(Integer, ForeignKey("users.id"))
    quality_checked_at = Column(DateTime(timezone=True))
    quality_notes = Column(Text)
    dependencies = Column(Text)  # JSON array of stage IDs that must complete first
    is_critical = Column(Boolean, default=False)  # Critical path indicator
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    work_order = relationship("WorkOrder", back_populates="stages")
    work_center = relationship("WorkCenter", back_populates="stages")
    operator = relationship("User", foreign_keys=[operator_id], back_populates="operated_stages")
    quality_checker = relationship("User", foreign_keys=[quality_checked_by], back_populates="checked_stages")
    timeline_events = relationship("StageTimelineEvent", back_populates="stage", cascade="all, delete-orphan")


class StageTypeDefinition(Base):
    """Master definition of stage types with standard parameters."""
    __tablename__ = "stage_type_definitions"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
    stage_type = Column(SQLEnum(StageType), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    default_duration = Column(Float)  # Default planned duration in hours
    requires_quality_check = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class WorkOrderComment(Base):
    """Comments and notes on work orders."""
    __tablename__ = "work_order_comments"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment_text = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=True)  # Internal vs customer-visible
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    work_order = relationship("WorkOrder", back_populates="comments")
    author = relationship("User", back_populates="comments")


class StageTimelineEvent(Base):
    """Timeline events for production stages (audit trail)."""
    __tablename__ = "stage_timeline_events"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
    stage_id = Column(Integer, ForeignKey("production_stages.id"), nullable=False)
    event_type = Column(String(50), nullable=False)  # e.g., "started", "completed", "paused", "quality_check"
    event_data = Column(Text)  # JSON data for the event
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    stage = relationship("ProductionStage", back_populates="timeline_events")


class Product(Base):
    """Product model for manufactured items."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
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
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
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
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
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
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
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
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
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
