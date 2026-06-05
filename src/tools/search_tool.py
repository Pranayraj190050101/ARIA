from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from src.utils.embeddings import get_embedding
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

COLLECTION_NAME = "aria_documents"
VECTOR_SIZE =  384 # all-MiniLM-L6-v2 dimension


def create_collection():
    """
    Create Qdrant collection if it doesn't exist.
    """
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )
        print(f"[Search Tool] Collection '{COLLECTION_NAME}' created!")
    else:
        print(f"[Search Tool] Collection '{COLLECTION_NAME}' already exists.")


def store_chunks(chunks: list[dict]):
    """
    Embed and store chunks into Qdrant.
    """
    create_collection()

    points = []
    for chunk in chunks:
        embedding = get_embedding(chunk["content"])
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "content": chunk["content"],
                "source": chunk.get("source", "unknown"),
                "page": chunk.get("page", chunk.get("row", chunk.get("chunk", 0)))
            }
        ))

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"[Search Tool] Stored {len(points)} chunks in Qdrant")


def semantic_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Search Qdrant using semantic similarity.
    """
    query_embedding = get_embedding(query)

    results = client.query_points(
    collection_name=COLLECTION_NAME,
    query=query_embedding,
    limit=top_k
    ).points
    return [
        {
            "content": r.payload["content"],
            "source": r.payload["source"],
            "score": r.score
        }
        for r in results
    ]