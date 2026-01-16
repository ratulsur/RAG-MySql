from typing import List, Dict, Any
from app.rag.embedder import Embedder
from app.rag.vector_store import vector_store


class Retriever:
    def __init__(self, embedder: Embedder):
        self.embedder = embedder

    def retrieve(self, session_id: str, query: str, k: int = 5) -> List[Dict[str, Any]]:
        q_emb = self.embedder.embed_query(query)
        return vector_store.search(session_id, q_emb, k)
