# app/rag/orchestrator.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from sqlalchemy.engine import Engine

from app.rag.sql_agent import answer_question_with_sql
from app.rag.embedder import Embedder
from app.rag.retriever import Retriever


@dataclass
class OrchestratorResult:
    answer: str
    sql_used: Optional[str]
    rows: List[Dict[str, Any]]
    semantic_chunks: List[Dict[str, Any]]


class Orchestrator:
    """
    Hybrid RAG Orchestrator (clean + production-friendly).

    - Runs SQL tool path (structured facts) via sql_agent
    - Runs semantic retrieval path via retriever (if indexed)
    - Returns a single payload that the API can send to UI

    NOTE: No module-level side effects (important for uvicorn reload).
    """

    def __init__(self) -> None:
        self.embedder = Embedder()
        self.retriever = Retriever(self.embedder)

    def answer(
        self,
        session_id: str,
        question: str,
        engine: Engine,
        schema: Dict[str, Any],
        k: int = 5,
    ) -> Dict[str, Any]:
        # ---- 1) SQL path ----
        # Keep this wrapped so SQL/LLM failures don't crash the whole request.
        sql_answer = ""
        sql_used: Optional[str] = None
        rows: List[Dict[str, Any]] = []

        try:
            sql_answer, sql_used, rows = answer_question_with_sql(
                question=question,
                engine=engine,
                schema=schema,
            )
        except Exception as e:
            sql_answer = f"(SQL path failed: {type(e).__name__}: {e})"
            sql_used = None
            rows = []

        # ---- 2) Semantic path ----
        semantic_chunks: List[Dict[str, Any]] = []
        try:
            semantic_chunks = self.retriever.retrieve(
                session_id=session_id,
                query=question,
                k=k,
            )
        except Exception as e:
            semantic_chunks = [{
                "text": f"(Semantic retrieve failed: {type(e).__name__}: {e})",
                "score": 0.0,
                "metadata": {"error": True},
            }]

        # ---- 3) Simple fusion (safe, deterministic) ----
        if semantic_chunks and semantic_chunks[0].get("metadata", {}).get("error") is not True:
            top_text = semantic_chunks[0].get("text", "")
            sem_summary = f"\n\nTop semantic match:\n{top_text}"
        else:
            sem_summary = "\n\n(No semantic matches found or index is empty.)"

        combined_answer = (sql_answer or "").strip() + sem_summary

        result = OrchestratorResult(
            answer=combined_answer,
            sql_used=sql_used,
            rows=rows,
            semantic_chunks=semantic_chunks if semantic_chunks else [],
        )

        # Return dict (easy for FastAPI JSON response)
        return {
            "answer": result.answer,
            "sql_used": result.sql_used,
            "rows": result.rows,
            "semantic_chunks": result.semantic_chunks,
        }
