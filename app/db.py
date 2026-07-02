from __future__ import annotations

"""Database helpers for Évora LeadFlow.

A demo premium roda na Vercel antes da configuração final de PostgreSQL e
WhatsApp. Para evitar 500 com DATABASE_URL vazio/placeholder, a demo usa SQLite
em /tmp por padrão. Na versão final, use DEMO_FORCE_SQLITE=false e um PostgreSQL.
"""

import os
from collections.abc import Generator
from pathlib import Path
from threading import Lock

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import DEFAULT_DATABASE_URL, get_settings
from app.models import Base

settings = get_settings()


def _truthy(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    normalized = str(value).strip().lower()
    if normalized == "":
        return default
    return normalized in {"1", "true", "t", "yes", "y", "sim", "s", "on"}


def _looks_like_placeholder(url: str) -> bool:
    lowered = url.lower()
    placeholders = [
        "usuario",
        "senha",
        "@host",
        "database?",
        "coloque",
        "troque",
        "your_",
        "example",
        "seu_",
        "sua_",
    ]
    return any(token in lowered for token in placeholders)


def _demo_sqlite_url() -> str:
    running_on_vercel = os.getenv("VERCEL") == "1" or settings.app_env.lower() in {"vercel", "demo"}
    if running_on_vercel:
        return DEFAULT_DATABASE_URL
    local_path = Path.cwd() / "leadflow_demo.db"
    return f"sqlite:///{local_path.as_posix()}"


def resolve_database_url() -> str:
    raw_url = (settings.database_url or "").strip()
    app_env = settings.app_env.lower().strip()
    force_sqlite_default = app_env in {"demo", "vercel"}
    force_sqlite = _truthy(os.getenv("DEMO_FORCE_SQLITE"), default=force_sqlite_default)

    if force_sqlite:
        return _demo_sqlite_url()

    if not raw_url or _looks_like_placeholder(raw_url):
        return _demo_sqlite_url()

    try:
        make_url(raw_url)
    except Exception:
        return _demo_sqlite_url()

    return raw_url


DATABASE_URL = resolve_database_url()
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite:////"):
        sqlite_path = "/" + DATABASE_URL.removeprefix("sqlite:////")
        parent = os.path.dirname(sqlite_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
    elif DATABASE_URL.startswith("sqlite:///"):
        sqlite_path = DATABASE_URL.removeprefix("sqlite:///")
        parent = os.path.dirname(sqlite_path)
        if parent:
            os.makedirs(parent, exist_ok=True)

engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

_db_lock = Lock()
_db_initialized = False
_db_seeded = False


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def ensure_db_ready(seed: bool = True) -> None:
    """Garante tabelas e dados também em ambiente serverless.

    É idempotente e seguro para ser chamado no lifespan, no /health e antes de
    cada sessão de banco.
    """
    global _db_initialized, _db_seeded
    if _db_initialized and ((not seed) or _db_seeded):
        return
    with _db_lock:
        if not _db_initialized:
            init_db()
            _db_initialized = True
        if seed and not _db_seeded:
            with SessionLocal() as db:
                from app.seed_data import seed_if_empty

                seed_if_empty(db)
            _db_seeded = True


def get_db() -> Generator[Session, None, None]:
    ensure_db_ready(seed=True)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
