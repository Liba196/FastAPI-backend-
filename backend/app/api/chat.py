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
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {str(e)}")

    all_chunks = result["retrieved_chunks"]
    cited_indices = result["cited_indices"]

    if cited_indices:
        # Only include chunks the model actually claimed to use.
        # Indices are 1-based (matching build_context's [1], [2], ...)
        # and we defensively ignore any out-of-range index rather than
        # crash, in case the model hallucinates a source number that
        # was never actually given to it.
        seen = set()
        citations = []
        for i in cited_indices:
            if not (1 <= i <= len(all_chunks)):
                continue
            chunk = all_chunks[i - 1]
            key = (chunk["document_title"], chunk["page_number"])
            if key in seen:
                continue
            seen.add(key)
            citations.append(
                Citation(document_title=chunk["document_title"], page_number=chunk["page_number"])
            )
    else:
        # No parseable "Sources used" line — either a refusal, or the
        # model didn't follow the format. Either way, we do NOT fall
        # back to returning all retrieved chunks as citations: an
        # unverifiable citation is worse than no citation at all for
        # a legal-accuracy system.
        citations = []

    grounded = bool(citations)

    return ChatResponse(
        session_id=session_id,
        answer=result["answer"],
        citations=citations,
        grounded=grounded,
    )