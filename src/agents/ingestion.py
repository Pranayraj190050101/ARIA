from src.tools.pdf_tool import load_pdf
from src.tools.csv_tool import load_csv
from src.tools.text_tool import load_text
from pathlib import Path


def run_ingestion_agent(file_path: str) -> list[dict]:
    """
    Ingestion Agent — detects file type and routes
    to the correct tool automatically.
    """
    ext = Path(file_path).suffix.lower()

    print(f"[Ingestion Agent] Processing: {file_path} (type: {ext})")

    if ext == ".pdf":
        chunks = load_pdf(file_path)
    elif ext == ".csv":
        chunks = load_csv(file_path)
    elif ext == ".txt":
        chunks = load_text(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    print(f"[Ingestion Agent] Extracted {len(chunks)} chunks")
    return chunks