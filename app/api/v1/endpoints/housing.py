from sqlalchemy.ext.asyncio import AsyncSession
from app.db.operations import run_db

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User, UserRole
from app.schemas.location import (
    ApartmentCreate,
    ApartmentGenerateRequest,
    ApartmentResponse,
    ApartmentUpdate,
    HouseCreate,
    HouseEntranceCreate,
    HouseEntranceResponse,
    HouseEntranceUpdate,
    HouseResponse,
    HouseStructureResponse,
    HouseUpdate,
    HouseWithStructureCreateRequest,
)
from app.services.house_service import HouseService
from app.services.permissions import can_manage_houses

router = APIRouter()


def _ensure_house_manager(current_user: User):
    if can_manage_houses(current_user):
        return
    raise HTTPException(status_code=403, detail="Not enough permissions")


@router.post("/", response_model=HouseResponse)
async def create_house(
    house_in: HouseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        _ensure_house_manager(current_user)

        service = HouseService(db)
        return service.create_house(house_in)

    return await run_db(db, operation, HouseResponse)


@router.post("/with-structure", response_model=HouseStructureResponse)
async def create_house_with_structure(
    payload: HouseWithStructureCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        _ensure_house_manager(current_user)

        service = HouseService(db)
        return service.create_house_with_structure(payload)

    return await run_db(db, operation, HouseStructureResponse)


@router.get("/", response_model=List[HouseResponse])
async def read_houses(db: AsyncSession = Depends(get_db)):
    def operation(db: Session):
        service = HouseService(db)
        return service.get_all_houses()

    return await run_db(db, operation, List[HouseResponse])


@router.get("/{house_id}/structure", response_model=HouseStructureResponse)
async def read_house_structure(
    house_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        service = HouseService(db)
        return service.get_house_structure(house_id)

    return await run_db(db, operation, HouseStructureResponse)


@router.put("/{house_id}", response_model=HouseResponse)
async def update_house(
    house_id: int,
    house_in: HouseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        _ensure_house_manager(current_user)

        service = HouseService(db)
        return service.update_house(house_id, house_in)

    return await run_db(db, operation, HouseResponse)


@router.delete("/{house_id}")
async def delete_house(
    house_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Удалять дома может только администратор")

        service = HouseService(db)
        return service.delete_house(house_id)

    return await run_db(db, operation, None)


@router.get("/{house_id}/entrances", response_model=List[HouseEntranceResponse])
async def read_house_entrances(
    house_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        service = HouseService(db)
        return service.list_entrances(house_id)

    return await run_db(db, operation, List[HouseEntranceResponse])


@router.post("/{house_id}/entrances", response_model=HouseEntranceResponse)
async def create_house_entrance(
    house_id: int,
    payload: HouseEntranceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        _ensure_house_manager(current_user)

        service = HouseService(db)
        return service.create_entrance(house_id, payload)

    return await run_db(db, operation, HouseEntranceResponse)


@router.put("/entrances/{entrance_id}", response_model=HouseEntranceResponse)
async def update_house_entrance(
    entrance_id: int,
    payload: HouseEntranceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        _ensure_house_manager(current_user)

        service = HouseService(db)
        return service.update_entrance(entrance_id, payload)

    return await run_db(db, operation, HouseEntranceResponse)


@router.delete("/entrances/{entrance_id}")
async def delete_house_entrance(
    entrance_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        _ensure_house_manager(current_user)

        service = HouseService(db)
        return service.delete_entrance(entrance_id)

    return await run_db(db, operation, None)


@router.get("/{house_id}/apartments", response_model=List[ApartmentResponse])
async def read_house_apartments(
    house_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        service = HouseService(db)
        return service.list_apartments_for_house(house_id)

    return await run_db(db, operation, List[ApartmentResponse])


@router.get("/entrances/{entrance_id}/apartments", response_model=List[ApartmentResponse])
async def read_entrance_apartments(
    entrance_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        service = HouseService(db)
        return service.list_apartments_for_entrance(entrance_id)

    return await run_db(db, operation, List[ApartmentResponse])


@router.post("/entrances/{entrance_id}/apartments", response_model=ApartmentResponse)
async def create_entrance_apartment(
    entrance_id: int,
    payload: ApartmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        _ensure_house_manager(current_user)

        service = HouseService(db)
        return service.create_apartment(entrance_id, payload)

    return await run_db(db, operation, ApartmentResponse)


@router.post("/entrances/{entrance_id}/generate-apartments", response_model=List[ApartmentResponse])
async def generate_entrance_apartments(
    entrance_id: int,
    payload: ApartmentGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        _ensure_house_manager(current_user)

        service = HouseService(db)
        return service.generate_apartments(entrance_id, payload)

    return await run_db(db, operation, List[ApartmentResponse])


@router.put("/apartments/{apartment_id}", response_model=ApartmentResponse)
async def update_apartment(
    apartment_id: int,
    payload: ApartmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        _ensure_house_manager(current_user)

        service = HouseService(db)
        return service.update_apartment(apartment_id, payload)

    return await run_db(db, operation, ApartmentResponse)


@router.delete("/apartments/{apartment_id}")
async def delete_apartment(
    apartment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        _ensure_house_manager(current_user)

        service = HouseService(db)
        return service.delete_apartment(apartment_id)

    return await run_db(db, operation, None)
