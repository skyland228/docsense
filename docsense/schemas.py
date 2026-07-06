from pydantic import BaseModel
from docsense.data_base.models import DocumentStatus, SummaryStatus
from datetime import datetime

class DocumentUploadResponse(BaseModel):
  id: int
  original_filename : str
  stored_filename : str
  file_path : str
  topic : str | None = None
  
class DocumentResponse(BaseModel):
  id: int
  stored_filename: str
  status: DocumentStatus
  topic: str|None = None
  created_at: datetime
  
class DocumentAnalysisUpdate(BaseModel):
  status: DocumentStatus
  topic: str|None = None
  
class DocumentTopicUpdateBulk(BaseModel):
  document_ids: list[int]
  topic : str | None = None
  status: DocumentStatus
  
class DocumentSummary(BaseModel):
  document_ids: list[int]
  summary_title: str | None = None
  summary_status: SummaryStatus
  
class DocumentDelete(BaseModel):
  ids: list[int]