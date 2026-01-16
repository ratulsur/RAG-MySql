# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.routers.connect import router as connect_router
from app.routers.ask import router as ask_router

app = FastAPI(title="Universal RAG over MySQL")

app.include_router(connect_router)
app.include_router(ask_router)

STATIC_DIR = Path(__file__).resolve().parent / "static"  # ✅ app/static

app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
