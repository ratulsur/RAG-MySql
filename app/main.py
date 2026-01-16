from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.routers.connect import router as connect_router
from app.routers.ask import router as ask_router

app = FastAPI(title="Universal RAG over MySQL")

app.include_router(connect_router)
app.include_router(ask_router)

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "app" / "static"   # ✅ FIX HERE

app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
