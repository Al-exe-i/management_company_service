"""add missing ticket_files.kind

Revision ID: d450d1c926f5
Revises: 73f6fae7681b
Create Date: 2026-02-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d450d1c926f5"
down_revision: Union[str, Sequence[str], None] = "73f6fae7681b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'ticketfilekind') THEN
            CREATE TYPE ticketfilekind AS ENUM ('BEFORE', 'AFTER', 'LEGACY');
        END IF;
    END $$;
    """)


    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name='ticket_files' AND column_name='kind'
        ) THEN
            ALTER TABLE ticket_files
            ADD COLUMN kind ticketfilekind NOT NULL DEFAULT 'LEGACY';
        END IF;
    END $$;
    """)





def downgrade() -> None:
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name='ticket_files' AND column_name='kind'
        ) THEN
            ALTER TABLE ticket_files DROP COLUMN kind;
        END IF;
    END $$;
    """)
