from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from docsense.dependencies import get_db
from docsense.schemas import DocumentDelete
from docsense.services import documents_delete_service


router = APIRouter(tags=["documents delete"])

@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    return documents_delete_service.delete_document(db, document_id)

@router.delete("")
def delete_documents(data: DocumentDelete,db: Session = Depends(get_db)):
    return documents_delete_service.delete_documents(db,data.ids)
