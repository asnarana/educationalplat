"""
GradeMaster - Adaptive Remediation Quiz System
FastAPI main application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import init_db
from app.routes import seed, quiz, history, feedback, tts

# Initialize FastAPI app
app = FastAPI(
    title="GradeMaster API",
    description="Adaptive remediation quiz system for personalized learning",
    version="1.0.0"
)

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

