from collections.abc import Callable
from typing import Any, TypeVar

from fastapi.responses import Response
from pydantic import TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

T = TypeVar("T")


async def run_db(
    db: AsyncSession,
    operation: Callable[[Session], T],
    response_model: Any = None,
) -> T:
    def execute(session: Session):
        result = operation(session)
        if response_model is not None and not isinstance(result, Response):
            return TypeAdapter(response_model).validate_python(result, from_attributes=True)
        return result

    try:
        result = await db.run_sync(execute)
    except BaseException:
        db.info.pop("pending_push_deliveries", None)
        raise
    from app.services.push_notification_service import schedule_push_deliveries

    schedule_push_deliveries(db.info.pop("pending_push_deliveries", []))
    return result
