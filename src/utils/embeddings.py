from sentence_transformers import SentenceTransformer


# Runs locally — no API key needed, no rate limits!
model = SentenceTransformer('all-MiniLM-L6-v2')

VECTOR_SIZE = 384  # all-MiniLM-L6-v2 dimension


def get_embedding(text: str) -> list[float]:
    """
    Generate embedding locally using HuggingFace SentenceTransformer.
    """
    return model.encode(text).tolist()


def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of texts.
    """
    return model.encode(texts).tolist()