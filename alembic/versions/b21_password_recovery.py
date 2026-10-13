"""password recovery requests

Revision ID: b21_password_recovery
Revises: b20_user_announcement_history
Create Date: 2026-06-18
"""
from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = "b21_password_recovery"
down_revision: Union[str, None] = "b20_user_announcement_history"
branch_labels: Union[str, None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("can_manage_password_recovery", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "users",
        sa.Column("must_change_password", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "app_settings",
        sa.Column("password_recovery_cooldown_minutes", sa.Integer(), nullable=False, server_default="5"),
    )
    op.create_table(
        "password_recovery_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("requester_login", sa.String(length=120), nullable=False),
        sa.Column("requester_name", sa.String(length=200), nullable=True),
        sa.Column("contact_phone", sa.String(length=60), nullable=False),
        sa.Column("house_address", sa.String(length=300), nullable=True),
        sa.Column("apartment", sa.String(length=40), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=24), nullable=False, server_default="open"),
        sa.Column("matched_user_id", sa.Integer(), nullable=True),
        sa.Column("processed_by_id", sa.Integer(), nullable=True),
        sa.Column("admin_comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("processed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["matched_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["processed_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_password_recovery_requests_id"), "password_recovery_requests", ["id"], unique=False)
    op.create_index(op.f("ix_password_recovery_requests_requester_login"), "password_recovery_requests", ["requester_login"], unique=False)
    op.create_index(op.f("ix_password_recovery_requests_status"), "password_recovery_requests", ["status"], unique=False)
    op.create_index(op.f("ix_password_recovery_requests_matched_user_id"), "password_recovery_requests", ["matched_user_id"], unique=False)
    op.create_index(op.f("ix_password_recovery_requests_processed_by_id"), "password_recovery_requests", ["processed_by_id"], unique=False)
    op.create_index(op.f("ix_password_recovery_requests_created_at"), "password_recovery_requests", ["created_at"], unique=False)
    op.alter_column("users", "can_manage_password_recovery", server_default=None)
    op.alter_column("users", "must_change_password", server_default=None)
    op.alter_column("app_settings", "password_recovery_cooldown_minutes", server_default=None)
    op.alter_column("password_recovery_requests", "status", server_default=None)
    op.alter_column("password_recovery_requests", "created_at", server_default=None)
    op.alter_column("password_recovery_requests", "updated_at", server_default=None)


def downgrade() -> None:
    op.drop_index(op.f("ix_password_recovery_requests_created_at"), table_name="password_recovery_requests")
    op.drop_index(op.f("ix_password_recovery_requests_processed_by_id"), table_name="password_recovery_requests")
    op.drop_index(op.f("ix_password_recovery_requests_matched_user_id"), table_name="password_recovery_requests")
    op.drop_index(op.f("ix_password_recovery_requests_status"), table_name="password_recovery_requests")
    op.drop_index(op.f("ix_password_recovery_requests_requester_login"), table_name="password_recovery_requests")
    op.drop_index(op.f("ix_password_recovery_requests_id"), table_name="password_recovery_requests")
    op.drop_table("password_recovery_requests")
    op.drop_column("app_settings", "password_recovery_cooldown_minutes")
    op.drop_column("users", "must_change_password")
    op.drop_column("users", "can_manage_password_recovery")
