import os
from dotenv import load_dotenv
import psycopg
from pgvector.psycopg import register_vector
# FIX 1: Import the modern GenAI SDK
from google import genai 

load_dotenv()

# FIX 2: Initialize the modern client (it automatically picks up GEMINI_API_KEY or GOOGLE_API_KEY from env)
client = genai.Client()

DB_URL = os.environ["DATABASE_URL"]
EMBEDDING_MODEL = "gemini-embedding-2" # Standard text embedding model for Gemini

def embed_query(question: str) -> list[float]:
    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=question, 
    )
    
    # 1. Safely extract the embeddings list
    embeddings_list = result.embeddings
    
    # 2. Check that the response is valid and contains data
    if not embeddings_list or not embeddings_list[0].values:
        raise ValueError("Failed to generate embedding vector from Google API.")
        
    # 3. Return the guaranteed list of floats (Pylance is now happy)
    return embeddings_list[0].values


def search_chunks(question: str, top_k: int = 5) -> list[dict]:
    """
    Embeds the question, then finds the top_k closest chunks in Postgres by cosine distance.
    Returns them ordered from most to least relevant.
    """
    query_vector = embed_query(question)
    
    with psycopg.connect(DB_URL) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 
                    chunks.id, 
                    chunks.chunk_text, 
                    chunks.page_number, 
                    documents.title AS document_title, 
                    chunks.embedding <=> %s::vector AS distance -- FIX: Added ::vector cast here
                FROM chunks
                JOIN documents ON documents.id = chunks.document_id
                ORDER BY distance ASC
                LIMIT %s
                """,
                (query_vector, top_k),
            )
            rows = cur.fetchall()
            
    # Also fixed the row index unpacking bug from earlier
    return [
        {
            "chunk_id": row[0],
            "chunk_text": row[1],
            "page_number": row[2],
            "document_title": row[3],
            "distance": row[4],
        }
        for row in rows
    ]

if __name__ == "__main__":
    question = input("Ask a question about the pension directive: ")
    results = search_chunks(question, top_k=5)
    
    print(f"\nTop {len(results)} matches:\n")
    for i, r in enumerate(results, start=1):
        print(f"#{i} — distance={r['distance']:.4f}, page {r['page_number']}")
        print(f"   {r['chunk_text']}")
        print()
