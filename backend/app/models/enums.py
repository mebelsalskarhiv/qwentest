from enum import Enum


class UserRole(str, Enum):
    """User roles in the system."""
    ADMIN = "admin"
    MANAGER = "manager"
    SUPERVISOR = "supervisor"
    OPERATOR = "operator"
    QUALITY_INSPECTOR = "quality_inspector"
    MAINTENANCE_TECHNICIAN = "maintenance_technician"
    WAREHOUSE_KEEPER = "warehouse_keeper"
    ENGINEER = "engineer"
    GUEST = "guest"


class Permission(str, Enum):
    """System permissions."""
    # User management
    USERS_READ = "users:read"
    USERS_CREATE = "users:create"
    USERS_UPDATE = "users:update"
    USERS_DELETE = "users:delete"
    
    # Production
    PRODUCTION_READ = "production:read"
    PRODUCTION_CREATE = "production:create"
    PRODUCTION_UPDATE = "production:update"
    PRODUCTION_DELETE = "production:delete"
    
    # Inventory
    INVENTORY_READ = "inventory:read"
    INVENTORY_CREATE = "inventory:create"
    INVENTORY_UPDATE = "inventory:update"
    INVENTORY_DELETE = "inventory:delete"
    
    # Quality
    QUALITY_READ = "quality:read"
    QUALITY_CREATE = "quality:create"
    QUALITY_UPDATE = "quality:update"
    QUALITY_DELETE = "quality:delete"
    
    # Maintenance
    MAINTENANCE_READ = "maintenance:read"
    MAINTENANCE_CREATE = "maintenance:create"
    MAINTENANCE_UPDATE = "maintenance:update"
    MAINTENANCE_DELETE = "maintenance:delete"
    
    # Reports
    REPORTS_READ = "reports:read"
    REPORTS_EXPORT = "reports:export"
    
    # Admin
    ADMIN_ACCESS = "admin:access"
    SYSTEM_CONFIG = "system:config"


class ActionType(str, Enum):
    """Audit log action types."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    VIEW = "view"
    EXPORT = "export"
    IMPORT = "import"
    APPROVE = "approve"
    REJECT = "reject"
