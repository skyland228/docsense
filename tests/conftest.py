

from httpx import ASGITransport, AsyncClient
import pytest_asyncio
from sqlalchemy import make_url
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,    
) 

from app.core.security import create_access_token, hash_password
from app.db.database import Base
from app.db.models.user import User
from app.dependencies import get_db
from app.main import app
from app.core.config import settings

TEST_DATABASE_URL = settings.test_database_url
test_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    expire_on_commit=False,
)

db_name = make_url(settings.test_database_url).database

if db_name != "docsense_test":
    raise RuntimeError("Wrong test database!")

async def override_get_db():
    async with TestSessionLocal() as db:
        yield db


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        yield client


@pytest_asyncio.fixture
async def test_user():
    async with TestSessionLocal() as db:
        user = User(
            username='user_1',
            email='test@example.com',
            password_hash=hash_password('test12345'),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        yield user


@pytest_asyncio.fixture
async def authorized_client(client, test_user):
    token = create_access_token(test_user.id)

    client.headers["Authorization"] = f"Bearer {token}"

    yield client