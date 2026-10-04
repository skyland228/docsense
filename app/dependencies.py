

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException

from app.db.database import async_session_local
from app.core.security import oauth2_scheme, verify_access_token
from app.db.models.user import User

async def get_db():
    async with async_session_local() as session:
        yield session


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    user_id = verify_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail='Invalid token',
        )
    return await db.get(User, int(user_id))