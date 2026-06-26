from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from docsense.dependencies import get_db
from docsense.services import documents_download_service

router = APIRouter(tags=["documents download"])

@router.get("/download")
def get_documents_files(db: Session = Depends(get_db)):
    zip_path = documents_download_service.get_documents_files(db)
    return FileResponse(
        path=zip_path,
        filename="documents.zip",
        media_type="application/zip",
    )

@router.get("/{document_id}/download")
def download_document(document_id: int, db: Session = Depends(get_db)):
    document = documents_download_service.get_document_file(db, document_id)
    return FileResponse(
        path=document.file_path,
        filename=document.original_filename,
    )

