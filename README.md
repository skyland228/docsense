# DocSense

DocSense is a full-stack document management application built with FastAPI. It lets authenticated users upload PDF and TXT files, extract their text, keep document versions, and use an AI model to explain the differences between two versions.

The repository contains the API, a lightweight HTML/CSS/JavaScript interface, PostgreSQL migrations, automated tests, and Docker configuration.

## What DocSense can do

- Register users and authenticate them with JWT access tokens.
- Keep every user's documents isolated from other accounts.
- Upload PDF and TXT files up to 5 MB.
- Store original files locally and download them later.
- Extract and persist document text automatically or on demand.
- Display processing status and extraction errors.
- Upload new versions of an existing document.
- Calculate similarity between consecutive versions.
- Reject a version when it is unrelated to the original document.
- Generate and cache an AI explanation of changes between two versions.
- Delete a document together with its text, versions, and cached comparisons.
- Use the application through a browser or directly through the REST API.

## Web interface

The frontend uses server-served HTML templates and vanilla JavaScript. It calls the same API that is available through Swagger; there is no React application or Node.js build step.

| URL | Page |
| --- | --- |
| `/` | Sign in |
| `/register` | Create an account |
| `/app/documents` | Upload and list documents |
| `/app/documents/{id}` | Text, download, versions, deletion, and AI comparison |
| `/docs` | Swagger UI |
| `/redoc` | ReDoc |

The frontend stores the JWT access token in browser local storage and sends it as a Bearer token when calling protected endpoints.

## Main API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/users` | Register a user |
| `POST` | `/login` | Receive a JWT access token |
| `POST` | `/documents` | Upload a document |
| `GET` | `/documents` | List the current user's documents |
| `GET` | `/documents/{id}` | Get document metadata |
| `DELETE` | `/documents/{id}` | Delete a document |
| `GET` | `/documents/{id}/file` | Download the original file |
| `POST` | `/documents/{id}/process` | Extract document text |
| `GET` | `/documents/{id}/text` | Get extracted text |
| `POST` | `/documents/{id}/versions` | Upload a new version |
| `GET` | `/documents/{id}/versions` | List versions |
| `GET` | `/documents/{id}/versions/{number}` | Get a version and its text |
| `POST` | `/documents/{id}/diff` | Compare two versions with AI |

## Technology

- FastAPI and Uvicorn
- Pydantic v2 and Pydantic Settings
- SQLAlchemy 2.0 async ORM
- PostgreSQL and asyncpg
- Alembic migrations
- PyJWT and pwdlib with Argon2
- pypdf and aiofiles
- OpenAI-compatible async client connected to Groq
- HTML, CSS, and vanilla JavaScript
- pytest, pytest-asyncio, and HTTPX
- Docker and Docker Compose

## Project structure

```text
app/
├── core/                 # Settings, password hashing, and JWT helpers
├── db/                   # Async database configuration and ORM models
├── documents/            # Document API, services, storage, processing, and AI
├── frontend/
│   ├── router.py         # Routes that serve HTML pages
│   ├── templates/        # Login, registration, document list, and detail pages
│   └── static/           # Shared CSS and JavaScript API clients
├── users/                # Registration, login, and user persistence
├── dependencies.py       # Database session and current-user dependencies
├── handlers.py           # Application exception handlers
└── main.py               # FastAPI application assembly
alembic/                  # Database migrations
tests/                    # Integration and behavior tests
compose.yaml              # Base API and PostgreSQL services
compose.dev.yaml          # Development ports, bind mount, and auto-reload
```

## Environment

Copy `.env.example` to `.env` and replace every placeholder:

```dotenv
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/docsense
TEST_DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/docsense_test
POSTGRES_PASSWORD=password
SECRET_KEY=replace_with_a_long_random_value
GROQ_API_KEY=your_groq_api_key
```

`DATABASE_URL` is used by the application and Alembic. `TEST_DATABASE_URL` must point to a separate `docsense_test` database because the test suite recreates its schema. `POSTGRES_PASSWORD` is used by Docker Compose.

The default AI model is `openai/gpt-oss-20b`. It can be overridden with `AI_MODEL`.

## Run locally

Requirements: Python 3.12 or newer and PostgreSQL.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Create the `docsense` and `docsense_test` databases, fill in `.env`, and apply migrations:

```powershell
alembic upgrade head
uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000> for the web interface or <http://127.0.0.1:8000/docs> for Swagger.

## Run with Docker

The development override publishes port `8000`, mounts the repository into the API container, and enables Uvicorn auto-reload:

```powershell
docker compose -f compose.yaml -f compose.dev.yaml up --build -d
docker compose -f compose.yaml -f compose.dev.yaml exec api alembic upgrade head
```

Open <http://127.0.0.1:8000>.

Stop the services with:

```powershell
docker compose -f compose.yaml -f compose.dev.yaml down
```

PostgreSQL data is stored in the `postgres_data` volume. Uploaded files currently use local filesystem storage; a production deployment should mount `uploads/` as persistent storage.

## Tests

Install development dependencies and make sure `TEST_DATABASE_URL` points to a disposable `docsense_test` database:

```powershell
pip install -r requirements-dev.txt
pytest
```

The test suite covers authentication, access isolation, uploads, downloads, text processing, deletion, version validation, and cached AI comparisons.

## Current limitations

- Uploaded files are stored on the local filesystem rather than object storage.
- JWT authentication uses access tokens without refresh tokens.
- Document processing runs in the API process rather than a background queue.
- AI comparison requires network access and a valid Groq API key.
- Semantic search and question answering over document contents are not implemented yet.
