

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile

from app.core import exception
from app.db.models.document import Document
from app.repositories import document as document_repository
from app.documents.storage import delete_file, storage

async def upload_document(file: UploadFile, user_id: int, db: AsyncSession) -> Document:
    upload_path = None
    try:
        original_filename, stored_filename, size, upload_path = await storage(file)
        document = document_repository.create_document(
            original_filename=original_filename,
            stored_filename=stored_filename,
            content_type=file.content_type,
            size=size,
            user_id=user_id,
            db=db,
        )
        await db.commit()
    except exception.FileTooLargeError:
        await db.rollback()
        raise
    except Exception:
        await db.rollback()
        delete_file(upload_path)
        raise exception.FailedSaveDocument
    await db.refresh(document)
    return document


async def get_documents(user_id: int, db: AsyncSession) -> list[Document]:
    documents = await document_repository.get_documents(user_id, db)
    return documents