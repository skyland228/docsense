from pydantic import BaseModel
from docsense.data_base.models import DocumentStatus
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