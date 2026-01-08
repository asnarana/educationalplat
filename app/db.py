"""
Database setup and session management for GradeMaster.
Supports Oracle Database.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models import Base

# Oracle Database connection URL
# Format: oracle+oracledb://username:password@host:port/service_name
# Or: oracle+oracledb://username:password@host:port/?service_name=service_name
# Get connection details from environment variables
ORACLE_USER = os.getenv("ORACLE_USER", "your_username")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", "your_password")
ORACLE_HOST = os.getenv("ORACLE_HOST", "localhost")
ORACLE_PORT = os.getenv("ORACLE_PORT", "1521")
ORACLE_SERVICE_NAME = os.getenv("ORACLE_SERVICE_NAME", "XE")  # XE for Express Edition

# Construct Oracle database URL
SQLALCHEMY_DATABASE_URL = (
    f"oracle+oracledb://{ORACLE_USER}:{ORACLE_PASSWORD}@"
    f"{ORACLE_HOST}:{ORACLE_PORT}/?service_name={ORACLE_SERVICE_NAME}"
)

# Create engine with Oracle-specific settings
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database by creating all tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

