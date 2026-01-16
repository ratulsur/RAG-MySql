from sqlalchemy import text
from sqlalchemy.engine import Engine
from typing import Dict, Any

from app.rag.embedder import Embedder
from app.rag.chunker import simple_chunk
from app.rag.vector_store import vector_store


def index_all_text(
    session_id: str,
    engine: Engine,
    schema: Dict[str, Any],
    max_rows: int = 500,
):
    embedder = Embedder()
    stats = {}

    text_types = {"varchar", "text", "mediumtext", "longtext"}

    for table, cols in schema.items():
        text_cols = [c["name"] for c in cols if c["type"].lower() in text_types]
        if not text_cols:
            continue

        rows = engine.execute(
            text(f"SELECT * FROM `{table}` LIMIT :limit"),
            {"limit": max_rows}
        ).fetchall()

        chunk_count = 0

        for row_idx, row in enumerate(rows):
            row_dict = dict(row._mapping)
            combined = "\n".join(
                f"{col}: {row_dict[col]}"
                for col in text_cols
                if row_dict.get(col)
            )

            for chunk in simple_chunk(combined):
                emb = embedder.embed_query(chunk)
                vector_store.add(
                    session_id=session_id,
                    embedding=emb,
                    text=chunk,
                    metadata={
                        "table": table,
                        "row": row_idx,
                        "columns": text_cols,
                    },
                )
                chunk_count += 1

        stats[table] = {
            "rows": len(rows),
            "chunks": chunk_count,
            "columns": text_cols,
        }

    return stats
