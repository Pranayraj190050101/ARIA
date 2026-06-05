import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.orchestrator import run_aria

def test_orchestrator():
    result = run_aria(
        file_path="data/sample_docs/company_policy.txt",
        query="What is the leave policy?"
    )

    print("\n" + "="*50)
    print("ARIA RESPONSE")
    print("="*50)
    print(f"\nAnswer:\n{result['answer']}")
    print(f"\nSources: {result['sources']}")
    print("="*50)

if __name__ == "__main__":
    test_orchestrator()