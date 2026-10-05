

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, UploadFile

from app.db.models.document import Document
from app.db.models.user import User
from app.dependencies import get_current_user, get_db
from app.schemas.document import DocumentResponse
from app.services import document as document_service


router = APIRouter(prefix='/documents', tags=['document'])


@router.post('', response_model=DocumentResponse)
async def upload_document(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Document:
    document = await document_service.upload_document(file, current_user.id, db)
    return document


@router.get('', response_model=list[DocumentResponse])
async def get_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Document]:
    return await document_service.get_documents(current_user.id, db)