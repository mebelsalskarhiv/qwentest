from enum import Enum


class UserRole(str, Enum):
    """User roles in the system."""
    SUPERADMIN = "superadmin"
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
    WORK_ORDER_READ = "work_order:read"
    WORK_ORDER_CREATE = "work_order:create"
    WORK_ORDER_UPDATE = "work_order:update"
    WORK_ORDER_DELETE = "work_order:delete"
    STAGE_READ = "stage:read"
    STAGE_CREATE = "stage:create"
    STAGE_UPDATE = "stage:update"
    STAGE_DELETE = "stage:delete"
    
    # Inventory
    INVENTORY_READ = "inventory:read"
    INVENTORY_CREATE = "inventory:create"
    INVENTORY_UPDATE = "inventory:update"
    INVENTORY_DELETE = "inventory:delete"
    MATERIAL_RESERVATION_READ = "material_reservation:read"
    MATERIAL_RESERVATION_CREATE = "material_reservation:create"
    MATERIAL_RESERVATION_UPDATE = "material_reservation:update"
    MATERIAL_RESERVATION_DELETE = "material_reservation:delete"
    
    # Planning & Calendars
    PLANNING_READ = "planning:read"
    PLANNING_CREATE = "planning:create"
    PLANNING_UPDATE = "planning:update"
    CALENDAR_READ = "calendar:read"
    CALENDAR_CREATE = "calendar:create"
    CALENDAR_UPDATE = "calendar:update"
    
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
    
    # Equipment & OEE
    EQUIPMENT_READ = "equipment:read"
    EQUIPMENT_CREATE = "equipment:create"
    EQUIPMENT_UPDATE = "equipment:update"
    EQUIPMENT_DELETE = "equipment:delete"
    OEE_READ = "oee:read"
    OEE_MANAGE = "oee:manage"
    TELEMETRY_READ = "telemetry:read"
    TELEMETRY_WRITE = "telemetry:write"
    
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
    ERROR = "error"
