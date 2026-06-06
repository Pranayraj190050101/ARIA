from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from typing import TypedDict
import os

from src.agents.retriever import hybrid_search, build_bm25_index
from src.tools.search_tool import store_chunks
from src.agents.ingestion import run_ingestion_agent
from src.agents.evaluator import guard_input, run_evaluator_agent

load_dotenv()

# Initialize Gemini LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.2
)

# Define ARIA's state
class ARIAState(TypedDict):
    query: str
    file_path: str
    chunks: list
    search_results: list
    answer: str
    sources: list
    metrics: dict
    blocked: bool
    block_reason: str


# ── Node 1: Guard input ───────────────────────────────────
def guard_node(state: ARIAState) -> ARIAState:
    print("\n[Orchestrator] Step 1: Checking input safety...")
    is_safe, result = guard_input(state["query"])

    if not is_safe:
        state["blocked"] = True
        state["block_reason"] = result
        state["answer"] = result
    else:
        state["blocked"] = False
        state["query"] = result  # use redacted version if PII found

    return state


# ── Node 2: Ingest documents ──────────────────────────────
def ingest_node(state: ARIAState) -> ARIAState:
    print("[Orchestrator] Step 2: Ingesting all documents...")
    all_chunks = []
    doc_dir = "data/sample_docs"

    for filename in os.listdir(doc_dir):
        if filename.endswith((".pdf", ".csv", ".txt")):
            file_path = os.path.join(doc_dir, filename)
            try:
                chunks = run_ingestion_agent(file_path)
                all_chunks.extend(chunks)
                print(f"[Orchestrator] Ingested: {filename}")
            except Exception as e:
                print(f"[Orchestrator] Skipped {filename}: {e}")

    store_chunks(all_chunks)
    build_bm25_index(all_chunks)
    state["chunks"] = all_chunks
    return state


# ── Node 3: Retrieve relevant chunks ─────────────────────
def retrieve_node(state: ARIAState) -> ARIAState:
    print("[Orchestrator] Step 3: Searching for relevant context...")
    results = hybrid_search(state["query"], top_k=5)

    # Filter by score threshold
    filtered = [r for r in results if r["score"] >= 0.60]
    if not filtered:
        filtered = results[:2]  # fallback to top 2

    state["search_results"] = filtered
    state["sources"] = list(set([r["source"] for r in filtered]))
    return state


# ── Node 4: Generate answer ───────────────────────────────
def generate_node(state: ARIAState) -> ARIAState:
    print("[Orchestrator] Step 4: Generating answer...")
    groq_key = os.getenv("GROQ_API_KEY")
    print(f"[Orchestrator] GROQ_API_KEY loaded: {bool(groq_key)}")

    context = "\n\n".join([r["content"] for r in state["search_results"]])

    prompt = f"""You are ARIA — Agentic Retrieval and Intelligent Analysis assistant.
Answer the question using ONLY the context provided below.
If the answer is not in the context, say "I don't have enough information to answer that."
Always be concise and precise.

Context:
{context}

Question: {state["query"]}

Answer:"""

    response = llm.invoke(prompt)
    state["answer"] = response.content
    return state


# ── Node 5: Evaluate response ─────────────────────────────
def evaluate_node(state: ARIAState) -> ARIAState:
    print("[Orchestrator] Step 5: Evaluating response...")
    result = run_evaluator_agent(
        query=state["query"],
        answer=state["answer"],
        context_chunks=state["search_results"]
    )
    state["answer"] = result["answer"]
    state["metrics"] = result["metrics"]
    return state


# ── Conditional routing ───────────────────────────────────
def should_continue(state: ARIAState) -> str:
    if state.get("blocked"):
        return END
    return "ingest"


# ── Build LangGraph ───────────────────────────────────────
def build_aria_graph():
    graph = StateGraph(ARIAState)

    graph.add_node("guard", guard_node)
    graph.add_node("ingest", ingest_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("generate", generate_node)
    graph.add_node("evaluate", evaluate_node)

    graph.set_entry_point("guard")
    graph.add_conditional_edges("guard", should_continue)
    graph.add_edge("ingest", "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", "evaluate")
    graph.add_edge("evaluate", END)

    return graph.compile()


# ── Main runner ───────────────────────────────────────────
def run_aria(file_path: str, query: str) -> dict:
    aria = build_aria_graph()

    result = aria.invoke({
        "query": query,
        "file_path": file_path,
        "chunks": [],
        "search_results": [],
        "answer": "",
        "sources": [],
        "metrics": {},
        "blocked": False,
        "block_reason": ""
    })

    return {
        "answer": result["answer"],
        "sources": result["sources"],
        "metrics": result.get("metrics", {}),
        "blocked": result.get("blocked", False)
    }