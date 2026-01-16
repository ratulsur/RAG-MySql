# app/routers/ask.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import asyncio

from app.session.session_registry import DATABASE_SESSIONS
from app.rag.orchestrator import Orchestrator

router = APIRouter(prefix="/api", tags=["ask"])
_orchestrator = Orchestrator()

class AskRequest(BaseModel):
    session_id: str
    question: str

@router.post("/ask")
async def ask(req: AskRequest):
    db_session = DATABASE_SESSIONS.get(req.session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Invalid or expired session_id")

    try:
        # Run sync code safely without blocking the event loop
        result = await asyncio.wait_for(
            asyncio.to_thread(
                _orchestrator.answer,
                session_id=req.session_id,
                question=req.question,
                engine=db_session.engine,
                schema=db_session.schema,
            ),
            timeout=45,  # seconds
        )
        return result

    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Ask timed out (SQL/LLM took too long).")

    except Exception as e:
        # Always return something instead of hanging
        raise HTTPException(status_code=500, detail=f"Ask failed: {type(e).__name__}: {e}")
