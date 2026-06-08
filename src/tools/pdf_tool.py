import fitz  # PyMuPDF
from pathlib import Path


def load_pdf(file_path: str) -> list[dict]:
    """
    Load and extract text from PDF with smart chunking.
    Splits by paragraphs within pages for better retrieval.
    """
    doc = fitz.open(file_path)
    chunks = []
    chunk_idx = 1

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        if not text.strip():
            continue

        # Split page into paragraphs
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        # Group small paragraphs together (min 100 chars per chunk)
        current_chunk = ""
        for para in paragraphs:
            current_chunk += " " + para
            if len(current_chunk) >= 300:
                chunks.append({
                    "source": Path(file_path).name,
                    "page": page_num,
                    "chunk": chunk_idx,
                    "content": current_chunk.strip()
                })
                chunk_idx += 1
                current_chunk = ""

        # Add remaining text
        if current_chunk.strip():
            chunks.append({
                "source": Path(file_path).name,
                "page": page_num,
                "chunk": chunk_idx,
                "content": current_chunk.strip()
            })
            chunk_idx += 1

    doc.close()
    print(f"[PDF Tool] Extracted {len(chunks)} chunks from {Path(file_path).name}")
    return chunks