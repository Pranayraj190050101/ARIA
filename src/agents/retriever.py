from src.tools.search_tool import store_chunks, semantic_search
from src.agents.ingestion import run_ingestion_agent
from rank_bm25 import BM25Okapi


# Store BM25 index in memory
bm25_index = None
bm25_chunks = []


def build_bm25_index(chunks: list[dict]):
    """
    Build BM25 index from chunks for keyword search.
    """
    global bm25_index, bm25_chunks
    bm25_chunks = chunks
    tokenized = [chunk["content"].lower().split() for chunk in chunks]
    bm25_index = BM25Okapi(tokenized)
    print(f"[Retriever Agent] BM25 index built with {len(chunks)} chunks")


def bm25_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Search using BM25 keyword matching.
    """
    if bm25_index is None:
        print("[Retriever Agent] BM25 index not built yet!")
        return []

    tokenized_query = query.lower().split()
    scores = bm25_index.get_scores(tokenized_query)

    top_indices = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )[:top_k]

    return [
        {
            "content": bm25_chunks[i]["content"],
            "source": bm25_chunks[i].get("source", "unknown"),
            "score": scores[i]
        }
        for i in top_indices
    ]


def hybrid_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Hybrid search — combines semantic + BM25 results.
    Deduplicates and returns top results.
    """
    semantic_results = semantic_search(query, top_k)
    bm25_results = bm25_search(query, top_k)

    # Combine and deduplicate by content
    seen = set()
    combined = []

    for result in semantic_results + bm25_results:
        content_key = result["content"][:100]
        if content_key not in seen:
            seen.add(content_key)
            combined.append(result)

    print(f"[Retriever Agent] Hybrid search returned {len(combined)} results")
    return combined[:top_k]


def run_retriever_agent(file_path: str, query: str) -> list[dict]:
    """
    Retriever Agent — ingests document and runs hybrid search.
    """
    # Step 1: Ingest
    chunks = run_ingestion_agent(file_path)

    # Step 2: Store in Qdrant
    store_chunks(chunks)

    # Step 3: Build BM25 index
    build_bm25_index(chunks)

    # Step 4: Hybrid search
    results = hybrid_search(query)

    return results