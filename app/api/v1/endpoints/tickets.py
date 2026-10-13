from sqlalchemy.ext.asyncio import AsyncSession
from app.db.operations import run_db

from fastapi import APIRouter, Body, Depends, HTTPException, File, UploadFile
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime

from app.api.dependencies import get_db, get_current_user
from app.schemas.ticket import (
    TicketAssign,
    TicketCancelRequest,
    TicketCreate,
    TicketExecutorReviewCreate,
    TicketExecutorReviewParticipant,
    TicketExecutorReviewResponse,
    TicketFileResponse,
    TicketResponse,
    TicketUpdate,
)
from app.services.ticket_service import TicketService
from app.models.user import User, UserRole
from app.schemas.history import HistoryResponse
from app.models.history import TicketHistory
from app.models.ticket import TicketPriority, TicketStatus
from app.services.notification_service import NotificationService

router = APIRouter()


def _executor_completed_ticket(ticket, executor_id: int) -> bool:
    return any(
        history.user_id == executor_id
        and str(history.new_status or "").lower() == TicketStatus.DONE.value
        for history in (ticket.history or [])
    )


def _ticket_response(ticket, current_user: User) -> TicketResponse:
    response = TicketResponse.model_validate(ticket)
    if ticket.status == TicketStatus.CANCELED:
        is_rejected = any(
            str(history.comment or "").strip().lower().startswith("заявка отклонена.")
            for history in (ticket.history or [])
        )
        response.status_label = "Отклонена" if is_rejected else "Отменена"
    if (
        response.author
        and response.author_id != current_user.id
        and not response.show_contact_phone
    ):
        response.author.contact_phone = None
    if current_user.role == UserRole.RESIDENT and response.author_id != current_user.id:
        response.external_contact_phone = None
    if (
        current_user.role == UserRole.EXECUTOR
        and ticket.executor_id != current_user.id
        and _executor_completed_ticket(ticket, current_user.id)
    ):
        response.status = TicketStatus.DONE
        response.status_label = "Выполнена Вами"
        response.executor_id = current_user.id
        response.executor = None
        response.result_comment = None
        response.resident_rating = None
        response.files = [
            file
            for file in response.files
            if str(file.kind or "").upper() != "AFTER"
        ]
        response.historical_executor_view = True
    return response


def _ticket_responses(tickets, current_user: User) -> list[TicketResponse]:
    return [_ticket_response(ticket, current_user) for ticket in tickets]


@router.post("/", response_model=TicketResponse)
async def create_ticket(
        ticket_in: TicketCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        if current_user.role == UserRole.AUDITOR:
            raise HTTPException(status_code=403, detail="Auditors cannot create tickets")

        service = TicketService(db)
        return _ticket_response(service.create_ticket(ticket_in, user=current_user), current_user)

    return await run_db(db, operation, TicketResponse)


@router.get("/", response_model=List[TicketResponse])
async def read_tickets(
        status: TicketStatus | None = None,
        house_id: int | None = None,
        executor_id: int | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        overdue_hours: int | None = None,
        priority: TicketPriority | None = None,
        limit: int = 100,
        skip: int = 0,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        service = TicketService(db)
        tickets = service.get_tickets(
            user=current_user,
            status=status,
            house_id=house_id,
            executor_id=executor_id,
            created_from=created_from,
            created_to=created_to,
            overdue_hours=overdue_hours,
            priority=priority,
            limit=limit,
            skip=skip,
        )
        return _ticket_responses(tickets, current_user)

    return await run_db(db, operation, List[TicketResponse])


@router.patch("/{ticket_id}/assign", response_model=TicketResponse)
async def assign_ticket(
        ticket_id: int,
        assign_data: TicketAssign,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        service = TicketService(db)
        return _ticket_response(service.assign_executor(ticket_id, assign_data, current_user), current_user)

    return await run_db(db, operation, TicketResponse)


@router.post("/{ticket_id}/photos", response_model=TicketFileResponse)
async def upload_ticket_photo(
        ticket_id: int,
        file: UploadFile = File(...),
        kind: str | None = None,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        service = TicketService(db)
        return service.upload_file(ticket_id, file, current_user, kind=kind)

    return await run_db(db, operation, TicketFileResponse)


@router.delete("/photos/{file_id}")
async def delete_ticket_photo(
        file_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        service = TicketService(db)
        return service.delete_file(file_id, current_user)

    return await run_db(db, operation, None)


@router.post("/{ticket_id}/cancel")
async def cancel_ticket(
    ticket_id: int,
    payload: TicketCancelRequest | None = Body(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        service = TicketService(db)
        return service.cancel_ticket(ticket_id, current_user, payload)

    return await run_db(db, operation, None)


@router.get("/{ticket_id}", response_model=TicketResponse)
async def read_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        service = TicketService(db)
        ticket = service.get_ticket_by_id(ticket_id, current_user)
        if current_user.role in [UserRole.ADMIN, UserRole.ADMIN_ASSISTANT, UserRole.DISPATCHER]:
            NotificationService(db).mark_ticket_created_read_for_staff(ticket_id)
        return _ticket_response(ticket, current_user)

    return await run_db(db, operation, TicketResponse)


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
async def update_ticket_status(
    ticket_id: int,
    status_data: TicketUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        service = TicketService(db)
        return _ticket_response(service.update_status(ticket_id, status_data, current_user), current_user)

    return await run_db(db, operation, TicketResponse)


@router.get("/{ticket_id}/history", response_model=List[HistoryResponse])
async def read_ticket_history(
        ticket_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        service = TicketService(db)
        ticket = service.get_ticket_by_id(ticket_id, current_user)

        if current_user.role == UserRole.RESIDENT and ticket.author_id != current_user.id:
            raise HTTPException(status_code=403, detail="Only ticket author can view history")

        query = (
            db.query(TicketHistory)
            .options(joinedload(TicketHistory.user))
            .filter(TicketHistory.ticket_id == ticket_id)
        )

        if current_user.role == UserRole.EXECUTOR:
            query = query.filter(
                or_(
                    TicketHistory.user_id == current_user.id,
                    and_(
                        TicketHistory.new_status == TicketStatus.CREATED.value,
                        TicketHistory.comment.ilike("Заявка создана%"),
                    ),
                )
            )

        history = query.order_by(TicketHistory.created_at.desc()).all()

        return history

    return await run_db(db, operation, List[HistoryResponse])


@router.get("/{ticket_id}/executor-reviews", response_model=List[TicketExecutorReviewParticipant])
async def read_ticket_executor_reviews(
        ticket_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        service = TicketService(db)
        return service.list_executor_reviews_for_ticket(ticket_id, current_user)

    return await run_db(db, operation, List[TicketExecutorReviewParticipant])


@router.post("/{ticket_id}/executor-reviews", response_model=TicketExecutorReviewResponse)
async def save_ticket_executor_review(
        ticket_id: int,
        payload: TicketExecutorReviewCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        service = TicketService(db)
        review = service.create_executor_review(ticket_id, payload, current_user)
        db.commit()
        db.refresh(review)
        return service._review_payload(review)

    return await run_db(db, operation, TicketExecutorReviewResponse)


@router.get("/history/all", response_model=List[HistoryResponse])
async def read_all_history(
        ticket_id: int | None = None,
        user_id: int | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        if current_user.role not in [UserRole.ADMIN, UserRole.DISPATCHER, UserRole.AUDITOR]:
            raise HTTPException(status_code=403, detail="Not enough permissions")

        q = db.query(TicketHistory).options(joinedload(TicketHistory.user))

        if ticket_id is not None:
            q = q.filter(TicketHistory.ticket_id == ticket_id)
        if user_id is not None:
            q = q.filter(TicketHistory.user_id == user_id)
        if created_from is not None:
            q = q.filter(TicketHistory.created_at >= created_from)
        if created_to is not None:
            q = q.filter(TicketHistory.created_at <= created_to)

        return q.order_by(TicketHistory.created_at.desc()).limit(1000).all()

    return await run_db(db, operation, List[HistoryResponse])
