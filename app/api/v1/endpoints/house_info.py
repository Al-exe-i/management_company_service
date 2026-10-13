from sqlalchemy.ext.asyncio import AsyncSession
from app.db.operations import run_db

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.house_info import (
    EmergencyContactCreate,
    EmergencyContactResponse,
    HouseEventCreate,
    HouseEventResponse,
    HouseInfoTypeCreate,
    HouseInfoTypeResponse,
    HouseScheduleCreate,
    HouseScheduleResponse,
)
from app.services.house_info_service import HouseInfoService

router = APIRouter()


@router.get("/types", response_model=List[HouseInfoTypeResponse])
async def read_house_info_types(
    type_group: str | None = None,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        service = HouseInfoService(db)
        return service.get_types(type_group=type_group, active_only=active_only)

    return await run_db(db, operation, List[HouseInfoTypeResponse])


@router.post("/types", response_model=HouseInfoTypeResponse)
async def create_house_info_type(
    payload: HouseInfoTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        service = HouseInfoService(db)
        return service.create_type(current_user, payload)

    return await run_db(db, operation, HouseInfoTypeResponse)


@router.delete("/types/{type_id}", response_model=HouseInfoTypeResponse)
async def delete_house_info_type(
    type_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        service = HouseInfoService(db)
        return service.delete_type(current_user, type_id)

    return await run_db(db, operation, HouseInfoTypeResponse)


@router.get("/events", response_model=List[HouseEventResponse])
async def read_house_events(
    house_id: int | None = None,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        service = HouseInfoService(db)
        return service.get_events(current_user, house_id=house_id, active_only=active_only)

    return await run_db(db, operation, List[HouseEventResponse])


@router.post("/events", response_model=HouseEventResponse)
async def create_house_event(
    payload: HouseEventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        service = HouseInfoService(db)
        return service.create_event(current_user, payload)

    return await run_db(db, operation, HouseEventResponse)


@router.patch("/events/{event_id}", response_model=HouseEventResponse)
async def update_house_event(
    event_id: int,
    payload: HouseEventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        service = HouseInfoService(db)
        return service.update_event(current_user, event_id, payload)

    return await run_db(db, operation, HouseEventResponse)


@router.delete("/events/{event_id}")
async def delete_house_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        service = HouseInfoService(db)
        return service.delete_event(current_user, event_id)

    return await run_db(db, operation, None)


@router.get("/contacts", response_model=List[EmergencyContactResponse])
async def read_emergency_contacts(
    house_id: int | None = None,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        service = HouseInfoService(db)
        return service.get_contacts(current_user, house_id=house_id, active_only=active_only)

    return await run_db(db, operation, List[EmergencyContactResponse])


@router.post("/contacts", response_model=EmergencyContactResponse)
async def create_emergency_contact(
    payload: EmergencyContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        service = HouseInfoService(db)
        return service.create_contact(current_user, payload)

    return await run_db(db, operation, EmergencyContactResponse)


@router.patch("/contacts/{contact_id}", response_model=EmergencyContactResponse)
async def update_emergency_contact(
    contact_id: int,
    payload: EmergencyContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        service = HouseInfoService(db)
        return service.update_contact(current_user, contact_id, payload)

    return await run_db(db, operation, EmergencyContactResponse)


@router.delete("/contacts/{contact_id}")
async def delete_emergency_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        service = HouseInfoService(db)
        return service.delete_contact(current_user, contact_id)

    return await run_db(db, operation, None)


@router.get("/schedules", response_model=List[HouseScheduleResponse])
async def read_house_schedules(
    house_id: int | None = None,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        service = HouseInfoService(db)
        return service.get_schedules(current_user, house_id=house_id, active_only=active_only)

    return await run_db(db, operation, List[HouseScheduleResponse])


@router.post("/schedules", response_model=HouseScheduleResponse)
async def create_house_schedule(
    payload: HouseScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        service = HouseInfoService(db)
        return service.create_schedule(current_user, payload)

    return await run_db(db, operation, HouseScheduleResponse)


@router.patch("/schedules/{schedule_id}", response_model=HouseScheduleResponse)
async def update_house_schedule(
    schedule_id: int,
    payload: HouseScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        service = HouseInfoService(db)
        return service.update_schedule(current_user, schedule_id, payload)

    return await run_db(db, operation, HouseScheduleResponse)


@router.delete("/schedules/{schedule_id}")
async def delete_house_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        service = HouseInfoService(db)
        return service.delete_schedule(current_user, schedule_id)

    return await run_db(db, operation, None)
