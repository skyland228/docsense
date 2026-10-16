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


class DocumentSummaryResponse(BaseModel):
    document_id: int
    summary: str


class DocumentVersionResponse(BaseModel):
    document_id: int
    version_number: int
    extracted_text: str
    similarity: float | None
    warning: str | None


class DocumentDiffRequest(BaseModel):
    version_from: int
    version_to: int


class DocumentDiffResponse(BaseModel):
    document_id: int
    version_from: int
    version_to: int
    diff_summary: str