"""
Модели системы документооборота Virtuoso MES.
Поддерживает версионирование, категории и привязку к объектам производства.
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, Boolean, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.base import Base


class DocumentStatus(str, enum.Enum):
    """Статусы жизненного цикла документа"""
    DRAFT = "draft"              # Черновик
    IN_REVIEW = "in_review"      # На согласовании
    APPROVED = "approved"        # Утвержден (активная версия)
    OBSOLETE = "obsolete"        # Устарел (заменен новой версией)
    ARCHIVED = "archived"        # Архивирован


class DocumentType(str, enum.Enum):
    """Типы документов"""
    DRAWING = "drawing"                  # Чертеж
    TECH_PROCESS = "tech_process"        # Маршрутная карта/Техпроцесс
    INSTRUCTION = "instruction"          # Инструкция рабочего
    SPECIFICATION = "specification"      # Спецификация
    CERTIFICATE = "certificate"          # Сертификат/Паспорт
    REPORT = "report"                    # Отчет
    OTHER = "other"                      # Прочее


class DocumentCategory(Base):
    """Категории документов для группировки (папки)"""
    __tablename__ = "document_categories"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True) # Например: "DRAWINGS", "TECH"
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("document_categories.id"), nullable=True)
    
    # Связи
    parent = relationship("DocumentCategory", remote_side=[id], backref="children")
    documents = relationship("Document", back_populates="category")
    created_at = Column(DateTime, default=datetime.utcnow)


class Document(Base):
    """
    Основной объект документа. Хранит мета-информацию.
    Физические файлы хранятся в DocumentVersion.
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    code = Column(String(100), nullable=True, index=True) # Внутренний код (АБВГ.123456.001)
    
    type = Column(Enum(DocumentType), nullable=False, default=DocumentType.OTHER)
    category_id = Column(Integer, ForeignKey("document_categories.id"), nullable=True, index=True)
    
    status = Column(Enum(DocumentStatus), nullable=False, default=DocumentStatus.DRAFT)
    current_version_id = Column(Integer, ForeignKey("document_versions.id"), nullable=True)
    
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False) # Создатель/Владелец
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Кто утвердил
    
    description = Column(Text, nullable=True)
    tags = Column(String(500), nullable=True) # JSON список тегов или строка через запятую
    
    # Связи
    category = relationship("DocumentCategory", back_populates="documents")
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan", order_by="DocumentVersion.version_number.desc()")
    relations = relationship("DocumentRelation", back_populates="document", cascade="all, delete-orphan")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DocumentVersion(Base):
    """
    Конкретная версия файла документа.
    При изменении файла создается новая запись здесь, статус родителя меняется.
    """
    __tablename__ = "document_versions"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    
    version_number = Column(Integer, nullable=False, default=1) # 1, 2, 3...
    version_label = Column(String(50), nullable=True) # "1.0", "1.1-beta"
    
    file_path = Column(String(500), nullable=False) # Путь к файлу (S3 key или локальный путь)
    file_name = Column(String(255), nullable=False) # Оригинальное имя файла
    file_size = Column(Integer, nullable=False) # Размер в байтах
    mime_type = Column(String(100), nullable=False) # application/pdf, image/png
    
    file_hash = Column(String(64), nullable=True, index=True) # SHA256 для контроля целостности
    
    change_comment = Column(Text, nullable=True) # Комментарий к изменениям в этой версии
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    is_active = Column(Boolean, default=False) # Является ли эта версия активной
    
    # Связи
    document = relationship("Document", back_populates="versions")
    uploader = relationship("User", foreign_keys=[uploaded_by_id])
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('document_id', 'version_number', name='uq_doc_ver_num'),
    )


class DocumentRelation(Base):
    """
    Связь документа с объектами системы.
    Позволяет привязать чертеж к Детали, Техпроцесс к Этапу, Инструкцию к Станку.
    """
    __tablename__ = "document_relations"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    
    # Полиморфная связь (объект назначения)
    entity_type = Column(String(50), nullable=False, index=True) # 'work_order', 'production_stage', 'equipment', 'part'
    entity_id = Column(Integer, nullable=False, index=True)       # ID объекта
    
    context = Column(String(100), nullable=True) # Контекст привязки (напр. "setup", "operation_10", "maintenance")
    is_mandatory = Column(Boolean, default=False) # Обязательно ли изучение документа перед началом работы
    
    # Связи
    document = relationship("Document", back_populates="relations")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
