from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.document import Document, DocumentText, DocumentVersion


def create_document(
    original_filename: str,
    stored_filename: str,
    content_type: str,
    size: int,
    user_id: int,
    db: AsyncSession,
) -> Document:
    document = Document(
        original_filename=original_filename,
        stored_filename=stored_filename,
        content_type=content_type,
        size=size,
        user_id=user_id,
    )
    db.add(document)
    return document


async def get_documents(user_id: int, db: AsyncSession) -> list[Document]:
    stmt = select(Document).where(Document.user_id == user_id)
    results = await db.execute(stmt)
    return results.scalars().all()


async def get_document(document_id: int, user_id: int, db: AsyncSession) -> Document:
    stmt = select(Document).where(
        Document.id == document_id,
        Document.user_id == user_id,
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_document_for_update(
        document_id: int,
        user_id: int,
        db: AsyncSession,
) -> Document | None:
    stmt = select(Document).where(
        Document.id == document_id,
        Document.user_id == user_id,
    ).with_for_update()
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def delete_document(document: Document, db: AsyncSession) -> None:
    await db.delete(document)


async def fill_text(document_id: int, text: str, db: AsyncSession) -> None:
    document_text = await db.get(DocumentText, document_id)
    if document_text is None:
        document_text = DocumentText(
            document_id=document_id,
            text=text,
        )
        db.add(document_text)
    else:
        document_text.text = text
        

async def get_document_text(
    document_id: int,
    db: AsyncSession,
) -> DocumentText | None:
    return await db.get(DocumentText, document_id)


def create_version(
    document_id: int,
    version_number: int,
    file_path: str,
    extracted_text: str,
    db: AsyncSession,
) -> DocumentVersion:
    version = DocumentVersion(
        document_id=document_id,
        version_number=version_number,
        file_path=file_path,
        extracted_text=extracted_text,
    )
    db.add(version)
    return version


async def get_next_version_number(document_id: int, db: AsyncSession) -> int:
    query = select(func.coalesce(func.max(DocumentVersion.version_number), 0)).where(
        DocumentVersion.document_id == document_id
    )
    current_max = await db.scalar(query)
    return (current_max or 0) + 1


async def get_version_by_number(
    document_id: int,
    version_number: int,
    db: AsyncSession,
) -> DocumentVersion | None:
    query = select(DocumentVersion).where(
        DocumentVersion.document_id == document_id,
        DocumentVersion.version_number == version_number,
    )
    return await db.scalar(query)