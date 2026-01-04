"""
Routes for LLM-based feedback generation.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.db import get_db
from app.models import Attempt, Quiz, Question
from app.logic.feedback import generate_feedback
from app.logic.llm_provider import get_llm_provider, LLMProvider

router = APIRouter(prefix="/attempt", tags=["feedback"])


class FeedbackResponse(BaseModel):
    """Response model for feedback endpoint."""
    summary: str
    topics: Dict[str, Dict[str, Any]]


@router.post("/{attempt_id}/feedback", response_model=FeedbackResponse)
def get_feedback(
    attempt_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate personalized feedback for a quiz attempt using LLM.
    
    The LLM provides:
    - A brief summary of performance
    - 3 study recommendations per weak topic
    - 2 practice questions per weak topic (with answers and explanations)
    
    If no weak topics exist, generates a review plan for all topics.
    
    Note: The LLM does NOT grade answers. Grading remains deterministic.
    """
    # Get attempt
    attempt = db.query(Attempt).filter(Attempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    
    # Get quiz
    quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found for this attempt")
    
    # Get questions
    questions = db.query(Question).filter(Question.id.in_(quiz.question_ids)).all()
    if len(questions) != len(quiz.question_ids):
        raise HTTPException(status_code=500, detail="Some questions not found")
    
    # Check if LLM provider is configured
    try:
        llm_provider = get_llm_provider()
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"LLM provider not configured or unavailable: {str(e)}. "
                   "Please set LLM_PROVIDER environment variable and required API keys."
        )
    
    # Generate feedback
    try:
        feedback = generate_feedback(attempt, quiz, questions, llm_provider=llm_provider)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate feedback: {str(e)}"
        )
    
    return FeedbackResponse(**feedback)

