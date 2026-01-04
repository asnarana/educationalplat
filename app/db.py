"""
Database setup and session management for GradeMaster.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models import Base

# SQLite database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./grademaster.db"

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
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

