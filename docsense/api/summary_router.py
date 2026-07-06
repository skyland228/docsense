from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from docsense.dependencies import get_db
from docsense.schemas import DocumentSummary
from docsense.services import documents_summary_service

router = APIRouter(tags = ['summary'])

@router.patch('/summary')
def summary_documents(data: list[DocumentSummary],db: Session = Depends(get_db)):
  return documents_summary_service.documents_summary(db,data)