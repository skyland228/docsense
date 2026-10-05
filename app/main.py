#

from fastapi import FastAPI

from app.routers.users import router as user_router
from app.routers.documents import router as document_router


app = FastAPI()
app.include_router(user_router)
app.include_router(document_router)
