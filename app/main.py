# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Routers
from app.routers.connect import router as connect_router
from app.routers.ask import router as ask_router

# If you already created index_all router, keep this import.
# If not created yet, comment it for now.
try:
    from app.routers.index_all import router as index_router
    _HAS_INDEX = True
except Exception:
    index_router = None
    _HAS_INDEX = False


app = FastAPI(title="Universal RAG over MySQL", version="0.1.0")

# API routes
app.include_router(connect_router)
app.include_router(ask_router)
if _HAS_INDEX and index_router:
    app.include_router(index_router)

# Serve the sidebar UI (app/static/index.html) at "/"
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
