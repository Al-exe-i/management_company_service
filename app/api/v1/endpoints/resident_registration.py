from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.password_recovery import PasswordRecoveryApartmentOption, PasswordRecoveryHouseOption
from app.schemas.resident_registration import (
    ResidentRegistrationApproveRequest,
    ResidentRegistrationApproveResponse,
    ResidentRegistrationCreate,
    ResidentRegistrationDecision,
    ResidentRegistrationResponse,
)
from app.services.resident_registration_service import ResidentRegistrationService

router = APIRouter()


@router.get("/houses", response_model=list[PasswordRecoveryHouseOption])
def list_registration_houses(
    query: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = ResidentRegistrationService(db)
    return service.list_house_options(query=query, limit=limit)


@router.get("/houses/{house_id}/apartments", response_model=list[PasswordRecoveryApartmentOption])
def list_registration_apartments(
    house_id: int,
    db: Session = Depends(get_db),
):
    service = ResidentRegistrationService(db)
    return service.list_apartment_options(house_id)


@router.post("/requests", response_model=ResidentRegistrationResponse)
def create_registration_request(
    payload: ResidentRegistrationCreate,
    db: Session = Depends(get_db),
):
    service = ResidentRegistrationService(db)
    return service.create_request(payload)


@router.get("/requests", response_model=list[ResidentRegistrationResponse])
def list_registration_requests(
    status: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ResidentRegistrationService(db)
    return service.list_requests(current_user=current_user, status=status, skip=skip, limit=limit)


@router.get("/requests/{request_id}", response_model=ResidentRegistrationResponse)
def get_registration_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ResidentRegistrationService(db)
    return service.get_request(request_id, current_user=current_user)


@router.post("/requests/{request_id}/approve", response_model=ResidentRegistrationApproveResponse)
def approve_registration_request(
    request_id: int,
    payload: ResidentRegistrationApproveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ResidentRegistrationService(db)
    request_obj, user, temporary_password = service.approve_request(request_id, payload, current_user=current_user)
    return {"request": request_obj, "user": user, "temporary_password": temporary_password}


@router.post("/requests/{request_id}/reject", response_model=ResidentRegistrationResponse)
def reject_registration_request(
    request_id: int,
    payload: ResidentRegistrationDecision,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ResidentRegistrationService(db)
    return service.reject_request(request_id, payload, current_user=current_user)
