from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from docsense.data_base.models import Document
from docsense.repositories import documents_repository
from docsense.schemas import DocumentAnalyseUpdate
from docsense.services import storage_service

def upload_document(db: Session,file: UploadFile) -> Document:  
  saved_file =  storage_service.save_upload_file(file)
  document = documents_repository.create_document(db,
                                                  saved_file['original_filename'],
                                                  stored_filename=saved_file['stored_filename'],
                                                  file_path=saved_file['path'],
                                                  )
  db.commit()
  db.refresh(document)
  return document

def get_document_file(db:Session,id:int) -> Document:
  document = documents_repository.get_document(db,id)
  if document is None:
    raise HTTPException(status_code=404, detail='Document not found')
  file_path = Path(document.file_path)
  if not file_path.exists():
    raise HTTPException(status_code=404,detail='Document file not found')
  return document

def get_documents(db: Session) -> list[Document]:
  return documents_repository.get_documents(db)

def delete_document(db: Session, document_id:int) -> None:
  document = documents_repository.get_document(db,document_id)
  if document is None:
    raise HTTPException(status_code=404,detail='Document not found')
  file_path = Path(document.file_path)
  if file_path.exists():
    file_path.unlink()
  documents_repository.delete_document(db,document)
  db.commit()
  
def anylysis_document(db: Session,
                      document_id: int,
                      data: DocumentAnalyseUpdate,
                      ) -> Document:
  document = documents_repository.get_document(db,document_id)
  if document is None:
    raise HTTPException(status_code=404, detail='Document not found')
  if data.status == 'PROCESSED' and data.topic is None:
    raise HTTPException(status_code=400,detail='Topic is required when status is processed')
  updated_document = documents_repository.update_document_analysis(document,data.status,data.topic)
  db.commit()
  db.refresh(updated_document)
  return updated_document
  