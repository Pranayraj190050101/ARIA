from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.agents.orchestrator import run_aria
import shutil
import os

app = FastAPI(
    title="ARIA — Agentic Retrieval & Intelligent Analysis",
    description="Multi-document AI Agent with RAG, Hybrid Search, Guardrails & RAGAS",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

UPLOAD_DIR = "data/sample_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ── Health check ──────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ARIA is running!", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}


# ── Upload document ───────────────────────────────────────
@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {
        "message": f"File '{file.filename}' uploaded successfully!",
        "file_path": file_path
    }


# ── Query ARIA ────────────────────────────────────────────
class QueryRequest(BaseModel):
    query: str
    filename: str


@app.post("/query")
async def query_aria(request: QueryRequest):
    file_path = os.path.join(UPLOAD_DIR, request.filename)

    if not os.path.exists(file_path):
        return {"error": f"File '{request.filename}' not found. Please upload it first."}

    result = run_aria(
        file_path=file_path,
        query=request.query
    )

    return {
        "query": request.query,
        "answer": result["answer"],
        "sources": result["sources"],
        "metrics": result["metrics"],
        "blocked": result["blocked"]
    }


# ── List uploaded documents ───────────────────────────────
@app.get("/documents")
def list_documents():
    files = os.listdir(UPLOAD_DIR)
    return {"documents": files}