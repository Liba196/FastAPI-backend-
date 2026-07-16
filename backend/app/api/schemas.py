from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str = Field(..., min_length=1, max_length=2000)


class Citation(BaseModel):
    document_title: str
    page_number: Optional[int] = None


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    citations: list[Citation]
    grounded: bool