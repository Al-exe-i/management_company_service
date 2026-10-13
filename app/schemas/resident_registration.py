from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.location import ApartmentResponse, HouseResponse
from app.schemas.user import UserResponse


class ResidentRegistrationCreate(BaseModel):
    login: str = Field(..., min_length=1, max_length=120)
    full_name: str = Field(..., min_length=1, max_length=200)
    contact_phone: str = Field(..., min_length=3, max_length=60)
    house_id: int
    apartment_id: int
    message: str | None = Field(default=None, max_length=1000)


class ResidentRegistrationDecision(BaseModel):
    admin_comment: str | None = Field(default=None, max_length=1000)


class ResidentRegistrationApproveRequest(ResidentRegistrationDecision):
    temporary_password: str | None = Field(default=None, max_length=64)


class ResidentRegistrationResponse(BaseModel):
    id: int
    login: str
    full_name: str
    contact_phone: str
    house_id: int
    apartment_id: int
    house_address: str | None = None
    apartment: str | None = None
    message: str | None = None
    status: str
    created_user_id: int | None = None
    created_user_name: str | None = None
    processed_by_id: int | None = None
    processed_by_name: str | None = None
    admin_comment: str | None = None
    house: HouseResponse | None = None
    apartment_ref: ApartmentResponse | None = None
    created_at: datetime
    updated_at: datetime
    processed_at: datetime | None = None

    class Config:
        from_attributes = True


class ResidentRegistrationApproveResponse(BaseModel):
    request: ResidentRegistrationResponse
    user: UserResponse
    temporary_password: str
