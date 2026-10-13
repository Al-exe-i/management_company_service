from sqlalchemy.ext.asyncio import AsyncSession
from app.db.operations import run_db

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.message import (
    MessageContactResponse,
    MessageConversationCreate,
    MessageConversationResponse,
    MessageCreate,
    MessageMuteRequest,
)
from app.services.message_service import MessageService

router = APIRouter()


@router.get("/contacts", response_model=list[MessageContactResponse])
async def list_message_contacts(
    role: str | None = Query(default=None),
    q: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        return MessageService(db).list_contacts(current_user, role=role, q=q)

    return await run_db(db, operation, list[MessageContactResponse])


@router.get("/conversations", response_model=list[MessageConversationResponse])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        return MessageService(db).list_conversations(current_user)

    return await run_db(db, operation, list[MessageConversationResponse])


@router.post("/conversations", response_model=MessageConversationResponse)
async def create_conversation(
    payload: MessageConversationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        return MessageService(db).create_or_get_conversation(payload, current_user)

    return await run_db(db, operation, MessageConversationResponse)


@router.post("/admin", response_model=MessageConversationResponse)
async def create_admin_conversation(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        return MessageService(db).create_or_get_admin_conversation(current_user)

    return await run_db(db, operation, MessageConversationResponse)


@router.get("/conversations/{conversation_id}", response_model=MessageConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        return MessageService(db).get_conversation(conversation_id, current_user)

    return await run_db(db, operation, MessageConversationResponse)


@router.post("/conversations/{conversation_id}/messages", response_model=MessageConversationResponse)
async def create_message(
    conversation_id: int,
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        return MessageService(db).create_message(conversation_id, payload, current_user)

    return await run_db(db, operation, MessageConversationResponse)


@router.patch("/conversations/{conversation_id}/read", response_model=MessageConversationResponse)
async def mark_conversation_read(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        return MessageService(db).mark_read(conversation_id, current_user)

    return await run_db(db, operation, MessageConversationResponse)


@router.patch("/conversations/{conversation_id}/mute", response_model=MessageConversationResponse)
async def mute_conversation(
    conversation_id: int,
    payload: MessageMuteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    def operation(db: Session):
        return MessageService(db).mute(conversation_id, payload, current_user)

    return await run_db(db, operation, MessageConversationResponse)
