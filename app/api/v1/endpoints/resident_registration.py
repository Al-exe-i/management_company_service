from sqlalchemy.ext.asyncio import AsyncSession
from app.db.operations import run_db

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
async def list_registration_houses(
    query: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    def operation(db: Session):
        service = ResidentRegistrationService(db)
        return service.list_house_options(query=query, limit=limit)

    return await run_db(db, operation, list[PasswordRecoveryHouseOption])


@router.get("/houses/{house_id}/apartments", response_model=list[PasswordRecoveryApartmentOption])
async def list_registration_apartments(
    house_id: int,
    db: AsyncSession = Depends(get_db),
):
    def operation(db: Session):
        service = ResidentRegistrationService(db)
        return service.list_apartment_options(house_id)

    return await run_db(db, operation, list[PasswordRecoveryApartmentOption])


@router.post("/requests", response_model=ResidentRegistrationResponse)
async def create_registration_request(
    payload: ResidentRegistrationCreate,
    db: AsyncSession = Depends(get_db),
):
    def operation(db: Session):
        service = ResidentRegistrationService(db)
        return service.create_request(payload)

    return await run_db(db, operation, ResidentRegistrationResponse)


@router.get("/requests", response_model=list[ResidentRegistrationResponse])
async def list_registration_requests(
    status: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        service = ResidentRegistrationService(db)
        return service.list_requests(current_user=current_user, status=status, skip=skip, limit=limit)

    return await run_db(db, operation, list[ResidentRegistrationResponse])


@router.get("/requests/{request_id}", response_model=ResidentRegistrationResponse)
async def get_registration_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        service = ResidentRegistrationService(db)
        return service.get_request(request_id, current_user=current_user)

    return await run_db(db, operation, ResidentRegistrationResponse)


@router.post("/requests/{request_id}/approve", response_model=ResidentRegistrationApproveResponse)
async def approve_registration_request(
    request_id: int,
    payload: ResidentRegistrationApproveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        service = ResidentRegistrationService(db)
        request_obj, user, temporary_password = service.approve_request(request_id, payload, current_user=current_user)
        return {"request": request_obj, "user": user, "temporary_password": temporary_password}

    return await run_db(db, operation, ResidentRegistrationApproveResponse)


@router.post("/requests/{request_id}/reject", response_model=ResidentRegistrationResponse)
async def reject_registration_request(
    request_id: int,
    payload: ResidentRegistrationDecision,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        service = ResidentRegistrationService(db)
        return service.reject_request(request_id, payload, current_user=current_user)

    return await run_db(db, operation, ResidentRegistrationResponse)
