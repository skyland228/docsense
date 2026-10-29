import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.documents.router import router as document_router
from app.frontend.router import STATIC_DIR, router as frontend_router
from app.handlers import register_handlers
from app.users.router import router as user_router

logging.getLogger("pypdf").setLevel(logging.ERROR)
app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(user_router)
app.include_router(document_router)
app.include_router(frontend_router)

register_handlers(app)
