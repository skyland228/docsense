from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from docsense.dependencies import get_db
from docsense.services import documents_sort_service


router = APIRouter(tags = ['sort'])

@router.post("/sort")
def sort_documents(db: Session = Depends(get_db)):
  return documents_sort_service.sort_documents(db)