import os
import time
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

After your answer, list which source number(s) you relied on, like:
Sources used: [1, 3]

CONTEXT:
{context}

QUESTION:
{question}
"""


def build_context(chunks: list[dict]) -> str:
    """
    Formats retrieved chunks into a numbered list the model can
    reference by number in its citation — this numbering is what
    makes 'Sources used:' possible and verifiable afterward.
    """
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        parts.append(
            f"[{i}] (Document: {chunk['document_title']}, Page: {chunk['page_number']})\n"
            f"{chunk['chunk_text']}"
        )
    return "\n\n".join(parts)


def answer_question(question: str, top_k: int = 3) -> dict:
    chunks = search_chunks(question, top_k=top_k)
    context = build_context(chunks)
    prompt = SYSTEM_PROMPT.format(context=context, question=question)

    try:
        response = client.models.generate_content(
            model=GENERATION_MODEL,
            contents=prompt,
        )
        return {
            "answer": response.text,
            "retrieved_chunks": chunks,
        }
    except ClientError as e:
        if e.code == 429:
            print("\n⚠️ Hit Gemini Free Tier limits. Waiting 20 seconds to auto-retry...")
            time.sleep(20)
            # Retry the exact same request once more after waiting
            response = client.models.generate_content(
                model=GENERATION_MODEL,
                contents=prompt,
            )
            return {
                "answer": response.text,
                "retrieved_chunks": chunks,
            }
        else:
            raise e


if __name__ == "__main__":
    question = input("Ask a question: ")
    # Change top_k from 5 to 2 to dramatically lower input tokens
    result = answer_question(question, top_k=2) 


    print("\n=== ANSWER ===")
    print(result["answer"])

    print("\n=== RETRIEVED SOURCES (for verification) ===")
    for i, c in enumerate(result["retrieved_chunks"], start=1):
        print(f"[{i}] Page {c['page_number']}: {c['chunk_text'][:100]}...")

        
