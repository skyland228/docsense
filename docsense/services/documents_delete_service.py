from pathlib import Path
from fastapi import HTTPException
from sqlalchemy.orm import Session
from docsense.repositories import documents_repository

def delete_document(db: Session, document_id:int) -> None:
  document = documents_repository.get_document(db,document_id)
  if document is None:
    raise HTTPException(status_code=404,detail='Document not found')
  file_path = Path(document.file_path)
  if file_path.exists():
    file_path.unlink()
  documents_repository.delete_document(db,document)
  db.commit()
  
def delete_documents(db: Session, documents_ids: list[int]) -> None:
  documents = documents_repository.get_document_by_ids(db,documents_ids)
  if not documents:
    return None
  for document in documents:
    file_path = Path(document.file_path)
    if file_path.exists():
      file_path.unlink()
    documents_repository.delete_document(db,document)
  db.commit()
  