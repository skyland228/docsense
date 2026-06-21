from pydantic import BaseModel

class DocumentUploadResponse(BaseModel):
  id: int
  original_filename : str
  stored_filename : str
  file_path : str
  topic : str | None = None