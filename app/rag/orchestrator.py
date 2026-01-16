# app/rag/orchestrator.py
from typing import Dict, Any
from sqlalchemy.engine import Engine

from app.rag.sql_agent import answer_question_with_sql
from app.rag.embedder import Embedder
from app.rag.retriever import Retriever


class Orchestrator:
    """
    Hybrid RAG orchestrator.

    Current behavior:
      - Always runs SQL agent
      - Always runs semantic retrieval (if index exists)
      - Returns both in a structured payload
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
    ) -> Dict[str, Any]:
        """
        For now, we:
          - Run SQL agent to generate & execute SQL
          - Run semantic retriever over indexed text for this session

        Later, you can add:
          - intent classification (SQL-only vs semantic-only vs hybrid)
          - LLM-based fusion of SQL rows + semantic chunks
        """
        # 1) SQL path
        sql_answer, sql_used, rows = answer_question_with_sql(
            question=question,
            engine=engine,
            schema=schema,
        )

        # 2) Semantic path
        semantic_results = self.retriever.retrieve(
            session_id=session_id,
            query=question,
            k=5,
        )

        # 3) Construct a simple combined answer for now
        if semantic_results:
            top_chunk = semantic_results[0]
            sem_summary = f"\n\nTop semantic match:\n{top_chunk['text']}"
        else:
            sem_summary = "\n\n(No semantic matches found or index is empty.)"

        combined_answer = sql_answer + sem_summary

        return {
            "answer": combined_answer,
            "sql_used": sql_used,
            "rows": rows,
            "semantic_chunks": semantic_results,
        }


print("ORCH: starting SQL agent")
sql_answer, sql_used, rows = answer_question_with_sql(...)
print("ORCH: SQL agent done")

print("ORCH: starting semantic retrieve")
semantic_results = self.retriever.retrieve(...)
print("ORCH: semantic retrieve done")
