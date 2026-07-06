

from fastapi import HTTPException
from sqlalchemy.orm import Session

from docsense.data_base.models import Document, SummaryStatus
from docsense.repositories import documents_repository
from docsense.schemas import DocumentSummary


def documents_summary(db: Session,data: list[DocumentSummary]) -> list[Document]:
  updated_documents = []
  for i in range(len(data)):
    documents = documents_repository.get_document_by_ids(db,data[i].document_ids)
    if not documents:
      raise HTTPException(status_code=404,detail = 'Documents not found')
    for document in documents:
      if data[i].summary_status == SummaryStatus.CREATED and data[i].summary_title is None:
        raise HTTPException(status_code=400, detail='summary is required, when SummaryStatus is created')
      updated_document = documents_repository.patch_summary(document,data[i].summary_title,data[i].summary_status)
      updated_documents.append(updated_document)
  db.commit()
  for document in updated_documents:
    db.refresh(document)
  return updated_documents  
