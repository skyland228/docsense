from pathlib import Path

from sqlalchemy.orm import Session

from docsense.data_base.models import Document
from docsense.repositories import documents_repository


def get_documents_orphans(db: Session) -> dict:
  documents = documents_repository.get_all_documents(db) 
  missing_files = []
  db_file_paths = set()
  
  for document in documents:
    file_path = Path(document.file_path)
    db_file_paths.add(file_path)
    
    if not file_path.exists():
      missing_files.append({
          "document_id": document.id,
          "file_path": document.file_path,
      })
            
  uploads_dir = Path('uploads')
  orphan_files = []
  
  if uploads_dir.exists():
    for file_path in uploads_dir.iterdir():
      if file_path.is_file() and file_path not in db_file_paths:
        orphan_files.append(str(file_path))
        
  return {
      "missing_files_count": len(missing_files),
      "orphan_files_count": len(orphan_files),
      "missing_files": missing_files,
      "orphan_files": orphan_files,
  }
  
def cleanup_documents_orphans(db: Session) -> dict:
  documents = documents_repository.get_all_documents(db)
  db_file_paths = set()
  deleted_db_records = 0
  deleted_files = 0
  for document in documents:
    file_path = Path(document.file_path)
    db_file_paths.add(file_path)
    if not file_path.exists():
      documents_repository.delete_document(db, document)  
      deleted_db_records += 1
  uploads_dir = Path('uploads')
  
  if uploads_dir.exists():
    for file_path in uploads_dir.iterdir():
      if file_path.is_file() and file_path not in db_file_paths:
        file_path.unlink()
        deleted_files += 1
  db.commit()
  return {
    'deleted_db_records': deleted_db_records,
    'delete_files': deleted_files,
  }
  
def cleanup_documents_for_analysis(db: Session,documents:list[Document]) -> None:
  for document in documents:
    file_path = Path(document.file_path)
    if not(file_path.exists()):
      documents_repository.delete_document(db,document)
  db.commit()

