from pathlib import Path


def load_text(file_path: str) -> list[dict]:
    """
    Load and extract text from a plain text file.
    Returns list of dicts with chunk number and content.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Split into paragraphs
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks = []
    for idx, paragraph in enumerate(paragraphs, start=1):
        chunks.append({
            "source": Path(file_path).name,
            "chunk": idx,
            "content": paragraph
        })

    return chunks