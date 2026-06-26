from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from docsense.dependencies import get_db
from docsense.schemas import DocumentUploadResponse
from docsense.services import documents_upload_service

router = APIRouter(tags=["documents upload"])

@router.post("/upload", response_model=DocumentUploadResponse)
def upload_document(db: Session = Depends(get_db), file: UploadFile = File(...)):
    return documents_upload_service.upload_document(db, file)

@router.post("/upload/bulk", response_model=list[DocumentUploadResponse])
def upload_documents(db:Session = Depends(get_db),
                     files: list[UploadFile] = File(...)):
    return documents_upload_service.upload_documents(db,files)


