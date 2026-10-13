"""dd announcement flags

Revision ID: 6fc7e53f3e24
Revises: 9590ba5dc44b
Create Date: 2026-02-09 21:14:49.414274

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa



revision: str = '6fc7e53f3e24'
down_revision: Union[str, Sequence[str], None] = '9590ba5dc44b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column('announcements', sa.Column('is_important', sa.Boolean(), nullable=True))
    op.add_column('announcements', sa.Column('is_active', sa.Boolean(), nullable=True))



def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column('announcements', 'is_active')
    op.drop_column('announcements', 'is_important')

