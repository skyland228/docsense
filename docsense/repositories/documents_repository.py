from sqlalchemy.orm import Session
from docsense.data_base.models import Document, DocumentStatus

def create_document(db:Session,original_filename:str,
                    stored_filename: str,
                    file_path:str) -> Document:
  document = Document(original_filename = original_filename,
                      stored_filename = stored_filename,
                      file_path = file_path,)
  db.add(document)
  return document

def get_document(db:Session,document_id:int) -> Document | None:
  return db.query(Document).filter(Document.id == document_id).first()

def get_documents(db: Session) -> list[Document]:
  return db.query(Document).all()

def delete_document(db: Session, document: Document) -> None:
  db.delete(document)
  
def update_document_analysis(
  document: Document,
  status: DocumentStatus,
  topic: str|None,
) -> Document:
  document.status = status
  document.topic = topic
  return document