from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from docsense.dependencies import get_db
from docsense.services import maintenance_service

router = APIRouter(prefix = '/maintenance',tags=['maintenance'])

@router.get('/orphans')
def get_documents_orphans(db: Session = Depends(get_db)):
  return maintenance_service.get_documents_orphans(db)

@router.post('/clean_up')
def cleanup_documents_orphans(db: Session = Depends(get_db)):
  return maintenance_service.cleanup_documents_orphans(db)