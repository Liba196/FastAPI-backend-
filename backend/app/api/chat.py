import uuid
from fastapi import APIRouter, HTTPException

from app.api.schemas import ChatRequest, ChatResponse, Citation
from app.services.answer import answer_question

router = APIRouter()

REFUSAL_TEXT = "I could not find an official answer to this question in the available documents."


@router.post("/api/v1/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())

    try:
        result = answer_question(request.message)
    except Exception as e:
        # We don't yet distinguish "Gemini down" from "DB down" from
        # other failures — that's real hardening work for later
        # (Phase 8's UPSTREAM_UNAVAILABLE error code). For now, fail
        # loudly and honestly rather than pretend everything's fine.
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {str(e)}")

    citations = [
        Citation(document_title=chunk["document_title"], page_number=chunk["page_number"])
        for chunk in result["retrieved_chunks"]
    ]

    grounded = REFUSAL_TEXT not in result["answer"]

    return ChatResponse(
        session_id=session_id,
        answer=result["answer"],
        citations=citations,
        grounded=grounded,
    )