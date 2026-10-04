from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import exception
from app.services import user as user_service
from app.db.models.user import User
from app.dependencies import get_current_user, get_db
from app.schemas.user import TokenResponse, UserCreate, UserResponse

router = APIRouter()


@router.post('/users', response_model=UserResponse)
async def register_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        user = await user_service.register(payload, db)
    except exception.UserWithThisEmailAlreadyExistsError:
        raise HTTPException(
            status_code=400,
            detail='User with this Email already exists',
        )
    except exception.UserWithThisUsernameAlreadyExistsError:
        raise HTTPException(
            status_code=400,
            detail='This username is taken',
        )
    return user

@router.post('/login')
async def user_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    try:
        token = await user_service.login(form_data, db)
    except exception.InvalidCredentialException:
        raise HTTPException(
            status_code=401,
            detail='Incorrect username or password',
        )
    return {
        'access_token': token,
        'token_type': 'bearer',
    }
