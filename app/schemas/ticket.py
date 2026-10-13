from datetime import datetime

from pydantic import BaseModel, Field

from app.models.ticket import TicketPriority, TicketStatus
from app.schemas.location import ApartmentResponse


class UserShortResponse(BaseModel):
    id: int
    full_name: str
    login: str | None = None
    phone: str | None = None
    contact_phone: str | None = None
    role: str | None = None
    house_id: int | None = None
    apartment_id: int | None = None
    specialty: str | None = None
    banned_until: datetime | None = None

    class Config:
        from_attributes = True


class HouseShortResponse(BaseModel):
    id: int
    address: str
    city: str | None = None

    class Config:
        from_attributes = True


class CategoryShortResponse(BaseModel):
    id: int
    name: str
    category_type: str = "problem"

    class Config:
        from_attributes = True


class TicketFileResponse(BaseModel):
    id: int
    file_path: str
    kind: str | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class TicketBase(BaseModel):
    title: str
    description: str | None = None
    house_id: int | None = None
    apartment_id: int | None = None
    apartment: str | None = None
    category_id: int | None = None
    place_category_id: int | None = None
    priority: TicketPriority = TicketPriority.NORMAL
    show_contact_phone: bool = False
    external_contact_phone: str | None = None


class TicketCreate(TicketBase):
    created_for_user_id: int | None = None


class TicketUpdate(BaseModel):
    status: TicketStatus | None = None
    executor_id: int | None = None
    description: str | None = None
    comment: str | None = None
    resident_rating: int | None = Field(default=None, ge=1, le=5)


class TicketAssign(BaseModel):
    executor_id: int | None = None
    executor_profile_id: int | None = None


class TicketCancelRequest(BaseModel):
    reason: str | None = None


class TicketExecutorReviewCreate(BaseModel):
    executor_id: int
    rating: int = Field(..., ge=1, le=5)
    review_text: str | None = Field(default=None, max_length=2000)


class TicketExecutorReviewExecutor(BaseModel):
    id: int
    full_name: str
    role: str | None = None
    specialty: str | None = None

    class Config:
        from_attributes = True


class TicketExecutorReviewResponse(BaseModel):
    id: int | None = None
    ticket_id: int
    ticket_title: str | None = None
    executor_id: int
    resident_id: int | None = None
    rating: int | None = None
    review_text: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    executor: TicketExecutorReviewExecutor | None = None
    legacy: bool = False

    class Config:
        from_attributes = True


class TicketExecutorReviewParticipant(BaseModel):
    executor: TicketExecutorReviewExecutor
    review: TicketExecutorReviewResponse | None = None
    can_review: bool = False


class TicketResponse(TicketBase):
    id: int
    status: TicketStatus
    status_label: str | None = None
    author_id: int
    executor_id: int | None = None
    created_at: datetime
    is_external_request: bool = False

    house: HouseShortResponse | None = None
    apartment_ref: ApartmentResponse | None = None
    category: CategoryShortResponse | None = None
    place_category: CategoryShortResponse | None = None
    author: UserShortResponse | None = None
    executor: UserShortResponse | None = None

    result_comment: str | None = None
    resident_rating: int | None = None
    files: list[TicketFileResponse] = []
    historical_executor_view: bool = False

    class Config:
        from_attributes = True
