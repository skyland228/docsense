from pathlib import Path
import shutil
from sqlalchemy.orm import Session
from docsense.repositories import documents_repository


def sort_documents(db: Session) -> list[dict]:
  documents = documents_repository.get_processed_document_with_topic(db)
  result = []
  for document in documents:
    topic = document.topic
    old_path = Path(document.file_path)
    upload_dir = Path("sorted") / topic
    upload_dir.mkdir(parents=True, exist_ok=True) 
    new_path = upload_dir / document.stored_filename
    if not old_path.exists():
      result.append({
        "filename": document.stored_filename,
        "error": "file not found",
      })
      continue
    if old_path == new_path:
      continue
    shutil.move(old_path,new_path)
    document.file_path = str(new_path)
    result.append({
      'filename' : document.stored_filename,
      'Path' : str(new_path),
    })
  db.commit()
  
  return result
    