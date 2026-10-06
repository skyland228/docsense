

from sqlalchemy.exc import IntegrityError

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import exception
from app.repositories import user as user_repository
from app.core.security import create_access_token, hash_password, verify_password
from app.db.models.user import User
from app.schemas.user import UserCreate


async def register(user_data: UserCreate, db: AsyncSession) -> User:
    password_hash = hash_password(user_data.plain_password)
    try:
        user = user_repository.create_user(
            user_data.username,
            user_data.email,
            password_hash,
            db
            )
        await db.commit()
    except IntegrityError as e:
        if 'email' in str(e):
            raise exception.UserWithThisEmailAlreadyExistsError
        if 'username' in str(e):
            raise exception.UserWithThisUsernameAlreadyExistsError
    return user


async def login(username: str, password: str, db: AsyncSession) -> str:
    user = await user_repository.get_user_by_name(username, db)
    if user is None or not verify_password(password, user.password_hash):
        raise exception.InvalidCredentialExceptionError
    token = create_access_token(user.id)
    return token