# database.py
"""
Database configuration for AutoEval+ backend.

Uses SQLite (autoeval.db) with SQLAlchemy ORM and exposes:
- engine: SQLAlchemy engine
- SessionLocal: database session factory
- Base: declarative base for models
- get_db: FastAPI dependency to provide a DB session per request
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database file in the current directory
SQLALCHEMY_DATABASE_URL = "sqlite:///./autoeval.db"

# For SQLite, check_same_thread must be False when using in multithreaded environments (like FastAPI)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Each request gets its own session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session and ensures
    it is closed after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()