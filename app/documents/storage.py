from pathlib import Path
from uuid import uuid4

import aiofiles
from fastapi import UploadFile

from app.documents import exceptions as document_exceptions

UPLOAD_DIR = Path('uploads')
MAX_FILE_SIZE = 5 * 1024 * 1024


async def save_file(file: UploadFile) -> tuple[str, str, int, Path]:
    original_filename = file.filename or 'document'
    extension = Path(original_filename).suffix
    stored_filename = f'{uuid4()}{extension}'
    UPLOAD_DIR.mkdir(exist_ok=True)
    upload_path = UPLOAD_DIR / stored_filename
    chunk_size = 1024 * 1024
    size = 0
    try:
        async with aiofiles.open(upload_path, 'wb') as f:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_FILE_SIZE:
                    raise document_exceptions.FileTooLargeError
                await f.write(chunk)
    except Exception:
        if upload_path.exists():
            upload_path.unlink()
        raise
    return original_filename, stored_filename, size, upload_path


def delete_file(upload_path: Path | None) -> None:
    if upload_path is not None and upload_path.exists():
        upload_path.unlink()


def get_file_path(stored_filename: str) -> Path:
    file_path = UPLOAD_DIR / stored_filename
    if file_path.exists():
        return file_path
    raise document_exceptions.StoredFileNotFoundError
