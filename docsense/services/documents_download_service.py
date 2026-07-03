from pathlib import Path
import zipfile
from fastapi import HTTPException
from sqlalchemy.orm import Session
from docsense.data_base.models import Document
from docsense.repositories import documents_repository
from docsense.services import maintenance_service


def get_document_file(db:Session,id:int) -> Document:
  document = documents_repository.get_document(db,id)
  if document is None:
    raise HTTPException(status_code=404, detail='Document not found')
  file_path = Path(document.file_path)
  if not file_path.exists():
    raise HTTPException(status_code=404,detail='Document file not found')
  return document

def get_documents_files(db: Session,analysis:bool) -> Path:
  documents = documents_repository.get_documents_for_download(db,analysis)
  if analysis:
    maintenance_service.cleanup_documents_for_analysis(db,documents)
    documents = documents_repository.get_documents_for_download(db,analysis)
  if not documents:
    raise HTTPException(status_code = 404, detail = 'Documents not found')
  existing_documents = []
  for document in documents:
    file_path = Path(document.file_path)
    if file_path.exists():
      existing_documents.append(document)
  if not existing_documents:
    raise HTTPException(
      status_code = 404,
      detail ='No document files found'
    )
  zip_dir = Path('temp')
  zip_dir.mkdir(parents = True, exist_ok=True)
  zip_path = zip_dir/"documents.zip"
  
  with zipfile.ZipFile(zip_path,'w') as zip_file:
    for document in existing_documents:
      file_path = Path(document.file_path)
      zip_file.write(
        file_path,
        arcname = f"{document.id}__{document.stored_filename}",
      )
  return zip_path
  