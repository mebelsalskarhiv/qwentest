from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.schemas.hr import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse,
    DepartmentCreate, DepartmentUpdate, DepartmentResponse,
    CustomerCreate, CustomerUpdate, CustomerResponse,
    StationCreate, StationUpdate, StationResponse
)
from app.models.hr import Employee, Department, Customer, Station
from app.models.user import User
from app.services.auth import get_current_user

router = APIRouter(prefix="/hr", tags=["HR & Stations"])


# ==================== Employees ====================

@router.get("/employees", response_model=List[EmployeeResponse])
async def get_employees(
    skip: int = 0,
    limit: int = 100,
    department_id: int = None,
    is_active: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all employees."""
    query = select(Employee).where(Employee.is_active == is_active)
    
    if department_id:
        query = query.where(Employee.department_id == department_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/employees/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get employee by ID."""
    result = await db.execute(
        select(Employee).where(Employee.id == employee_id)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    return employee


@router.post("/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_data: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new employee."""
    # Check if employee code exists
    result = await db.execute(
        select(Employee).where(Employee.employee_code == employee_data.employee_code)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee code already exists"
        )
    
    employee = Employee(**employee_data.model_dump())
    db.add(employee)
    await db.flush()
    await db.refresh(employee)
    
    return employee


@router.put("/employees/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update employee."""
    result = await db.execute(
        select(Employee).where(Employee.id == employee_id)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    update_data = employee_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(employee, field, value)
    
    await db.flush()
    await db.refresh(employee)
    
    return employee


@router.delete("/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete employee (soft delete)."""
    result = await db.execute(
        select(Employee).where(Employee.id == employee_id)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    employee.is_active = False
    await db.flush()
    
    return None


# ==================== Departments ====================

@router.get("/departments", response_model=List[DepartmentResponse])
async def get_departments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all departments."""
    result = await db.execute(select(Department).where(Department.is_active == True))
    return result.scalars().all()


@router.post("/departments", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    department_data: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new department."""
    # Check if department code exists
    result = await db.execute(
        select(Department).where(Department.code == department_data.code)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department code already exists"
        )
    
    department = Department(**department_data.model_dump())
    db.add(department)
    await db.flush()
    await db.refresh(department)
    
    return department


@router.put("/departments/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: int,
    department_data: DepartmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update department."""
    result = await db.execute(
        select(Department).where(Department.id == department_id)
    )
    department = result.scalar_one_or_none()
    
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    update_data = department_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(department, field, value)
    
    await db.flush()
    await db.refresh(department)
    
    return department


# ==================== Customers ====================

@router.get("/customers", response_model=List[CustomerResponse])
async def get_customers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all customers."""
    query = select(Customer).where(Customer.is_active == True)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new customer."""
    # Check if customer code exists
    result = await db.execute(
        select(Customer).where(Customer.code == customer_data.code)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer code already exists"
        )
    
    customer = Customer(**customer_data.model_dump())
    db.add(customer)
    await db.flush()
    await db.refresh(customer)
    
    return customer


@router.put("/customers/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update customer."""
    result = await db.execute(
        select(Customer).where(Customer.id == customer_id)
    )
    customer = result.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    update_data = customer_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)
    
    await db.flush()
    await db.refresh(customer)
    
    return customer


# ==================== Stations ====================

@router.get("/stations", response_model=List[StationResponse])
async def get_stations(
    work_center_id: int = None,
    status_filter: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all stations."""
    query = select(Station).where(Station.is_active == True)
    
    if work_center_id:
        query = query.where(Station.work_center_id == work_center_id)
    
    if status_filter:
        query = query.where(Station.status == status_filter)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/stations/{station_id}", response_model=StationResponse)
async def get_station(
    station_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get station by ID."""
    result = await db.execute(
        select(Station).where(Station.id == station_id)
    )
    station = result.scalar_one_or_none()
    
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station not found"
        )
    
    return station


@router.post("/stations", response_model=StationResponse, status_code=status.HTTP_201_CREATED)
async def create_station(
    station_data: StationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new station."""
    # Check if station code exists
    result = await db.execute(
        select(Station).where(Station.code == station_data.code)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Station code already exists"
        )
    
    station_data_dict = station_data.model_dump()
    password = station_data_dict.pop('password', None)
    
    station = Station(**station_data_dict)
    if password:
        # In production, encrypt password here
        station.password_encrypted = password
    
    db.add(station)
    await db.flush()
    await db.refresh(station)
    
    return station


@router.put("/stations/{station_id}", response_model=StationResponse)
async def update_station(
    station_id: int,
    station_data: StationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update station."""
    result = await db.execute(
        select(Station).where(Station.id == station_id)
    )
    station = result.scalar_one_or_none()
    
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station not found"
        )
    
    update_data = station_data.model_dump(exclude_unset=True)
    password = update_data.pop('password', None)
    
    for field, value in update_data.items():
        setattr(station, field, value)
    
    if password:
        # In production, encrypt password here
        station.password_encrypted = password
    
    await db.flush()
    await db.refresh(station)
    
    return station


@router.post("/stations/{station_id}/status", response_model=StationResponse)
async def update_station_status(
    station_id: int,
    status: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update station status (online/offline/maintenance)."""
    from datetime import datetime
    
    result = await db.execute(
        select(Station).where(Station.id == station_id)
    )
    station = result.scalar_one_or_none()
    
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station not found"
        )
    
    station.status = status
    if status == "online":
        station.last_seen = datetime.utcnow()
    
    await db.flush()
    await db.refresh(station)
    
    return station
