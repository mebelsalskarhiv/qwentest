"""Add tenant scope to MVP inventory and production data.

Revision ID: 4d7c1e9a2b10
Revises: ff0ac631235a
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4d7c1e9a2b10"
down_revision: Union[str, None] = "ff0ac631235a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DEMO_TENANT_ID = "00000000-0000-0000-0000-000000000001"


def upgrade() -> None:
    tenant_id = sa.Column("tenant_id", sa.String(length=36), nullable=True)
    for table in (
        "inventory_categories",
        "suppliers",
        "inventory_items",
        "stock_movements",
        "products",
        "work_centers",
        "production_orders",
        "production_operations",
        "bill_of_materials",
        "material_consumptions",
        "employees",
        "departments",
        "customers",
        "stations",
    ):
        op.add_column(table, tenant_id.copy())
        op.create_index(
            op.f(f"ix_{table}_tenant_id"), table, ["tenant_id"], unique=False
        )
        op.create_foreign_key(
            f"fk_{table}_tenant_id_tenants", table, "tenants", ["tenant_id"], ["id"]
        )
        op.execute(
            sa.text(f"UPDATE {table} SET tenant_id = :tenant_id WHERE tenant_id IS NULL")
            .bindparams(tenant_id=DEMO_TENANT_ID)
        )


def downgrade() -> None:
    for table in (
        "material_consumptions",
        "bill_of_materials",
        "production_operations",
        "production_orders",
        "work_centers",
        "products",
        "stock_movements",
        "inventory_items",
        "suppliers",
        "inventory_categories",
        "stations",
        "customers",
        "departments",
        "employees",
    ):
        op.drop_constraint(f"fk_{table}_tenant_id_tenants", table, type_="foreignkey")
        op.drop_index(op.f(f"ix_{table}_tenant_id"), table_name=table)
        op.drop_column(table, "tenant_id")
