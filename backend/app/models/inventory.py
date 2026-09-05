from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float, Boolean, Enum as SQLEnum
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


class InventoryItem(Base):
    """Inventory item model."""
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
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
