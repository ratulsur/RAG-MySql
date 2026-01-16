# app/routers/connect.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from uuid import uuid4

from app.schema.schema_loader import load_schema, get_text_columns
from app.session.session_registry import DATABASE_SESSIONS, DBSession

router = APIRouter(prefix="/api", tags=["connect"])


class ConnectRequest(BaseModel):
    host: str
    port: int = 3306
    user: str
    password: str
    database: str


@router.post("/connect")
def connect_mysql(req: ConnectRequest):
    print("CONNECT HIT", req.host, req.port, req.user, req.database, flush=True)



@router.post("/connect")
def connect_db(req: ConnectRequest):
    print("CONNECT: request received")  


@router.post("/connect")
def connect_mysql(req: ConnectRequest):
    """
    Creates a SQLAlchemy engine for user-supplied MySQL credentials,
    introspects schema, stores it in an in-memory session registry,
    and returns a session_id.
    """
    url = f"mysql+pymysql://{req.user}:{req.password}@{req.host}:{req.port}/{req.database}"

    try:
        engine = create_engine(
    url,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 5},
)


        # connection smoke test
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=f"MySQL connection failed: {e}")

    try:
        schema = load_schema(engine, req.database)
        text_cols = get_text_columns(schema)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Schema introspection failed: {e}")

    session_id = uuid4().hex
    DATABASE_SESSIONS[session_id] = DBSession(
        engine=engine,
        database=req.database,
        schema=schema,
        text_columns=text_cols,
    )

    return {
        "session_id": session_id,
        "tables": list(schema.keys()),
        "text_columns": text_cols,
    }
