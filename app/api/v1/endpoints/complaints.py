from sqlalchemy.ext.asyncio import AsyncSession
from app.db.operations import run_db

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.dependencies import get_db, get_current_user
from app.core.profanity import ensure_clean_text
from app.models.user import User, UserRole
from app.models.complaint import TicketComplaint, ComplaintStatus
from app.schemas.complaint import TicketComplaintResponse, ComplaintResolve

router = APIRouter()


def _ensure_staff(user: User) -> None:
    if user.role not in [UserRole.ADMIN, UserRole.DISPATCHER, UserRole.AUDITOR]:
        raise HTTPException(status_code=403, detail="Not enough permissions")


@router.get("/", response_model=list[TicketComplaintResponse])
async def list_complaints(
        status: ComplaintStatus | None = None,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        """Список всех жалоб (для диспетчера/аудитора/админа)."""
        _ensure_staff(current_user)

        q = db.query(TicketComplaint)
        if status is not None:
            q = q.filter(TicketComplaint.status == status)

        return q.order_by(TicketComplaint.created_at.desc()).limit(500).all()

    return await run_db(db, operation, list[TicketComplaintResponse])


@router.patch("/{complaint_id}/resolve", response_model=TicketComplaintResponse)
async def resolve_complaint(
        complaint_id: int,
        data: ComplaintResolve,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        """Закрыть/отклонить жалобу (диспетчер/админ/аудитор)."""
        _ensure_staff(current_user)

        complaint = db.query(TicketComplaint).filter(TicketComplaint.id == complaint_id).first()
        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")

        ensure_clean_text(data.resolution_comment)

        complaint.status = data.status
        complaint.resolution_comment = data.resolution_comment
        complaint.resolver_id = current_user.id
        complaint.resolved_at = datetime.utcnow()

        db.commit()
        db.refresh(complaint)
        return complaint

    return await run_db(db, operation, TicketComplaintResponse)
