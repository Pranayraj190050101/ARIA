import streamlit as st
from src.agents.orchestrator import run_aria
import os
# Pre-load documents on startup
import threading

def startup_ingest():
    try:
        from src.agents.orchestrator import run_aria
        print("[Startup] Pre-ingesting documents...")
        run_aria(file_path="data/sample_docs", query="startup")
        print("[Startup] Documents ready!")
    except Exception as e:
        print(f"[Startup] Ingestion error: {e}")

threading.Thread(target=startup_ingest, daemon=True).start()

# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title="ARIA",
    page_icon="🤖",
    layout="wide"
)

# ── Header ────────────────────────────────────────────────
st.title("🤖 ARIA")
st.caption("Agentic Retrieval & Intelligent Analysis")
st.divider()

UPLOAD_DIR = "data/sample_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.header("📁 Document Manager")

    uploaded_file = st.file_uploader(
        "Upload a document",
        type=["pdf", "csv", "txt"]
    )

    if uploaded_file:
        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ {uploaded_file.name} uploaded!")

    st.divider()

    # Just show documents — no selector needed
    st.subheader("📄 Loaded Documents")
    documents = os.listdir(UPLOAD_DIR) if os.path.exists(UPLOAD_DIR) else []
    if documents:
        for doc in documents:
            st.caption(f"📄 {doc}")
    else:
        st.info("No documents yet. Upload one!")

    st.divider()
    st.info("💡 ARIA automatically searches across ALL documents to find the best answer!")

# ── Main chat area ────────────────────────────────────────
st.subheader("💬 Ask ARIA")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask anything about your documents..."):
    if not documents:
        st.error("Please upload at least one document first!")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("ARIA is thinking..."):
                try:
                    result = run_aria(
                        file_path=UPLOAD_DIR,
                        query=prompt
                    )

                    if result.get("blocked"):
                        answer = f"🚫 {result['answer']}"
                    else:
                        answer = result["answer"]

                    st.markdown(answer)

                    if result.get("metrics"):
                        with st.expander("📊 RAGAS Metrics"):
                            metrics = result["metrics"]
                            col1, col2, col3, col4 = st.columns(4)
                            col1.metric("Faithfulness", metrics.get("faithfulness", 0))
                            col2.metric("Relevancy", metrics.get("answer_relevancy", 0))
                            col3.metric("Precision", metrics.get("context_precision", 0))
                            col4.metric("Overall", metrics.get("overall_score", 0))

                    if result.get("sources"):
                        st.caption(f"📄 Sources: {', '.join(result['sources'])}")

                except Exception as e:
                    answer = f"❌ Error: {str(e)}"
                    st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})