from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import FileResponse, FileResponse
from sqlalchemy.orm import Session
from docsense.dependencies import get_db
from docsense.services import documents_service
from docsense.schemas import DocumentResponse, DocumentUploadResponse

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload",response_model=DocumentUploadResponse)
def upload_document(db: Session = Depends(get_db),file : UploadFile = File(...)):
    return documents_service.upload_document(db,file)

@router.get("/{document_id}/download")
def download_document( document_id: int,db: Session = Depends(get_db)):
    document= documents_service.get_document_file(db,document_id)
    return FileResponse(
        path=document.file_path,
        filename=document.original_filename,   
    )
@router.delete('/{document_id}/delete')
def delete_document(document_id: int,db: Session = Depends(get_db)):
    return documents_service.delete_document(db,document_id)

@router.get("",response_model=list[DocumentResponse])
def get_documents(db: Session = Depends(get_db)):
    return documents_service.get_documents(db)
