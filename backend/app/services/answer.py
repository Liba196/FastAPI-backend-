import os
import time
import re 
from google.genai.errors import ClientError
from dotenv import load_dotenv

# FIX 1: Import the modern GenAI SDK
from google import genai 

from app.services.search import search_chunks

load_dotenv()

# FIX 2: Initialize the modern client (automatically detects API keys)
client = genai.Client()

# FIX 3: Clean model identifier without the "models/" prefix
GENERATION_MODEL = "gemini-3.5-flash"  

SYSTEM_PROMPT = """You are POESSA's official pension-law assistant.

Answer ONLY using the CONTEXT below. Every factual statement you make
must be traceable to a specific numbered source in the CONTEXT.

If the CONTEXT does not contain enough information to answer the
QUESTION, say exactly: "I could not find an official answer to this
question in the available documents." Do not guess or use outside
knowledge, even if you believe you know the answer.

Formatting rules:
- Write in plain sentences and simple numbered lines only. Do NOT use
  Markdown formatting (no **bold**, no bullet asterisks, no headers).
- Do NOT include bracketed source numbers like [1] or [2, 3] anywhere
  inside the answer text itself.

After the full answer, on its own final line, list which source
number(s) you relied on, like:
Sources used: [1, 3]

CONTEXT:
{context}

QUESTION:
{question}
"""
def build_context(chunks: list) -> str:
    """Formats retrieved chunks into a numbered context string."""
    context_str = ""
    for i, chunk in enumerate(chunks, start=1):
        context_str += f"[{i}] Page {chunk.get('page_number', 'N/A')}:\n{chunk.get('chunk_text', '')}\n\n"
    return context_str.strip()


def parse_sources_used(raw_answer: str) -> tuple[str, list[int] | None]:
    match = re.search(r"Sources used:\s*\[(.*?)\]", raw_answer, re.IGNORECASE)

    cleaned = re.sub(r"\n*Sources used:.*", "", raw_answer, flags=re.IGNORECASE).strip()

    # Defense-in-depth: strip any inline bracket-number citations that
    # slipped through despite the prompt instruction — these are
    # internal source-list indices, meaningless to a citizen reading
    # the prose. Real citations are rendered separately as chips.
    cleaned = re.sub(r"\s*\[\s*\d+(?:\s*,\s*\d+)*\s*\]", "", cleaned)

    if not match:
        return cleaned, None

    try:
        indices = [int(n.strip()) for n in match.group(1).split(",") if n.strip()]
        return cleaned, indices
    except ValueError:
        return cleaned, None


def answer_question(question: str, top_k: int = 5) -> dict:
    chunks = search_chunks(question, top_k=top_k)
    context = build_context(chunks)
    prompt = SYSTEM_PROMPT.format(context=context, question=question)

    try:
        # 1. Call the API and assign it explicitly to the response variable
        response = client.models.generate_content(
            model=GENERATION_MODEL,
            contents=prompt
        )
        
        # 2. Extract the text safely
        raw_text = response.text or ""
        
    except Exception as e:
        # Fallback if the network call fails entirely
        print(f"API Error occurred: {e}")
        raw_text = ""

    # 3. Pass the valid string variable into your parser
    clean_answer, cited_indices = parse_sources_used(raw_text)

    return {
        "answer": clean_answer,
        "retrieved_chunks": chunks,
        "cited_indices": cited_indices,
    }

if __name__ == "__main__":
    question = input("Ask a question: ")
    # Change top_k from 5 to 2 to dramatically lower input tokens
    result = answer_question(question, top_k=2) 


    print("\n=== ANSWER ===")
    print(result["answer"])

    print("\n=== RETRIEVED SOURCES (for verification) ===")
    for i, c in enumerate(result["retrieved_chunks"], start=1):
        print(f"[{i}] Page {c['page_number']}: {c['chunk_text'][:100]}...")
