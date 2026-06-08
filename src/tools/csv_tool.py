import pandas as pd
from pathlib import Path


def load_csv(file_path: str) -> list[dict]:
    """
    Load CSV with rich summary chunks for better comparison queries.
    """
    df = pd.read_csv(file_path)
    chunks = []
    filename = Path(file_path).name

    # Chunk 1: Full summary with ALL data in one searchable block
    summary = f"File: {filename} | Total records: {len(df)}\n"
    summary += f"Columns: {', '.join(df.columns.tolist())}\n\n"
    summary += "COMPLETE DATA:\n"
    for idx, row in df.iterrows():
        row_text = " | ".join([f"{col}: {val}" for col, val in row.items()])
        summary += f"Row {idx+1}: {row_text}\n"

    chunks.append({
        "source": filename,
        "chunk": 0,
        "content": summary
    })

    # Chunk 2: Sorted summaries for comparison queries
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            try:
                sorted_df = df.sort_values(col, ascending=False)
                sorted_text = f"Ranking by {col} (highest to lowest) in {filename}:\n"
                for idx, row in sorted_df.iterrows():
                    name_col = next((c for c in df.columns if 'name' in c.lower()), df.columns[0])
                    sorted_text += f"{row[name_col]}: {col} = {row[col]}\n"
                chunks.append({
                    "source": filename,
                    "chunk": f"ranking_{col}",
                    "content": sorted_text
                })
            except:
                pass

    # Chunk 3+: One rich chunk per row
    for idx, row in df.iterrows():
        content = f"Record from {filename}:\n"
        content += "\n".join([f"{col}: {val}" for col, val in row.items()])
        chunks.append({
            "source": filename,
            "row": idx + 1,
            "chunk": idx + 1,
            "content": content
        })

    return chunks