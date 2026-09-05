"""
Скрипт для генерации демо-данных системы Virtuoso MES.
Создает продукты, заказы, материалы, сотрудников и станции для демонстрации Kanban.
"""
import asyncio
import sys
from datetime import datetime, timedelta
from decimal import Decimal
import random

sys.path.insert(0, "/workspace/backend")

from app.core.database import async_session_maker, engine, Base
from app.models.user import User, UserRole
from app.models.tenant import Tenant, TenantStatus, BillingPlan
from app.models.inventory import InventoryCategory, InventoryItem, Supplier, StockMovement
from app.models.production import Product, WorkCenter, ProductionOrder, ProductionOrderStatus, ProductionOperation, BillOfMaterial, MaterialConsumption
from app.models.hr import Department, Employee, Customer, Station
from app.core.security import get_password_hash
from sqlalchemy import select


async def seed_demo_data():
    """Генерирует полные демо-данные для системы."""
    
    # Сначала создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Таблицы БД созданы")
    
    async with async_session_maker() as session:
        print("🌱 Начинаем генерацию демо-данных...")
        
        # 1. Создаем демо-тенанта
        tenant = Tenant(
            name="Demo Company",
            subdomain="demo",
            custom_domain=None,
            status=TenantStatus.ACTIVE,
            billing_plan=BillingPlan.PROFESSIONAL,
            ssl_enabled=True,
            letsencrypt_email="admin@demo.com",
        )
        session.add(tenant)
        await session.flush()
        print(f"✅ Создан тенант: {tenant.name} (ID: {tenant.id})")
        
        # 2. Создаем категории материалов
        categories_data = [
            ("Raw Materials", "Сырье и основные материалы"),
            ("Components", "Компоненты и запчасти"),
            ("Packaging", "Упаковочные материалы"),
            ("Tools", "Инструменты и оснастка"),
            ("Consumables", "Расходные материалы"),
        ]
        
        categories = {}
        for name, desc in categories_data:
            cat = InventoryCategory(name=name, description=desc, tenant_id=tenant.id)
            session.add(cat)
            await session.flush()
            categories[name] = cat
        print(f"✅ Создано {len(categories)} категорий материалов")
        
        # 3. Создаем поставщиков
        suppliers_data = [
            ("MetalCorp Inc.", "metal@corp.com", "+1-555-0101", "Поставщик металла"),
            ("PlasticWorld", "info@plasticworld.com", "+1-555-0102", "Пластиковые компоненты"),
            ("ElectroSupply", "sales@electrosupply.com", "+1-555-0103", "Электроника"),
            ("PackagePro", "orders@packagepro.com", "+1-555-0104", "Упаковка"),
        ]
        
        suppliers = {}
        for name, email, phone, desc in suppliers_data:
            supplier = Supplier(
                name=name,
                contact_email=email,
                contact_phone=phone,
                address=f"{random.randint(100, 999)} Industrial Ave, City, State",
                description=desc,
                tenant_id=tenant.id,
            )
            session.add(supplier)
            await session.flush()
            suppliers[name] = supplier
        print(f"✅ Создано {len(suppliers)} поставщиков")
        
        # 4. Создаем материалы
        materials_data = [
            ("Steel Sheet 2mm", "Raw Materials", "кг", Decimal("2.50"), 500, 100),
            ("Aluminum Rod 10mm", "Raw Materials", "м", Decimal("5.75"), 200, 50),
            ("Plastic Granulate ABS", "Raw Materials", "кг", Decimal("3.20"), 1000, 200),
            ("Bearing 6205", "Components", "шт", Decimal("12.50"), 300, 50),
            ("Electric Motor 500W", "Components", "шт", Decimal("85.00"), 50, 10),
            ("Control Board PCB", "Components", "шт", Decimal("45.00"), 100, 20),
            ("Cardboard Box 50x40x30", "Packaging", "шт", Decimal("1.20"), 2000, 500),
            ("Stretch Film", "Packaging", "рул", Decimal("8.50"), 100, 20),
            ("Drill Bit 6mm", "Tools", "шт", Decimal("3.50"), 150, 30),
            ("Lubricant Oil", "Consumables", "л", Decimal("15.00"), 80, 20),
        ]
        
        items = {}
        for name, cat_name, unit, price, qty, reorder in materials_data:
            item = InventoryItem(
                sku=f"MAT-{random.randint(1000, 9999)}",
                name=name,
                description=f"Demo {name}",
                category_id=categories[cat_name].id,
                unit_of_measure=unit,
                unit_price=price,
                quantity_in_stock=qty,
                reorder_point=reorder,
                supplier_id=suppliers[list(suppliers.keys())[random.randint(0, len(suppliers)-1)]].id,
                tenant_id=tenant.id,
            )
            session.add(item)
            await session.flush()
            items[name] = item
        print(f"✅ Создано {len(items)} материалов")
        
        # 5. Создаем отделы
        departments_data = [
            "Production",
            "Quality Control",
            "Warehouse",
            "Maintenance",
            "Engineering",
            "Sales",
        ]
        
        depts = {}
        for name in departments_data:
            dept = Department(name=name, tenant_id=tenant.id)
            session.add(dept)
            await session.flush()
            depts[name] = dept
        print(f"✅ Создано {len(depts)} отделов")
        
        # 6. Создаем сотрудников
        employees_data = [
            ("John", "Smith", "Operator", "Production"),
            ("Maria", "Garcia", "Senior Operator", "Production"),
            ("Alex", "Johnson", "QC Inspector", "Quality Control"),
            ("David", "Williams", "Warehouse Manager", "Warehouse"),
            ("Sarah", "Brown", "Maintenance Tech", "Maintenance"),
            ("Michael", "Davis", "Engineer", "Engineering"),
            ("Emma", "Miller", "Sales Manager", "Sales"),
        ]
        
        employees = {}
        for first, last, position, dept_name in employees_data:
            emp = Employee(
                employee_id=f"EMP{random.randint(1000, 9999)}",
                first_name=first,
                last_name=last,
                position=position,
                department_id=depts[dept_name].id,
                email=f"{first.lower()}.{last.lower()}@demo.com",
                phone=f"+1-555-{random.randint(1000, 9999)}",
                hire_date=datetime.now() - timedelta(days=random.randint(30, 365)),
                tenant_id=tenant.id,
            )
            session.add(emp)
            await session.flush()
            employees[f"{first} {last}"] = emp
        print(f"✅ Создано {len(employees)} сотрудников")
        
        # 7. Создаем рабочих центры
        workcenters_data = [
            ("CNC Machining", "CNC станки для обработки металла"),
            ("Assembly Line A", "Линия сборки продукции A"),
            ("Assembly Line B", "Линия сборки продукции B"),
            ("Painting Booth", "Камера покраски"),
            ("Quality Inspection", "Зона контроля качества"),
            ("Packaging Station", "Упаковочная станция"),
        ]
        
        workcenters = {}
        for name, desc in workcenters_data:
            wc = WorkCenter(
                name=name,
                description=desc,
                capacity_per_hour=Decimal(str(random.uniform(10, 50))),
                tenant_id=tenant.id,
            )
            session.add(wc)
            await session.flush()
            workcenters[name] = wc
        print(f"✅ Создано {len(workcenters)} рабочих центров")
        
        # 8. Создаем станции
        stations_data = [
            ("Station-001", "CNC Machining"),
            ("Station-002", "Assembly Line A"),
            ("Station-003", "Assembly Line B"),
            ("Station-004", "Painting Booth"),
            ("Station-005", "Quality Inspection"),
            ("Station-006", "Packaging Station"),
        ]
        
        stations = {}
        for name, wc_name in stations_data:
            station = Station(
                code=name,
                name=f"Workstation {name}",
                description=f"Demo station at {wc_name}",
                work_center_id=workcenters[wc_name].id,
                status="online",
                is_active=True,
            )
            session.add(station)
            await session.flush()
            stations[name] = station
        print(f"✅ Создано {len(stations)} станций")
        
        # 9. Создаем продукты
        products_data = [
            ("Industrial Pump X100", "Промышленный насос для жидкостей", Decimal("450.00")),
            ("Hydraulic Motor M200", "Гидравлический мотор", Decimal("680.00")),
            ("Control Panel CP-500", "Панель управления", Decimal("1200.00")),
            ("Conveyor Belt Unit CB-100", "Конвейерная лента", Decimal("890.00")),
            ("Air Compressor AC-300", "Воздушный компрессор", Decimal("1500.00")),
        ]
        
        products = {}
        for name, desc, price in products_data:
            product = Product(
                sku=f"PRD-{random.randint(1000, 9999)}",
                name=name,
                description=desc,
                unit_price=price,
                tenant_id=tenant.id,
            )
            session.add(product)
            await session.flush()
            products[name] = product
        print(f"✅ Создано {len(products)} продуктов")
        
        # 10. Создаем производственные заказы
        orders_data = [
            ("Industrial Pump X100", 20, "pending"),
            ("Hydraulic Motor M200", 15, "in_progress"),
            ("Control Panel CP-500", 10, "pending"),
            ("Conveyor Belt Unit CB-100", 8, "in_progress"),
            ("Air Compressor AC-300", 5, "completed"),
            ("Industrial Pump X100", 25, "pending"),
            ("Hydraulic Motor M200", 12, "quality_check"),
        ]
        
        orders = {}
        for product_name, qty, status_str in orders_data:
            due_date = datetime.now() + timedelta(days=random.randint(3, 14))
            order = ProductionOrder(
                order_number=f"PO-{random.randint(10000, 99999)}",
                product_id=products[product_name].id,
                quantity=qty,
                status=status_str,
                priority=random.choice(["low", "medium", "high", "urgent"]),
                due_date=due_date,
                tenant_id=tenant.id,
            )
            session.add(order)
            await session.flush()
            orders[f"{product_name}-{qty}"] = order
        print(f"✅ Создано {len(orders)} производственных заказов")
        
        # 11. Создаем операции для заказов
        operations_templates = [
            ("Cutting", "CNC Machining", 2.5),
            ("Machining", "CNC Machining", 4.0),
            ("Assembly", "Assembly Line A", 3.0),
            ("Wiring", "Assembly Line B", 2.0),
            ("Painting", "Painting Booth", 1.5),
            ("Inspection", "Quality Inspection", 1.0),
            ("Packaging", "Packaging Station", 0.5),
        ]
        
        op_count = 0
        for order_key, order in orders.items():
            if order.status == "completed":
                continue
            
            for op_name, wc_name, duration in operations_templates[:random.randint(3, 6)]:
                operation = ProductionOperation(
                    production_order_id=order.id,
                    work_center_id=workcenters[wc_name].id,
                    sequence=op_count % len(operations_templates) + 1,
                    name=op_name,
                    estimated_duration=Decimal(str(duration)),
                    status="pending" if op_count % 3 != 0 else "completed",
                    tenant_id=tenant.id,
                )
                session.add(operation)
                op_count += 1
        
        await session.flush()
        print(f"✅ Создано {op_count} производственных операций")
        
        # 12. Создаем клиентов
        customers_data = [
            ("Acme Industries", "manufacturing@acme.com", "+1-555-1001", "Промышленное оборудование"),
            ("GlobalTech Corp", "procurement@globaltech.com", "+1-555-1002", "Технологии"),
            ("BuildRight Construction", "orders@buildright.com", "+1-555-1003", "Строительство"),
            ("AutoParts Ltd", "supply@autoparts.com", "+1-555-1004", "Автозапчасти"),
            ("FoodProcess Inc", "equipment@foodprocess.com", "+1-555-1005", "Пищевая промышленность"),
        ]
        
        customers = {}
        for name, email, phone, industry in customers_data:
            customer = Customer(
                name=name,
                email=email,
                phone=phone,
                address=f"{random.randint(100, 999)} Business Blvd, City, State",
                industry=industry,
                tenant_id=tenant.id,
            )
            session.add(customer)
            await session.flush()
            customers[name] = customer
        print(f"✅ Создано {len(customers)} клиентов")
        
        # 13. Создаем движения запасов (история)
        movement_count = 0
        for item_name, item in list(items.items())[:5]:
            for _ in range(random.randint(2, 4)):
                movement = StockMovement(
                    item_id=item.id,
                    movement_type=random.choice(["receipt", "consumption"]),
                    quantity=random.randint(10, 100),
                    reference=f"REF-{random.randint(1000, 9999)}",
                    notes=f"Demo movement for {item_name}",
                    tenant_id=tenant.id,
                )
                session.add(movement)
                movement_count += 1
        
        await session.flush()
        print(f"✅ Создано {movement_count} движений запасов")
        
        # Commit всех данных
        await session.commit()
        print("\n🎉 Демо-данные успешно созданы!")
        print(f"\n📊 Итого:")
        print(f"   - Тенантов: 1")
        print(f"   - Категорий: {len(categories)}")
        print(f"   - Поставщиков: {len(suppliers)}")
        print(f"   - Материалов: {len(items)}")
        print(f"   - Отделов: {len(depts)}")
        print(f"   - Сотрудников: {len(employees)}")
        print(f"   - Рабочих центров: {len(workcenters)}")
        print(f"   - Станций: {len(stations)}")
        print(f"   - Продуктов: {len(products)}")
        print(f"   - Заказов: {len(orders)}")
        print(f"   - Операций: {op_count}")
        print(f"   - Клиентов: {len(customers)}")
        print(f"   - Движений запасов: {movement_count}")
        print(f"\n🔐 Логин для демо: admin@virtuoso.com / admin123")


if __name__ == "__main__":
    asyncio.run(seed_demo_data())
