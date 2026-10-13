from sqlalchemy.ext.asyncio import AsyncSession
from app.db.operations import run_db

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.remark import RemarkStatus
from app.schemas.remark import RemarkCreate, RemarkResponse
from app.services.remark_service import RemarkService

router = APIRouter()


@router.post("/", response_model=RemarkResponse)
async def create_remark(
    data: RemarkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        service = RemarkService(db)
        return service.create_remark(data, current_user)

    return await run_db(db, operation, RemarkResponse)


@router.get("/sent", response_model=list[RemarkResponse])
async def list_sent(
    skip: int = 0,
    limit: int = 100,
    status: RemarkStatus | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        service = RemarkService(db)
        return service.list_sent(current_user, skip=skip, limit=limit, status=status)

    return await run_db(db, operation, list[RemarkResponse])


@router.get("/my", response_model=list[RemarkResponse])
async def list_my(
    skip: int = 0,
    limit: int = 100,
    status: RemarkStatus | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        service = RemarkService(db)
        return service.list_my(current_user, skip=skip, limit=limit, status=status)

    return await run_db(db, operation, list[RemarkResponse])



@router.get("/all", response_model=list[RemarkResponse])
async def list_all(
    skip: int = 0,
    limit: int = 200,
    status: RemarkStatus | None = None,
    issuer_id: int | None = None,
    executor_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        service = RemarkService(db)
        return service.list_all(
            current_user=current_user,
            skip=skip,
            limit=limit,
            status=status,
            issuer_id=issuer_id,
            executor_id=executor_id
        )

    return await run_db(db, operation, list[RemarkResponse])


@router.get("/{remark_id}", response_model=RemarkResponse)
async def get_remark(
    remark_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        service = RemarkService(db)
        return service.get_remark(remark_id, current_user)

    return await run_db(db, operation, RemarkResponse)


@router.post("/{remark_id}/cancel", response_model=RemarkResponse)
async def cancel_remark(
    remark_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    def operation(db: Session):
        service = RemarkService(db)
        return service.cancel_remark(remark_id, current_user)
    return await run_db(db, operation, RemarkResponse)
