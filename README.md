---
title: ARIA
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: 1.58.0
app_file: app.py
pinned: false
---

# 🤖 ARIA — Agentic Retrieval & Intelligent Analysis

![Python](https://img.shields.io/badge/Python-3.11-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic-orange)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-red)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-black)

A production-grade multi-document AI agent that intelligently answers questions across PDF, CSV, and text files using agentic RAG, hybrid search, guardrails, and RAGAS evaluation.

---

## 🏗️ Architecture

```
User Query
    ↓
🛡️  Guardrails Agent (PII + Prompt Injection check)
    ↓
🧠  Orchestrator Agent (LangGraph)
    ↙           ↓           ↘
PDF Tool    CSV Tool    Text Tool
    ↘           ↓           ↙
    Hybrid Search (BM25 + Qdrant Semantic)
            ↓
    Groq LLM — Answer Generation
            ↓
    RAGAS Evaluation (Faithfulness, Relevancy, Precision)
            ↓
    Final Answer + Sources + Metrics
```

---

## ⚡ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Agent Framework | LangGraph | Orchestration & routing |
| LLM | Groq (llama-3.3-70b) | Answer generation |
| Embeddings | HuggingFace (all-MiniLM-L6-v2) | Local, no rate limits |
| Vector DB | Qdrant Cloud | Vector storage & search |
| Hybrid Search | BM25 + Semantic | Best of keyword + meaning |
| Document Parsing | PyMuPDF, Pandas, Plain Text | PDF, CSV, TXT support |
| Guardrails | Custom PII + Injection Detection | Safety & security |
| Evaluation | RAGAS-style Metrics | Answer quality scoring |
| API | FastAPI | Production REST API |
| Frontend | Huggingface | Interactive chat UI |
| Containerization | Docker | Deployment ready |
| CI/CD | GitHub Actions | Automated pipeline |

---

## 🤖 Multi-Agent Design

ARIA is built as a system of specialized agents:

| Agent | Responsibility |
|---|---|
| **Ingestion Agent** | Detects file type, routes to correct parser |
| **Retriever Agent** | Hybrid BM25 + semantic search over Qdrant |
| **Orchestrator Agent** | LangGraph brain — plans, routes, generates |
| **Evaluator Agent** | RAGAS metrics + guardrails safety checks |

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/Pranayraj190050101/ARIA.git
cd ARIA
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate       # Mac/Linux
venv\Scripts\activate          # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
```

Add your keys to `.env`:
```env
GROQ_API_KEY=your_groq_api_key
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
```

### 5. Run FastAPI backend
```bash
uvicorn api:app --reload
```

### 6. Run Streamlit frontend
```bash
streamlit run app.py
```

### 7. Or run with Docker
```bash
docker build -t aria:latest .
docker run -p 8000:8000 -p 8501:8501 aria:latest
```

---

## 🛡️ Guardrails

ARIA protects against:

- **PII Detection & Redaction** — emails, phone numbers, SSNs automatically redacted
- **Prompt Injection Blocking** — malicious instructions detected and blocked
- **Output Safety Filtering** — responses scanned before delivery

---

## 📊 RAGAS Evaluation Metrics

Every response is automatically evaluated:

| Metric | Description |
|---|---|
| **Faithfulness** | Is the answer grounded in the source document? |
| **Answer Relevancy** | Does the answer address the user's question? |
| **Context Precision** | How precisely is the retrieved context used? |
| **Overall Score** | Combined quality metric |

---

## 📁 Supported Document Types

| Type | Extension | Parser |
|---|---|---|
| PDF Reports | `.pdf` | PyMuPDF |
| Structured Data | `.csv` | Pandas |
| Plain Text | `.txt` | Custom chunker |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/health` | API status |
| GET | `/documents` | List uploaded documents |
| POST | `/upload` | Upload a document |
| POST | `/query` | Query ARIA |

---

## 🔄 CI/CD Pipeline

Every push to `main` triggers:

```
Push to GitHub
      ↓
1. Lint (ruff)
2. Unit Tests (pytest)
3. Docker Build
      ↓
✅ All green = production ready
```

---

## 📂 Project Structure

```
ARIA/
├── .github/
│   └── workflows/
│       └── ci.yml          ← CI/CD pipeline
├── src/
│   ├── agents/
│   │   ├── orchestrator.py ← LangGraph master agent
│   │   ├── ingestion.py    ← Document routing agent
│   │   ├── retriever.py    ← Hybrid search agent
│   │   └── evaluator.py    ← RAGAS + guardrails agent
│   ├── tools/
│   │   ├── pdf_tool.py     ← PDF parser
│   │   ├── csv_tool.py     ← CSV parser
│   │   ├── text_tool.py    ← Text parser
│   │   └── search_tool.py  ← Qdrant search
│   └── utils/
│       └── embeddings.py   ← HuggingFace embeddings
├── tests/                  ← pytest test suite
├── data/sample_docs/       ← Sample documents
├── app.py                  ← Streamlit frontend
├── api.py                  ← FastAPI backend
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## 💬 Example Queries

```
"What is the leave policy?"           → company_policy.txt
"Who is the highest paid employee?"   → employees.csv
"What was Q4 revenue for Data Science?" → financial_report.csv
"How does ARIA do hybrid search?"     → product_faq.txt
"Who leads the AI Research team?"     → annual_report.pdf
```

---

## 👤 Author

Built by **Pranay Rodda** as part of a Gen AI portfolio project targeting roles in LLM Engineering, MLOps, and Agentic AI.

---

## 📄 License

MIT License
