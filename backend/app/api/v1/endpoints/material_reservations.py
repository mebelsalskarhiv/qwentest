"""Material Reservations and Resource Calendars API."""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.core.database import get_db
from app.services.auth import require_permission
from app.models.inventory import MaterialReservationStatus, ResourceCalendarType, DayOfWeek
from app.models.enums import Permission
from datetime import datetime, timedelta

router = APIRouter(prefix="/planning", tags=["Planning"])


# ============== Material Reservations ==============

@router.get("/material-reservations", response_model=List[dict])
async def read_material_reservations(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_permission(Permission.MATERIAL_RESERVATION_READ)),
    skip: int = 0,
    limit: int = 100,
    status_filter: MaterialReservationStatus = None,
    work_order_id: int = None,
    production_order_id: int = None,
):
    """
    Retrieve material reservations.
    - **status_filter**: Filter by reservation status
    - **work_order_id**: Filter by work order
    - **production_order_id**: Filter by production order
    """
    query = select(models.MaterialReservation).where(
        models.MaterialReservation.tenant_id == current_user.tenant_id
    )
    
    if status_filter:
        query = query.where(models.MaterialReservation.status == status_filter)
    if work_order_id:
        query = query.where(models.MaterialReservation.work_order_id == work_order_id)
    if production_order_id:
        query = query.where(models.MaterialReservation.production_order_id == production_order_id)
    
    result = await db.execute(query.offset(skip).limit(limit))
    reservations = result.scalars().all()
    return reservations


@router.get("/material-reservations/{reservation_id}", response_model=dict)
async def read_material_reservation(
    reservation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_permission(Permission.MATERIAL_RESERVATION_READ)),
):
    """Retrieve a specific material reservation by ID."""
    reservation = db.query(models.MaterialReservation).filter(
        and_(
            models.MaterialReservation.id == reservation_id,
            models.MaterialReservation.tenant_id == current_user.tenant_id
        )
    ).first()
    
    if not reservation:
        raise HTTPException(status_code=404, detail="Material reservation not found")
    
    return reservation


@router.post("/material-reservations", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_material_reservation(
    *,
    db: AsyncSession = Depends(get_db),
    reservation_in: dict,
    current_user: models.User = Depends(require_permission(Permission.MATERIAL_RESERVATION_CREATE)),
):
    """
    Create a new material reservation.
    Required fields: item_id, quantity_requested, unit_of_measure
    Optional: work_order_id, production_order_id, notes
    """
    # Generate reservation number
    reservation_number = f"RES-{datetime.now().strftime('%Y%m%d')}-{reservation_in.get('item_id', 0)}"
    
    # Check item exists and belongs to tenant
    item = db.query(models.InventoryItem).filter(
        and_(
            models.InventoryItem.id == reservation_in["item_id"],
            models.InventoryItem.tenant_id == current_user.tenant_id
        )
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    # Validate work_order_id or production_order_id if provided
    if reservation_in.get("work_order_id"):
        work_order = db.query(models.WorkOrder).filter(
            and_(
                models.WorkOrder.id == reservation_in["work_order_id"],
                models.WorkOrder.tenant_id == current_user.tenant_id
            )
        ).first()
        if not work_order:
            raise HTTPException(status_code=404, detail="Work order not found")
    
    if reservation_in.get("production_order_id"):
        prod_order = db.query(models.ProductionOrder).filter(
            and_(
                models.ProductionOrder.id == reservation_in["production_order_id"],
                models.ProductionOrder.tenant_id == current_user.tenant_id
            )
        ).first()
        if not prod_order:
            raise HTTPException(status_code=404, detail="Production order not found")
    
    reservation = models.MaterialReservation(
        reservation_number=reservation_number,
        tenant_id=current_user.tenant_id,
        item_id=reservation_in["item_id"],
        work_order_id=reservation_in.get("work_order_id"),
        production_order_id=reservation_in.get("production_order_id"),
        quantity_requested=reservation_in["quantity_requested"],
        quantity_allocated=0,
        quantity_issued=0,
        unit_of_measure=reservation_in["unit_of_measure"],
        status=MaterialReservationStatus.PENDING,
        requested_by=current_user.id,
        notes=reservation_in.get("notes"),
        expires_at=datetime.now() + timedelta(days=7),  # Default 7 days expiry
    )
    
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    
    return reservation


@router.put("/material-reservations/{reservation_id}/allocate", response_model=dict)
async def allocate_material_reservation(
    reservation_id: int,
    *,
    db: AsyncSession = Depends(get_db),
    allocation_data: dict,
    current_user: models.User = Depends(require_permission(Permission.MATERIAL_RESERVATION_UPDATE)),
):
    """
    Allocate materials for a reservation.
    Updates quantity_allocated and status.
    """
    reservation = db.query(models.MaterialReservation).filter(
        and_(
            models.MaterialReservation.id == reservation_id,
            models.MaterialReservation.tenant_id == current_user.tenant_id
        )
    ).first()
    
    if not reservation:
        raise HTTPException(status_code=404, detail="Material reservation not found")
    
    if reservation.status == MaterialReservationStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Cannot allocate cancelled reservation")
    
    quantity_to_allocate = allocation_data.get("quantity_allocated", reservation.quantity_requested)
    
    # Update reservation
    reservation.quantity_allocated = min(quantity_to_allocate, reservation.quantity_requested)
    reservation.allocated_by = current_user.id
    reservation.allocated_at = datetime.now()
    
    # Update status
    if reservation.quantity_allocated >= reservation.quantity_requested:
        reservation.status = MaterialReservationStatus.ALLOCATED
    elif reservation.quantity_allocated > 0:
        reservation.status = MaterialReservationStatus.PARTIALLY_ALLOCATED
    
    # Update inventory item reserved_stock
    item = db.query(models.InventoryItem).get(reservation.item_id)
    if item:
        item.reserved_stock = (item.reserved_stock or 0) + reservation.quantity_allocated
        item.available_stock = item.current_stock - item.reserved_stock
    
    db.commit()
    db.refresh(reservation)
    
    return reservation


@router.put("/material-reservations/{reservation_id}/issue", response_model=dict)
async def issue_material_reservation(
    reservation_id: int,
    *,
    db: AsyncSession = Depends(get_db),
    issue_data: dict,
    current_user: models.User = Depends(require_permission(Permission.MATERIAL_RESERVATION_UPDATE)),
):
    """
    Issue materials for a reservation (remove from inventory).
    Creates a StockMovement record.
    """
    reservation = db.query(models.MaterialReservation).filter(
        and_(
            models.MaterialReservation.id == reservation_id,
            models.MaterialReservation.tenant_id == current_user.tenant_id
        )
    ).first()
    
    if not reservation:
        raise HTTPException(status_code=404, detail="Material reservation not found")
    
    if reservation.status not in [MaterialReservationStatus.ALLOCATED, MaterialReservationStatus.PARTIALLY_ALLOCATED]:
        raise HTTPException(status_code=400, detail="Can only issue allocated reservations")
    
    quantity_to_issue = issue_data.get("quantity_issued", reservation.quantity_allocated - reservation.quantity_issued)
    
    # Update reservation
    reservation.quantity_issued += quantity_to_issue
    reservation.issued_by = current_user.id
    
    if reservation.quantity_issued >= reservation.quantity_allocated:
        reservation.status = MaterialReservationStatus.CONFIRMED
    
    # Update inventory
    item = db.query(models.InventoryItem).get(reservation.item_id)
    if item:
        item.current_stock -= quantity_to_issue
        item.reserved_stock -= quantity_to_issue
        item.available_stock = item.current_stock - item.reserved_stock
        
        # Create stock movement
        movement = models.StockMovement(
            tenant_id=current_user.tenant_id,
            item_id=item.id,
            movement_type="OUT",
            quantity=quantity_to_issue,
            reference_type="MATERIAL_RESERVATION",
            reference_id=reservation.id,
            notes=f"Issued for reservation {reservation.reservation_number}",
            performed_by=current_user.id,
        )
        db.add(movement)
    
    db.commit()
    db.refresh(reservation)
    
    return reservation


@router.put("/material-reservations/{reservation_id}/cancel", response_model=dict)
async def cancel_material_reservation(
    reservation_id: int,
    *,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_permission(Permission.MATERIAL_RESERVATION_DELETE)),
):
    """Cancel a material reservation."""
    reservation = db.query(models.MaterialReservation).filter(
        and_(
            models.MaterialReservation.id == reservation_id,
            models.MaterialReservation.tenant_id == current_user.tenant_id
        )
    ).first()
    
    if not reservation:
        raise HTTPException(status_code=404, detail="Material reservation not found")
    
    if reservation.status == MaterialReservationStatus.CONFIRMED:
        raise HTTPException(status_code=400, detail="Cannot cancel confirmed reservation")
    
    # Release reserved stock
    if reservation.quantity_allocated > reservation.quantity_issued:
        item = db.query(models.InventoryItem).get(reservation.item_id)
        if item:
            released_qty = reservation.quantity_allocated - reservation.quantity_issued
            item.reserved_stock -= released_qty
            item.available_stock = item.current_stock - item.reserved_stock
    
    reservation.status = MaterialReservationStatus.CANCELLED
    db.commit()
    db.refresh(reservation)
    
    return reservation


@router.delete("/material-reservations/{reservation_id}")
async def delete_material_reservation(
    reservation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_permission(Permission.MATERIAL_RESERVATION_DELETE)),
):
    """Delete a material reservation."""
    reservation = db.query(models.MaterialReservation).filter(
        and_(
            models.MaterialReservation.id == reservation_id,
            models.MaterialReservation.tenant_id == current_user.tenant_id
        )
    ).first()
    
    if not reservation:
        raise HTTPException(status_code=404, detail="Material reservation not found")
    
    if reservation.status == MaterialReservationStatus.CONFIRMED:
        raise HTTPException(status_code=400, detail="Cannot delete confirmed reservation")
    
    db.delete(reservation)
    db.commit()
    
    return {"detail": "Material reservation deleted"}


# ============== Resource Calendars ==============

@router.get("/resource-calendars", response_model=List[dict])
async def read_resource_calendars(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_permission(Permission.PRODUCTION_READ)),
    resource_type: ResourceCalendarType = None,
    resource_id: int = None,
):
    """
    Retrieve resource calendars.
    - **resource_type**: Filter by type (work_center, station, employee)
    - **resource_id**: Filter by specific resource ID
    """
    query = db.query(models.ResourceCalendar).filter(
        models.ResourceCalendar.tenant_id == current_user.tenant_id
    )
    
    if resource_type:
        query = query.filter(models.ResourceCalendar.resource_type == resource_type)
    if resource_id is not None:
        query = query.filter(models.ResourceCalendar.resource_id == resource_id)
    
    calendars = query.all()
    return calendars


@router.post("/resource-calendars", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_resource_calendar(
    *,
    db: AsyncSession = Depends(get_db),
    calendar_in: dict,
    current_user: models.User = Depends(require_permission(Permission.PRODUCTION_CREATE)),
):
    """
    Create a resource calendar entry.
    Required: resource_type, resource_id, day_of_week, start_time, end_time
    """
    # Check for existing calendar
    existing = db.query(models.ResourceCalendar).filter(
        and_(
            models.ResourceCalendar.tenant_id == current_user.tenant_id,
            models.ResourceCalendar.resource_type == calendar_in["resource_type"],
            models.ResourceCalendar.resource_id == calendar_in["resource_id"],
            models.ResourceCalendar.day_of_week == calendar_in["day_of_week"]
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Calendar already exists for {calendar_in['resource_type']} {calendar_in['resource_id']} on {calendar_in['day_of_week']}"
        )
    
    calendar = models.ResourceCalendar(
        tenant_id=current_user.tenant_id,
        resource_type=calendar_in["resource_type"],
        resource_id=calendar_in["resource_id"],
        day_of_week=calendar_in["day_of_week"],
        start_time=calendar_in["start_time"],
        end_time=calendar_in["end_time"],
        is_working_day=calendar_in.get("is_working_day", True),
        capacity_hours=calendar_in.get("capacity_hours", 8.0),
    )
    
    db.add(calendar)
    db.commit()
    db.refresh(calendar)
    
    return calendar


@router.put("/resource-calendars/{calendar_id}", response_model=dict)
async def update_resource_calendar(
    calendar_id: int,
    *,
    db: AsyncSession = Depends(get_db),
    calendar_in: dict,
    current_user: models.User = Depends(require_permission(Permission.PRODUCTION_UPDATE)),
):
    """Update a resource calendar."""
    calendar = db.query(models.ResourceCalendar).filter(
        and_(
            models.ResourceCalendar.id == calendar_id,
            models.ResourceCalendar.tenant_id == current_user.tenant_id
        )
    ).first()
    
    if not calendar:
        raise HTTPException(status_code=404, detail="Resource calendar not found")
    
    for key, value in calendar_in.items():
        if hasattr(calendar, key):
            setattr(calendar, key, value)
    
    db.commit()
    db.refresh(calendar)
    
    return calendar


@router.delete("/resource-calendars/{calendar_id}")
async def delete_resource_calendar(
    calendar_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_permission(Permission.PRODUCTION_DELETE)),
):
    """Delete a resource calendar."""
    calendar = db.query(models.ResourceCalendar).filter(
        and_(
            models.ResourceCalendar.id == calendar_id,
            models.ResourceCalendar.tenant_id == current_user.tenant_id
        )
    ).first()
    
    if not calendar:
        raise HTTPException(status_code=404, detail="Resource calendar not found")
    
    db.delete(calendar)
    db.commit()
    
    return {"detail": "Resource calendar deleted"}


# ============== Calendar Exceptions ==============

@router.get("/calendar-exceptions", response_model=List[dict])
async def read_calendar_exceptions(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_permission(Permission.PRODUCTION_READ)),
    resource_type: ResourceCalendarType = None,
    resource_id: int = None,
    start_date: datetime = None,
    end_date: datetime = None,
):
    """Retrieve calendar exceptions (holidays, overtime, maintenance)."""
    query = db.query(models.CalendarException).filter(
        models.CalendarException.tenant_id == current_user.tenant_id
    )
    
    if resource_type:
        query = query.filter(models.CalendarException.resource_type == resource_type)
    if resource_id is not None:
        query = query.filter(models.CalendarException.resource_id == resource_id)
    if start_date:
        query = query.filter(models.CalendarException.exception_date >= start_date)
    if end_date:
        query = query.filter(models.CalendarException.exception_date <= end_date)
    
    exceptions = query.all()
    return exceptions


@router.post("/calendar-exceptions", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_calendar_exception(
    *,
    db: AsyncSession = Depends(get_db),
    exception_in: dict,
    current_user: models.User = Depends(require_permission(Permission.PRODUCTION_CREATE)),
):
    """
    Create a calendar exception (holiday, overtime, maintenance).
    Required: resource_type, resource_id, exception_date, exception_type
    """
    exception = models.CalendarException(
        tenant_id=current_user.tenant_id,
        resource_type=exception_in["resource_type"],
        resource_id=exception_in["resource_id"],
        exception_date=exception_in["exception_date"],
        exception_type=exception_in["exception_type"],
        start_time=exception_in.get("start_time"),
        end_time=exception_in.get("end_time"),
        capacity_hours=exception_in.get("capacity_hours"),
        description=exception_in.get("description"),
        created_by=current_user.id,
    )
    
    db.add(exception)
    db.commit()
    db.refresh(exception)
    
    return exception


@router.delete("/calendar-exceptions/{exception_id}")
async def delete_calendar_exception(
    exception_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_permission(Permission.PRODUCTION_DELETE)),
):
    """Delete a calendar exception."""
    exception = db.query(models.CalendarException).filter(
        and_(
            models.CalendarException.id == exception_id,
            models.CalendarException.tenant_id == current_user.tenant_id
        )
    ).first()
    
    if not exception:
        raise HTTPException(status_code=404, detail="Calendar exception not found")
    
    db.delete(exception)
    db.commit()
    
    return {"detail": "Calendar exception deleted"}
