"""executor resident rating

Revision ID: b25_exec_rating
Revises: b24_apt_res_lock
Create Date: 2026-06-21
"""

from alembic import op
import sqlalchemy as sa


revision = "b25_exec_rating"
down_revision = "b24_apt_res_lock"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tickets", sa.Column("resident_rating", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("tickets", "resident_rating")
