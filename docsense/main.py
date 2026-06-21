from fastapi import FastAPI
import uvicorn
from docsense.api.documents_router import router as documents_router
from docsense.data_base.database import Base,engine
from docsense.data_base import models
app = FastAPI()
app.include_router(documents_router, prefix="/api/v1")
Base.metadata.create_all(bind = engine)
if __name__ == '__main__':
  uvicorn.run('docsense.main:app', reload=True)
