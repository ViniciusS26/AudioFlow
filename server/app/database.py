from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from server.app.config import BASE_DIR, settings


class Base(DeclarativeBase):
    pass


def build_engine():
    if settings.DATABASE_URL.startswith("sqlite"):
        return create_engine(settings.DATABASE_URL, pool_pre_ping=True)

    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except OperationalError:
        sqlite_path = BASE_DIR / "audio_local.db"
        sqlite_url = f"sqlite:///{sqlite_path}"
        return create_engine(sqlite_url, pool_pre_ping=True)


engine = build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
