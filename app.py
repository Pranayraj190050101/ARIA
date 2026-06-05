import streamlit as st
import requests
import os

API_URL = "http://127.0.0.1:8000"

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

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.header("📁 Document Manager")

    # Upload document
    uploaded_file = st.file_uploader(
        "Upload a document",
        type=["pdf", "csv", "txt"]
    )

    if uploaded_file:
        with st.spinner("Uploading..."):
            response = requests.post(
                f"{API_URL}/upload",
                files={"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            )
            if response.status_code == 200:
                st.success(f"✅ {uploaded_file.name} uploaded!")
            else:
                st.error("Upload failed!")

    st.divider()

    # List documents
    st.subheader("📄 Available Documents")
    try:
        docs_response = requests.get(f"{API_URL}/documents")
        if docs_response.status_code == 200:
            documents = docs_response.json()["documents"]
            if documents:
                selected_doc = st.selectbox(
                    "Select document to query:",
                    documents
                )
            else:
                st.info("No documents yet. Upload one!")
                selected_doc = None
    except:
        st.error("⚠️ API not running. Start with: uvicorn api:app --reload")
        selected_doc = None

# ── Main chat area ────────────────────────────────────────
st.subheader("💬 Ask ARIA")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask anything about your documents..."):
    if not selected_doc:
        st.error("Please select a document first!")
    else:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get ARIA response
        with st.chat_message("assistant"):
            with st.spinner("ARIA is thinking..."):
                try:
                    response = requests.post(
                        f"{API_URL}/query",
                        json={"query": prompt, "filename": selected_doc}
                    )
                    result = response.json()

                    if result.get("blocked"):
                        answer = f"🚫 {result['answer']}"
                    else:
                        answer = result["answer"]

                    st.markdown(answer)

                    # Show metrics
                    if result.get("metrics"):
                        with st.expander("📊 RAGAS Metrics"):
                            metrics = result["metrics"]
                            col1, col2, col3, col4 = st.columns(4)
                            col1.metric("Faithfulness", metrics.get("faithfulness", 0))
                            col2.metric("Relevancy", metrics.get("answer_relevancy", 0))
                            col3.metric("Precision", metrics.get("context_precision", 0))
                            col4.metric("Overall", metrics.get("overall_score", 0))

                    # Show sources
                    if result.get("sources"):
                        st.caption(f"📄 Sources: {', '.join(result['sources'])}")

                except Exception as e:
                    answer = f"❌ Error: {str(e)}"
                    st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})