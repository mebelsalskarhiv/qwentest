from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class Employee(Base):
    """Employee model for staff management."""
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String(50), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    middle_name = Column(String(100))
    position = Column(String(100))
    department_id = Column(Integer, ForeignKey("departments.id"))
    email = Column(String(255))
    phone = Column(String(50))
    hire_date = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    department = relationship("Department", back_populates="employees", foreign_keys=[department_id])
    # user = relationship("User", back_populates="employee", uselist=False)  # TODO: Phase 2
    # production_operations = relationship("ProductionOperation", back_populates="operator")  # TODO: Phase 2


class Department(Base):
    """Department model for organizational structure."""
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("departments.id"))
    manager_id = Column(Integer, ForeignKey("employees.id"))
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    parent = relationship("Department", remote_side=[id], backref="children")
    employees = relationship("Employee", back_populates="department", foreign_keys="[Employee.department_id]")
    manager = relationship("Employee", foreign_keys=[manager_id])


class Customer(Base):
    """Customer model for order management."""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    contact_person = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    inn = Column(String(20))  # Tax ID
    kpp = Column(String(20))  # Registration reason code
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Station(Base):
    """Station model for production workstations."""
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    work_center_id = Column(Integer, ForeignKey("work_centers.id"))
    delivery_mode = Column(String(50), default="mounted")  # mounted, smb, nfs, ftp
    mount_point = Column(String(255))  # For mounted mode
    smb_path = Column(String(255))  # For SMB mode
    nfs_path = Column(String(255))  # For NFS mode
    username = Column(String(100))  # For network modes
    password_encrypted = Column(String(500))  # Encrypted password
    ip_address = Column(String(45))
    is_active = Column(Boolean, default=True, nullable=False)
    status = Column(String(50), default="offline")  # online, offline, maintenance
    last_seen = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    work_center = relationship("WorkCenter", back_populates="stations")


# Add relationship to WorkCenter
from app.models.production import WorkCenter
WorkCenter.stations = relationship("Station", back_populates="work_center")

# Add relationship to ProductionOperation (commented out for Phase 1 to avoid circular dependency)
# from app.models.production import ProductionOperation
# ProductionOperation.operator = relationship("Employee", back_populates="production_operations")

# Add relationship to User (commented out for Phase 1 to avoid circular dependency issues)
# from app.models.user import User
# User.employee = relationship("Employee", back_populates="user", uselist=False)
