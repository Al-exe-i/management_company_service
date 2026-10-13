from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base


class TicketExecutorReview(Base):
    __tablename__ = "ticket_executor_reviews"
    __table_args__ = (
        UniqueConstraint("ticket_id", "executor_id", "resident_id", name="uq_ticket_executor_review_once"),
    )

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False, index=True)
    executor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    resident_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    review_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    ticket = relationship("Ticket", back_populates="executor_reviews")
    executor = relationship("User", foreign_keys=[executor_id])
    resident = relationship("User", foreign_keys=[resident_id])
