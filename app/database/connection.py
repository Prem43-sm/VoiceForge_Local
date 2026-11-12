"""SQLite database connection manager."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, declarative_base, sessionmaker


class Base(DeclarativeBase):
    pass


_engine = None
_SessionLocal = None


class DatabaseManager:
    """Wrapper around SQLAlchemy engine and session factory."""

    def __init__(self, db_path: Path | str) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False, future=True)
        self.SessionLocal = sessionmaker(
            bind=self.engine, autoflush=False, autocommit=False, future=True
        )
        Base.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        return self.SessionLocal()


def init_db(db_path: Path | str) -> None:
    """Initialize the SQLite database engine and session factory (global)."""
    global _engine, _SessionLocal

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    _engine = create_engine(f"sqlite:///{db_path}", echo=False, future=True)
    _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)

    Base.metadata.create_all(_engine)


def get_session() -> Session:
    """Return a new database session."""
    if _SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _SessionLocal()


def get_engine():
    """Return the SQLAlchemy engine."""
    if _engine is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _engine