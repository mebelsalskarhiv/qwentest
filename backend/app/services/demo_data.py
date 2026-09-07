from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker
from app.models.enums import UserRole
from app.models.hr import Customer, Department, Employee, Station
from app.models.inventory import InventoryCategory, InventoryItem, InventoryItemType, Supplier
from app.models.production import (
    ProductionOrder,
    ProductionOrderPriority,
    ProductionOrderStatus,
    Product,
    WorkCenter,
)
from app.models.tenant import Tenant


async def seed_demo_data() -> None:
    """Create a small, repeatable dataset for the demo tenant."""
    async with async_session_maker() as session:
        tenant = (await session.execute(
            select(Tenant).where(Tenant.subdomain == "demo")
        )).scalar_one_or_none()
        if not tenant:
            return

        existing_product = (await session.execute(
            select(Product).where(Product.sku == "DEMO-PRD-001")
        )).scalar_one_or_none()
        if existing_product:
            return

        categories = []
        for index, (name, description) in enumerate([
            ("Листовой металл", "Материалы для раскроя и гибки"),
            ("Комплектующие", "Детали и узлы для сборки"),
            ("Расходные материалы", "Материалы производственного цикла"),
        ], start=1):
            category = InventoryCategory(
                name=f"Демо: {name}",
                description=description,
                is_active=True,
            )
            session.add(category)
            await session.flush()
            categories.append(category)

        supplier = Supplier(
            name="Демо-поставщик металла",
            code="DEMO-SUP-001",
            contact_person="Анна Смирнова",
            email="demo-supplier@example.com",
            phone="+7 495 000-00-01",
            is_active=True,
        )
        session.add(supplier)
        await session.flush()

        materials = [
            ("DEMO-MAT-001", "Лист стальной 2 мм", InventoryItemType.RAW_MATERIAL, "кг", 840, 120, 185.0),
            ("DEMO-MAT-002", "Профиль алюминиевый 40x40", InventoryItemType.RAW_MATERIAL, "м", 320, 80, 420.0),
            ("DEMO-MAT-003", "Крепёжный комплект М8", InventoryItemType.COMPONENT, "компл.", 1250, 200, 95.0),
            ("DEMO-MAT-004", "Порошковая краска белая", InventoryItemType.CONSUMABLE, "кг", 95, 25, 680.0),
        ]
        for index, (sku, name, item_type, unit, stock, reorder, price) in enumerate(materials):
            session.add(InventoryItem(
                sku=sku,
                name=name,
                description="Демо-позиция склада",
                item_type=item_type,
                category_id=categories[index % len(categories)].id,
                unit_of_measure=unit,
                min_stock_level=reorder,
                max_stock_level=stock * 2,
                current_stock=stock,
                reserved_stock=round(stock * 0.18, 1),
                available_stock=round(stock * 0.82, 1),
                reorder_point=reorder,
                reorder_quantity=reorder * 2,
                cost_price=price,
                supplier_id=supplier.id,
                location=f"Склад А-{index + 1:02d}",
                barcode=f"46000000000{index + 1}",
                is_active=True,
            ))

        departments = []
        for code, name in [
            ("DEMO-CNC", "Участок ЧПУ"),
            ("DEMO-ASM", "Сборочный участок"),
            ("DEMO-QC", "Отдел контроля качества"),
        ]:
            department = Department(code=code, name=name, description="Демо-подразделение", is_active=True)
            session.add(department)
            await session.flush()
            departments.append(department)

        for index, (first_name, last_name, position) in enumerate([
            ("Иван", "Петров", "Оператор станка"),
            ("Мария", "Соколова", "Мастер смены"),
            ("Алексей", "Волков", "Контролёр ОТК"),
        ]):
            session.add(Employee(
                employee_code=f"DEMO-EMP-{index + 1:03d}",
                first_name=first_name,
                last_name=last_name,
                position=position,
                department_id=departments[index].id,
                email=f"demo.employee{index + 1}@example.com",
                phone=f"+7 495 000-00-1{index}",
                hire_date=datetime.utcnow() - timedelta(days=180 + index * 45),
                is_active=True,
            ))

        session.add_all([
            Customer(code="DEMO-CUS-001", name="ООО Промтех", contact_person="Олег Орлов", email="sales@promtech.example", is_active=True),
            Customer(code="DEMO-CUS-002", name="Завод Север", contact_person="Елена Крылова", email="orders@sever.example", is_active=True),
        ])

        work_centers = []
        for code, name, capacity in [
            ("DEMO-WC-01", "Лазерный раскрой", 16),
            ("DEMO-WC-02", "Гибка металла", 12),
            ("DEMO-WC-03", "Сборка изделий", 20),
        ]:
            work_center = WorkCenter(code=code, name=name, description="Демо-рабочий центр", capacity=capacity, efficiency=0.92, is_active=True)
            session.add(work_center)
            await session.flush()
            work_centers.append(work_center)

        session.add_all([
            Station(code="DEMO-ST-01", name="Лазерный станок L-01", description="Демо-станция раскроя", work_center_id=work_centers[0].id, delivery_mode="mounted", ip_address="192.168.10.21", status="online", is_active=True),
            Station(code="DEMO-ST-02", name="Гибочный пресс G-01", description="Демо-станция гибки", work_center_id=work_centers[1].id, delivery_mode="smb", ip_address="192.168.10.22", status="maintenance", is_active=True),
            Station(code="DEMO-ST-03", name="Сборочный пост S-01", description="Демо-сборочная станция", work_center_id=work_centers[2].id, delivery_mode="mounted", ip_address="192.168.10.23", status="online", is_active=True),
        ])

        products = []
        for sku, name, price in [
            ("DEMO-PRD-001", "Корпус контроллера X100", 45000),
            ("DEMO-PRD-002", "Монтажная панель M200", 28500),
            ("DEMO-PRD-003", "Защитный кожух K300", 19800),
        ]:
            product = Product(sku=sku, name=name, description="Демо-изделие Virtuoso MES", category="Металлоконструкции", unit_of_measure="шт", standard_cost=price * 0.62, selling_price=price, lead_time_days=7, is_active=True)
            session.add(product)
            await session.flush()
            products.append(product)

        orders = [
            ("DEMO-PO-001", products[0], 24, ProductionOrderStatus.IN_PROGRESS, ProductionOrderPriority.HIGH, work_centers[0]),
            ("DEMO-PO-002", products[1], 60, ProductionOrderStatus.RELEASED, ProductionOrderPriority.MEDIUM, work_centers[1]),
            ("DEMO-PO-003", products[2], 18, ProductionOrderStatus.PLANNED, ProductionOrderPriority.URGENT, work_centers[2]),
            ("DEMO-PO-004", products[0], 12, ProductionOrderStatus.COMPLETED, ProductionOrderPriority.LOW, work_centers[0]),
        ]
        for number, product, quantity, status, priority, work_center in orders:
            session.add(ProductionOrder(
                order_number=number,
                product_id=product.id,
                quantity_planned=quantity,
                quantity_completed=quantity if status == ProductionOrderStatus.COMPLETED else round(quantity * 0.45),
                status=status,
                priority=priority,
                work_center_id=work_center.id,
                scheduled_start=datetime.utcnow() - timedelta(days=1),
                scheduled_end=datetime.utcnow() + timedelta(days=5),
                notes="Демо-заказ для презентации системы",
                is_active=True,
            ))

        await session.commit()
