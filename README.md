# DocSense

Backend-сервис на FastAPI для работы с заметками и документами.

Проект развивается как учебный production-like backend: от базового CRUD и авторизации к загрузке документов, обработке файлов, поиску и AI Q&A по пользовательским материалам.

## Status

Проект находится на ранней стадии разработки.

Сейчас формируется базовая архитектура приложения:

- FastAPI application;
- конфигурация приложения;
- SQLAlchemy models;
- repository layer;
- service layer;
- routers;
- Pydantic schemas;
- authentication/security utilities;
- database dependencies.

Следующие этапы:

- регистрация и login;
- JWT authentication;
- защищённые endpoints;
- Document model;
- загрузка PDF/TXT;
- файловое хранилище;
- обработка документов;
- поиск;
- AI Q&A.

## Tech stack

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- PyJWT
- pwdlib
- pytest

## Project structure

```text
app/
├── core/
│   ├── __init__.py
│   ├── config.py
│   └── security.py
│
├── db/
│   ├── models/
│   ├── __init__.py
│   └── database.py
│
├── repositories/
│   └── __init__.py
│
├── routers/
│   └── __init__.py
│
├── schemas/
│   └── __init__.py
│
├── services/
│   └── __init__.py
│
├── dependencies.py
└── main.py

.env
.gitignore
requirements.txt
README.md