# app/rag/embedder.py
from typing import List

from rag.utils.model_loader import ModelLoader


class Embedder:
    """
    Thin wrapper around your existing embedding model from RAG_Sql.
    """

    def __init__(self) -> None:
        loader = ModelLoader()
        # This uses the working embedding config you already tested
        self._embeddings = loader.load_embeddings()

    def embed_query(self, text: str) -> List[float]:
        return self._embeddings.embed_query(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # If your embeddings object already has embed_documents, use it.
        if hasattr(self._embeddings, "embed_documents"):
            return self._embeddings.embed_documents(texts)
        # fallback: loop
        return [self.embed_query(t) for t in texts]
