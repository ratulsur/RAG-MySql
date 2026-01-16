# app/rag/vector_store.py
from typing import Dict, Any, List
import math

class InMemoryVectorStore:
    def __init__(self):
        self._store: Dict[str, List[Dict[str, Any]]] = {}

    def add(self, session_id: str, embedding: List[float], text: str, metadata: Dict[str, Any]):
        self._store.setdefault(session_id, []).append(
            {"embedding": embedding, "text": text, "metadata": metadata}
        )

    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        return dot / (na * nb) if na and nb else 0.0

    def search(self, session_id: str, query_emb: List[float], k: int = 5):
        docs = self._store.get(session_id, [])
        scored = [{**d, "score": self._cosine(query_emb, d["embedding"])} for d in docs]
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:k]

vector_store = InMemoryVectorStore()
