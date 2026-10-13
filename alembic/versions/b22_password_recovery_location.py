"""password recovery location links

Revision ID: b22_password_recovery_location
Revises: b21_password_recovery
Create Date: 2026-06-19
"""
from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = "b22_password_recovery_location"
down_revision: Union[str, None] = "b21_password_recovery"
branch_labels: Union[str, None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    op.add_column("password_recovery_requests", sa.Column("house_id", sa.Integer(), nullable=True))
    op.add_column("password_recovery_requests", sa.Column("apartment_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_password_recovery_requests_house_id"), "password_recovery_requests", ["house_id"], unique=False)
    op.create_index(op.f("ix_password_recovery_requests_apartment_id"), "password_recovery_requests", ["apartment_id"], unique=False)
    op.create_foreign_key(
        "fk_password_recovery_requests_house_id_houses",
        "password_recovery_requests",
        "houses",
        ["house_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_password_recovery_requests_apartment_id_apartments",
        "password_recovery_requests",
        "apartments",
        ["apartment_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_password_recovery_requests_apartment_id_apartments", "password_recovery_requests", type_="foreignkey")
    op.drop_constraint("fk_password_recovery_requests_house_id_houses", "password_recovery_requests", type_="foreignkey")
    op.drop_index(op.f("ix_password_recovery_requests_apartment_id"), table_name="password_recovery_requests")
    op.drop_index(op.f("ix_password_recovery_requests_house_id"), table_name="password_recovery_requests")
    op.drop_column("password_recovery_requests", "apartment_id")
    op.drop_column("password_recovery_requests", "house_id")
