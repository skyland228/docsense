
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User


def create_user(
    username: str,
    email: str,
    password_hash: str,
    db: AsyncSession,
) -> User:
    user = User(username=username, email=email, password_hash=password_hash)
    db.add(user)
    return user