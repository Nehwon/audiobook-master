from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DEFAULT_DATABASE_URL = "sqlite+pysqlite:///:memory:"

# Base declarative for SQLAlchemy models
Base = declarative_base()


def get_database_url() -> str:
    return os.getenv("AUDIOBOOK_DATABASE_URL", DEFAULT_DATABASE_URL)


def build_engine(url: str | None = None) -> Engine:
    database_url = url or get_database_url()
    return create_engine(database_url, future=True)


def build_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False, future=True)


@contextmanager
def session_scope(session_factory: sessionmaker[Session]) -> Iterator[Session]:
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
