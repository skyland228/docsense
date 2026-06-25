from pathlib import Path
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from docsense.data_base.models import Document, DocumentStatus
from docsense.repositories import documents_repository
from docsense.schemas import DocumentAnalysisUpdate
from docsense.services import storage_service
import zipfile

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

def get_document(db: Session, document_id:int) -> Document:
  document = documents_repository.get_document(db,document_id)
  if document is None:
    raise HTTPException(status_code = 404, detail = 'Document not found')
  return document

def get_documents(db: Session,status: DocumentStatus | None = None) -> list[Document]:
  return documents_repository.get_documents(db,status)

def get_documents_files(db: Session) -> Path:
  documents = documents_repository.get_documents_without_topic(db)
  if documents is None:
    raise HTTPException(status_code = 404, detail = 'Documents not found')
  existing_file_paths = []
  for document in documents:
    file_path = Path(document.file_path)
    if file_path.exists():
      existing_file_paths.append(file_path)
  if not existing_file_paths:
    raise HTTPException(
      status_code = 404,
      detail ='No document files found'
    )
  zip_dir = Path('temp')
  zip_dir.mkdir(parents = True, exist_ok=True)
  zip_path = zip_dir/"documents.zip"
  
  with zipfile.ZipFile(zip_path,'w') as zip_file:
    for file_path in existing_file_paths:
      zip_file.write(
        file_path,
        arcname = file_path.name,
      )
  return zip_path
  
def delete_document(db: Session, document_id:int) -> None:
  document = documents_repository.get_document(db,document_id)
  if document is None:
    raise HTTPException(status_code=404,detail='Document not found')
  file_path = Path(document.file_path)
  if file_path.exists():
    file_path.unlink()
  documents_repository.delete_document(db,document)
  db.commit()
  
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
  db.commit()
  db.refresh(updated_document)
  return updated_document
  