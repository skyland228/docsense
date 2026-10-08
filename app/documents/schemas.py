from pydantic import BaseModel, ConfigDict

from app.db.models.document import DocumentStatus


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_filename: str
    size: int
    content_type: str | None = None
    status: DocumentStatus
    error: str | None = None
