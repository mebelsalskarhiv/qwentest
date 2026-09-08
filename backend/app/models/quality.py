"""
Quality Control Models for Virtuoso MES
Implements QC inspections, defects, and CAPA (Corrective and Preventive Actions)
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .base import Base


class DefectSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DefectType(str, enum.Enum):
    DIMENSIONAL = "dimensional"
    VISUAL = "visual"
    MATERIAL = "material"
    FUNCTIONAL = "functional"
    OTHER = "other"


class CapaStatus(str, enum.Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    ACTION_PLANNED = "action_planned"
    IMPLEMENTING = "implementing"
    VERIFIED = "verified"
    CLOSED = "closed"


class InspectionResult(str, enum.Enum):
    PASS = "pass"
    FAIL = "fail"
    PENDING = "pending"
    WAIVED = "waived"  # Отклонение от нормы согласовано


class QualityControlPoint(Base):
    """
    Контрольная точка (Operation/Inspection Plan)
    Определяет ЧТО и КАК проверять на конкретном этапе производства
    """
    __tablename__ = "quality_control_points"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
    stage_type_id = Column(Integer, ForeignKey("stage_type_definitions.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Тип контроля
    inspection_type = Column(String(50), default="visual")  # visual, dimensional, functional
    
    # Параметры допуска
    target_value = Column(Float, nullable=True)  # Целевое значение
    lower_limit = Column(Float, nullable=True)   # Нижняя граница
    upper_limit = Column(Float, nullable=True)   # Верхняя граница
    unit_of_measure = Column(String(50), nullable=True)  # мм, град, шт и т.д.
    
    # Обязательность
    is_mandatory = Column(Boolean, default=True)
    sampling_plan = Column(String(50), default="100%")  # 100%, AQL 1.5, etc.
    
    # Связи
    stage_type = relationship("StageTypeDefinition", back_populates="control_points")
    inspection_records = relationship("QualityInspectionRecord", back_populates="control_point")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class QualityInspectionRecord(Base):
    """
    Запись о проведении конкретной проверки (Результат ОТК)
    Привязывается к этапу производства (ProductionStage)
    """
    __tablename__ = "quality_inspection_records"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
    
    # Связи
    production_stage_id = Column(Integer, ForeignKey("production_stages.id"), nullable=False, index=True)
    control_point_id = Column(Integer, ForeignKey("quality_control_points.id"), nullable=False)
    performed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Результаты
    result = Column(SQLEnum(InspectionResult), default=InspectionResult.PENDING)
    
    # Измеренные значения (для количественных признаков)
    measured_value = Column(Float, nullable=True)
    measurement_unit = Column(String(50), nullable=True)
    
    # Для качественных признаков (годен/не годен по визуальному осмотру)
    is_conforming = Column(Boolean, default=True)
    
    # Комментарий инспектора
    comments = Column(Text)
    
    # Сертификаты/фото (ссылки на S3/File storage)
    attachment_urls = Column(Text)  # JSON string with URLs
    
    inspected_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    production_stage = relationship("ProductionStage", back_populates="inspection_records")
    control_point = relationship("QualityControlPoint", back_populates="inspection_records")
    performed_by = relationship("User", foreign_keys=[performed_by_id])
    defects = relationship("QualityDefect", back_populates="inspection_record", cascade="all, delete-orphan")


class QualityDefect(Base):
    """
    Запись о выявленном дефекте
    """
    __tablename__ = "quality_defects"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
    
    inspection_record_id = Column(Integer, ForeignKey("quality_inspection_records.id"), nullable=False)
    detected_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Классификация
    defect_type = Column(SQLEnum(DefectType), nullable=False)
    severity = Column(SQLEnum(DefectSeverity), default=DefectSeverity.MEDIUM)
    
    # Описание
    description = Column(Text, nullable=False)
    quantity_defective = Column(Integer, default=1)
    
    # Решение по дефекту
    disposition = Column(String(50))  # Rework, Scrap, Use As Is, Return to Vendor
    
    # Связь с CAPA (если требуется)
    capa_id = Column(Integer, ForeignKey("quality_capa_actions.id"), nullable=True)
    
    detected_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    inspection_record = relationship("QualityInspectionRecord", back_populates="defects")
    detected_by = relationship("User", foreign_keys=[detected_by_id])
    capa_action = relationship("QualityCapaAction", back_populates="defects")


class QualityCapaAction(Base):
    """
    Корректирующие и Предупреждающие Действия (CAPA)
    Для системного устранения причин брака
    """
    __tablename__ = "quality_capa_actions"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Root Cause Analysis
    root_cause = Column(Text)
    root_cause_category = Column(String(100))  # Man, Machine, Material, Method, Environment
    
    status = Column(SQLEnum(CapaStatus), default=CapaStatus.OPEN)
    
    # План действий
    action_plan = Column(Text)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    due_date = Column(DateTime, nullable=True)
    
    # Верификация эффективности
    effectiveness_check = Column(Text)
    closed_at = Column(DateTime, nullable=True)
    closed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    closed_by = relationship("User", foreign_keys=[closed_by_id])
    defects = relationship("QualityDefect", back_populates="capa_action")
