from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.document import Document, DocumentStatus, DocumentVersion
from app.documents import exceptions as document_exceptions
from app.documents import processing, repository, storage
from app.documents.ai_service import ai_service


async def commit_or_fail(db: AsyncSession) -> None:
    try:
        await db.commit()
    except Exception as exc:
        await db.rollback()
        raise document_exceptions.FailedChangeStatusError from exc


# Document CRUD
async def upload_document(
    file: UploadFile,
    auto_extract: bool,
    user_id: int,
    db: AsyncSession,
) -> Document:
    upload_path = None
    try:
        original_filename, stored_filename, size, upload_path = await storage.save_file(
            file
        )
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
            text = await processing.extract_document_text(
                upload_path,
                document.content_type,
            )
            await repository.fill_text(document.id, text, db)
            repository.create_version(
                document_id=document.id,
                version_number=1,
                file_path=str(upload_path),
                extracted_text=text,
                db=db,
            )
            document.status = DocumentStatus.ready

        await db.commit()
    except (
        document_exceptions.FileTooLargeError,
        document_exceptions.ProcessingError,
    ):
        await db.rollback()
        raise
    except Exception as exc:
        await db.rollback()
        storage.delete_file(upload_path)
        raise document_exceptions.FailedSaveDocumentError from exc

    await db.refresh(document)
    return document


async def get_documents(user_id: int, db: AsyncSession) -> list[Document]:
    return await repository.get_documents(user_id, db)


async def get_document(
    document_id: int,
    user_id: int,
    db: AsyncSession,
) -> Document:
    document = await repository.get_document(document_id, user_id, db)
    if document is None:
        raise document_exceptions.DocumentDoesNotExistError
    return document


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


async def get_file(
    document_id: int,
    user_id: int,
    db: AsyncSession,
) -> tuple[Path, str, str]:
    document = await get_document(document_id, user_id, db)
    file_path = storage.get_file_path(document.stored_filename)
    return file_path, document.original_filename, document.content_type


# Document processing
async def process_document(
    document_id: int,
    user_id: int,
    db: AsyncSession,
) -> Document:
    document = await repository.get_document_for_update(document_id, user_id, db)
    if document is None:
        raise document_exceptions.DocumentDoesNotExistError
    if document.status == DocumentStatus.processing:
        raise document_exceptions.DocumentAlreadyHandleError

    document.status = DocumentStatus.processing
    document.error = None
    await commit_or_fail(db)

    try:
        file_path = storage.get_file_path(document.stored_filename)
        text = await processing.extract_document_text(
            file_path,
            document.content_type,
        )
        await repository.fill_text(document_id, text, db)
        document.status = DocumentStatus.ready
        document.error = None
        await commit_or_fail(db)
    except Exception as exc:
        await db.rollback()
        document = await repository.get_document_for_update(document_id, user_id, db)
        if document is not None:
            document.status = DocumentStatus.failed
            document.error = str(exc)
            await commit_or_fail(db)
        raise

    return document


async def get_document_text(
    document_id: int,
    user_id: int,
    db: AsyncSession,
) -> str:
    document = await get_document(document_id, user_id, db)
    document_text = await repository.get_document_text(document.id, db)
    if document_text is None:
        raise document_exceptions.DocumentTextNotReadyError
    return document_text.text


# Document versioning
async def create_version(
    document_id: int,
    file: UploadFile,
    user_id: int,
    db: AsyncSession,
) -> tuple[DocumentVersion, float | None, str | None]:
    await get_document(document_id, user_id, db)
    upload_path = None

    try:
        *_, upload_path = await storage.save_file(file)
        text = await processing.extract_document_text(upload_path, file.content_type)
        version_number = await repository.get_next_version_number(document_id, db)
        previous_version = await repository.get_version_by_number(
            document_id,
            version_number - 1,
            db,
        )

        similarity = None
        msg = None
        if previous_version is not None:
            similarity = processing.calculate_similarity(
                previous_version.extracted_text,
                text,
            )
            if similarity <= 0.2:
                raise document_exceptions.DocumentVersionTooDifferentError
            if similarity <= 0.7:
                msg = "New version differs significantly from the previous version"

        version = repository.create_version(
            document_id=document_id,
            version_number=version_number,
            file_path=str(upload_path),
            extracted_text=text,
            similarity=similarity,
            msg=msg,
            db=db,
        )
        await db.commit()
    except Exception:
        await db.rollback()
        storage.delete_file(upload_path)
        raise

    return version, similarity, msg


async def get_versions(
    document_id: int,
    user_id: int,
    db: AsyncSession,
) -> list[dict[str, object]]:
    await get_document(document_id, user_id, db)
    versions = await repository.get_versions(document_id, db)
    return [
        {
            "document_id": version.document_id,
            "version_number": version.version_number,
            "similarity": version.similarity,
            "msg": version.msg,
        }
        for version in versions
    ]


async def get_version(
    document_id: int,
    version_number: int,
    user_id: int,
    db: AsyncSession,
) -> dict[str, object]:
    await get_document(document_id, user_id, db)
    version = await repository.get_version_by_number(
        document_id,
        version_number,
        db,
    )
    if version is None:
        raise document_exceptions.DocumentVersionDoesNotExist

    return {
        "document_id": version.document_id,
        "version_number": version.version_number,
        "extracted_text": version.extracted_text,
        "similarity": version.similarity,
        "msg": version.msg,
    }


# AI version comparison
async def diff_document_versions(
    document_id: int,
    version_from_number: int,
    version_to_number: int,
    user_id: int,
    db: AsyncSession,
) -> str:
    await get_document(document_id, user_id, db)

    version_from = await repository.get_version_by_number(
        document_id,
        version_from_number,
        db,
    )
    if version_from is None:
        raise document_exceptions.DocumentVersionDoesNotExist(
            detail=f"Version {version_from_number} does not exist"
        )

    version_to = await repository.get_version_by_number(
        document_id,
        version_to_number,
        db,
    )
    if version_to is None:
        raise document_exceptions.DocumentVersionDoesNotExist(
            detail=f"Version {version_to_number} does not exist"
        )

    document_diff = await repository.get_document_diff(
        document_id=document_id,
        from_version_id=version_from.id,
        to_version_id=version_to.id,
        db=db,
    )
    if document_diff is not None:
        return document_diff.ai_summary

    raw_diff = processing.compute_text_diff(
        version_from.extracted_text,
        version_to.extracted_text,
    )
    if not raw_diff:
        return "no changes"

    ai_summary = await ai_service.diff_versions(raw_diff)
    repository.create_document_diff(
        document_id=document_id,
        from_version_id=version_from.id,
        to_version_id=version_to.id,
        raw_diff=raw_diff,
        ai_summary=ai_summary,
        db=db,
    )
    await db.commit()
    return ai_summary
