"""
Pydantic schemas for Quality Control module
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class DefectSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DefectType(str, Enum):
    DIMENSIONAL = "dimensional"
    VISUAL = "visual"
    MATERIAL = "material"
    FUNCTIONAL = "functional"
    OTHER = "other"


class CapaStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    ACTION_PLANNED = "action_planned"
    IMPLEMENTING = "implementing"
    VERIFIED = "verified"
    CLOSED = "closed"


class InspectionResult(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    PENDING = "pending"
    WAIVED = "waived"


# ============================================================================
# Quality Control Point Schemas
# ============================================================================

class QualityControlPointBase(BaseModel):
    stage_type_id: int
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    inspection_type: str = Field(default="visual", max_length=50)
    target_value: Optional[float] = None
    lower_limit: Optional[float] = None
    upper_limit: Optional[float] = None
    unit_of_measure: Optional[str] = Field(None, max_length=50)
    is_mandatory: bool = True
    sampling_plan: str = Field(default="100%", max_length=50)


class QualityControlPointCreate(QualityControlPointBase):
    pass


class QualityControlPointUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    inspection_type: Optional[str] = Field(None, max_length=50)
    target_value: Optional[float] = None
    lower_limit: Optional[float] = None
    upper_limit: Optional[float] = None
    unit_of_measure: Optional[str] = Field(None, max_length=50)
    is_mandatory: Optional[bool] = None
    sampling_plan: Optional[str] = Field(None, max_length=50)


class QualityControlPointRead(QualityControlPointBase):
    id: int
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Quality Inspection Record Schemas
# ============================================================================

class QualityInspectionRecordBase(BaseModel):
    production_stage_id: int
    control_point_id: int
    result: InspectionResult = InspectionResult.PENDING
    measured_value: Optional[float] = None
    measurement_unit: Optional[str] = Field(None, max_length=50)
    is_conforming: bool = True
    comments: Optional[str] = None
    attachment_urls: Optional[str] = None


class QualityInspectionRecordCreate(QualityInspectionRecordBase):
    pass


class QualityInspectionRecordUpdate(BaseModel):
    result: Optional[InspectionResult] = None
    measured_value: Optional[float] = None
    measurement_unit: Optional[str] = Field(None, max_length=50)
    is_conforming: Optional[bool] = None
    comments: Optional[str] = None
    attachment_urls: Optional[str] = None


class QualityInspectionRecordRead(QualityInspectionRecordBase):
    id: int
    tenant_id: str
    performed_by_id: int
    inspected_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Quality Defect Schemas
# ============================================================================

class QualityDefectBase(BaseModel):
    inspection_record_id: int
    defect_type: DefectType
    severity: DefectSeverity = DefectSeverity.MEDIUM
    description: str
    quantity_defective: int = 1
    disposition: Optional[str] = None
    capa_id: Optional[int] = None


class QualityDefectCreate(QualityDefectBase):
    pass


class QualityDefectUpdate(BaseModel):
    defect_type: Optional[DefectType] = None
    severity: Optional[DefectSeverity] = None
    description: Optional[str] = None
    quantity_defective: Optional[int] = None
    disposition: Optional[str] = None
    capa_id: Optional[int] = None


class QualityDefectRead(QualityDefectBase):
    id: int
    tenant_id: str
    detected_by_id: int
    detected_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# CAPA Action Schemas
# ============================================================================

class QualityCapaActionBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: str
    root_cause: Optional[str] = None
    root_cause_category: Optional[str] = Field(None, max_length=100)
    status: CapaStatus = CapaStatus.OPEN
    action_plan: Optional[str] = None
    assigned_to_id: Optional[int] = None
    due_date: Optional[datetime] = None
    effectiveness_check: Optional[str] = None


class QualityCapaActionCreate(QualityCapaActionBase):
    pass


class QualityCapaActionUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    root_cause: Optional[str] = None
    root_cause_category: Optional[str] = Field(None, max_length=100)
    status: Optional[CapaStatus] = None
    action_plan: Optional[str] = None
    assigned_to_id: Optional[int] = None
    due_date: Optional[datetime] = None
    effectiveness_check: Optional[str] = None


class QualityCapaActionRead(QualityCapaActionBase):
    id: int
    tenant_id: str
    closed_at: Optional[datetime] = None
    closed_by_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
