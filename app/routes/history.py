"""
Routes for retrieving student history.
Uses Redis caching for improved performance.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from app.db import get_db
from app.models import Quiz, Attempt
from app.redis_client import cache_get, cache_set, CACHE_KEYS

router = APIRouter(prefix="/student", tags=["history"])


@router.get("/{student_id}/history")
def get_student_history(
    student_id: str,
    db: Session = Depends(get_db)
):
    """
    Get complete quiz and attempt history for a student.
    Uses Redis cache for improved performance.
    
    Returns:
    - List of quizzes with their attempts
    - Overall progress summary
    """
    # Try cache first
    cache_key = CACHE_KEYS["student_history"].format(student_id=student_id)
    cached_history = cache_get(cache_key)
    if cached_history is not None:
        return cached_history
    
    # Get all quizzes for student
    quizzes = (
        db.query(Quiz)
        .filter(Quiz.student_id == student_id)
        .order_by(Quiz.created_at.desc())
        .all()
    )
    
    # Get all attempts for student
    attempts = (
        db.query(Attempt)
        .filter(Attempt.student_id == student_id)
        .order_by(Attempt.submitted_at.desc())
        .all()
    )
    
    # Build response
    quiz_history = []
    for quiz in quizzes:
        quiz_attempts = [a for a in attempts if a.quiz_id == quiz.id]
        quiz_history.append({
            "quiz": quiz.to_dict(),
            "attempts": [a.to_dict() for a in quiz_attempts]
        })
    
    # Calculate summary statistics
    total_quizzes = len(quizzes)
    total_attempts = len(attempts)
    avg_score = sum(a.score_total for a in attempts) / total_attempts if total_attempts > 0 else 0.0
    
    # Get unique weak topics across all attempts
    all_weak_topics = set()
    for attempt in attempts:
        all_weak_topics.update(attempt.weak_topics)
    
    # Group mastery status by grade level
    from app.logic.adaptive import check_mastery_status
    grade_levels = list(set([q.grade_level for q in quizzes]))
    mastery_by_grade = {}
    for grade in grade_levels:
        mastery_by_grade[grade] = check_mastery_status(db, student_id, grade, mastery_threshold=0.80)
    
    result = {
        "student_id": student_id,
        "summary": {
            "total_quizzes": total_quizzes,
            "total_attempts": total_attempts,
            "average_score": round(avg_score, 4),
            "all_weak_topics": list(all_weak_topics),
            "mastery_by_grade": mastery_by_grade
        },
        "history": quiz_history
    }
    
    # Cache the result (TTL: 15 minutes)
    cache_set(cache_key, result, ttl=900)
    
    return result

