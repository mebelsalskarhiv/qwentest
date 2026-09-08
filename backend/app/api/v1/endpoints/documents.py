"""
API endpoints для системы документооборота.
Управление документами, версиями, категориями и связями.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import hashlib
import os

from app.core.database import get_db
from app.services.auth import get_current_user, require_permission
from app.models.user import User
from app.models.documents import (
    Document, DocumentVersion, DocumentCategory, DocumentRelation,
    DocumentStatus, DocumentType
)
from app.models.enums import Permission

router = APIRouter()


# ==================== Категории документов ====================

@router.get("/categories", response_model=List[dict])
async def list_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.DOCUMENTS_READ))
):
    """Список категорий документов"""
    result = await db.execute(
        select(DocumentCategory).where(DocumentCategory.tenant_id == current_user.tenant_id)
    )
    return result.scalars().all()


@router.post("/categories", response_model=dict)
async def create_category(
    name: str = Form(...),
    code: str = Form(...),
    description: Optional[str] = Form(None),
    parent_id: Optional[int] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.DOCUMENTS_CREATE))
):
    """Создание категории документов"""
    # Проверка уникальности кода
    result = await db.execute(
        select(DocumentCategory).where(
            DocumentCategory.code == code,
            DocumentCategory.tenant_id == current_user.tenant_id
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Категория с таким кодом уже существует")
    
    category = DocumentCategory(
        tenant_id=current_user.tenant_id,
        name=name,
        code=code,
        description=description,
        parent_id=parent_id
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


# ==================== Документы ====================

@router.get("/documents", response_model=List[dict])
async def list_documents(
    skip: int = 0,
    limit: int = 50,
    category_id: Optional[int] = None,
    doc_type: Optional[DocumentType] = None,
    status: Optional[DocumentStatus] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.DOCUMENTS_READ))
):
    """Список документов с фильтрацией"""
    query = select(Document).where(Document.tenant_id == current_user.tenant_id)
    
    if category_id:
        query = query.where(Document.category_id == category_id)
    if doc_type:
        query = query.where(Document.type == doc_type)
    if status:
        query = query.where(Document.status == status)
    if search:
        query = query.where(
            (Document.title.ilike(f"%{search}%")) | 
            (Document.code.ilike(f"%{search}%"))
        )
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/documents/{doc_id}", response_model=dict)
async def get_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.DOCUMENTS_READ))
):
    """Получение документа с версиями"""
    result = await db.execute(
        select(Document).where(
            Document.id == doc_id,
            Document.tenant_id == current_user.tenant_id
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")
    return doc


@router.post("/documents", response_model=dict)
async def create_document(
    title: str = Form(...),
    code: Optional[str] = Form(None),
    type: DocumentType = Form(DocumentType.OTHER),
    category_id: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.DOCUMENTS_CREATE))
):
    """Создание документа с загрузкой файла"""
    # Чтение файла
    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()
    file_size = len(content)
    
    # Сохранение файла (локально, в продакшене - S3)
    upload_dir = f"/tmp/documents/{current_user.tenant_id}"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = f"{upload_dir}/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Создание документа
    doc = Document(
        tenant_id=current_user.tenant_id,
        title=title,
        code=code,
        type=type,
        category_id=category_id,
        description=description,
        tags=tags,
        status=DocumentStatus.DRAFT,
        owner_id=current_user.id
    )
    db.add(doc)
    await db.flush()
    
    # Создание первой версии
    version = DocumentVersion(
        tenant_id=current_user.tenant_id,
        document_id=doc.id,
        version_number=1,
        version_label="1.0",
        file_path=file_path,
        file_name=file.filename,
        file_size=file_size,
        mime_type=file.content_type or "application/octet-stream",
        file_hash=file_hash,
        uploaded_by_id=current_user.id,
        is_active=True
    )
    db.add(version)
    await db.flush()
    
    # Обновление текущей версии документа
    doc.current_version_id = version.id
    await db.commit()
    await db.refresh(doc)
    
    return doc


@router.put("/documents/{doc_id}", response_model=dict)
async def update_document(
    doc_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.DOCUMENTS_UPDATE))
):
    """Обновление мета-информации документа"""
    result = await db.execute(
        select(Document).where(
            Document.id == doc_id,
            Document.tenant_id == current_user.tenant_id
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")
    
    if title:
        doc.title = title
    if description is not None:
        doc.description = description
    if tags is not None:
        doc.tags = tags
    
    doc.updated_at = func.now()
    await db.commit()
    await db.refresh(doc)
    return doc


@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.DOCUMENTS_DELETE))
):
    """Удаление документа"""
    result = await db.execute(
        select(Document).where(
            Document.id == doc_id,
            Document.tenant_id == current_user.tenant_id
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")
    
    await db.delete(doc)
    await db.commit()
    return {"status": "deleted"}


# ==================== Версии документов ====================

@router.get("/documents/{doc_id}/versions", response_model=List[dict])
async def list_versions(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.DOCUMENTS_READ))
):
    """Список версий документа"""
    result = await db.execute(
        select(DocumentVersion)
        .where(
            DocumentVersion.document_id == doc_id,
            DocumentVersion.tenant_id == current_user.tenant_id
        )
        .order_by(DocumentVersion.version_number.desc())
    )
    return result.scalars().all()


@router.post("/documents/{doc_id}/versions", response_model=dict)
async def upload_version(
    doc_id: int,
    file: UploadFile = File(...),
    change_comment: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.DOCUMENTS_UPDATE))
):
    """Загрузка новой версии документа"""
    # Проверка существования документа
    result = await db.execute(
        select(Document).where(
            Document.id == doc_id,
            Document.tenant_id == current_user.tenant_id
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")
    
    # Чтение файла
    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()
    file_size = len(content)
    
    # Сохранение файла
    upload_dir = f"/tmp/documents/{current_user.tenant_id}"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = f"{upload_dir}/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Получение последнего номера версии
    last_version = await db.execute(
        select(func.max(DocumentVersion.version_number)).where(
            DocumentVersion.document_id == doc_id
        )
    )
    last_ver_num = last_version.scalar_one_or_none() or 0
    new_ver_num = last_ver_num + 1
    
    # Деактивация предыдущей активной версии
    await db.execute(
        (DocumentVersion.__table__.update())
        .where(DocumentVersion.document_id == doc_id)
        .values(is_active=False)
    )
    
    # Создание новой версии
    version = DocumentVersion(
        tenant_id=current_user.tenant_id,
        document_id=doc_id,
        version_number=new_ver_num,
        version_label=f"{new_ver_num}.0",
        file_path=file_path,
        file_name=file.filename,
        file_size=file_size,
        mime_type=file.content_type or "application/octet-stream",
        file_hash=file_hash,
        change_comment=change_comment,
        uploaded_by_id=current_user.id,
        is_active=True
    )
    db.add(version)
    await db.flush()
    
    # Обновление документа
    doc.current_version_id = version.id
    if doc.status == DocumentStatus.OBSOLETE:
        doc.status = DocumentStatus.APPROVED
    
    await db.commit()
    await db.refresh(version)
    return version


# ==================== Согласование документов ====================

@router.post("/documents/{doc_id}/submit-review", response_model=dict)
async def submit_for_review(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.DOCUMENTS_UPDATE))
):
    """Отправка документа на согласование"""
    result = await db.execute(
        select(Document).where(
            Document.id == doc_id,
            Document.tenant_id == current_user.tenant_id
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")
    
    doc.status = DocumentStatus.IN_REVIEW
    await db.commit()
    await db.refresh(doc)
    return doc


@router.post("/documents/{doc_id}/approve", response_model=dict)
async def approve_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.DOCUMENTS_APPROVE))
):
    """Утверждение документа"""
    result = await db.execute(
        select(Document).where(
            Document.id == doc_id,
            Document.tenant_id == current_user.tenant_id
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")
    
    doc.status = DocumentStatus.APPROVED
    doc.approver_id = current_user.id
    await db.commit()
    await db.refresh(doc)
    return doc


@router.post("/documents/{doc_id}/reject", response_model=dict)
async def reject_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.DOCUMENTS_APPROVE))
):
    """Отклонение документа (возврат в черновики)"""
    result = await db.execute(
        select(Document).where(
            Document.id == doc_id,
            Document.tenant_id == current_user.tenant_id
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")
    
    doc.status = DocumentStatus.DRAFT
    await db.commit()
    await db.refresh(doc)
    return doc


# ==================== Связи документов ====================

@router.get("/documents/{doc_id}/relations", response_model=List[dict])
async def list_relations(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.DOCUMENTS_READ))
):
    """Список связей документа"""
    result = await db.execute(
        select(DocumentRelation).where(
            DocumentRelation.document_id == doc_id,
            DocumentRelation.tenant_id == current_user.tenant_id
        )
    )
    return result.scalars().all()


@router.post("/documents/{doc_id}/relations", response_model=dict)
async def create_relation(
    doc_id: int,
    entity_type: str = Form(...),
    entity_id: int = Form(...),
    context: Optional[str] = Form(None),
    is_mandatory: bool = Form(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.DOCUMENTS_UPDATE))
):
    """Создание связи документа с объектом"""
    relation = DocumentRelation(
        tenant_id=current_user.tenant_id,
        document_id=doc_id,
        entity_type=entity_type,
        entity_id=entity_id,
        context=context,
        is_mandatory=is_mandatory,
        created_by_id=current_user.id
    )
    db.add(relation)
    await db.commit()
    await db.refresh(relation)
    return relation


@router.delete("/documents/relations/{relation_id}")
async def delete_relation(
    relation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.DOCUMENTS_UPDATE))
):
    """Удаление связи"""
    result = await db.execute(
        select(DocumentRelation).where(
            DocumentRelation.id == relation_id,
            DocumentRelation.tenant_id == current_user.tenant_id
        )
    )
    relation = result.scalar_one_or_none()
    if not relation:
        raise HTTPException(status_code=404, detail="Связь не найдена")
    
    await db.delete(relation)
    await db.commit()
    return {"status": "deleted"}


# ==================== Поиск по связям ====================

@router.get("/relations/by-entity", response_model=List[dict])
async def get_docs_by_entity(
    entity_type: str = Query(...),
    entity_id: int = Query(...),
    mandatory_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.DOCUMENTS_READ))
):
    """Получить все документы, связанные с объектом"""
    query = select(DocumentRelation).where(
        DocumentRelation.entity_type == entity_type,
        DocumentRelation.entity_id == entity_id,
        DocumentRelation.tenant_id == current_user.tenant_id
    )
    
    if mandatory_only:
        query = query.where(DocumentRelation.is_mandatory == True)
    
    result = await db.execute(query)
    relations = result.scalars().all()
    
    # Загружаем связанные документы
    doc_ids = [r.document_id for r in relations]
    docs_result = await db.execute(
        select(Document).where(Document.id.in_(doc_ids))
    )
    docs = {d.id: d for d in docs_result.scalars().all()}
    
    return [{"relation": r, "document": docs.get(r.document_id)} for r in relations]
