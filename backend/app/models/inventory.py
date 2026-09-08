from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float, Boolean, Enum as SQLEnum, UniqueConstraint, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
from enum import Enum


class InventoryItemType(str, Enum):
    RAW_MATERIAL = "raw_material"
    COMPONENT = "component"
    SEMI_FINISHED = "semi_finished"
    FINISHED_GOOD = "finished_good"
    TOOL = "tool"
    CONSUMABLE = "consumable"


class MaterialReservationStatus(str, Enum):
    """Status of material reservation."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PARTIALLY_ALLOCATED = "partially_allocated"
    ALLOCATED = "allocated"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class ResourceCalendarType(str, Enum):
    """Type of resource calendar."""
    WORK_CENTER = "work_center"
    STATION = "station"
    EMPLOYEE = "employee"
    TOOL = "tool"


class DayOfWeek(str, Enum):
    """Days of the week."""
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class InventoryItem(Base):
    """Inventory item model."""
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
    sku = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    item_type = Column(SQLEnum(InventoryItemType), nullable=False)
    category_id = Column(Integer, ForeignKey("inventory_categories.id"))
    unit_of_measure = Column(String(50), nullable=False)  # pcs, kg, m, etc.
    min_stock_level = Column(Float, default=0)
    max_stock_level = Column(Float)
    current_stock = Column(Float, default=0)
    reserved_stock = Column(Float, default=0)
    available_stock = Column(Float, default=0)
    reorder_point = Column(Float)
    reorder_quantity = Column(Float)
    cost_price = Column(Float)
    selling_price = Column(Float)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    location = Column(String(255))  # Warehouse location
    barcode = Column(String(100), unique=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    category = relationship("InventoryCategory", back_populates="items")
    stock_movements = relationship("StockMovement", back_populates="item")
    supplier = relationship("Supplier", back_populates="items")


class InventoryCategory(Base):
    """Inventory category for grouping items."""
    __tablename__ = "inventory_categories"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("inventory_categories.id"))
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    items = relationship("InventoryItem", back_populates="category")
    parent = relationship("InventoryCategory", remote_side=[id], backref="children")


class StockMovement(Base):
    """Stock movement tracking."""
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    movement_type = Column(String(50), nullable=False)  # IN, OUT, ADJUSTMENT, TRANSFER
    quantity = Column(Float, nullable=False)
    reference_type = Column(String(50))  # PRODUCTION_ORDER, PURCHASE_ORDER, etc.
    reference_id = Column(Integer)
    from_location = Column(String(255))
    to_location = Column(String(255))
    notes = Column(Text)
    performed_by = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    item = relationship("InventoryItem", back_populates="stock_movements")


class Supplier(Base):
    """Supplier model."""
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, index=True)
    contact_person = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    tax_id = Column(String(50))
    payment_terms = Column(String(255))
    lead_time_days = Column(Integer)
    rating = Column(Float)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    items = relationship("InventoryItem", back_populates="supplier")


class MaterialReservation(Base):
    """Material reservation for production orders and work orders."""
    __tablename__ = "material_reservations"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
    reservation_number = Column(String(50), unique=True, index=True, nullable=False)
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=True)
    production_order_id = Column(Integer, ForeignKey("production_orders.id"), nullable=True)
    quantity_requested = Column(Float, nullable=False)
    quantity_allocated = Column(Float, default=0)
    quantity_issued = Column(Float, default=0)
    unit_of_measure = Column(String(50), nullable=False)
    status = Column(SQLEnum(MaterialReservationStatus), default=MaterialReservationStatus.PENDING, nullable=False)
    requested_by = Column(Integer, ForeignKey("users.id"))
    allocated_by = Column(Integer, ForeignKey("users.id"))
    issued_by = Column(Integer, ForeignKey("users.id"))
    requested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    allocated_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    item = relationship("InventoryItem", back_populates="reservations")
    work_order = relationship("WorkOrder", back_populates="material_reservations")
    production_order = relationship("ProductionOrder", back_populates="material_reservations")
    requested_by_user = relationship("User", foreign_keys=[requested_by], back_populates="requested_reservations")
    allocated_by_user = relationship("User", foreign_keys=[allocated_by], back_populates="allocated_reservations")


class ResourceCalendar(Base):
    """Resource calendar for work centers, stations, and employees."""
    __tablename__ = "resource_calendars"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
    resource_type = Column(SQLEnum(ResourceCalendarType), nullable=False)
    resource_id = Column(Integer, nullable=False)  # work_center_id, station_id, employee_id
    day_of_week = Column(SQLEnum(DayOfWeek), nullable=False)
    start_time = Column(String(8), nullable=False)  # HH:MM format
    end_time = Column(String(8), nullable=False)  # HH:MM format
    is_working_day = Column(Boolean, default=True, nullable=False)
    capacity_hours = Column(Float, default=8.0)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('tenant_id', 'resource_type', 'resource_id', 'day_of_week', name='uq_resource_calendar'),
    )


class CalendarException(Base):
    """Exceptions to regular calendar (holidays, overtime, maintenance)."""
    __tablename__ = "calendar_exceptions"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
    resource_type = Column(SQLEnum(ResourceCalendarType), nullable=False)
    resource_id = Column(Integer, nullable=False)
    exception_date = Column(DateTime(timezone=True), nullable=False)
    exception_type = Column(String(50), nullable=False)  # holiday, overtime, maintenance
    start_time = Column(String(8))  # HH:MM format, optional
    end_time = Column(String(8))  # HH:MM format, optional
    capacity_hours = Column(Float)  # Override capacity
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    creator = relationship("User", back_populates="created_exceptions")


# Add relationships to InventoryItem
InventoryItem.reservations = relationship("MaterialReservation", back_populates="item")


class WorkShift(Base):
    """Standard work shift definitions."""
    __tablename__ = "work_shifts"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
    
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(Text)
    
    # Shift times
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    
    # Working days
    monday = Column(Boolean, default=True)
    tuesday = Column(Boolean, default=True)
    wednesday = Column(Boolean, default=True)
    thursday = Column(Boolean, default=True)
    friday = Column(Boolean, default=True)
    saturday = Column(Boolean, default=False)
    sunday = Column(Boolean, default=False)
    
    # Capacity
    hours_per_day = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Holiday(Base):
    """Company holidays affecting all resources."""
    __tablename__ = "holidays"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
    
    name = Column(String(255), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    is_paid = Column(Boolean, default=True)
    description = Column(Text)
    
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
