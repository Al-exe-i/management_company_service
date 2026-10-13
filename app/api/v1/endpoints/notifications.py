from sqlalchemy.ext.asyncio import AsyncSession
from app.db.operations import run_db

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.notification import (
    NotificationResponse,
    NotificationSummaryResponse,
    PushDeviceTokenResponse,
    PushTokenDeactivateRequest,
    PushTokenRegisterRequest,
)
from app.services.notification_service import NotificationService
from app.services.push_notification_service import PushNotificationService

router = APIRouter()


@router.get("/", response_model=list[NotificationResponse])
async def list_my_notifications(
    unread_only: bool = False,
    notif_type: str | None = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        service = NotificationService(db)
        return service.list_my(
            current_user.id,
            unread_only=unread_only,
            notif_type=notif_type,
            skip=skip,
            limit=limit,
        )

    return await run_db(db, operation, list[NotificationResponse])


@router.get("/summary", response_model=NotificationSummaryResponse)
async def get_notifications_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        service = NotificationService(db)
        return service.get_summary(current_user.id)

    return await run_db(db, operation, NotificationSummaryResponse)


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        service = NotificationService(db)
        return service.mark_read(current_user.id, notification_id)

    return await run_db(db, operation, NotificationResponse)


@router.patch("/read-all")
async def mark_all_notifications_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        service = NotificationService(db)
        count = service.mark_all_read(current_user.id)
        return {"status": "ok", "marked": count}

    return await run_db(db, operation, None)


@router.post("/push-token", response_model=PushDeviceTokenResponse)
async def register_push_token(
    payload: PushTokenRegisterRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        service = PushNotificationService(db)
        return service.register_token(
            user=current_user,
            token=payload.token,
            platform=payload.platform,
            device_name=payload.device_name,
        )

    return await run_db(db, operation, PushDeviceTokenResponse)


@router.delete("/push-token")
async def deactivate_push_token(
    payload: PushTokenDeactivateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        service = PushNotificationService(db)
        deactivated = service.deactivate_token(current_user, payload.token)
        return {"status": "ok", "deactivated": deactivated}

    return await run_db(db, operation, None)
