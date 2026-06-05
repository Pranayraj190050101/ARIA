from src.agents.ingestion import run_ingestion_agent

def test_text_ingestion():
    chunks = run_ingestion_agent("data/sample_docs/sample.txt")
    assert len(chunks) > 0
    assert "content" in chunks[0]
    print("\n[TEST PASSED] Text ingestion works!")
    for chunk in chunks:
        print(f"  Chunk {chunk['chunk']}: {chunk['content'][:50]}...")

if __name__ == "__main__":
    test_text_ingestion()