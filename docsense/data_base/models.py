from datetime import datetime
from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column
from docsense.data_base.database import Base
from sqlalchemy import Enum as SqlEnum
from enum import Enum

class DocumentStatus(str,Enum):
  UPLOADED = 'uploaded'
  PROCESSED = 'processed'
  FAILED = 'failed'
  
class SummaryStatus(str,Enum):
  NOT_CREATED = 'not_created'
  CREATED = 'created'
  FAILED = 'failed'
  
class Document(Base):
  __tablename__ = "documents"
  
  id: Mapped[int] = mapped_column(primary_key=True)
  original_filename: Mapped[str] = mapped_column(String(255))
  stored_filename: Mapped[str] = mapped_column(String(255),unique=True)
  file_path: Mapped[str] = mapped_column(String(500), unique=True)
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
  summary_title: Mapped[str | None] = mapped_column(nullable=True)
  summary_status: Mapped[SummaryStatus] = mapped_column(SqlEnum(SummaryStatus),
                                                        default = SummaryStatus.NOT_CREATED)
  
