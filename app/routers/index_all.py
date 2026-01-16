from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.session.session_registry import DATABASE_SESSIONS
from app.rag.indexer import index_all_text

router = APIRouter(prefix="/api", tags=["index"])


class IndexRequest(BaseModel):
    session_id: str
    max_rows: int = 500


@router.post("/index_all")
def index_all(req: IndexRequest):
    session = DATABASE_SESSIONS.get(req.session_id)
    if not session:
        raise HTTPException(404, "Invalid session_id")

    stats = index_all_text(
        session_id=req.session_id,
        engine=session.engine,
        schema=session.schema,
        max_rows=req.max_rows,
    )

    return {"status": "ok", "stats": stats}
