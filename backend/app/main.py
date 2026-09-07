from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys
from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.router import api_router
from app.models import User, Role, InventoryItem, ProductionOrder
from app.models.tenant import Tenant, TenantStatus, BillingPlan
from app.middleware.audit import AuditMiddleware


# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level=settings.LOG_LEVEL,
)


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Virtuoso MES - Manufacturing Execution System",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add Audit Middleware (after CORS, before routing)
    app.add_middleware(AuditMiddleware)
    
    # Exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    
    # Include routers
    app.include_router(api_router, prefix="/api/v1")
    
    # Startup event
    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting up Virtuoso MES...")

        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")

            from sqlalchemy import select
            from app.core.database import async_session_maker
            from app.core.security import get_password_hash
            from app.models.user import UserRole

            async with async_session_maker() as session:
                result = await session.execute(select(User).where(User.is_superuser == True))
                admin = result.scalar_one_or_none()

                if not admin:
                    admin_user = User(
                        email="admin@virtuoso.com",
                        username="admin",
                        full_name="System Administrator",
                        hashed_password=get_password_hash("admin123"),
                        role=UserRole.ADMIN,
                        is_active=True,
                        is_superuser=True
                    )
                    session.add(admin_user)
                    await session.commit()
                    logger.info("Default admin user created: admin / admin123")

                demo_result = await session.execute(
                    select(Tenant).where(Tenant.subdomain == "demo")
                )
                demo_tenant = demo_result.scalar_one_or_none()
                if not demo_tenant:
                    demo_tenant = Tenant(
                        id="00000000-0000-0000-0000-000000000001",
                        name="Demo Company",
                        subdomain="demo",
                        status=TenantStatus.ACTIVE,
                        billing_plan=BillingPlan.FREE,
                        admin_email="demo@virtuoso.com",
                    )
                    session.add(demo_tenant)
                    await session.flush()

                demo_user_result = await session.execute(
                    select(User).where(User.username == "demo")
                )
                demo_user = demo_user_result.scalar_one_or_none()
                if not demo_user:
                    demo_user = User(
                        email="demo@virtuoso.com",
                        username="demo",
                        full_name="Demo User",
                        hashed_password=get_password_hash("demo12345"),
                        role=UserRole.ADMIN,
                        is_active=True,
                        tenant_id=demo_tenant.id,
                    )
                    session.add(demo_user)
                    await session.flush()

                if demo_tenant.admin_user_id != demo_user.id:
                    demo_tenant.admin_user_id = demo_user.id
                await session.commit()

            from app.services.demo_data import seed_demo_data
            await seed_demo_data()
            logger.info("Virtuoso MES started successfully!")
        except Exception as exc:
            logger.warning(f"Database startup initialization skipped because the configured DB is unavailable: {exc}")
    
    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Shutting down Virtuoso MES...")
        await engine.dispose()
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
