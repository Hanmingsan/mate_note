# backend/app/db/session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

# Import settings, especially DATABASE_URL
from app.core.config import settings
# Import the Base class for metadata
from app.db.models.base import Base
# Explicitly import models to ensure they are known to Base.metadata
from app.db.models import student # noqa - Ensures student model is registered

logger = logging.getLogger(__name__)

# Create the SQLAlchemy engine
# connect_args is specific to SQLite to allow multi-threaded access (FastAPI is async)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True, # Recommended for checking connection validity
    connect_args={"check_same_thread": False} # Only needed for SQLite
)

# Create the SessionLocal class, which will be a factory for new Session objects
# autocommit=False and autoflush=False are standard practices
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Database Session Dependency ---
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.
    It ensures the session is always closed after the request,
    even if an error occurs.
    Yields:
        Session: The SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db # Provide the session to the path operation function
    finally:
        db.close() # Close the session when the request/response cycle is finished

# --- (Optional) Database Initialization Function ---
def init_db():
    """
    Creates database tables based on SQLAlchemy models.
    This function is idempotent; it won't recreate tables that already exist.
    Call this function once, e.g., during application startup.
    """
    logger.info("Attempting to create database tables...")
    try:
        # Base.metadata contains table information from all models inheriting from Base
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables checked/created successfully.")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        # Depending on the application, you might want to exit or handle this differently
        raise


