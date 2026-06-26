from fastapi import UploadFile
from sqlalchemy.orm import Session
from docsense.data_base.models import Document
from docsense.repositories import documents_repository
from docsense.services import file_storage_service

def upload_document(db: Session,file: UploadFile) -> Document:  
  saved_file =  file_storage_service.save_upload_file(file)
  document = documents_repository.create_document(db,
                                                  saved_file['original_filename'],
                                                  stored_filename=saved_file['stored_filename'],
                                                  file_path=saved_file['path'],
                                                  )
  db.commit()
  db.refresh(document)
  return document


def upload_documents(db: Session,files: list[UploadFile]) -> list[Document]:
  saved_files = file_storage_service.save_upload_files(files)
  documents = []
  for saved_file in saved_files:
    document = documents_repository.create_document(db,
                                                    saved_file['original_filename'],
                                                    stored_filename=saved_file['stored_filename'],
                                                    file_path=saved_file['path'])
    documents.append(document)
  db.commit()
  for document in documents:
    db.refresh(document)
  return documents