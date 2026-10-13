```markdown
# DocSense

A production-like backend service built with **FastAPI** for document management, text extraction, and note processing.

The project is designed to bridge fundamental backend concepts (clean architecture, user authentication, domain error handling) with practical data workflows: file ingestion, parsing, database persistence, and future AI-driven search and Q&A.

---

## Features & Implementation Status

### Core Features

- **Document Flow**:
  - Secure document upload (PDF, TXT) with local file storage persistence.
  - Metadata inspection, document retrieval, file download, and document deletion.
  - Text extraction pipeline parsing raw document content into dedicated database entities.
- **Authentication & Security**:
  - User registration and login flow.
  - Stateless JWT-based authentication (`PyJWT`, `pwdlib`).
  - Strict resource isolation: users can access, process, and delete only their own documents.
- **Centralized Exception Handling**:
  - Standardized domain exception hierarchy (`AppException`) with consistent HTTP status codes and response schemas.
  - Centralized FastAPI exception handlers keeping route handlers clean and declarative.
- **Database & Migrations**:
  - Fully asynchronous PostgreSQL integration using SQLAlchemy 2.0 and `asyncpg`.
  - Schema versioning and migration management via **Alembic**.
- **Automated Testing**:
  - Test suite built with **pytest** and `pytest-asyncio`.
  - Comprehensive integration and end-to-end test coverage for the authentication flow and complete Document Flow.

### Roadmap

- [x] User Registration & JWT Authentication
- [x] Document Ingestion (PDF / TXT) & File Storage
- [x] Document Text Extraction & Dedicated Model Persistence
- [x] Centralized Exception Handling (`AppException`)
- [x] Database Migrations (Alembic) & Comprehensive Tests
- [ ] AI-Powered Q&A over Uploaded Documents

---

## Tech Stack

- **Framework**: FastAPI
- **Data Validation & Settings**: Pydantic v2, Pydantic-Settings
- **ORM & Database**: SQLAlchemy 2.0 (Async), PostgreSQL, asyncpg
- **Migrations**: Alembic
- **Security & Hashing**: PyJWT, pwdlib
- **Testing**: pytest, pytest-asyncio, httpx

---

## Project Structure

```text
app/
├── core/             # Application configuration, security & JWT utilities
├── db/               # Database engine, session setup, and SQLAlchemy models
├── documents/        # Documents domain: router, service, repository, schemas, exceptions
├── users/            # Users domain: auth router, user service, models, schemas
├── handlers.py       # Global FastAPI exception handlers
├── dependencies.py   # FastAPI dependencies (database session, current user)
└── main.py           # Application entrypoint & router registration
alembic/              # Alembic migration environments and revision scripts
tests/                # Automated pytest suite and test fixtures

```
---

## Getting Started

### 1. Prerequisites

Ensure you have the following installed:
* **Python 3.12+**
* **PostgreSQL** instance running locally or via Docker
Make sure both databases (`docsense` and `docsense_test`) are created in your PostgreSQL instance before running migrations or tests.

### 2. Environment Setup

Create your local `.env` file from the example template:

```bash
cp .env.example .env
```

Open `.env` and configure your credentials and connection strings:

```dotenv
DATABASE_URL=postgresql+asyncpg://<username>:<password>@localhost:5432/docsense
TEST_DATABASE_URL=postgresql+asyncpg://<username>:<password>@localhost:5432/docsense_test
SECRET_KEY=your_secret_key_here
```

### 3. Installation

Create a virtual environment and install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Database Migrations

Apply the database schema using Alembic:

```bash
alembic upgrade head
```

### 5. Running the Application

Start the development server using Uvicorn:

```bash
uvicorn app.main:app --reload
```

Once running, interactive API documentation is available at:

* **Swagger UI**: `http://127.0.0.1:8000/docs`
* **ReDoc**: `http://127.0.0.1:8000/redoc`

---

## Running Tests

Execute the full automated test suite with `pytest`:

```bash
pytest
```
```