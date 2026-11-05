# DocSense

DocSense is a backend API for uploading documents, extracting text, storing document versions, and comparing versions with AI.

The project intentionally contains only the FastAPI backend. Use Swagger UI at `/docs` to work with the API during development.

## Features

- User registration and JWT authentication.
- Per-user access control for documents.
- PDF and TXT upload, download, listing, and deletion.
- Automatic or manual text extraction.
- Document version history with similarity checks.
- AI-generated summaries of changes between versions through the Groq API.
- Asynchronous PostgreSQL access with SQLAlchemy.
- Alembic database migrations.
- Docker Compose configuration for local development.
- Integration tests with pytest.

## Tech stack

- FastAPI and Uvicorn
- PostgreSQL, SQLAlchemy 2.0, and asyncpg
- Alembic
- Pydantic v2
- PyJWT and pwdlib
- pypdf and aiofiles
- OpenAI Python client with a Groq-compatible endpoint
- pytest, pytest-asyncio, and HTTPX

## API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/users` | Register a user |
| `POST` | `/login` | Log in and receive a bearer token |
| `POST` | `/documents` | Upload a document |
| `GET` | `/documents` | List the current user's documents |
| `GET` | `/documents/{id}` | Get document metadata |
| `DELETE` | `/documents/{id}` | Delete a document |
| `GET` | `/documents/{id}/file` | Download the original file |
| `POST` | `/documents/{id}/process` | Extract document text |
| `GET` | `/documents/{id}/text` | Return extracted text |
| `POST` | `/documents/{id}/versions` | Upload a new version |
| `GET` | `/documents/{id}/versions` | List document versions |
| `GET` | `/documents/{id}/versions/{number}` | Get a specific version |
| `POST` | `/documents/{id}/diff` | Compare two versions with AI |

Protected endpoints require `Authorization: Bearer <token>`.

## Project structure

```text
app/
|-- core/          # Settings and security
|-- db/            # Database session and SQLAlchemy models
|-- documents/     # Document routes, services, repository, and schemas
|-- users/         # Registration, login, and user logic
|-- dependencies.py
|-- handlers.py
`-- main.py
alembic/            # Database migrations
tests/              # Integration tests
```

## Environment variables

Copy `.env.example` to `.env` and set:

```dotenv
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/docsense
TEST_DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/docsense_test
POSTGRES_PASSWORD=password
SECRET_KEY=replace_with_a_random_secret
GROQ_API_KEY=your_groq_api_key
```

`AI_MODEL` is optional and defaults to `openai/gpt-oss-20b`.

## Local development

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

Apply migrations and start the API:

```powershell
alembic upgrade head
uvicorn app.main:app --reload
```

Open:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Docker development

```powershell
docker compose -f compose.yaml -f compose.dev.yaml up --build
docker compose exec api alembic upgrade head
```

The API is available at `http://127.0.0.1:8000`.

## Tests

Create the database referenced by `TEST_DATABASE_URL`, then run:

```powershell
pytest
```

## Current limitations

- Uploaded files are stored on the local filesystem.
- AI comparison requires a valid Groq API key and external network access.
