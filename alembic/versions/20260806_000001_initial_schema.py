"""initial schema

Revision ID: 20260806_000001
Revises: 
Create Date: 2026-08-06 00:00:01

"""

from alembic import op
import sqlalchemy as sa


revision = "20260806_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "Categories",
        sa.Column("categoryID", sa.Integer(), primary_key=True),
        sa.Column("categoryName", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("picture", sa.LargeBinary(), nullable=True),
    )

    op.create_table(
        "Customers",
        sa.Column("customerID", sa.String(length=32), primary_key=True),
        sa.Column("companyName", sa.String(length=255), nullable=True),
        sa.Column("contactName", sa.String(length=255), nullable=True),
        sa.Column("contactTitle", sa.String(length=255), nullable=True),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=255), nullable=True),
        sa.Column("region", sa.String(length=255), nullable=True),
        sa.Column("postalCode", sa.String(length=64), nullable=True),
        sa.Column("country", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=64), nullable=True),
        sa.Column("fax", sa.String(length=64), nullable=True),
    )

    op.create_table(
        "Employees",
        sa.Column("employeeID", sa.Integer(), primary_key=True),
        sa.Column("lastName", sa.String(length=255), nullable=True),
        sa.Column("firstName", sa.String(length=255), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("titleOfCourtesy", sa.String(length=255), nullable=True),
        sa.Column("birthDate", sa.DateTime(), nullable=True),
        sa.Column("hireDate", sa.DateTime(), nullable=True),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=255), nullable=True),
        sa.Column("region", sa.String(length=255), nullable=True),
        sa.Column("postalCode", sa.String(length=64), nullable=True),
        sa.Column("country", sa.String(length=255), nullable=True),
        sa.Column("homePhone", sa.String(length=64), nullable=True),
        sa.Column("extension", sa.String(length=64), nullable=True),
        sa.Column("photo", sa.LargeBinary(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("reportsTo", sa.Integer(), nullable=True),
        sa.Column("photoPath", sa.String(length=512), nullable=True),
    )

    op.create_table(
        "Orders",
        sa.Column("orderID", sa.Integer(), primary_key=True),
        sa.Column("customerID", sa.String(length=32), nullable=True),
        sa.Column("employeeID", sa.Integer(), nullable=True),
        sa.Column("orderDate", sa.DateTime(), nullable=True),
        sa.Column("requiredDate", sa.DateTime(), nullable=True),
        sa.Column("shippedDate", sa.DateTime(), nullable=True),
        sa.Column("shipVia", sa.Integer(), nullable=True),
        sa.Column("freight", sa.Float(), nullable=True),
        sa.Column("shipName", sa.String(length=255), nullable=True),
        sa.Column("shipAddress", sa.String(length=255), nullable=True),
        sa.Column("shipCity", sa.String(length=255), nullable=True),
        sa.Column("shipRegion", sa.String(length=255), nullable=True),
        sa.Column("shipPostalCode", sa.String(length=64), nullable=True),
        sa.Column("shipCountry", sa.String(length=255), nullable=True),
    )

    op.create_table(
        "Products",
        sa.Column("productID", sa.Integer(), primary_key=True),
        sa.Column("productName", sa.String(length=255), nullable=True),
        sa.Column("supplierID", sa.Integer(), nullable=True),
        sa.Column("categoryID", sa.Integer(), nullable=True),
        sa.Column("quantityPerUnit", sa.String(length=255), nullable=True),
        sa.Column("unitPrice", sa.Float(), nullable=True),
        sa.Column("unitsInStock", sa.SmallInteger(), nullable=False),
        sa.Column("unitsOnOrder", sa.SmallInteger(), nullable=False),
        sa.Column("reorderLevel", sa.SmallInteger(), nullable=False),
        sa.Column("discontinued", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.create_table(
        "Shippers",
        sa.Column("shipperID", sa.Integer(), primary_key=True),
        sa.Column("companyName", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=64), nullable=True),
    )

    op.create_table(
        "Suppliers",
        sa.Column("supplierID", sa.Integer(), primary_key=True),
        sa.Column("companyName", sa.String(length=255), nullable=True),
        sa.Column("contactName", sa.String(length=255), nullable=True),
        sa.Column("contactTitle", sa.String(length=255), nullable=True),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=255), nullable=True),
        sa.Column("region", sa.String(length=255), nullable=True),
        sa.Column("postalCode", sa.String(length=64), nullable=True),
        sa.Column("country", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=64), nullable=True),
        sa.Column("fax", sa.String(length=64), nullable=True),
        sa.Column("homePage", sa.Text(), nullable=True),
    )

    op.create_table(
        "Order Details",
        sa.Column("orderID", sa.Integer(), primary_key=True),
        sa.Column("productID", sa.Integer(), primary_key=True),
        sa.Column("unitPrice", sa.Float(), nullable=False),
        sa.Column("quantity", sa.SmallInteger(), nullable=False),
        sa.Column("discount", sa.Float(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("Order Details")
    op.drop_table("Suppliers")
    op.drop_table("Shippers")
    op.drop_table("Products")
    op.drop_table("Orders")
    op.drop_table("Employees")
    op.drop_table("Customers")
    op.drop_table("Categories")
