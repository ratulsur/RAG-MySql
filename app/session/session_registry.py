from dataclasses import dataclass, field
from typing import Dict, Any
from sqlalchemy.engine import Engine

@dataclass
class DBSession:
    engine: Engine
    database: str
    schema: Dict[str, Any]
    text_columns: list[tuple[str, str]] = field(default_factory=list)

DATABASE_SESSIONS: Dict[str, DBSession] = {}
