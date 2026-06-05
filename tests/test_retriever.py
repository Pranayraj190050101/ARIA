import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.retriever import run_retriever_agent

def test_retriever():
    results = run_retriever_agent(
        file_path="data/sample_docs/company_policy.txt",
        query="What is the leave policy?"
    )

    print("\n[TEST] Hybrid Search Results:")
    for i, result in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"Source: {result['source']}")
        print(f"Score:  {result['score']:.4f}")
        print(f"Content: {result['content'][:150]}...")

if __name__ == "__main__":
    test_retriever()