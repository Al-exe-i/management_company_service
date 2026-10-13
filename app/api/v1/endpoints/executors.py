from sqlalchemy.ext.asyncio import AsyncSession
from app.db.operations import run_db

from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User, UserRole
from app.schemas.executor import (
    ExecutorAnalyticsResponse,
    ExecutorAvailabilityResponse,
    ExecutorCreateRequest,
    ExecutorDayOffCreate,
    ExecutorDayOffResponse,
    ExecutorProfileResponse,
    ExecutorUpdateRequest,
    ExecutorWorkScheduleCreate,
    ExecutorWorkScheduleResponse,
    SpecialtyCreate,
    SpecialtyResponse,
)
from app.schemas.ticket import TicketExecutorReviewResponse
from app.services.executor_availability import moscow_today
from app.services.executor_service import ExecutorService
from app.services.ticket_service import TicketService
from app.services.permissions import can_create_users, can_manage_executor_schedules, is_staff_like

router = APIRouter()


def _ensure_staff(current_user: User):
    if not is_staff_like(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")


def _ensure_admin(current_user: User):
    if not can_manage_executor_schedules(current_user):
        raise HTTPException(status_code=403, detail="Only admin can do this")


def _ensure_can_create_executor(current_user: User):
    if not can_create_users(current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")


@router.get("/specialties", response_model=List[SpecialtyResponse])
async def list_specialties(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        _ensure_staff(current_user)
        service = ExecutorService(db)
        return service.list_specialties()

    return await run_db(db, operation, List[SpecialtyResponse])


@router.post("/specialties", response_model=SpecialtyResponse)
async def create_specialty(
    payload: SpecialtyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        _ensure_admin(current_user)
        service = ExecutorService(db)
        return service.create_specialty(payload)

    return await run_db(db, operation, SpecialtyResponse)


@router.delete("/specialties/{specialty_id}")
async def delete_specialty(
    specialty_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        _ensure_admin(current_user)
        service = ExecutorService(db)
        service.delete_specialty(specialty_id)
        return {"ok": True}

    return await run_db(db, operation, None)


@router.get("/", response_model=List[ExecutorProfileResponse])
async def list_executors(
    house_id: int | None = None,
    active_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        _ensure_staff(current_user)
        service = ExecutorService(db)
        return service.list_executors(house_id=house_id, active_only=active_only)

    return await run_db(db, operation, List[ExecutorProfileResponse])


@router.get("/availability", response_model=List[ExecutorAvailabilityResponse])
async def list_executor_availability(
    target_date: date | None = None,
    house_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        _ensure_staff(current_user)
        service = ExecutorService(db)
        return service.list_availability(target_date=target_date or moscow_today(), house_id=house_id)

    return await run_db(db, operation, List[ExecutorAvailabilityResponse])


@router.get("/me/profile", response_model=ExecutorProfileResponse)
async def get_my_executor_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        service = ExecutorService(db)
        return service.get_executor_for_user(current_user)

    return await run_db(db, operation, ExecutorProfileResponse)


@router.get("/me/reviews", response_model=List[TicketExecutorReviewResponse])
async def get_my_executor_reviews(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        service = TicketService(db)
        return service.list_reviews_for_executor(current_user)

    return await run_db(db, operation, List[TicketExecutorReviewResponse])


@router.patch("/me/profile", response_model=ExecutorProfileResponse)
async def update_my_executor_profile(
    payload: ExecutorUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        service = ExecutorService(db)
        return service.update_own_executor_profile(current_user, payload)

    return await run_db(db, operation, ExecutorProfileResponse)


@router.put("/me/schedules", response_model=List[ExecutorWorkScheduleResponse])
async def replace_my_executor_schedules(
    payload: List[ExecutorWorkScheduleCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        service = ExecutorService(db)
        return service.replace_own_work_schedules(current_user, payload)

    return await run_db(db, operation, List[ExecutorWorkScheduleResponse])


@router.post("/me/days-off", response_model=ExecutorDayOffResponse)
async def create_my_executor_day_off(
    payload: ExecutorDayOffCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        service = ExecutorService(db)
        return service.add_own_day_off(current_user, payload)

    return await run_db(db, operation, ExecutorDayOffResponse)


@router.delete("/me/days-off/{day_off_id}")
async def delete_my_executor_day_off(
    day_off_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        service = ExecutorService(db)
        return service.delete_own_day_off(current_user, day_off_id)

    return await run_db(db, operation, None)


@router.get("/{executor_id}", response_model=ExecutorProfileResponse)
async def get_executor(
    executor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        _ensure_staff(current_user)
        service = ExecutorService(db)
        return service.get_executor(executor_id)

    return await run_db(db, operation, ExecutorProfileResponse)


@router.get("/{executor_id}/analytics", response_model=ExecutorAnalyticsResponse)
async def get_executor_analytics(
    executor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        _ensure_staff(current_user)
        service = ExecutorService(db)
        return service.get_executor_analytics(executor_id)

    return await run_db(db, operation, ExecutorAnalyticsResponse)


@router.post("/", response_model=ExecutorProfileResponse)
async def create_executor(
    payload: ExecutorCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        _ensure_can_create_executor(current_user)
        service = ExecutorService(db)
        return service.create_executor(payload)

    return await run_db(db, operation, ExecutorProfileResponse)


@router.patch("/{executor_id}", response_model=ExecutorProfileResponse)
async def update_executor(
    executor_id: int,
    payload: ExecutorUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        _ensure_admin(current_user)
        service = ExecutorService(db)
        return service.update_executor(executor_id, payload)

    return await run_db(db, operation, ExecutorProfileResponse)


@router.put("/{executor_id}/schedules", response_model=List[ExecutorWorkScheduleResponse])
async def replace_executor_schedules(
    executor_id: int,
    payload: List[ExecutorWorkScheduleCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        _ensure_admin(current_user)
        service = ExecutorService(db)
        return service.replace_work_schedules(executor_id, payload)

    return await run_db(db, operation, List[ExecutorWorkScheduleResponse])


@router.get("/{executor_id}/days-off", response_model=List[ExecutorDayOffResponse])
async def list_executor_days_off(
    executor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        _ensure_staff(current_user)
        service = ExecutorService(db)
        return service.list_day_offs(executor_id)

    return await run_db(db, operation, List[ExecutorDayOffResponse])


@router.post("/{executor_id}/days-off", response_model=ExecutorDayOffResponse)
async def create_executor_day_off(
    executor_id: int,
    payload: ExecutorDayOffCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        _ensure_admin(current_user)
        service = ExecutorService(db)
        return service.add_day_off(executor_id, payload)

    return await run_db(db, operation, ExecutorDayOffResponse)
