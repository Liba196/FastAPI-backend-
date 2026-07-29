# backend/app/api/document_schemas.py
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    title: str
    source_filename: str
    status: str
    error_message: str | None