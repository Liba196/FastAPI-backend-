import os
import time
from dotenv import load_dotenv
import psycopg
from pgvector.psycopg import register_vector

# Modern Google GenAI SDK imports
from google import genai
from google.genai.errors import APIError

from app.services.ingest import extract_text, chunk_text

load_dotenv()
# Load API key from common environment variable names. Prefer a dedicated
# GOOGLE_API_KEY but fall back to a generic API_KEY. Ensure we authenticate
# in a way that's compatible with different versions of the SDK.
api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("API_KEY")
if not api_key:
    raise RuntimeError("Missing Google Generative AI API key (set GOOGLE_API_KEY or API_KEY)")

# Use configure() if provided by the package, otherwise set the attribute.
# Use getattr to avoid static analyzers complaining when 'configure' is not
# exported from the google.generativeai package.
configure_fn = getattr(genai, "configure", None)
if callable(configure_fn):
    configure_fn(api_key=api_key)
else:
    setattr(genai, "api_key", api_key)

client = genai.Client(api_key=api_key)

DB_URL = os.environ["DATABASE_URL"]

EMBEDDING_MODEL = "gemini-embedding-2"
# 15 Requests Per Minute maximum means 1 call every 4 seconds. 
# 4.5 seconds gives a safe boundary padding against network fluctuations.
SECONDS_BETWEEN_CALLS = 4.5  


def embed_chunk(text: str, max_retries: int = 5) -> list[float]:
    for attempt in range(1, max_retries + 1):
        try:
            # FIX: Matches the exact object overload pattern for the new SDK
            result = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=text
            )
            # Validate response shape and return a concrete list[float]
            if not result:
                raise RuntimeError("Empty response from embedding API")

            embeddings = getattr(result, "embeddings", None)
            if not embeddings or len(embeddings) == 0:
                raise RuntimeError("No embeddings found in API response")

            first = embeddings[0]
            values = getattr(first, "values", None)
            if values is None:
                raise RuntimeError("Embedding values missing in API response")

            return list(values)
            
        except APIError as e:
            # Catch resource constraints / rate limits (status 429)
            if e.code == 429:
                wait = 5 * (2 ** (attempt - 1))
                print(f"    Rate limited. Waiting {wait}s before retry {attempt}/{max_retries}...")
                time.sleep(wait)
            else:
                raise e

    raise RuntimeError(f"Failed to embed chunk after {max_retries} retries")


def get_or_create_document(cur, title: str, filename: str) -> tuple[int, int]:
    """
    Makes ingestion resumable. If this file was already (partially)
    ingested, reuse its document_id and report how many chunks already
    exist for it, so we can skip re-embedding work that already succeeded
    instead of starting over and wasting API calls.
    """
    cur.execute("SELECT id FROM documents WHERE source_filename = %s", (filename,))
    row = cur.fetchone()

    if row:
        document_id = row[0]
        cur.execute("SELECT count(*) FROM chunks WHERE document_id = %s", (document_id,))
        existing_count = cur.fetchone()[0]
        print(f"Found existing document id={document_id} with {existing_count} chunks already stored. Resuming.")
        return document_id, existing_count

    cur.execute(
        "INSERT INTO documents (title, source_filename) VALUES (%s, %s) RETURNING id",
        (title, filename),
    )
    document_id = cur.fetchone()[0]
    print(f"Created new document record, id={document_id}")
    return document_id, 0


def ingest_document(pdf_path: str, title: str):
    print(f"Extracting text from {pdf_path}...")
    pages = extract_text(pdf_path)
    chunks = chunk_text(pages)
    print(f"Produced {len(chunks)} chunks")

    with psycopg.connect(DB_URL) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            document_id, already_done = get_or_create_document(cur, title, pdf_path)
            conn.commit()  # commit immediately so the document row is safe even if we crash later

            for i, chunk in enumerate(chunks):
                if i < already_done:
                    continue  # skip chunks we already embedded and stored in a previous run

                vector = embed_chunk(chunk["text"])

                cur.execute(
                    """
                    INSERT INTO chunks (document_id, page_number, chunk_text, embedding)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (document_id, chunk["page_number"], chunk["text"], vector),
                )
                conn.commit()  # commit after EVERY chunk so progress is cached securely

                print(f"  Embedded + stored chunk {i + 1}/{len(chunks)}")
                time.sleep(SECONDS_BETWEEN_CALLS)

    print("Done.")
    return document_id


if __name__ == "__main__":
    # Make sure you run this script with your terminal located inside F:\COLLEGE\Poessa\
    # Run command: python -m backend.app.services.embed_and_store
    ingest_document(
        "backend/documents/sample.pdf",  # Fixed: Added 'backend/' prefix path
        title="Private Organizations Employees' Pension Implementation Directive No. 01/2016",
    )
