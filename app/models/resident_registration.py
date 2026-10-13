from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class ResidentRegistrationRequest(Base):
    __tablename__ = "resident_registration_requests"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(120), nullable=False, index=True)
    full_name = Column(String(200), nullable=False)
    contact_phone = Column(String(60), nullable=False)
    house_id = Column(Integer, ForeignKey("houses.id"), nullable=False, index=True)
    apartment_id = Column(Integer, ForeignKey("apartments.id"), nullable=False, index=True)
    house_address = Column(String(300), nullable=True)
    apartment = Column(String(40), nullable=True)
    message = Column(Text, nullable=True)
    status = Column(String(24), nullable=False, default="open", index=True)
    created_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    processed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    admin_comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)

    house = relationship("House", foreign_keys=[house_id])
    apartment_ref = relationship("Apartment", foreign_keys=[apartment_id])
    created_user = relationship("User", foreign_keys=[created_user_id])
    processed_by = relationship("User", foreign_keys=[processed_by_id])

    @property
    def processed_by_name(self) -> str | None:
        return self.processed_by.full_name if self.processed_by else None

    @property
    def created_user_name(self) -> str | None:
        return self.created_user.full_name if self.created_user else None
