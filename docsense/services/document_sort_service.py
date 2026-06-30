from pathlib import Path
import shutil
from sqlalchemy.orm import Session
from docsense.data_base.models import Document
from docsense.repositories import documents_repository


def sort_documents(db: Session) -> list[dict]:
  documents = documents_repository.get_processed_document_with_topic(db)

  result = []

  for document in documents:
    result.append(sort_document(document))

  db.commit()

  return result

def sort_document(document: Document) -> dict:
  if document.topic is None:
    return {
    "filename": document.stored_filename,
    "status": "skipped",
    "reason": "topic is empty",
  }
  old_path = Path(document.file_path)
  
  if not old_path.exists():
    return {
      'filename': document.stored_filename,
      'status': 'error',
      'reason': 'file not found',
    }
  upload_dir = Path('sorted') / document.topic
  upload_dir.mkdir(parents=True, exist_ok=True)
  new_path = upload_dir / document.stored_filename
  if old_path == new_path:
    return {
    "filename": document.stored_filename,
    "status": "skipped",
    "reason": "already sorted",
    "path": str(new_path),
  }
  shutil.move(old_path,new_path)
  document.file_path = str(new_path)
  
  return {
    'filename': document.stored_filename,
    'status': 'sorted',
    'path': str(new_path)
  }