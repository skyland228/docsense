

from datetime import datetime, timedelta, timezone

from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
import jwt
from pwdlib import PasswordHash


SECRET_KEY = settings.secret_key
ALGORITHM = 'HS256'
password_hash = PasswordHash.recommended()
EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')


def hash_password(plain_password: str) -> str:
    return password_hash.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MINUTES)
    payload = {
        'sub': str(user_id),
        'exp': expire,
    }
    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def verify_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        user_id = payload.get('sub')
        if user_id is None:
            return None
        return user_id
    except jwt.InvalidTokenError:
        return None