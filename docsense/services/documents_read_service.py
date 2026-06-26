
from fastapi import HTTPException
from sqlalchemy.orm import Session

from docsense.data_base.models import Document, DocumentStatus
from docsense.repositories import documents_repository


def get_document(db: Session, document_id:int) -> Document:
  document = documents_repository.get_document(db,document_id)
  if document is None:
    raise HTTPException(status_code = 404, detail = 'Document not found')
  return document

def get_documents(db: Session,status: DocumentStatus | None = None) -> list[Document]:
  return documents_repository.get_documents(db,status)
