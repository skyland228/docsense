from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.document import Document
from app.db.models.user import User
from app.dependencies import get_current_user, get_db
from app.documents import exceptions as document_exceptions
from app.documents import service
from app.documents.schemas import DocumentResponse


router = APIRouter(prefix='/documents', tags=['document'])


@router.post('', response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Document:
    document = await service.upload_document(file, current_user.id, db)
    return document


@router.get('', response_model=list[DocumentResponse])
async def get_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Document]:
    return await service.get_documents(current_user.id, db)


@router.get('/{document_id}', response_model=DocumentResponse)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Document:
    document = await service.get_document(document_id, current_user.id, db)
    return document


@router.get('/{document_id}/file')
async def download_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    file_path, original_filename, content_type = await service.get_file(
        document_id,
        current_user.id,
        db
    )
    return FileResponse(
        path=file_path,
        filename=original_filename,
        media_type=content_type,
    )


@router.delete('/{document_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await service.delete_document(document_id, current_user.id, db)


@router.post('/{document_id}/process', response_model=DocumentResponse)
async def process_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Document:
    document = await service.process_document(document_id, current_user.id, db)
    return document


@router.get('/{document_id}/text')
async def get_document_text(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PlainTextResponse:
    text = await service.get_document_text(document_id, current_user.id, db)
    return PlainTextResponse(content=text)