from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.password_recovery import (
    PasswordRecoveryCreate,
    PasswordRecoveryDecision,
    PasswordRecoveryApartmentOption,
    PasswordRecoveryHouseOption,
    PasswordRecoveryResetRequest,
    PasswordRecoveryResetResponse,
    PasswordRecoveryResponse,
)
from app.services.password_recovery_service import PasswordRecoveryService

router = APIRouter()


@router.get("/houses", response_model=list[PasswordRecoveryHouseOption])
def list_password_recovery_houses(
    query: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = PasswordRecoveryService(db)
    return service.list_house_options(query=query, limit=limit)


@router.get("/houses/{house_id}/apartments", response_model=list[PasswordRecoveryApartmentOption])
def list_password_recovery_apartments(
    house_id: int,
    db: Session = Depends(get_db),
):
    service = PasswordRecoveryService(db)
    return service.list_apartment_options(house_id)


@router.post("/requests", response_model=PasswordRecoveryResponse)
def create_password_recovery_request(
    payload: PasswordRecoveryCreate,
    db: Session = Depends(get_db),
):
    service = PasswordRecoveryService(db)
    return service.create_request(payload)


@router.get("/requests", response_model=list[PasswordRecoveryResponse])
def list_password_recovery_requests(
    status: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = PasswordRecoveryService(db)
    return service.list_requests(current_user=current_user, status=status, skip=skip, limit=limit)


@router.get("/requests/{request_id}", response_model=PasswordRecoveryResponse)
def get_password_recovery_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = PasswordRecoveryService(db)
    return service.get_request(request_id, current_user=current_user)


@router.post("/requests/{request_id}/reset", response_model=PasswordRecoveryResetResponse)
def reset_password_by_recovery_request(
    request_id: int,
    payload: PasswordRecoveryResetRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = PasswordRecoveryService(db)
    request_obj, temporary_password = service.reset_password(request_id, payload, current_user=current_user)
    return {"request": request_obj, "temporary_password": temporary_password}


@router.post("/requests/{request_id}/reject", response_model=PasswordRecoveryResponse)
def reject_password_recovery_request(
    request_id: int,
    payload: PasswordRecoveryDecision,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = PasswordRecoveryService(db)
    return service.reject_request(request_id, payload, current_user=current_user)
