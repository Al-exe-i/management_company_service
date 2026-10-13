import argparse
import asyncio
import getpass
import os

from fastapi import HTTPException
from sqlalchemy import or_, select, text

from app.core.auth_validation import validate_login_value, validate_password_value
from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.user import User, UserRole


async def create_admin(login: str, password: str, full_name: str) -> int:
    login = validate_login_value(login)
    password = validate_password_value(password)
    full_name = full_name.strip()
    if not full_name:
        raise ValueError("Administrator name must not be empty")
    password_hash = await asyncio.to_thread(get_password_hash, password)

    async with SessionLocal() as db:
        await db.execute(text("LOCK TABLE users IN SHARE ROW EXCLUSIVE MODE"))
        if await db.scalar(select(User.id).where(User.role == UserRole.ADMIN)) is not None:
            raise ValueError("An administrator already exists; the account was not changed")
        if await db.scalar(select(User.id).where(or_(User.login == login, User.phone == login))) is not None:
            raise ValueError("This login is already in use")
        user = User(
            full_name=full_name,
            login=login,
            phone=login,
            password_hash=password_hash,
            role=UserRole.ADMIN,
        )
        db.add(user)
        await db.commit()
        return user.id


def main() -> None:
    parser = argparse.ArgumentParser(description="Create the first administrator without demo credentials")
    parser.add_argument("--login", default=os.getenv("INITIAL_ADMIN_LOGIN", "admin"))
    parser.add_argument("--name", default=os.getenv("INITIAL_ADMIN_NAME", "Administrator"))
    args = parser.parse_args()
    password = os.getenv("INITIAL_ADMIN_PASSWORD")
    if not password:
        password = getpass.getpass("Administrator password: ")
        if password != getpass.getpass("Repeat password: "):
            parser.exit(1, "Passwords do not match\n")
    try:
        user_id = asyncio.run(create_admin(args.login, password, args.name))
    except (ValueError, HTTPException) as exc:
        message = exc.detail if isinstance(exc, HTTPException) else str(exc)
        parser.exit(1, f"Administrator was not created: {message}\n")
    print(f"Administrator created (id={user_id}, login={args.login})")


if __name__ == "__main__":
    main()
