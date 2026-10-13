from urllib.parse import unquote

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from jose import JWTError, jwt
from sqlalchemy import select

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User
from app.services.live_update_hub import live_update_hub

router = APIRouter()


def _normalize_ws_token(raw_token: str | None) -> str:
    if not raw_token:
        return ""
    token = unquote(str(raw_token)).strip()
    if len(token) >= 2 and token[0] == token[-1] and token[0] in {"'", '"'}:
        token = token[1:-1]
    return token


@router.websocket("/updates")
async def websocket_updates(websocket: WebSocket):
    token = _normalize_ws_token(websocket.cookies.get("uk_token") or websocket.query_params.get("token"))
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        async with SessionLocal() as db:
            existing_user_id = await db.scalar(select(User.id).where(User.id == int(user_id)))
        if existing_user_id is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        await live_update_hub.connect(websocket)
        while True:
            message = await websocket.receive_text()
            if message == "ping":
                await websocket.send_text("pong")
    except (JWTError, ValueError, TypeError):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    except WebSocketDisconnect:
        live_update_hub.disconnect(websocket)
    finally:
        live_update_hub.disconnect(websocket)
