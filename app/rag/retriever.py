from typing import List, Dict, Any


class Retriever:
    """
    Stub semantic retriever.

    Later (Module 5/6), this will call AstraDB (or any vector DB) to return
    top-k chunks. For now it returns an empty list so the rest of the system runs.
    """

    def __init__(self, embedder=None) -> None:
        self.embedder = embedder

    def retrieve(self, session_id: str, query: str, k: int = 5) -> List[Dict[str, Any]]:
        return []
