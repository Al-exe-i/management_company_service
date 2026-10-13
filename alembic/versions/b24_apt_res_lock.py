"""apartment resident addition lock

Revision ID: b24_apt_res_lock
Revises: b23_reg_requests
Create Date: 2026-06-20 00:00:00.000000
"""

from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = "b24_apt_res_lock"
down_revision: Union[str, None] = "b23_reg_requests"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "blocks_apartment_resident_additions",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.alter_column("users", "blocks_apartment_resident_additions", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "blocks_apartment_resident_additions")
