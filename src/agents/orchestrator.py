from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from typing import TypedDict
import os

from src.agents.retriever import run_retriever_agent, hybrid_search, build_bm25_index
from src.tools.search_tool import store_chunks
from src.agents.ingestion import run_ingestion_agent

load_dotenv()

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
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


# ── Node 1: Ingest documents ──────────────────────────────
def ingest_node(state: ARIAState) -> ARIAState:
    print("\n[Orchestrator] Step 1: Ingesting document...")
    chunks = run_ingestion_agent(state["file_path"])
    store_chunks(chunks)
    build_bm25_index(chunks)
    state["chunks"] = chunks
    return state


# ── Node 2: Retrieve relevant chunks ─────────────────────
def retrieve_node(state: ARIAState) -> ARIAState:
    print("[Orchestrator] Step 2: Searching for relevant context...")
    results = hybrid_search(state["query"], top_k=5)

    # Filter by score threshold
    filtered = [r for r in results if r["score"] >= 0.60]
    if not filtered:
        filtered = results[:2]  # fallback to top 2

    state["search_results"] = filtered
    state["sources"] = list(set([r["source"] for r in filtered]))
    return state


# ── Node 3: Generate answer ───────────────────────────────
def generate_node(state: ARIAState) -> ARIAState:
    print("[Orchestrator] Step 3: Generating answer...")

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


# ── Build LangGraph ───────────────────────────────────────
def build_aria_graph():
    graph = StateGraph(ARIAState)

    graph.add_node("ingest", ingest_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("generate", generate_node)

    graph.set_entry_point("ingest")
    graph.add_edge("ingest", "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)

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
        "sources": []
    })

    return {
        "answer": result["answer"],
        "sources": result["sources"]
    }