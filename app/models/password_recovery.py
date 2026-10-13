from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class PasswordRecoveryRequest(Base):
    __tablename__ = "password_recovery_requests"

    id = Column(Integer, primary_key=True, index=True)
    requester_login = Column(String(120), nullable=False, index=True)
    requester_name = Column(String(200), nullable=True)
    contact_phone = Column(String(60), nullable=False)
    house_id = Column(Integer, ForeignKey("houses.id"), nullable=True, index=True)
    apartment_id = Column(Integer, ForeignKey("apartments.id"), nullable=True, index=True)
    house_address = Column(String(300), nullable=True)
    apartment = Column(String(40), nullable=True)
    message = Column(Text, nullable=True)
    status = Column(String(24), nullable=False, default="open", index=True)
    matched_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    processed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    admin_comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)

    matched_user = relationship("User", foreign_keys=[matched_user_id])
    processed_by = relationship("User", foreign_keys=[processed_by_id])
    house = relationship("House", foreign_keys=[house_id])
    apartment_ref = relationship("Apartment", foreign_keys=[apartment_id])

    @property
    def processed_by_name(self) -> str | None:
        return self.processed_by.full_name if self.processed_by else None

    @staticmethod
    def _digits(value: str | None) -> str:
        return "".join(ch for ch in str(value or "") if ch.isdigit())

    @property
    def _address_matches(self) -> bool | None:
        if not self.matched_user:
            return None
        if not self.house_id and not self.apartment_id:
            return None
        if self.house_id and self.matched_user.house_id != self.house_id:
            return False
        if self.apartment_id:
            if self.matched_user.apartment_id:
                return self.matched_user.apartment_id == self.apartment_id
            if self.apartment_ref and self.matched_user.apartment_number:
                return str(self.matched_user.apartment_number) == str(self.apartment_ref.apartment_number)
            return False
        return True

    @property
    def verification_status(self) -> str:
        if not self.matched_user:
            return "not_found"

        request_phone = self._digits(self.contact_phone)
        profile_phone = self._digits(self.matched_user.contact_phone)
        address_matches = self._address_matches

        if profile_phone:
            if request_phone == profile_phone:
                return "phone_match"
            if address_matches is True:
                return "phone_mismatch_address_match"
            return "phone_mismatch"

        if address_matches is True:
            return "address_match"
        if address_matches is False:
            return "address_mismatch"
        return "manual_check"

    @property
    def verification_note(self) -> str:
        notes = {
            "not_found": "Пользователь с таким логином не найден.",
            "phone_match": "Логин и контактный телефон совпали с профилем.",
            "phone_mismatch_address_match": "Телефон отличается от профиля, но выбранный адрес совпадает.",
            "phone_mismatch": "Контактный телефон не совпадает с телефоном в профиле.",
            "address_match": "Телефон в профиле не указан, выбранный адрес совпадает.",
            "address_mismatch": "Телефон в профиле не указан, выбранный адрес не совпадает.",
            "manual_check": "Телефон в профиле не указан, нужна ручная проверка администратором.",
        }
        return notes.get(self.verification_status, "Нужна ручная проверка администратором.")
