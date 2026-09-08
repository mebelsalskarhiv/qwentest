"""Equipment and OEE models for Phase 4."""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List
from enum import Enum
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, 
    Enum as SQLEnum, Float, Boolean, Text, JSON, UniqueConstraint,
    Index, Numeric, func
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.models.base import Base
from app.models.enums import Permission


class EquipmentStatus(str, Enum):
    """Equipment status values."""
    OFFLINE = "offline"
    IDLE = "idle"
    RUNNING = "running"
    SETUP = "setup"
    PAUSED = "paused"
    DOWN = "down"
    MAINTENANCE = "maintenance"


class MaintenanceType(str, Enum):
    """Types of maintenance."""
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    EMERGENCY = "emergency"
    PREDICTIVE = "predictive"
    INSPECTION = "inspection"


class Equipment(Base):
    """
    Equipment/Station registry with capabilities and specifications.
    Extends the concept of 'Station' with detailed technical data.
    """
    __tablename__ = "equipment"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Basic info
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    
    # Classification
    category = Column(String(50))  # e.g., "CNC", "Press", "Robot"
    type = Column(String(50))      # e.g., "Milling Machine", "Hydraulic Press"
    manufacturer = Column(String(100))
    model = Column(String(100))
    serial_number = Column(String(100))
    
    # Location
    location = Column(String(200))  # Shop floor location
    station_id = Column(Integer, ForeignKey("stations.id"))  # Link to existing Station
    
    # Status tracking
    status = Column(SQLEnum(EquipmentStatus), default=EquipmentStatus.OFFLINE)
    is_active = Column(Boolean, default=True)
    
    # Technical specs
    specifications = Column(JSON)  # Flexible storage for tech specs
    max_speed = Column(Float)  # Max operational speed (units/hour)
    rated_power = Column(Float)  # kW
    
    # OEE Configuration
    availability_target = Column(Float, default=90.0)  # Target %
    performance_target = Column(Float, default=95.0)   # Target %
    quality_target = Column(Float, default=99.0)       # Target %
    shift_duration_hours = Column(Float, default=8.0)
    
    # Maintenance
    last_maintenance_date = Column(DateTime)
    next_maintenance_date = Column(DateTime)
    maintenance_interval_hours = Column(Integer)  # Operating hours between maintenance
    total_operating_hours = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    oee_logs: Mapped[List["OEELog"]] = relationship("OEELog", back_populates="equipment", cascade="all, delete-orphan")
    maintenance_requests: Mapped[List["MaintenanceRequest"]] = relationship(
        "MaintenanceRequest", back_populates="equipment", cascade="all, delete-orphan"
    )
    sensor_data: Mapped[List["SensorData"]] = relationship(
        "SensorData", back_populates="equipment", cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index('ix_equipment_tenant_status', 'tenant_id', 'status'),
        Index('ix_equipment_category', 'tenant_id', 'category'),
    )


class OEELog(Base):
    """
    OEE (Overall Equipment Effectiveness) calculation log.
    Records availability, performance, and quality metrics per shift/batch.
    """
    __tablename__ = "oee_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False, index=True)
    
    # Time period
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    shift_number = Column(Integer)  # 1, 2, 3
    shift_name = Column(String(50))  # e.g., "Morning", "Afternoon"
    
    # Availability metrics
    planned_production_time = Column(Float, nullable=False)  # minutes
    operating_time = Column(Float, nullable=False)  # minutes
    downtime_minutes = Column(Float, default=0.0)
    downtime_reasons = Column(JSON)  # [{"reason": "Breakdown", "duration": 30}, ...]
    
    # Performance metrics
    ideal_cycle_time = Column(Float, nullable=False)  # minutes per unit
    total_count = Column(Integer, default=0)  # Total units produced
    good_count = Column(Integer, default=0)    # Good units
    rejected_count = Column(Integer, default=0)  # Rejected units
    run_rate = Column(Float)  # Actual units per minute
    
    # Calculated OEE components (stored for historical analysis)
    availability = Column(Float, default=0.0)  # Operating Time / Planned Production Time
    performance = Column(Float, default=0.0)   # (Total Count * Ideal Cycle Time) / Operating Time
    quality = Column(Float, default=0.0)       # Good Count / Total Count
    oee_score = Column(Float, default=0.0)     # Availability * Performance * Quality
    
    # Status
    is_calculated = Column(Boolean, default=False)
    calculated_at = Column(DateTime)
    
    # Relationships
    equipment: Mapped["Equipment"] = relationship("Equipment", back_populates="oee_logs")
    
    __table_args__ = (
        Index('ix_oee_equipment_period', 'equipment_id', 'start_time', 'end_time'),
        Index('ix_oee_tenant_date', 'tenant_id', 'start_time'),
    )
    
    def calculate_oee(self):
        """Calculate OEE metrics."""
        if self.planned_production_time > 0:
            self.availability = self.operating_time / self.planned_production_time
        else:
            self.availability = 0.0
            
        if self.operating_time > 0 and self.ideal_cycle_time > 0:
            ideal_output = self.operating_time / self.ideal_cycle_time
            self.performance = min(self.total_count / ideal_output, 1.0) if ideal_output > 0 else 0.0
        else:
            self.performance = 0.0
            
        if self.total_count > 0:
            self.quality = self.good_count / self.total_count
        else:
            self.quality = 0.0
            
        self.oee_score = self.availability * self.performance * self.quality
        self.is_calculated = True
        self.calculated_at = datetime.utcnow()
        
        return {
            "availability": round(self.availability * 100, 2),
            "performance": round(self.performance * 100, 2),
            "quality": round(self.quality * 100, 2),
            "oee": round(self.oee_score * 100, 2)
        }


class MaintenanceRequest(Base):
    """
    Maintenance work requests (corrective, preventive, emergency).
    """
    __tablename__ = "maintenance_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    assigned_to = Column(Integer, ForeignKey("users.id"))  # Technician
    
    request_number = Column(String(50), unique=True, index=True)  # Auto-generated: MR-2024-001
    title = Column(String(200), nullable=False)
    description = Column(Text)
    maintenance_type = Column(SQLEnum(MaintenanceType), nullable=False)
    priority = Column(Integer, default=3)  # 1=Critical, 5=Low
    
    # Status workflow
    status = Column(String(50), default="open")  # open, in_progress, waiting_parts, completed, cancelled
    opened_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Work details
    work_performed = Column(Text)
    parts_used = Column(JSON)  # [{"part_id": 1, "quantity": 2}, ...]
    labor_hours = Column(Float, default=0.0)
    downtime_minutes = Column(Float, default=0.0)
    
    # Root cause analysis (for corrective maintenance)
    failure_mode = Column(String(200))
    root_cause = Column(Text)
    corrective_actions = Column(Text)
    
    # Cost tracking
    labor_cost = Column(Numeric(10, 2), default=0.0)
    parts_cost = Column(Numeric(10, 2), default=0.0)
    total_cost = Column(Numeric(10, 2), default=0.0)
    
    # Attachments
    attachments = Column(JSON)  # URLs to photos, documents
    
    # Relationships
    equipment: Mapped["Equipment"] = relationship("Equipment", back_populates="maintenance_requests")
    creator = relationship("User", foreign_keys=[created_by])
    assignee = relationship("User", foreign_keys=[assigned_to])
    
    __table_args__ = (
        Index('ix_maint_equipment_status', 'equipment_id', 'status'),
        Index('ix_maint_tenant_priority', 'tenant_id', 'priority'),
    )


class SensorData(Base):
    """
    Real-time sensor telemetry data from equipment.
    Supports MTConnect/OPC-UA data ingestion.
    """
    __tablename__ = "sensor_data"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False, index=True)
    
    # Sensor identification
    sensor_name = Column(String(100), nullable=False)  # e.g., "SpindleLoad", "Temperature"
    sensor_type = Column(String(50))  # e.g., "temperature", "pressure", "vibration"
    unit_of_measure = Column(String(20))  # e.g., "°C", "bar", "mm/s"
    
    # Data value
    value = Column(Float, nullable=False)
    quality = Column(String(20), default="GOOD")  # GOOD, BAD, UNCERTAIN (OPC-UA style)
    
    # Context
    context = Column(JSON)  # Additional metadata
    
    # Indexed for time-series queries
    recorded_at = Column(DateTime, nullable=False, index=True, default=datetime.utcnow)
    
    # Relationships
    equipment: Mapped["Equipment"] = relationship("Equipment", back_populates="sensor_data")
    
    __table_args__ = (
        Index('ix_sensor_equipment_time', 'equipment_id', 'recorded_at'),
        Index('ix_sensor_tenant_time', 'tenant_id', 'recorded_at'),
    )


class DowntimeEvent(Base):
    """
    Detailed downtime event tracking for availability calculations.
    Links to OEE logs but provides granular event data.
    """
    __tablename__ = "downtime_events"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False, index=True)
    oee_log_id = Column(Integer, ForeignKey("oee_logs.id"))
    reported_by = Column(Integer, ForeignKey("users.id"))
    
    # Timing
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    duration_minutes = Column(Float)
    
    # Classification
    category = Column(String(50))  # Unplanned, Planned, Break, Changeover
    reason_code = Column(String(50))  # Standardized reason codes
    reason_description = Column(Text)
    
    # Impact
    impact_level = Column(String(20))  # Minor, Major, Critical
    affects_oee = Column(Boolean, default=True)
    
    # Resolution
    resolution_notes = Column(Text)
    resolved_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    equipment: Mapped["Equipment"] = relationship("Equipment")
    oee_log: Mapped["OEELog"] = relationship("OEELog")
    reporter = relationship("User", foreign_keys=[reported_by])
    resolver = relationship("User", foreign_keys=[resolved_by])
    
    __table_args__ = (
        Index('ix_downtime_equipment_time', 'equipment_id', 'start_time'),
    )
