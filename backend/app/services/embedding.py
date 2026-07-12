from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-m3")


def generate_embedding(text: str):

    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    return embedding.tolist()

    