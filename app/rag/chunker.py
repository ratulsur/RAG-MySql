# app/rag/chunker.py
from typing import List

def simple_chunk(text: str, max_chars: int = 1000, overlap: int = 200) -> List[str]:
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks
