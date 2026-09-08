from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta, time as dt_time
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_

from app.core.database import get_db
from app.models.inventory import ResourceCalendar, CalendarException, WorkShift, ResourceCalendarType
from app.models.production import WorkOrder
from app.models.user import User
from app.models.enums import Permission, DayOfWeek
from app.services.auth import get_current_user, require_permission

router = APIRouter()


@router.get("/calendar/availability", response_model=Dict[str, Any])
async def get_resource_availability(
    resource_type: str = Query(..., description="Type of resource: work_center, user"),
    resource_id: int = Query(..., description="ID of the resource"),
    start_date: datetime = Query(..., description="Start date for availability check"),
    end_date: datetime = Query(..., description="End date for availability check"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.PLANNING_READ)),
) -> Dict[str, Any]:
    """
    Get resource availability for a given time period.
    Returns available hours considering calendars, shifts, and exceptions.
    """
    # Map resource type to enum
    if resource_type == "work_center":
        calendar_resource_type = ResourceCalendarType.WORK_CENTER
    elif resource_type == "user":
        calendar_resource_type = ResourceCalendarType.EMPLOYEE
    else:
        raise HTTPException(status_code=400, detail="Invalid resource type")
    
    # Get regular calendar
    calendars = db.query(ResourceCalendar).filter(
        and_(
            ResourceCalendar.tenant_id == current_user.tenant_id,
            ResourceCalendar.resource_type == calendar_resource_type,
            ResourceCalendar.resource_id == resource_id,
            ResourceCalendar.is_active == True
        )
    ).all()
    
    # Get exceptions (holidays, overtime, maintenance)
    exceptions = db.query(CalendarException).filter(
        and_(
            CalendarException.tenant_id == current_user.tenant_id,
            CalendarException.resource_type == calendar_resource_type,
            CalendarException.resource_id == resource_id,
            CalendarException.exception_date >= start_date.date(),
            CalendarException.exception_date <= end_date.date()
        )
    ).all()
    
    # Calculate availability
    availability = []
    current_date = start_date.date()
    end = end_date.date()
    
    while current_date <= end:
        day_of_week = DayOfWeek(current_date.strftime("%A").lower())
        
        # Check if it's an exception day
        exception = next((e for e in exceptions if e.exception_date.date() == current_date), None)
        
        if exception:
            # Exception day - use exception capacity
            if exception.capacity_hours is not None:
                available_hours = exception.capacity_hours
            else:
                available_hours = 0  # Holiday or closed day
        else:
            # Regular day - use calendar
            calendar = next((c for c in calendars if c.day_of_week == day_of_week and c.is_working_day), None)
            if calendar:
                available_hours = calendar.capacity_hours
            else:
                available_hours = 0  # Non-working day
        
        availability.append({
            "date": current_date.isoformat(),
            "available_hours": available_hours,
            "is_working_day": available_hours > 0
        })
        
        current_date += timedelta(days=1)
    
    return {
        "resource_type": resource_type,
        "resource_id": resource_id,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "availability": availability,
        "total_available_hours": sum(day["available_hours"] for day in availability)
    }


@router.post("/calendar/schedule", response_model=Dict[str, Any])
async def calculate_schedule(
    work_order_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(require_permission(Permission.PLANNING_CREATE)),
) -> Dict[str, Any]:
    """
    Calculate optimal schedule for a work order based on resource availability.
    Considers work center calendars, stage dependencies, and durations.
    """
    work_order = db.query(models.WorkOrder).filter(
        and_(
            models.WorkOrder.id == work_order_id,
            models.WorkOrder.tenant_id == current_user.tenant_id
        )
    ).options(
        joinedload(models.WorkOrder.stages),
        joinedload(models.WorkOrder.work_center)
    ).first()
    
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    if not work_order.work_center:
        raise HTTPException(status_code=400, detail="Work order has no assigned work center")
    
    # Get stages sorted by sequence
    stages = sorted(work_order.stages, key=lambda s: s.stage_number)
    
    if not stages:
        raise HTTPException(status_code=400, detail="Work order has no stages defined")
    
    # Get work center calendar
    calendars = db.query(models.ResourceCalendar).filter(
        and_(
            models.ResourceCalendar.tenant_id == current_user.tenant_id,
            models.ResourceCalendar.resource_type == models.ResourceCalendarType.WORK_CENTER,
            models.ResourceCalendar.resource_id == work_order.work_center_id,
            models.ResourceCalendar.is_active == True
        )
    ).all()
    
    # Calculate schedule starting from now or scheduled_start
    current_time = work_order.scheduled_start or datetime.now()
    schedule = []
    
    for stage in stages:
        # Find working slot for this stage
        planned_duration = stage.planned_duration or 1.0  # Default 1 hour
        
        # Simple scheduling: add duration to current time
        # TODO: Implement proper calendar-based scheduling
        stage_start = current_time
        stage_end = stage_start + timedelta(hours=planned_duration)
        
        schedule.append({
            "stage_id": stage.id,
            "stage_name": stage.name,
            "stage_number": stage.stage_number,
            "scheduled_start": stage_start.isoformat(),
            "scheduled_end": stage_end.isoformat(),
            "duration_hours": planned_duration
        })
        
        # Move to next stage
        current_time = stage_end
    
    return {
        "work_order_id": work_order_id,
        "work_order_number": work_order.work_order_number,
        "work_center_id": work_order.work_center_id,
        "schedule": schedule,
        "total_duration_hours": sum(item["duration_hours"] for item in schedule),
        "estimated_completion": schedule[-1]["scheduled_end"] if schedule else None
    }


@router.get("/holidays", response_model=List[Dict[str, Any]])
async def get_holidays(
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(require_permission(Permission.CALENDAR_READ)),
) -> List[Dict[str, Any]]:
    """Get company holidays."""
    query = db.query(models.Holiday).filter(
        models.Holiday.tenant_id == current_user.tenant_id,
        models.Holiday.is_active == True
    )
    
    if start_date:
        query = query.filter(models.Holiday.date >= start_date)
    if end_date:
        query = query.filter(models.Holiday.date <= end_date)
    
    holidays = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": h.id,
            "name": h.name,
            "date": h.date.isoformat() if h.date else None,
            "is_paid": h.is_paid,
            "description": h.description
        }
        for h in holidays
    ]


@router.post("/holidays", response_model=Dict[str, Any])
async def create_holiday(
    *,
    name: str,
    date: datetime,
    is_paid: bool = True,
    description: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(require_permission(Permission.CALENDAR_CREATE)),
) -> Dict[str, Any]:
    """Create a new holiday."""
    holiday = models.Holiday(
        tenant_id=current_user.tenant_id,
        name=name,
        date=date,
        is_paid=is_paid,
        description=description
    )
    
    db.add(holiday)
    db.commit()
    db.refresh(holiday)
    
    return {
        "id": holiday.id,
        "name": holiday.name,
        "date": holiday.date.isoformat() if holiday.date else None,
        "is_paid": holiday.is_paid,
        "description": holiday.description
    }


@router.get("/work-shifts", response_model=List[Dict[str, Any]])
async def get_work_shifts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(require_permission(Permission.CALENDAR_READ)),
) -> List[Dict[str, Any]]:
    """Get all work shifts for the tenant."""
    shifts = db.query(models.WorkShift).filter(
        and_(
            models.WorkShift.tenant_id == current_user.tenant_id,
            models.WorkShift.is_active == True
        )
    ).offset(skip).limit(limit).all()
    
    return [
        {
            "id": s.id,
            "name": s.name,
            "code": s.code,
            "description": s.description,
            "start_time": s.start_time.isoformat() if s.start_time else None,
            "end_time": s.end_time.isoformat() if s.end_time else None,
            "monday": s.monday,
            "tuesday": s.tuesday,
            "wednesday": s.wednesday,
            "thursday": s.thursday,
            "friday": s.friday,
            "saturday": s.saturday,
            "sunday": s.sunday,
            "hours_per_day": s.hours_per_day
        }
        for s in shifts
    ]


@router.post("/work-shifts", response_model=Dict[str, Any])
async def create_work_shift(
    *,
    name: str,
    code: str,
    start_time: str,  # HH:MM format
    end_time: str,  # HH:MM format
    hours_per_day: float,
    description: Optional[str] = None,
    monday: bool = True,
    tuesday: bool = True,
    wednesday: bool = True,
    thursday: bool = True,
    friday: bool = True,
    saturday: bool = False,
    sunday: bool = False,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(require_permission(Permission.CALENDAR_CREATE)),
) -> Dict[str, Any]:
    """Create a new work shift."""
    from datetime import time as dt_time
    
    # Parse time strings
    start_parts = start_time.split(":")
    end_parts = end_time.split(":")
    
    shift = models.WorkShift(
        tenant_id=current_user.tenant_id,
        name=name,
        code=code,
        description=description,
        start_time=dt_time(int(start_parts[0]), int(start_parts[1])),
        end_time=dt_time(int(end_parts[0]), int(end_parts[1])),
        hours_per_day=hours_per_day,
        monday=monday,
        tuesday=tuesday,
        wednesday=wednesday,
        thursday=thursday,
        friday=friday,
        saturday=saturday,
        sunday=sunday
    )
    
    db.add(shift)
    db.commit()
    db.refresh(shift)
    
    return {
        "id": shift.id,
        "name": shift.name,
        "code": shift.code,
        "message": "Work shift created successfully"
    }
