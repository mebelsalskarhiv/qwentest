"""Equipment and OEE management endpoints."""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.core.database import get_db
from app.services.auth import require_permission, get_current_user
from app.models.user import User
from app.models.enums import Permission
from app.models.equipment import (
    Equipment, OEELog, MaintenanceRequest, SensorData, DowntimeEvent,
    EquipmentStatus, MaintenanceType
)
from pydantic import BaseModel, Field
from decimal import Decimal

router = APIRouter()


# === Pydantic Schemas ===

class EquipmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    category: Optional[str] = None
    type: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    location: Optional[str] = None
    station_id: Optional[int] = None
    specifications: Optional[dict] = None
    max_speed: Optional[float] = None
    rated_power: Optional[float] = None
    availability_target: float = 90.0
    performance_target: float = 95.0
    quality_target: float = 99.0
    shift_duration_hours: float = 8.0
    maintenance_interval_hours: Optional[int] = None


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    type: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    location: Optional[str] = None
    station_id: Optional[int] = None
    specifications: Optional[dict] = None
    max_speed: Optional[float] = None
    rated_power: Optional[float] = None
    availability_target: Optional[float] = None
    performance_target: Optional[float] = None
    quality_target: Optional[float] = None
    shift_duration_hours: Optional[float] = None
    maintenance_interval_hours: Optional[int] = None
    status: Optional[EquipmentStatus] = None
    is_active: Optional[bool] = None
    last_maintenance_date: Optional[datetime] = None
    next_maintenance_date: Optional[datetime] = None
    total_operating_hours: Optional[float] = None


class EquipmentResponse(EquipmentBase):
    id: int
    tenant_id: int
    status: EquipmentStatus
    is_active: bool
    last_maintenance_date: Optional[datetime] = None
    next_maintenance_date: Optional[datetime] = None
    total_operating_hours: float = 0.0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class OEELogBase(BaseModel):
    equipment_id: int
    start_time: datetime
    end_time: datetime
    shift_number: Optional[int] = None
    shift_name: Optional[str] = None
    planned_production_time: float
    operating_time: float
    downtime_minutes: float = 0.0
    downtime_reasons: Optional[dict] = None
    ideal_cycle_time: float
    total_count: int = 0
    good_count: int = 0
    rejected_count: int = 0
    run_rate: Optional[float] = None


class OEELogCreate(OEELogBase):
    pass


class OEELogUpdate(BaseModel):
    operating_time: Optional[float] = None
    downtime_minutes: Optional[float] = None
    downtime_reasons: Optional[dict] = None
    total_count: Optional[int] = None
    good_count: Optional[int] = None
    rejected_count: Optional[int] = None
    run_rate: Optional[float] = None


class OEELogResponse(OEELogBase):
    id: int
    tenant_id: int
    availability: float = 0.0
    performance: float = 0.0
    quality: float = 0.0
    oee_score: float = 0.0
    is_calculated: bool = False
    calculated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MaintenanceRequestBase(BaseModel):
    equipment_id: int
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    maintenance_type: MaintenanceType
    priority: int = Field(default=3, ge=1, le=5)
    assigned_to: Optional[int] = None


class MaintenanceRequestCreate(MaintenanceRequestBase):
    pass


class MaintenanceRequestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    maintenance_type: Optional[MaintenanceType] = None
    priority: Optional[int] = None
    assigned_to: Optional[int] = None
    status: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    work_performed: Optional[str] = None
    parts_used: Optional[dict] = None
    labor_hours: Optional[float] = None
    downtime_minutes: Optional[float] = None
    failure_mode: Optional[str] = None
    root_cause: Optional[str] = None
    corrective_actions: Optional[str] = None
    labor_cost: Optional[Decimal] = None
    parts_cost: Optional[Decimal] = None


class MaintenanceRequestResponse(MaintenanceRequestBase):
    id: int
    tenant_id: int
    request_number: str
    status: str
    opened_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    work_performed: Optional[str] = None
    parts_used: Optional[dict] = None
    labor_hours: float = 0.0
    downtime_minutes: float = 0.0
    failure_mode: Optional[str] = None
    root_cause: Optional[str] = None
    corrective_actions: Optional[str] = None
    labor_cost: Decimal = Decimal('0.00')
    parts_cost: Decimal = Decimal('0.00')
    total_cost: Decimal = Decimal('0.00')
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SensorDataBase(BaseModel):
    equipment_id: int
    sensor_name: str = Field(..., min_length=1, max_length=100)
    sensor_type: Optional[str] = None
    unit_of_measure: Optional[str] = None
    value: float
    quality: str = "GOOD"
    context: Optional[dict] = None


class SensorDataCreate(SensorDataBase):
    pass


class SensorDataResponse(SensorDataBase):
    id: int
    tenant_id: int
    recorded_at: datetime
    
    class Config:
        from_attributes = True


class OEESummary(BaseModel):
    equipment_id: int
    equipment_name: str
    equipment_code: str
    date: datetime
    availability: float
    performance: float
    quality: float
    oee_score: float
    shift_count: int


# === Equipment Endpoints ===

@router.get("/equipment", response_model=List[EquipmentResponse], tags=["Equipment"])
async def list_equipment(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    status: Optional[EquipmentStatus] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.EQUIPMENT_READ))
):
    """List all equipment for the current tenant with optional filters."""
    query = db.query(Equipment).filter(Equipment.tenant_id == current_user.tenant_id)
    
    if category:
        query = query.filter(Equipment.category == category)
    if status:
        query = query.filter(Equipment.status == status)
    if is_active is not None:
        query = query.filter(Equipment.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()


@router.post("/equipment", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED, tags=["Equipment"])
async def create_equipment(
    equipment_data: EquipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.EQUIPMENT_CREATE))
):
    """Create a new equipment record."""
    # Check for duplicate code
    existing = db.query(Equipment).filter(
        Equipment.code == equipment_data.code,
        Equipment.tenant_id == current_user.tenant_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Equipment code already exists")
    
    equipment = Equipment(
        tenant_id=current_user.tenant_id,
        **equipment_data.model_dump(),
        status=EquipmentStatus.OFFLINE
    )
    db.add(equipment)
    db.commit()
    db.refresh(equipment)
    return equipment


@router.get("/equipment/{equipment_id}", response_model=EquipmentResponse, tags=["Equipment"])
async def get_equipment(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.EQUIPMENT_READ))
):
    """Get a specific equipment by ID."""
    equipment = db.query(Equipment).filter(
        Equipment.id == equipment_id,
        Equipment.tenant_id == current_user.tenant_id
    ).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment


@router.put("/equipment/{equipment_id}", response_model=EquipmentResponse, tags=["Equipment"])
async def update_equipment(
    equipment_id: int,
    equipment_data: EquipmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.EQUIPMENT_UPDATE))
):
    """Update an equipment record."""
    equipment = db.query(Equipment).filter(
        Equipment.id == equipment_id,
        Equipment.tenant_id == current_user.tenant_id
    ).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    update_data = equipment_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(equipment, field, value)
    
    db.commit()
    db.refresh(equipment)
    return equipment


@router.delete("/equipment/{equipment_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Equipment"])
async def delete_equipment(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.EQUIPMENT_DELETE))
):
    """Delete an equipment record."""
    equipment = db.query(Equipment).filter(
        Equipment.id == equipment_id,
        Equipment.tenant_id == current_user.tenant_id
    ).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    db.delete(equipment)
    db.commit()
    return None


@router.patch("/equipment/{equipment_id}/status", response_model=EquipmentResponse, tags=["Equipment"])
async def update_equipment_status(
    equipment_id: int,
    new_status: EquipmentStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.EQUIPMENT_UPDATE))
):
    """Update equipment status (e.g., RUNNING, DOWN, MAINTENANCE)."""
    equipment = db.query(Equipment).filter(
        Equipment.id == equipment_id,
        Equipment.tenant_id == current_user.tenant_id
    ).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    equipment.status = new_status
    db.commit()
    db.refresh(equipment)
    return equipment


# === OEE Log Endpoints ===

@router.get("/oee/logs", response_model=List[OEELogResponse], tags=["OEE"])
async def list_oee_logs(
    equipment_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.OEE_READ))
):
    """List OEE logs with optional filters."""
    query = db.query(OEELog).filter(OEELog.tenant_id == current_user.tenant_id)
    
    if equipment_id:
        query = query.filter(OEELog.equipment_id == equipment_id)
    if start_date:
        query = query.filter(OEELog.start_time >= start_date)
    if end_date:
        query = query.filter(OEELog.end_time <= end_date)
    
    return query.order_by(OEELog.start_time.desc()).offset(skip).limit(limit).all()


@router.post("/oee/logs", response_model=OEELogResponse, status_code=status.HTTP_201_CREATED, tags=["OEE"])
async def create_oee_log(
    oee_data: OEELogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.OEE_MANAGE))
):
    """Create a new OEE log entry."""
    # Verify equipment exists and belongs to tenant
    equipment = db.query(Equipment).filter(
        Equipment.id == oee_data.equipment_id,
        Equipment.tenant_id == current_user.tenant_id
    ).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    oee_log = OEELog(
        tenant_id=current_user.tenant_id,
        **oee_data.model_dump()
    )
    # Calculate OEE automatically
    oee_log.calculate_oee()
    
    db.add(oee_log)
    db.commit()
    db.refresh(oee_log)
    return oee_log


@router.get("/oee/logs/{log_id}", response_model=OEELogResponse, tags=["OEE"])
async def get_oee_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.OEE_READ))
):
    """Get a specific OEE log by ID."""
    oee_log = db.query(OEELog).filter(
        OEELog.id == log_id,
        OEELog.tenant_id == current_user.tenant_id
    ).first()
    if not oee_log:
        raise HTTPException(status_code=404, detail="OEE log not found")
    return oee_log


@router.put("/oee/logs/{log_id}", response_model=OEELogResponse, tags=["OEE"])
async def update_oee_log(
    log_id: int,
    oee_data: OEELogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.OEE_MANAGE))
):
    """Update an OEE log and recalculate metrics."""
    oee_log = db.query(OEELog).filter(
        OEELog.id == log_id,
        OEELog.tenant_id == current_user.tenant_id
    ).first()
    if not oee_log:
        raise HTTPException(status_code=404, detail="OEE log not found")
    
    update_data = oee_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(oee_log, field, value)
    
    # Recalculate OEE
    oee_log.calculate_oee()
    
    db.commit()
    db.refresh(oee_log)
    return oee_log


@router.get("/oee/summary", response_model=List[OEESummary], tags=["OEE"])
async def get_oee_summary(
    start_date: datetime,
    end_date: datetime,
    equipment_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.OEE_READ))
):
    """Get OEE summary for equipment within a date range."""
    query = db.query(OEELog).filter(
        OEELog.tenant_id == current_user.tenant_id,
        OEELog.start_time >= start_date,
        OEELog.end_time <= end_date
    )
    
    if equipment_id:
        query = query.filter(OEELog.equipment_id == equipment_id)
    
    logs = query.all()
    
    # Aggregate by equipment and date
    summary = {}
    for log in logs:
        key = (log.equipment_id, log.start_time.date())
        if key not in summary:
            summary[key] = {
                'availability': [],
                'performance': [],
                'quality': [],
                'oee_score': [],
                'shift_count': 0
            }
        summary[key]['availability'].append(log.availability)
        summary[key]['performance'].append(log.performance)
        summary[key]['quality'].append(log.quality)
        summary[key]['oee_score'].append(log.oee_score)
        summary[key]['shift_count'] += 1
    
    result = []
    for (equip_id, date), values in summary.items():
        equip = db.query(Equipment).filter(Equipment.id == equip_id).first()
        result.append(OEESummary(
            equipment_id=equip_id,
            equipment_name=equip.name if equip else "Unknown",
            equipment_code=equip.code if equip else "Unknown",
            date=date,
            availability=sum(values['availability']) / len(values['availability']) * 100,
            performance=sum(values['performance']) / len(values['performance']) * 100,
            quality=sum(values['quality']) / len(values['quality']) * 100,
            oee_score=sum(values['oee_score']) / len(values['oee_score']) * 100,
            shift_count=values['shift_count']
        ))
    
    return result


# === Maintenance Request Endpoints ===

@router.get("/maintenance/requests", response_model=List[MaintenanceRequestResponse], tags=["Maintenance"])
async def list_maintenance_requests(
    equipment_id: Optional[int] = None,
    status: Optional[str] = None,
    priority: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.MAINTENANCE_READ))
):
    """List maintenance requests with optional filters."""
    query = db.query(MaintenanceRequest).filter(
        MaintenanceRequest.tenant_id == current_user.tenant_id
    )
    
    if equipment_id:
        query = query.filter(MaintenanceRequest.equipment_id == equipment_id)
    if status:
        query = query.filter(MaintenanceRequest.status == status)
    if priority:
        query = query.filter(MaintenanceRequest.priority == priority)
    
    return query.order_by(MaintenanceRequest.priority.asc(), MaintenanceRequest.opened_at.desc()).offset(skip).limit(limit).all()


@router.post("/maintenance/requests", response_model=MaintenanceRequestResponse, status_code=status.HTTP_201_CREATED, tags=["Maintenance"])
async def create_maintenance_request(
    request_data: MaintenanceRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.MAINTENANCE_CREATE))
):
    """Create a new maintenance request."""
    # Verify equipment exists
    equipment = db.query(Equipment).filter(
        Equipment.id == request_data.equipment_id,
        Equipment.tenant_id == current_user.tenant_id
    ).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    # Generate request number
    count = db.query(MaintenanceRequest).filter(
        MaintenanceRequest.tenant_id == current_user.tenant_id
    ).count()
    request_number = f"MR-{datetime.utcnow().year}-{count + 1:04d}"
    
    request = MaintenanceRequest(
        tenant_id=current_user.tenant_id,
        request_number=request_number,
        created_by=current_user.id,
        **request_data.model_dump()
    )
    
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


@router.get("/maintenance/requests/{request_id}", response_model=MaintenanceRequestResponse, tags=["Maintenance"])
async def get_maintenance_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.MAINTENANCE_READ))
):
    """Get a specific maintenance request by ID."""
    request = db.query(MaintenanceRequest).filter(
        MaintenanceRequest.id == request_id,
        MaintenanceRequest.tenant_id == current_user.tenant_id
    ).first()
    if not request:
        raise HTTPException(status_code=404, detail="Maintenance request not found")
    return request


@router.put("/maintenance/requests/{request_id}", response_model=MaintenanceRequestResponse, tags=["Maintenance"])
async def update_maintenance_request(
    request_id: int,
    request_data: MaintenanceRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.MAINTENANCE_UPDATE))
):
    """Update a maintenance request."""
    request = db.query(MaintenanceRequest).filter(
        MaintenanceRequest.id == request_id,
        MaintenanceRequest.tenant_id == current_user.tenant_id
    ).first()
    if not request:
        raise HTTPException(status_code=404, detail="Maintenance request not found")
    
    update_data = request_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(request, field, value)
    
    # Auto-calculate total cost
    if request.labor_cost and request.parts_cost:
        request.total_cost = request.labor_cost + request.parts_cost
    
    db.commit()
    db.refresh(request)
    return request


# === Sensor Data Endpoints ===

@router.get("/sensor-data", response_model=List[SensorDataResponse], tags=["Telemetry"])
async def list_sensor_data(
    equipment_id: Optional[int] = None,
    sensor_name: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=10000),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.TELEMETRY_READ))
):
    """List sensor telemetry data with optional filters."""
    query = db.query(SensorData).filter(SensorData.tenant_id == current_user.tenant_id)
    
    if equipment_id:
        query = query.filter(SensorData.equipment_id == equipment_id)
    if sensor_name:
        query = query.filter(SensorData.sensor_name == sensor_name)
    if start_time:
        query = query.filter(SensorData.recorded_at >= start_time)
    if end_time:
        query = query.filter(SensorData.recorded_at <= end_time)
    
    return query.order_by(SensorData.recorded_at.desc()).offset(skip).limit(limit).all()


@router.post("/sensor-data", response_model=SensorDataResponse, status_code=status.HTTP_201_CREATED, tags=["Telemetry"])
async def create_sensor_data(
    sensor_data: SensorDataCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.TELEMETRY_WRITE))
):
    """Record new sensor telemetry data."""
    # Verify equipment exists
    equipment = db.query(Equipment).filter(
        Equipment.id == sensor_data.equipment_id,
        Equipment.tenant_id == current_user.tenant_id
    ).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    data = SensorData(
        tenant_id=current_user.tenant_id,
        **sensor_data.model_dump(),
        recorded_at=datetime.utcnow()
    )
    
    db.add(data)
    db.commit()
    db.refresh(data)
    return data


@router.post("/sensor-data/bulk", status_code=status.HTTP_201_CREATED, tags=["Telemetry"])
async def create_bulk_sensor_data(
    sensor_data_list: List[SensorDataCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.TELEMETRY_WRITE))
):
    """Record multiple sensor telemetry data points in bulk."""
    equipment_ids = set(d.equipment_id for d in sensor_data_list)
    
    # Verify all equipment exists
    equipment_query = db.query(Equipment.id).filter(
        Equipment.id.in_(equipment_ids),
        Equipment.tenant_id == current_user.tenant_id
    )
    valid_ids = {e.id for e in equipment_query.all()}
    
    if not valid_ids:
        raise HTTPException(status_code=404, detail="No valid equipment found")
    
    records = []
    for data in sensor_data_list:
        if data.equipment_id in valid_ids:
            record = SensorData(
                tenant_id=current_user.tenant_id,
                **data.model_dump(),
                recorded_at=datetime.utcnow()
            )
            records.append(record)
    
    db.add_all(records)
    db.commit()
    
    return {"status": "success", "records_created": len(records)}
