from pathlib import Path
import subprocess
import sys

from fastapi import HTTPException
from sqlalchemy.orm import Session
from docsense.data_base.models import Document, DocumentStatus
from docsense.repositories import documents_repository
from docsense.schemas import DocumentAnalysisUpdate, DocumentTopicUpdateBulk
from docsense.services import documents_sort_service

def update_document_analysis(db: Session,
                      document_id: int,
                      data: DocumentAnalysisUpdate,
                      ) -> Document:
  document = documents_repository.get_document(db,document_id)
  if document is None:
    raise HTTPException(status_code=404, detail='Document not found')
  if data.status not in (DocumentStatus.PROCESSED, DocumentStatus.FAILED):
    raise HTTPException(status_code=400, detail = 'Analysis status must be processed or failed')
  if data.status == DocumentStatus.PROCESSED and data.topic is None:
    raise HTTPException(status_code=400,detail='Topic is required when status is processed')
  updated_document = documents_repository.update_document_analysis(document,data.status,data.topic)
  if updated_document.status == DocumentStatus.PROCESSED:
    documents_sort_service.sort_document(updated_document)
  db.commit()
  db.refresh(updated_document)
  return updated_document
  
def fill_documents_topics(db: Session,
                              data:list[DocumentTopicUpdateBulk]) -> list[Document]:
  updated_documents = []
  for i in range(len(data)):
    documents = documents_repository.get_document_by_ids(
        db,
        data[i].document_ids,
    )
    if not documents:
      raise HTTPException(status_code=404,detail = 'Documents not found')
    for document in documents:
      if data[i].status == DocumentStatus.PROCESSED and data[i].topic is None:
        raise HTTPException(
            status_code=400,
            detail="Topic is required when status is processed"
        ) 
      updated_document = documents_repository.fill_document_topic(document,data[i].topic,data[i].status)
      updated_documents.append(updated_document)
      if updated_document.status == DocumentStatus.PROCESSED:
        documents_sort_service.sort_document(updated_document)

  db.commit()
  for document in updated_documents:
    db.refresh(document)
  return updated_documents  

def trigger_analysis() -> None:
  ml_service_path = Path('ml_service.py')
  if not ml_service_path.is_file():
    return
  subprocess.Popen(
    [sys.executable, str(ml_service_path)]
  )