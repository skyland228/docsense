from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import exception
from app.services import user as user_service
from app.db.models.user import User
from app.dependencies import get_db
from app.schemas.user import TokenResponse, UserCreate, UserResponse

router = APIRouter(tags=['user'])


@router.post('/users', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        user = await user_service.register(payload, db)
    except exception.UserWithThisEmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User with this Email already exists',
        )
    except exception.UserWithThisUsernameAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='This username is taken',
        )
    return user

@router.post('/login')
async def user_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    try:
        token = await user_service.login(form_data.username, form_data.password, db)
    except exception.InvalidCredentialExceptionError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
        )
    return {
        'access_token': token,
        'token_type': 'bearer',
    }
