from fastapi import FastAPI

from app.documents.router import router as document_router
from app.users.router import router as user_router
from app.handlers import register_handlers


app = FastAPI()
app.include_router(user_router)
app.include_router(document_router)

register_handlers(app)