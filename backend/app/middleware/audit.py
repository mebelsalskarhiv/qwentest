"""
Audit Middleware для записи всех изменений в БД.
Перехватывает запросы и логирует действия пользователей.
"""
import json
from datetime import datetime
from typing import Callable, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.database import async_session_maker
from app.models.user import AuditLog
from app.models.enums import ActionType


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware для автоматического логирования действий пользователей.
    
    Логирует:
    - Кто (user_id)
    - Что сделал (action_type, resource_type, resource_id)
    - Когда (timestamp)
    - Детали (old_values, new_values)
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.excluded_paths = {
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
        }
        self.excluded_methods = {"GET", "OPTIONS", "HEAD"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Пропускаем исключенные пути и методы
        if request.url.path in self.excluded_paths:
            return await call_next(request)
        
        if request.method in self.excluded_methods:
            return await call_next(request)

        # Извлекаем user_id из состояния запроса (устанавливается в Auth middleware)
        user_id = getattr(request.state, "user_id", None)
        tenant_id = getattr(request.state, "tenant_id", None)
        
        # Читаем тело запроса (для POST/PUT/PATCH)
        old_values = None
        new_values = None
        
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    new_values = json.loads(body.decode())
            except Exception:
                pass

        # Сохраняем оригинальный ответ
        response = await call_next(request)
        
        # Определяем тип действия
        action_type = self._get_action_type(request.method, response.status_code)
        
        if action_type and user_id:
            # Асинхронно записываем в БД (не блокируем ответ)
            try:
                await self._log_audit(
                    user_id=user_id,
                    tenant_id=tenant_id,
                    action_type=action_type,
                    resource_type=self._get_resource_type(request.url.path),
                    resource_id=self._extract_resource_id(request.url.path, request.method),
                    old_values=old_values,
                    new_values=new_values,
                    status_code=response.status_code,
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                )
            except Exception as e:
                # Не прерываем запрос если логирование не удалось
                print(f"Audit log error: {e}")
        
        return response

    def _get_action_type(self, method: str, status_code: int) -> ActionType | None:
        """Определяет тип действия по методу и статусу."""
        if status_code >= 400:
            return ActionType.ERROR
        
        mapping = {
            "POST": ActionType.CREATE,
            "PUT": ActionType.UPDATE,
            "PATCH": ActionType.UPDATE,
            "DELETE": ActionType.DELETE,
        }
        return mapping.get(method)

    def _get_resource_type(self, path: str) -> str:
        """Извлекает тип ресурса из пути."""
        # /api/v1/inventory/items/123 -> inventory_item
        parts = path.strip("/").split("/")
        if len(parts) >= 4:
            # api, v1, resource_type, id
            return parts[2].replace("-", "_")
        return "unknown"

    def _extract_resource_id(self, path: str, method: str) -> int | None:
        """Извлекает ID ресурса из пути."""
        parts = path.strip("/").split("/")
        if method == "POST":
            return None  # ID еще не известен
        
        # Ищем числовой ID в пути
        for part in reversed(parts):
            if part.isdigit():
                return int(part)
        return None

    async def _log_audit(
        self,
        user_id: int,
        tenant_id: int | None,
        action_type: ActionType,
        resource_type: str,
        resource_id: int | None,
        old_values: dict | None,
        new_values: dict | None,
        status_code: int,
        ip_address: str | None,
        user_agent: str | None,
    ):
        """Записывает запись аудита в БД."""
        async with async_session_maker() as db:
            audit_log = AuditLog(
                user_id=user_id,
                tenant_id=tenant_id,
                action_type=action_type,
                resource_type=resource_type,
                resource_id=resource_id,
                old_values=old_values,
                new_values=new_values,
                status_code=status_code,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            db.add(audit_log)
            await db.commit()
