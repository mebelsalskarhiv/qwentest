"""
Quality Control API endpoints for Virtuoso MES
Implements QC inspections, defects, and CAPA management
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.services.auth import require_permission, get_current_user
from app.models.user import User
from app.models.enums import Permission
from app.models.quality import (
    QualityControlPoint, QualityInspectionRecord, QualityDefect, QualityCapaAction,
    DefectSeverity, DefectType, CapaStatus, InspectionResult
)
from app.schemas.quality import (
    QualityControlPointCreate, QualityControlPointUpdate, QualityControlPointRead,
    QualityInspectionRecordCreate, QualityInspectionRecordUpdate, QualityInspectionRecordRead,
    QualityDefectCreate, QualityDefectUpdate, QualityDefectRead,
    QualityCapaActionCreate, QualityCapaActionUpdate, QualityCapaActionRead
)

router = APIRouter()


# ============================================================================
# Quality Control Points
# ============================================================================

@router.post("/control-points/", response_model=QualityControlPointRead, status_code=status.HTTP_201_CREATED)
async def create_control_point(
    control_point: QualityControlPointCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.QUALITY_CREATE))
):
    """Create a new quality control point."""
    db_control_point = QualityControlPoint(
        **control_point.dict(),
        tenant_id=current_user.tenant_id
    )
    db.add(db_control_point)
    await db.commit()
    await db.refresh(db_control_point)
    return db_control_point


@router.get("/control-points/", response_model=List[QualityControlPointRead])
async def list_control_points(
    stage_type_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.QUALITY_READ))
):
    """List all quality control points for the tenant."""
    query = select(QualityControlPoint).where(QualityControlPoint.tenant_id == current_user.tenant_id)
    
    if stage_type_id:
        query = query.where(QualityControlPoint.stage_type_id == stage_type_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/control-points/{control_point_id}", response_model=QualityControlPointRead)
async def get_control_point(
    control_point_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.QUALITY_READ))
):
    """Get a specific quality control point."""
    query = select(QualityControlPoint).where(
        QualityControlPoint.id == control_point_id,
        QualityControlPoint.tenant_id == current_user.tenant_id
    )
    result = await db.execute(query)
    control_point = result.scalar_one_or_none()
    
    if not control_point:
        raise HTTPException(status_code=404, detail="Control point not found")
    
    return control_point


@router.put("/control-points/{control_point_id}", response_model=QualityControlPointRead)
async def update_control_point(
    control_point_id: int,
    control_point_update: QualityControlPointUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.QUALITY_UPDATE))
):
    """Update a quality control point."""
    query = select(QualityControlPoint).where(
        QualityControlPoint.id == control_point_id,
        QualityControlPoint.tenant_id == current_user.tenant_id
    )
    result = await db.execute(query)
    db_control_point = result.scalar_one_or_none()
    
    if not db_control_point:
        raise HTTPException(status_code=404, detail="Control point not found")
    
    update_data = control_point_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_control_point, field, value)
    
    await db.commit()
    await db.refresh(db_control_point)
    return db_control_point


@router.delete("/control-points/{control_point_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_control_point(
    control_point_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.QUALITY_UPDATE))
):
    """Delete a quality control point."""
    query = select(QualityControlPoint).where(
        QualityControlPoint.id == control_point_id,
        QualityControlPoint.tenant_id == current_user.tenant_id
    )
    result = await db.execute(query)
    db_control_point = result.scalar_one_or_none()
    
    if not db_control_point:
        raise HTTPException(status_code=404, detail="Control point not found")
    
    await db.delete(db_control_point)
    await db.commit()
    return None


# ============================================================================
# Quality Inspection Records
# ============================================================================

@router.post("/inspections/", response_model=QualityInspectionRecordRead, status_code=status.HTTP_201_CREATED)
async def create_inspection_record(
    inspection: QualityInspectionRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.QUALITY_UPDATE))
):
    """Create a new quality inspection record."""
    db_inspection = QualityInspectionRecord(
        **inspection.dict(),
        tenant_id=current_user.tenant_id,
        performed_by_id=current_user.id
    )
    db.add(db_inspection)
    await db.commit()
    await db.refresh(db_inspection)
    return db_inspection


@router.get("/inspections/", response_model=List[QualityInspectionRecordRead])
async def list_inspections(
    production_stage_id: Optional[int] = None,
    result_filter: Optional[InspectionResult] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.QUALITY_READ))
):
    """List all quality inspection records for the tenant."""
    query = select(QualityInspectionRecord).where(
        QualityInspectionRecord.tenant_id == current_user.tenant_id
    )
    
    if production_stage_id:
        query = query.where(QualityInspectionRecord.production_stage_id == production_stage_id)
    
    if result_filter:
        query = query.where(QualityInspectionRecord.result == result_filter)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/inspections/{inspection_id}", response_model=QualityInspectionRecordRead)
async def get_inspection_record(
    inspection_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.QUALITY_READ))
):
    """Get a specific inspection record."""
    query = select(QualityInspectionRecord).where(
        QualityInspectionRecord.id == inspection_id,
        QualityInspectionRecord.tenant_id == current_user.tenant_id
    )
    result = await db.execute(query)
    inspection = result.scalar_one_or_none()
    
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection record not found")
    
    return inspection


@router.put("/inspections/{inspection_id}", response_model=QualityInspectionRecordRead)
async def update_inspection_record(
    inspection_id: int,
    inspection_update: QualityInspectionRecordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.QUALITY_UPDATE))
):
    """Update an inspection record."""
    query = select(QualityInspectionRecord).where(
        QualityInspectionRecord.id == inspection_id,
        QualityInspectionRecord.tenant_id == current_user.tenant_id
    )
    result = await db.execute(query)
    db_inspection = result.scalar_one_or_none()
    
    if not db_inspection:
        raise HTTPException(status_code=404, detail="Inspection record not found")
    
    update_data = inspection_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_inspection, field, value)
    
    await db.commit()
    await db.refresh(db_inspection)
    return db_inspection


# ============================================================================
# Quality Defects
# ============================================================================

@router.post("/defects/", response_model=QualityDefectRead, status_code=status.HTTP_201_CREATED)
async def create_defect(
    defect: QualityDefectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.QUALITY_UPDATE))
):
    """Create a new quality defect record."""
    db_defect = QualityDefect(
        **defect.dict(),
        tenant_id=current_user.tenant_id,
        detected_by_id=current_user.id
    )
    db.add(db_defect)
    await db.commit()
    await db.refresh(db_defect)
    return db_defect


@router.get("/defects/", response_model=List[QualityDefectRead])
async def list_defects(
    inspection_record_id: Optional[int] = None,
    severity_filter: Optional[DefectSeverity] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.QUALITY_READ))
):
    """List all quality defects for the tenant."""
    query = select(QualityDefect).where(QualityDefect.tenant_id == current_user.tenant_id)
    
    if inspection_record_id:
        query = query.where(QualityDefect.inspection_record_id == inspection_record_id)
    
    if severity_filter:
        query = query.where(QualityDefect.severity == severity_filter)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/defects/{defect_id}", response_model=QualityDefectRead)
async def get_defect(
    defect_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.QUALITY_READ))
):
    """Get a specific defect record."""
    query = select(QualityDefect).where(
        QualityDefect.id == defect_id,
        QualityDefect.tenant_id == current_user.tenant_id
    )
    result = await db.execute(query)
    defect = result.scalar_one_or_none()
    
    if not defect:
        raise HTTPException(status_code=404, detail="Defect not found")
    
    return defect


@router.put("/defects/{defect_id}", response_model=QualityDefectRead)
async def update_defect(
    defect_id: int,
    defect_update: QualityDefectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.QUALITY_UPDATE))
):
    """Update a defect record."""
    query = select(QualityDefect).where(
        QualityDefect.id == defect_id,
        QualityDefect.tenant_id == current_user.tenant_id
    )
    result = await db.execute(query)
    db_defect = result.scalar_one_or_none()
    
    if not db_defect:
        raise HTTPException(status_code=404, detail="Defect not found")
    
    update_data = defect_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_defect, field, value)
    
    await db.commit()
    await db.refresh(db_defect)
    return db_defect


# ============================================================================
# CAPA Actions
# ============================================================================

@router.post("/capa/", response_model=QualityCapaActionRead, status_code=status.HTTP_201_CREATED)
async def create_capa_action(
    capa: QualityCapaActionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.QUALITY_UPDATE))
):
    """Create a new CAPA action."""
    db_capa = QualityCapaAction(
        **capa.dict(),
        tenant_id=current_user.tenant_id
    )
    db.add(db_capa)
    await db.commit()
    await db.refresh(db_capa)
    return db_capa


@router.get("/capa/", response_model=List[QualityCapaActionRead])
async def list_capa_actions(
    status_filter: Optional[CapaStatus] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.QUALITY_READ))
):
    """List all CAPA actions for the tenant."""
    query = select(QualityCapaAction).where(QualityCapaAction.tenant_id == current_user.tenant_id)
    
    if status_filter:
        query = query.where(QualityCapaAction.status == status_filter)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/capa/{capa_id}", response_model=QualityCapaActionRead)
async def get_capa_action(
    capa_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.QUALITY_READ))
):
    """Get a specific CAPA action."""
    query = select(QualityCapaAction).where(
        QualityCapaAction.id == capa_id,
        QualityCapaAction.tenant_id == current_user.tenant_id
    )
    result = await db.execute(query)
    capa = result.scalar_one_or_none()
    
    if not capa:
        raise HTTPException(status_code=404, detail="CAPA action not found")
    
    return capa


@router.put("/capa/{capa_id}", response_model=QualityCapaActionRead)
async def update_capa_action(
    capa_id: int,
    capa_update: QualityCapaActionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.QUALITY_UPDATE))
):
    """Update a CAPA action."""
    query = select(QualityCapaAction).where(
        QualityCapaAction.id == capa_id,
        QualityCapaAction.tenant_id == current_user.tenant_id
    )
    result = await db.execute(query)
    db_capa = result.scalar_one_or_none()
    
    if not db_capa:
        raise HTTPException(status_code=404, detail="CAPA action not found")
    
    update_data = capa_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_capa, field, value)
    
    await db.commit()
    await db.refresh(db_capa)
    return db_capa


@router.delete("/capa/{capa_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_capa_action(
    capa_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.QUALITY_UPDATE))
):
    """Delete a CAPA action."""
    query = select(QualityCapaAction).where(
        QualityCapaAction.id == capa_id,
        QualityCapaAction.tenant_id == current_user.tenant_id
    )
    result = await db.execute(query)
    db_capa = result.scalar_one_or_none()
    
    if not db_capa:
        raise HTTPException(status_code=404, detail="CAPA action not found")
    
    await db.delete(db_capa)
    await db.commit()
    return None
