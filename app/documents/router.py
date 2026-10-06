from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
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
    try:
        document = await service.upload_document(file, current_user.id, db)
    except document_exceptions.FileTooLargeError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_PAYLOAD_TOO_LARGE,
            detail='File too large',
        ) from exc
    except document_exceptions.FailedSaveDocumentError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to save document',
        ) from exc
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
    try:
        document = await service.get_document(document_id, current_user.id, db)
    except document_exceptions.DocumentDoesNotExistError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Document does not exist',
        ) from exc
    return document
