# app/rag/embedder.py

from typing import List

from app.rag.utils.model_loader import ModelLoader


class Embedder:
    """
    Thin wrapper around your existing embedding model.

    It uses ModelLoader to load the embeddings object that you already
    tested via `python -m RAG_Sql.utils.model_loader` (or your new one in app.rag.utils).
    """

    def __init__(self) -> None:
        loader = ModelLoader()
        self._embeddings = loader.load_embeddings()

    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single string into a vector.
        """
        return self._embeddings.embed_query(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed multiple strings into vectors.
        """
        if hasattr(self._embeddings, "embed_documents"):
            return self._embeddings.embed_documents(texts)
        return [self.embed_query(t) for t in texts]


if __name__ == "__main__":
    # Simple smoke test
    emb = Embedder()
    vec = emb.embed_query("Hello from embedder!")
    print("Vector length:", len(vec))
