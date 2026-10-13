"""ticket executor reviews

Revision ID: b26_exec_reviews
Revises: b25_exec_rating
Create Date: 2026-06-22
"""

from alembic import op
import sqlalchemy as sa


revision = "b26_exec_reviews"
down_revision = "b25_exec_rating"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ticket_executor_reviews",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ticket_id", sa.Integer(), nullable=False),
        sa.Column("executor_id", sa.Integer(), nullable=False),
        sa.Column("resident_id", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("review_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["executor_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["resident_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["ticket_id"], ["tickets.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ticket_id", "executor_id", "resident_id", name="uq_ticket_executor_review_once"),
    )
    op.create_index(op.f("ix_ticket_executor_reviews_id"), "ticket_executor_reviews", ["id"], unique=False)
    op.create_index(op.f("ix_ticket_executor_reviews_ticket_id"), "ticket_executor_reviews", ["ticket_id"], unique=False)
    op.create_index(op.f("ix_ticket_executor_reviews_executor_id"), "ticket_executor_reviews", ["executor_id"], unique=False)
    op.create_index(op.f("ix_ticket_executor_reviews_resident_id"), "ticket_executor_reviews", ["resident_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_ticket_executor_reviews_resident_id"), table_name="ticket_executor_reviews")
    op.drop_index(op.f("ix_ticket_executor_reviews_executor_id"), table_name="ticket_executor_reviews")
    op.drop_index(op.f("ix_ticket_executor_reviews_ticket_id"), table_name="ticket_executor_reviews")
    op.drop_index(op.f("ix_ticket_executor_reviews_id"), table_name="ticket_executor_reviews")
    op.drop_table("ticket_executor_reviews")
