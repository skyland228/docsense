from collections.abc import Generator

from sqlalchemy.orm import Session

from docsense.data_base.database import SessionLocal


def get_db() -> Generator[Session,None,None]:
  db = SessionLocal()
  
  try:
    yield db
  finally:
    db.close()
    
