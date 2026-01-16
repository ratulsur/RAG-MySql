# app/routers/ask.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.session.session_registry import DATABASE_SESSIONS
from app.rag.orchestrator import Orchestrator

router = APIRouter(prefix="/api", tags=["ask"])

_orchestrator = Orchestrator()


class AskRequest(BaseModel):
    session_id: str
    question: str


@router.post("/ask")
def ask(req: AskRequest):
    db_session = DATABASE_SESSIONS.get(req.session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Invalid or expired session_id")

    result = _orchestrator.answer(
        session_id=req.session_id,
        question=req.question,
        engine=db_session.engine,
        schema=db_session.schema,
    )
    return result
