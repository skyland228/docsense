from datetime import datetime
from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column
from docsense.data_base.database import Base
from sqlalchemy import Enum as SqlEnum
from enum import Enum

class DocumentStatus(str,Enum):
  UPLOADED = 'uploaded'
  PROCESSING = 'processing'
  PROCESSED = 'processed'
  FAILED = 'failed'
  
class Document(Base):
  __tablename__ = "documents"
  
  id: Mapped[int] = mapped_column(primary_key=True)
  original_filename: Mapped[str] = mapped_column(String(255))
  stored_filename: Mapped[str] = mapped_column(String(255),unique=True)
  file_path: Mapped[str] = mapped_column(String(500), unique=True)
  content_type: Mapped[str | None] = mapped_column(
    String(100),
    nullable = True,
  )
  status: Mapped[DocumentStatus] = mapped_column(
    SqlEnum(DocumentStatus),
    default=DocumentStatus.UPLOADED,
  )
  topic: Mapped[str|None] = mapped_column(
    String(100),
    nullable = True,
  )
  created_at: Mapped[datetime] = mapped_column(
    DateTime,
    server_default=func.now(),
  )
