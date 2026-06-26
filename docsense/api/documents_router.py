from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from docsense.data_base.models import DocumentStatus
from docsense.dependencies import get_db
from docsense.services import documents_service
from docsense.schemas import DocumentResponse, DocumentTopicUpdate, DocumentUploadResponse, DocumentAnalysisUpdate

router = APIRouter(prefix="/documents", tags=["documents"])

# Upload

@router.post("/upload", response_model=DocumentUploadResponse)
def upload_document(db: Session = Depends(get_db), file: UploadFile = File(...)):
    return documents_service.upload_document(db, file)

@router.post("/upload/bulk", response_model=list[DocumentUploadResponse])
def upload_documents(db:Session = Depends(get_db),
                     files: list[UploadFile] = File(...)):
    return documents_service.upload_documents(db,files)

# Download

@router.get("/download")
def get_documents_files(db: Session = Depends(get_db)):
    zip_path = documents_service.get_documents_files(db)
    return FileResponse(
        path=zip_path,
        filename="documents.zip",
        media_type="application/zip",
    )


@router.get("/{document_id}/download")
def download_document(document_id: int, db: Session = Depends(get_db)):
    document = documents_service.get_document_file(db, document_id)
    return FileResponse(
        path=document.file_path,
        filename=document.original_filename,
    )


# Read

@router.get("", response_model=list[DocumentResponse])
def get_documents(
    status: DocumentStatus | None = None,
    db: Session = Depends(get_db),
):
    return documents_service.get_documents(db, status)


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db)):
    return documents_service.get_document(db, document_id)


# Update
@router.patch("/analysis", response_model = list[DocumentResponse])
def fill_documents_topics(data: list[DocumentTopicUpdate],
                              db: Session = Depends(get_db)):
    return documents_service.fill_documents_topics(db,data)

@router.patch("/{document_id}/analysis", response_model=DocumentResponse)
def update_document_analysis(
    document_id: int,
    data: DocumentAnalysisUpdate,
    db: Session = Depends(get_db),
):
    return documents_service.update_document_analysis(db, document_id, data)


# Delete

@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    return documents_service.delete_document(db, document_id)