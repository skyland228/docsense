from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.document import Document, DocumentStatus, DocumentVersion
from app.documents.ai_service import ai_service
from app.documents import exceptions as document_exceptions, processing
from app.documents import repository
from app.documents import storage


async def commit_or_fail(db: AsyncSession):
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise document_exceptions.FailedChangeStatusError from e

    
async def upload_document(file: UploadFile, auto_extract: bool, user_id: int, db: AsyncSession) -> Document:
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
        await db.flush()
        if auto_extract:
            text = await processing.extract_document_text(upload_path, document.content_type)
            await repository.fill_text(document_id=document.id, text=text, db=db)
            repository.create_version(
                document_id=document.id,
                version_number=1,
                file_path=str(upload_path),
                extracted_text=text,
                db=db,
            )
            document.status = DocumentStatus.ready
        await db.commit()
    except (document_exceptions.FileTooLargeError, document_exceptions.ProcessingError):
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


async def create_version(
    document_id: int,
    file: UploadFile,
    user_id: int,
    db: AsyncSession
) -> tuple[DocumentVersion, float | None, str | None]:
    document = await get_document(document_id, user_id, db)
    upload_path = None
    try:
        *_, upload_path = await storage.save_file(file)
        text = await processing.extract_document_text(upload_path, file.content_type)
        number_version = await repository.get_next_version_number(document_id, db)
        previous_version = await repository.get_version_by_number(
            document_id,
            number_version - 1,
            db,
        )
        similarity = None
        warning = None
        if previous_version is not None:
            similarity = processing.calculate_similarity(
                previous_version.extracted_text,
                text,
            )
            if similarity > 0.7:
                warning = None
            elif similarity > 0.2:
                warning = 'New version differs significantly from the previous version'
            else:
                raise document_exceptions.DocumentVersionTooDifferentError  
        version = repository.create_version(
                document_id,
                number_version,
                str(upload_path),
                text,
                db,
            )
        await db.commit()
    except Exception:
        await db.rollback()
        storage.delete_file(upload_path)
        raise 
    return version, similarity, warning


async def diff_document_versions(
    document_id: int,
    version_from_num: int,
    version_to_num: int,
    user_id: int,
    db: AsyncSession,
) -> str:
    await get_document(document_id, user_id, db)
    v_from = await repository.get_version_by_number(document_id, version_from_num, db)
    if not v_from:
        raise document_exceptions.DocumentVersionDoesNotExist(
            detail=f'Версия {version_from_num} не найдена')
    v_to = await repository.get_version_by_number(document_id, version_to_num, db)
    if not v_to:
        raise document_exceptions.DocumentVersionDoesNotExist(
            detail=f'Версия {version_to_num} не найдена')
    document_diff = await repository.get_document_diff(
        document_id,
        v_from.id,
        v_to.id,
        db,
    )
    if document_diff:
        return document_diff.ai_summary
    delta_lines = processing.compute_text_diff(
        v_from.extracted_text,
        v_to.extracted_text
    )
    if delta_lines:
        ai_summary = await ai_service.diff_versions(delta_lines)
        repository.create_document_diff(
            document_id,
            v_from.id,
            v_to.id,
            delta_lines,
            ai_summary,
            db,
        )
        await db.commit()
        return ai_summary
    return 'no changes'