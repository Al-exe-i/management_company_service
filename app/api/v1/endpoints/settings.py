from sqlalchemy.ext.asyncio import AsyncSession
from app.db.operations import run_db

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.app_settings import AppSettingsResponse, AppSettingsUpdate
from app.services.app_settings_service import AppSettingsService

router = APIRouter()


@router.get("/app", response_model=AppSettingsResponse)
async def read_app_settings(
    db: AsyncSession = Depends(get_db),
):
    def operation(db: Session):
        service = AppSettingsService(db)
        return service.get_settings()

    return await run_db(db, operation, AppSettingsResponse)


@router.patch("/app", response_model=AppSettingsResponse)
async def update_app_settings(
    data: AppSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        service = AppSettingsService(db)
        return service.update_settings(data, current_user)

    return await run_db(db, operation, AppSettingsResponse)


@router.post("/app/login-background", response_model=AppSettingsResponse)
async def upload_login_background(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        service = AppSettingsService(db)
        return service.upload_login_background(file, current_user)

    return await run_db(db, operation, AppSettingsResponse)


@router.delete("/app/login-background", response_model=AppSettingsResponse)
async def delete_login_background(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        service = AppSettingsService(db)
        return service.clear_login_background(current_user)

    return await run_db(db, operation, AppSettingsResponse)
