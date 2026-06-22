from sqlalchemy.orm import Session
from docsense.data_base.models import Document

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
