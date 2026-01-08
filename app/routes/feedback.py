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
from app.monitoring.metrics import track_llm_request
import time

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
    
    # Get questions - handle duplicates and missing questions
    # Deduplicate question_ids to avoid issues when repeats are allowed
    unique_question_ids = list(dict.fromkeys(quiz.question_ids))  # Preserves order, removes duplicates
    
    questions = db.query(Question).filter(Question.id.in_(unique_question_ids)).all()
    
    # Check if any questions are missing (may happen if questions were deleted after quiz creation)
    found_question_ids = {q.id for q in questions}
    missing_ids = [qid for qid in unique_question_ids if qid not in found_question_ids]
    
    if missing_ids:
        # Log warning but continue with available questions
        print(f"Warning: {len(missing_ids)} questions not found for quiz {quiz.id}: {missing_ids}")
        # Filter out missing questions from the list
        questions = [q for q in questions if q.id in found_question_ids]
    
    if not questions:
        raise HTTPException(
            status_code=500, 
            detail=f"None of the questions for this quiz could be found. "
                   f"This may happen if questions were deleted after the quiz was created."
        )
    
    # If there were duplicates in quiz.question_ids, expand the questions list to match original order
    if len(quiz.question_ids) != len(unique_question_ids):
        # Create a mapping of question ID to Question object
        question_map = {q.id: q for q in questions}
        # Rebuild questions list in the order of quiz.question_ids (allowing repeats)
        questions = [question_map[qid] for qid in quiz.question_ids if qid in question_map]
    
    # Check if LLM provider is configured
    try:
        llm_provider = get_llm_provider()
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Ollama LLM provider not configured or unavailable: {str(e)}. "
                   "Make sure Ollama is running and langchain-ollama is installed."
        )
    
    # Generate feedback with metrics tracking
    start_time = time.time()
    provider_name = "ollama"  # Always using Ollama now
    
    try:
        feedback = generate_feedback(attempt, quiz, questions, llm_provider=llm_provider)
        duration = time.time() - start_time
        track_llm_request(provider_name, duration, success=True)
    except Exception as e:
        duration = time.time() - start_time
        track_llm_request(provider_name, duration, success=False)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate feedback: {str(e)}"
        )
    
    return FeedbackResponse(**feedback)

