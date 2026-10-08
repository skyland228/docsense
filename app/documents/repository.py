from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.document import Document, DocumentText


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


def fill_text(document_id: int, text: str, db: AsyncSession) -> None:
    document_text = DocumentText(
        document_id=document_id,
        text=text,
    )
    db.add(document_text)