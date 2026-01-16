# app/rag/sql_agent.py
from typing import Dict, Any, List, Tuple
from sqlalchemy import text
from fastapi import HTTPException

from app.rag.groq_client import GroqLLM

# Initialize only once
_sql_llm = GroqLLM(model_name="llama-3.1-70b-versatile")


def build_schema_prompt(schema: Dict[str, Any]) -> str:
    """
    Convert schema into readable form for SQL generation.
    """
    lines = []
    for table, cols in schema.items():
        cols_formatted = ", ".join(f"{c['name']} ({c['type']})" for c in cols)
        lines.append(f"TABLE {table}: {cols_formatted}")
    return "\n".join(lines)


def generate_sql_with_groq(question: str, schema: Dict[str, Any]) -> str:
    schema_text = build_schema_prompt(schema)

    prompt = f"""
You are an expert MySQL SQL generator.

Use only the tables and columns listed below:
{schema_text}

Write ONE valid MySQL SELECT query to answer this question:

"{question}"

Rules:
- ONLY return SQL.
- NO explanation.
- NO markdown.
- MUST be valid MySQL.
- ALWAYS include LIMIT 50 unless told otherwise.
"""

    sql = _sql_llm.generate(prompt)
    return sql.strip()


def validate_sql(sql: str) -> str:
    lowered = sql.lower()

    if not lowered.startswith("select"):
        raise HTTPException(400, "Only SELECT queries allowed.")

    forbidden = ["insert", "update", "delete", "drop", "alter", "truncate"]
    if any(f in lowered for f in forbidden):
        raise HTTPException(400, "Forbidden SQL keyword detected.")

    # Ensure LIMIT
    if "limit" not in lowered:
        sql = sql.rstrip(";") + " LIMIT 50"

    return sql


def run_sql(engine, sql: str) -> List[Dict[str, Any]]:
    sql = validate_sql(sql)
    
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        return [dict(r._mapping) for r in result]


def answer_question_with_sql(
    question: str,
    engine,
    schema: Dict[str, Any],
) -> Tuple[str, str, List[Dict[str, Any]]]:

    sql = generate_sql_with_groq(question, schema)
    rows = run_sql(engine, sql)

    if rows:
        answer = f"Found {len(rows)} rows. Showing first row: {rows[0]}"
    else:
        answer = "Query ran successfully but returned no rows."

    return answer, sql, rows
