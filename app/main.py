"""
GradeMaster - Adaptive Remediation Quiz System
FastAPI main application entry point.
"""
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from app.db import init_db
from app.routes import seed, quiz, history, feedback, tts
from app.monitoring.middleware import PrometheusMiddleware
from app.monitoring.metrics import get_metrics, CONTENT_TYPE_LATEST

# Initialize FastAPI app
app = FastAPI(
    title="GradeMaster API",
    description="Adaptive remediation quiz system for personalized learning",
    version="1.0.0"
)

# Prometheus middleware (must be added before CORS)
app.add_middleware(PrometheusMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(seed.router)
app.include_router(quiz.router)
app.include_router(history.router)
app.include_router(feedback.router)
app.include_router(tts.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "message": "GradeMaster API - Adaptive Remediation Quiz System",
        "version": "1.0.0",
        "endpoints": {
            "seed": "POST /seed - Seed question bank",
            "generate_quiz": "POST /quiz/generate - Generate a new quiz",
            "submit_quiz": "POST /quiz/{quiz_id}/submit - Submit quiz answers",
            "student_history": "GET /student/{student_id}/history - Get student history",
            "feedback": "POST /attempt/{attempt_id}/feedback - Get LLM-generated feedback",
            "tts": "POST /tts - Convert text to speech (optional)"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/db/status")
def db_status():
    """Check database status and show entry counts."""
    from sqlalchemy import text, inspect
    from app.db import engine, SessionLocal
    from app.models import Question, Quiz, Attempt
    
    try:
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1 FROM DUAL"))
        
        db = SessionLocal()
        try:
            # Get table counts
            question_count = db.query(Question).count()
            quiz_count = db.query(Quiz).count()
            attempt_count = db.query(Attempt).count()
            
            # Get sequences
            with engine.connect() as conn:
                seq_result = conn.execute(text("""
                    SELECT sequence_name, last_number 
                    FROM user_sequences 
                    ORDER BY sequence_name
                """))
                sequences = {row[0]: row[1] for row in seq_result.fetchall()}
            
            # Get tables
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            return {
                "status": "connected",
                "database": "Oracle",
                "tables": tables,
                "counts": {
                    "questions": question_count,
                    "quizzes": quiz_count,
                    "attempts": attempt_count
                },
                "sequences": sequences
            }
        finally:
            db.close()
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=get_metrics(), media_type=CONTENT_TYPE_LATEST)

