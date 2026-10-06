from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.db.models.user import User
from app.users import exceptions as user_exceptions
from app.users import repository
from app.users.schemas import UserCreate


async def register(user_data: UserCreate, db: AsyncSession) -> User:
    password_hash = hash_password(user_data.plain_password)
    try:
        user = repository.create_user(
            user_data.username,
            user_data.email,
            password_hash,
            db,
        )
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        error_message = str(exc).lower()
        if 'email' in error_message:
            raise user_exceptions.UserWithThisEmailAlreadyExistsError from exc
        if 'username' in error_message:
            raise user_exceptions.UserWithThisUsernameAlreadyExistsError from exc
        raise
    return user


async def login(username: str, password: str, db: AsyncSession) -> str:
    user = await repository.get_user_by_name(username, db)
    if user is None or not verify_password(password, user.password_hash):
        raise user_exceptions.InvalidCredentialExceptionError
    token = create_access_token(user.id)
    return token
