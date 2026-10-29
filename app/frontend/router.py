from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse


FRONTEND_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = FRONTEND_DIR / "templates"
STATIC_DIR = FRONTEND_DIR / "static"

router = APIRouter(include_in_schema=False)


@router.get("/")
async def login_page() -> FileResponse:
    return FileResponse(TEMPLATES_DIR / "login.html")


@router.get("/register")
async def register_page() -> FileResponse:
    return FileResponse(TEMPLATES_DIR / "register.html")


@router.get("/app/documents")
async def documents_page() -> FileResponse:
    return FileResponse(TEMPLATES_DIR / "documents.html")


@router.get("/app/documents/{document_id}")
async def document_page(document_id: int) -> FileResponse:
    return FileResponse(TEMPLATES_DIR / "document.html")
