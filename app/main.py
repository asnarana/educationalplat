"""
GradeMaster - Adaptive Remediation Quiz System
FastAPI main application entry point.
"""
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from app.db import init_db
from app.routes import seed, quiz, history, feedback, tts, auth, admin
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
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(seed.router)
app.include_router(quiz.router)
app.include_router(history.router)
app.include_router(feedback.router)
app.include_router(tts.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    # Create default admin user if it doesn't exist
    from app.db import SessionLocal
    from app.models import User
    
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        
        # Always set admin password to "123" (create new or update existing)
        try:
            password_hash = User.hash_password("123")
            if not admin:
                admin_user = User(
                    username="admin",
                    password_hash=password_hash,
                    role="admin"
                )
                db.add(admin_user)
                db.commit()
                print("✅ Created default admin user: username='admin', password='123'")
            else:
                # Update existing admin password
                admin.password_hash = password_hash
                admin.role = "admin"  # Ensure role is admin
                db.commit()
                print("✅ Updated admin password to '123'")
        except Exception as e:
            print(f"⚠️  Error setting admin password: {e}")
            # If there's a corrupted admin user, delete and recreate
            if admin:
                try:
                    db.delete(admin)
                    db.commit()
                    password_hash = User.hash_password("123")
                    admin_user = User(
                        username="admin",
                        password_hash=password_hash,
                        role="admin"
                    )
                    db.add(admin_user)
                    db.commit()
                    print("✅ Recreated admin user with password '123'")
                except Exception as recreate_error:
                    print(f"⚠️  Could not recreate admin user: {recreate_error}")
    except Exception as e:
        print(f"⚠️  Note: Could not create/update admin user: {e}")
    finally:
        db.close()
    
    # Auto-seed questions if database is empty
    try:
        from app.routes.seed import auto_seed_questions
        db = SessionLocal()
        try:
            result = auto_seed_questions(db, force=False)
            if result:
                print(f"✅ Auto-seeded {result['questions_created']} questions on startup")
            else:
                # Questions already exist, but check if expanded questions need to be added
                from app.routes.seed import add_expanded_questions_to_existing_db
                expand_result = add_expanded_questions_to_existing_db(db)
                if expand_result['questions_added'] > 0:
                    print(f"✅ Added {expand_result['questions_added']} expanded questions. Total: {expand_result['new_total']} questions.")
                else:
                    # Questions already exist, no need to seed
                    from app.models import Question
                existing_count = db.query(Question).count()
                print(f"ℹ️  Question bank already contains {existing_count} questions (skipping auto-seed)")
        except Exception as seed_error:
            print(f"⚠️  Could not auto-seed questions: {seed_error}")
        finally:
            db.close()
    except Exception as e:
        print(f"⚠️  Note: Could not auto-seed questions: {e}")


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


@app.get("/db/quizzes")
def list_all_quizzes():
    """List all quizzes in the database with their IDs and details."""
    from app.db import SessionLocal
    from app.models import Quiz, Attempt
    
    db = SessionLocal()
    try:
        quizzes = db.query(Quiz).order_by(Quiz.student_id, Quiz.grade_level, Quiz.created_at).all()
        
        quiz_list = []
        for quiz in quizzes:
            # Get attempts for this quiz
            attempts = db.query(Attempt).filter(Attempt.quiz_id == quiz.id).all()
            
            quiz_list.append({
                "id": quiz.id,
                "student_id": quiz.student_id,
                "grade_level": quiz.grade_level,
                "grade_quiz_number": quiz.grade_quiz_number,
                "created_at": quiz.created_at.isoformat(),
                "num_questions": len(quiz.question_ids),
                "num_attempts": len(attempts),
                "attempts": [
                    {
                        "attempt_id": a.id,
                        "score": round(a.score_total * 100, 1),
                        "passed": a.passed,
                        "weak_topics": a.weak_topics
                    }
                    for a in attempts
                ]
            })
        
        return {
            "total_quizzes": len(quiz_list),
            "quizzes": quiz_list
        }
    finally:
        db.close()


@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=get_metrics(), media_type=CONTENT_TYPE_LATEST)

