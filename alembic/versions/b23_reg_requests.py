"""resident registration requests

Revision ID: b23_reg_requests
Revises: b22_password_recovery_location
Create Date: 2026-06-19
"""
from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = "b23_reg_requests"
down_revision: Union[str, None] = "b22_password_recovery_location"
branch_labels: Union[str, None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("can_approve_registrations", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_table(
        "resident_registration_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("login", sa.String(length=120), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("contact_phone", sa.String(length=60), nullable=False),
        sa.Column("house_id", sa.Integer(), nullable=False),
        sa.Column("apartment_id", sa.Integer(), nullable=False),
        sa.Column("house_address", sa.String(length=300), nullable=True),
        sa.Column("apartment", sa.String(length=40), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=24), nullable=False, server_default="open"),
        sa.Column("created_user_id", sa.Integer(), nullable=True),
        sa.Column("processed_by_id", sa.Integer(), nullable=True),
        sa.Column("admin_comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("processed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["apartment_id"], ["apartments.id"]),
        sa.ForeignKeyConstraint(["created_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["house_id"], ["houses.id"]),
        sa.ForeignKeyConstraint(["processed_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_resident_registration_requests_id"), "resident_registration_requests", ["id"], unique=False)
    op.create_index(op.f("ix_resident_registration_requests_login"), "resident_registration_requests", ["login"], unique=False)
    op.create_index(op.f("ix_resident_registration_requests_house_id"), "resident_registration_requests", ["house_id"], unique=False)
    op.create_index(op.f("ix_resident_registration_requests_apartment_id"), "resident_registration_requests", ["apartment_id"], unique=False)
    op.create_index(op.f("ix_resident_registration_requests_status"), "resident_registration_requests", ["status"], unique=False)
    op.create_index(op.f("ix_resident_registration_requests_created_user_id"), "resident_registration_requests", ["created_user_id"], unique=False)
    op.create_index(op.f("ix_resident_registration_requests_processed_by_id"), "resident_registration_requests", ["processed_by_id"], unique=False)
    op.create_index(op.f("ix_resident_registration_requests_created_at"), "resident_registration_requests", ["created_at"], unique=False)
    op.alter_column("users", "can_approve_registrations", server_default=None)
    op.alter_column("resident_registration_requests", "status", server_default=None)
    op.alter_column("resident_registration_requests", "created_at", server_default=None)
    op.alter_column("resident_registration_requests", "updated_at", server_default=None)


def downgrade() -> None:
    op.drop_index(op.f("ix_resident_registration_requests_created_at"), table_name="resident_registration_requests")
    op.drop_index(op.f("ix_resident_registration_requests_processed_by_id"), table_name="resident_registration_requests")
    op.drop_index(op.f("ix_resident_registration_requests_created_user_id"), table_name="resident_registration_requests")
    op.drop_index(op.f("ix_resident_registration_requests_status"), table_name="resident_registration_requests")
    op.drop_index(op.f("ix_resident_registration_requests_apartment_id"), table_name="resident_registration_requests")
    op.drop_index(op.f("ix_resident_registration_requests_house_id"), table_name="resident_registration_requests")
    op.drop_index(op.f("ix_resident_registration_requests_login"), table_name="resident_registration_requests")
    op.drop_index(op.f("ix_resident_registration_requests_id"), table_name="resident_registration_requests")
    op.drop_table("resident_registration_requests")
    op.drop_column("users", "can_approve_registrations")
