"""nullable product stock levels

Northwind (and the shared OpenAPI definition) allow null for unitsInStock, unitsOnOrder
and reorderLevel.

Revision ID: 20261025_000001
Revises: 20260806_000001
Create Date: 2026-10-25 00:00:01

"""

import sqlalchemy as sa
from alembic import op

revision = "20261025_000001"
down_revision = "20260806_000001"
branch_labels = None
depends_on = None

_COLUMNS = ("unitsInStock", "unitsOnOrder", "reorderLevel")


def upgrade() -> None:
    with op.batch_alter_table("Products") as batch_op:
        for column in _COLUMNS:
            batch_op.alter_column(column, existing_type=sa.SmallInteger(), nullable=True)


def downgrade() -> None:
    for column in _COLUMNS:
        op.execute(f'UPDATE "Products" SET "{column}" = 0 WHERE "{column}" IS NULL')
    with op.batch_alter_table("Products") as batch_op:
        for column in _COLUMNS:
            batch_op.alter_column(column, existing_type=sa.SmallInteger(), nullable=False)
