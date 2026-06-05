from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

VECTOR_SIZE = 3072  # gemini-embedding-001 dimension


def get_embedding(text: str) -> list[float]:
    """
    Generate embedding for a single text using Gemini.
    """
    result = client.models.embed_content(
        model="models/gemini-embedding-001",
        contents=text
    )
    return result.embeddings[0].values


def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of texts.
    """
    return [get_embedding(text) for text in texts]