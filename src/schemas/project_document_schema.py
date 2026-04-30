from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ProjectDocumentResponse(BaseModel):
    id: str
    project_id: str
    organization_id: str
    uploaded_by_user_id: str | None = None
    document_type: str
    upload_status: str
    file_name: str
    mime_type: str
    file_size: float
    storage_path: str
    checksum: str
    extracted_text: str | None = None
    visibility_scope: str
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime


class ProjectDocumentListResponse(BaseModel):
    project_id: str
    count: int
    documents: list[ProjectDocumentResponse]
