import fitz  # PyMuPDF
from pathlib import Path


def load_pdf(file_path: str) -> list[dict]:
    """
    Load and extract text from a PDF file.
    Returns list of dicts with page number and content.
    """
    doc = fitz.open(file_path)
    pages = []

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        if text.strip():  # skip empty pages
            pages.append({
                "source": Path(file_path).name,
                "page": page_num,
                "content": text.strip()
            })

    doc.close()
    return pages