"""
Database setup and session management for GradeMaster.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool  # Oracle works better with NullPool
from app.models import Base

# Load environment variables from .env file if it exists
load_dotenv()

# Oracle database URL
# Format: oracle+oracledb://username:password@host:port/service_name
# Using oracledb driver (recommended) instead of cx_Oracle
ORACLE_USER = os.getenv("ORACLE_USER", "system")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", "Oracle123")
ORACLE_HOST = os.getenv("ORACLE_HOST", "localhost")
ORACLE_PORT = os.getenv("ORACLE_PORT", "1522")
ORACLE_SERVICE = os.getenv("ORACLE_SERVICE", "FREEPDB1")

# Debug: Print connection info
print(f"Database connection: {ORACLE_HOST}:{ORACLE_PORT}/{ORACLE_SERVICE}")

# Oracle connection string for PDB
# Create DSN string with service_name explicitly specified (required for PDB connections)
# Format: (DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=host)(PORT=port))(CONNECT_DATA=(SERVICE_NAME=service)))
dsn = f"(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST={ORACLE_HOST})(PORT={ORACLE_PORT}))(CONNECT_DATA=(SERVICE_NAME={ORACLE_SERVICE})))"

# SQLAlchemy connection URL - user service_name in connect_args, not in URL path
SQLALCHEMY_DATABASE_URL = f"oracle+oracledb://{ORACLE_USER}:{ORACLE_PASSWORD}@"

# Create engine with Oracle-specific settings
# Use dsn parameter to specify the full connection string with service_name
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "dsn": dsn  # Use full DSN string with SERVICE_NAME for PDB
    },
    poolclass=NullPool,  # Oracle works better with NullPool for development
    echo=False,  # Set to True for SQL debugging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database by creating all tables and sequences."""
    from sqlalchemy import inspect
    
    # Create sequences first (Oracle requires explicit sequence creation)
    sequences = [
        ('question_id_seq', 'questions'),
        ('quiz_id_seq', 'quizzes'),
        ('attempt_id_seq', 'attempts')
    ]
    
    with engine.connect() as conn:
        for seq_name, table_name in sequences:
            # Check if sequence exists, create if not
            check_seq = text(f"""
                SELECT COUNT(*) FROM user_sequences WHERE sequence_name = UPPER(:seq_name)
            """)
            result = conn.execute(check_seq, {"seq_name": seq_name})
            exists = result.scalar() > 0
            
            if not exists:
                # Create sequence starting at 1
                create_seq = text(f"CREATE SEQUENCE {seq_name} START WITH 1 INCREMENT BY 1")
                conn.execute(create_seq)
                conn.commit()
                print(f"Created sequence: {seq_name}")
    
    # Create all tables (this will also handle foreign keys and indexes)
    Base.metadata.create_all(bind=engine)
    
    # Check if quizzes table exists and add grade_quiz_number column if missing
    inspector = inspect(engine)
    table_names = [name.upper() for name in inspector.get_table_names()]
    if 'QUIZZES' in table_names:
        try:
            columns = [col['name'].upper() for col in inspector.get_columns('quizzes')]
            if 'GRADE_QUIZ_NUMBER' not in columns:
                with engine.connect() as conn:
                    add_column = text("ALTER TABLE quizzes ADD grade_quiz_number INTEGER")
                    conn.execute(add_column)
                    conn.commit()
                    print("Added grade_quiz_number column to quizzes table")
        except Exception as e:
            # Column might already exist or there might be a race condition
            print(f"Note: Could not add grade_quiz_number column (may already exist): {e}")
    
    # Check if questions table exists and add image_url column if missing
    if 'QUESTIONS' in table_names:
        try:
            columns = [col['name'].upper() for col in inspector.get_columns('questions')]
            if 'IMAGE_URL' not in columns:
                with engine.connect() as conn:
                    add_column = text("ALTER TABLE questions ADD image_url VARCHAR2(500)")
                    conn.execute(add_column)
                    conn.commit()
                    print("Added image_url column to questions table")
        except Exception as e:
            # Column might already exist or there might be a race condition
            print(f"Note: Could not add image_url column (may already exist): {e}")
    
    # Check if questions table exists and add calculator_active column if missing
    if 'QUESTIONS' in table_names:
        try:
            columns = [col['name'].upper() for col in inspector.get_columns('questions')]
            if 'CALCULATOR_ACTIVE' not in columns:
                with engine.connect() as conn:
                    add_column = text("ALTER TABLE questions ADD calculator_active NUMBER(1)")
                    conn.execute(add_column)
                    conn.commit()
                    print("Added calculator_active column to questions table")
        except Exception as e:
            print(f"Note: Could not add calculator_active column (may already exist): {e}")


def get_db() -> Session:
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

