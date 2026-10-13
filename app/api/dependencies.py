from typing import AsyncIterator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from app.db.session import SessionLocal
from app.core.config import settings
from app.schemas.token import TokenData
from app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as db:
        yield db


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Сессия истекла или недействительна. Войдите снова.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        token_data = TokenData(user_id=user_id)
        numeric_user_id = int(token_data.user_id)

    except (JWTError, ValueError, TypeError):
        raise credentials_exception


    user = await db.scalar(select(User).where(User.id == numeric_user_id))

    if user is None:
        raise credentials_exception

    return user
