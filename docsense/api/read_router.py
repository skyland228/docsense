from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from docsense.data_base.models import DocumentStatus
from docsense.dependencies import get_db
from docsense.schemas import DocumentResponse
from docsense.services import documents_read_service

router = APIRouter(tags=["documents read"])

@router.get("", response_model=list[DocumentResponse])
def get_documents(
    status: DocumentStatus | None = None,
    db: Session = Depends(get_db),
):
    return documents_read_service.get_documents(db, status)


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db)):
    return documents_read_service.get_document(db, document_id)

