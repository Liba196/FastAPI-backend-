from app.services.ingestion.chunker import chunk_text

sample = """
Article 1

This is article one.

Article 2

This is article two.

Article 3

This is article three.
"""

chunks = chunk_text(sample)

for i, chunk in enumerate(chunks):
    print(f"\n------ Chunk {i+1} ------")
    print(chunk)