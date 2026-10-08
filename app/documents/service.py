from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.document import Document, DocumentStatus
from app.documents import exceptions as document_exceptions, processing
from app.documents import repository
from app.documents import storage


async def commit_or_fail(db: AsyncSession):
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise document_exceptions.FailedChangeStatusError from e

    
async def upload_document(file: UploadFile, user_id: int, db: AsyncSession) -> Document:
    upload_path = None
    try:
        original_filename, stored_filename, size, upload_path = await storage.save_file(file)
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
        storage.delete_file(upload_path)
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


async def get_file(
    document_id: int,
    user_id: int,
    db: AsyncSession
) -> tuple[Path, str, str]:
    document = await get_document(document_id, user_id, db)
    file_path = storage.get_file_path(document.stored_filename)
    return file_path, document.original_filename, document.content_type


async def delete_document(
    document_id: int,
    user_id: int,
    db: AsyncSession,
) -> None:
    document = await get_document(document_id, user_id, db)
    upload_path = storage.UPLOAD_DIR / document.stored_filename
    try:
        await repository.delete_document(document, db)
        await db.commit()
    except Exception as exc:
        await db.rollback()
        raise document_exceptions.FailedToDeleteDocumentError from exc
    try:
        storage.delete_file(upload_path)
    except Exception:
        pass


async def process_document(
    document_id: int,
    user_id: int,
    db: AsyncSession,
) -> Document:
    document = await repository.get_document_for_update(
        document_id,
        user_id,
        db,
    )
    if document is None:
        raise document_exceptions.DocumentDoesNotExistError
    if document.status == DocumentStatus.processing:
        raise document_exceptions.DocumentAlreadyHandleError
    document.status = DocumentStatus.processing
    document.error = None
    await commit_or_fail(db)
    try:
        file_path = storage.get_file_path(document.stored_filename)
        text = await processing.extract_document_text(file_path, document.content_type)
        await repository.fill_text(document_id, text, db)
        document.status = DocumentStatus.ready
        document.error = None
        await commit_or_fail(db)
    except Exception as e:
        await db.rollback()
        document = await repository.get_document_for_update(
            document_id, user_id, db
        )
        if document is not None:
            document.status = DocumentStatus.failed
            document.error = str(e)
            await commit_or_fail(db)
        raise
    return document


async def get_document_text(document_id: int, user_id, db: AsyncSession) -> str:
    document = await get_document(document_id, user_id, db)
    document_text = await repository.get_document_text(document.id, db)
    if document_text is None:
        raise document_exceptions.DocumentTextNotReadyError
    return document_text.text