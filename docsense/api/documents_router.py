from fastapi import APIRouter

from docsense.api import (
    analysis_router,
    delete_router,
    download_router,
    read_router,
    sort_router,
    summary_router,
    upload_router,
)

router = APIRouter()

router.include_router(upload_router.router, prefix="/documents")
router.include_router(download_router.router, prefix="/documents")
router.include_router(read_router.router, prefix="/documents")
router.include_router(analysis_router.router, prefix="/documents")
router.include_router(delete_router.router, prefix="/documents")
router.include_router(sort_router.router, prefix='/documents')
router.include_router(summary_router.router, prefix = '/documents')
