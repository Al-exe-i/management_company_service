import asyncio
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Any
from jose import jwt
from app.core.config import settings
from sqlalchemy.util.concurrency import await_only, in_greenlet


def _bcrypt_call(function, *args):
    if in_greenlet():
        return await_only(asyncio.to_thread(function, *args))
    return function(*args)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет пароль, используя 'bcrypt'.
    Принимает строки, внутри конвертирует в байты.
    """

    password_byte_enc = plain_password.encode('utf-8')
    hashed_password_byte_enc = hashed_password.encode('utf-8')

    try:
        return _bcrypt_call(bcrypt.checkpw, password_byte_enc, hashed_password_byte_enc)
    except ValueError:
        return False


def get_password_hash(password: str) -> str:
    """
    Хэширует пароль с солью.
    Возвращает строку (decoded bytes), чтобы сохранить в БД (Text/String).
    """
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = _bcrypt_call(bcrypt.hashpw, pwd_bytes, salt)

    return hashed_bytes.decode('utf-8')


def create_access_token(subject: str | Any) -> str:
    """
    Генерирует JWT.
    Аргумент expires_delta убран, время берется строго из настроек.
    Добавлены claims: iat (issued at), nbf (not before).
    """

    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,
        "nbf": now
    }

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
