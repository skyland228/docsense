from pathlib import Path
import shutil
from fastapi import UploadFile

def save_upload_file(file: UploadFile) -> dict:
  upload_dir = Path("uploads")
  upload_dir.mkdir(parents=True, exist_ok=True) # создание папки, если ее нет
  safe_filename = Path(file.filename).name
  original_path = upload_dir / safe_filename
  name = original_path.stem
  suffix = original_path.suffix
  file_path = upload_dir / safe_filename
  counter = 1
  while file_path.exists():
    new_filename = f"{name}({counter}){suffix}"
    file_path = upload_dir / new_filename
    counter += 1
  with file_path.open('wb') as buffer:
    shutil.copyfileobj(file.file, buffer)
  return {
    "original_filename": safe_filename,
    "stored_filename": file_path.name,
    "path": str(file_path),
        }
  
def get_file_path(stored_filename: str) -> Path:
  safe_filename = Path(stored_filename).name
  file_path = Path("uploads") / safe_filename
  return file_path