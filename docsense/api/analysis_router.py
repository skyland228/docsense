from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from docsense.dependencies import get_db
from docsense.schemas import (
    DocumentAnalysisUpdate,
    DocumentResponse,
    DocumentTopicUpdateBulk,
)
from docsense.services import documents_analysis_service

router = APIRouter(tags=["documents analysis"])

@router.patch("/analysis", response_model = list[DocumentResponse])
def fill_documents_topics(data: list[DocumentTopicUpdateBulk],
                              db: Session = Depends(get_db)):
    return documents_analysis_service.fill_documents_topics(db,data)

@router.patch("/{document_id}/analysis", response_model=DocumentResponse)
def update_document_analysis(
    document_id: int,
    data: DocumentAnalysisUpdate,
    db: Session = Depends(get_db),
):
    return documents_analysis_service.update_document_analysis(db, document_id, data)
