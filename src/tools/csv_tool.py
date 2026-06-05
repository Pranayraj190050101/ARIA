import pandas as pd
from pathlib import Path


def load_csv(file_path: str) -> list[dict]:
    """
    Load and extract text from a CSV file.
    Returns list of dicts with row number and content.
    """
    df = pd.read_csv(file_path)
    rows = []

    for idx, row in df.iterrows():
        content = " | ".join([f"{col}: {val}" for col, val in row.items()])
        rows.append({
            "source": Path(file_path).name,
            "row": idx + 1,
            "content": content.strip()
        })

    return rows