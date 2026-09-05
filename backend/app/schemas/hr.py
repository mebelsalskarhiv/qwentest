from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class EmployeeBase(BaseModel):
    employee_code: str = Field(..., max_length=50)
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    department_id: Optional[int] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    hire_date: Optional[datetime] = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(EmployeeBase):
    pass


class EmployeeResponse(EmployeeBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DepartmentBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    manager_id: Optional[int] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(DepartmentBase):
    pass


class DepartmentResponse(DepartmentBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CustomerBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=255)
    contact_person: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    inn: Optional[str] = Field(None, max_length=20)
    kpp: Optional[str] = Field(None, max_length=20)


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(CustomerBase):
    pass


class CustomerResponse(CustomerBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StationBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    work_center_id: Optional[int] = None
    delivery_mode: str = Field(default="mounted", max_length=50)
    mount_point: Optional[str] = Field(None, max_length=255)
    smb_path: Optional[str] = Field(None, max_length=255)
    nfs_path: Optional[str] = Field(None, max_length=255)
    username: Optional[str] = Field(None, max_length=100)
    ip_address: Optional[str] = Field(None, max_length=45)


class StationCreate(StationBase):
    password: Optional[str] = Field(None, max_length=100)


class StationUpdate(StationBase):
    password: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, max_length=50)


class StationResponse(StationBase):
    id: int
    status: str
    is_active: bool
    last_seen: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
