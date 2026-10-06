from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.document import Document
from app.documents import exceptions as document_exceptions
from app.documents import repository
from app.documents.storage import delete_file, storage


async def upload_document(file: UploadFile, user_id: int, db: AsyncSession) -> Document:
    upload_path = None
    try:
        original_filename, stored_filename, size, upload_path = await storage(file)
        document = repository.create_document(
            original_filename=original_filename,
            stored_filename=stored_filename,
            content_type=file.content_type,
            size=size,
            user_id=user_id,
            db=db,
        )
        await db.commit()
    except document_exceptions.FileTooLargeError:
        await db.rollback()
        raise
    except Exception as exc:
        await db.rollback()
        delete_file(upload_path)
        raise document_exceptions.FailedSaveDocumentError from exc
    await db.refresh(document)
    return document


async def get_documents(user_id: int, db: AsyncSession) -> list[Document]:
    documents = await repository.get_documents(user_id, db)
    return documents


async def get_document(document_id: int, user_id: int, db: AsyncSession) -> Document:
    document = await repository.get_document(document_id, user_id, db)
    if document is None:
        raise document_exceptions.DocumentDoesNotExistError
    return document
