from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User
from app.dependencies import get_db
from app.users import exceptions as user_exceptions
from app.users import service
from app.users.schemas import TokenResponse, UserCreate, UserResponse

router = APIRouter(tags=['user'])


@router.post('/users', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        user = await service.register(payload, db)
    except user_exceptions.UserWithThisEmailAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User with this Email already exists',
        ) from exc
    except user_exceptions.UserWithThisUsernameAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='This username is taken',
        ) from exc
    return user


@router.post('/login')
async def user_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    try:
        token = await service.login(form_data.username, form_data.password, db)
    except user_exceptions.InvalidCredentialExceptionError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
        ) from exc
    return {
        'access_token': token,
        'token_type': 'bearer',
    }
