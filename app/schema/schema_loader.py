from typing import Dict, Any, List, Tuple
from sqlalchemy.engine import Engine
from sqlalchemy import text

def load_schema(engine: Engine, database_name: str) -> Dict[str, Any]:
    q = text("""
        SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = :db
        ORDER BY TABLE_NAME, ORDINAL_POSITION
    """)
    with engine.connect() as conn:
        rows = conn.execute(q, {"db": database_name}).fetchall()

    schema: Dict[str, Any] = {}
    for table, column, dtype in rows:
        schema.setdefault(table, []).append({"name": column, "type": dtype})
    return schema

def get_text_columns(schema: Dict[str, Any]) -> List[Tuple[str, str]]:
    text_types = {"varchar", "text", "mediumtext", "longtext", "char"}
    out: List[Tuple[str, str]] = []
    for table, cols in schema.items():
        for c in cols:
            if c["type"].lower() in text_types:
                out.append((table, c["name"]))
    return out



