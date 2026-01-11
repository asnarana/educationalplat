"""
Routes for retrieving student history.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from app.db import get_db
from app.models import Quiz, Attempt, Question

router = APIRouter(prefix="/student", tags=["history"])


def determine_quiz_type(quiz: Quiz, db: Session) -> Dict[str, any]:
    """
    Determine if a quiz is a practice quiz (single topic) or full quiz (multiple topics).
    
    Returns a dictionary with quiz_type and practice_topic (if applicable).
    """
    # Get questions for this quiz
    questions = db.query(Question).filter(
        Question.id.in_(quiz.question_ids)
    ).all()
    
    if not questions:
        return {"quiz_type": "full", "practice_topic": None}
    
    # Get unique topics from questions
    unique_topics = set(q.topic for q in questions)
    
    # If all questions are from the same topic, it's a practice quiz
    if len(unique_topics) == 1:
        return {
            "quiz_type": "practice",
            "practice_topic": list(unique_topics)[0]
        }
    else:
        return {
            "quiz_type": "full",
            "practice_topic": None
        }


@router.get("/{student_id}/history")
def get_student_history(
    student_id: str,
    grade_level: Optional[int] = Query(None, description="Filter history by grade level"),
    db: Session = Depends(get_db)
):
    """
    Get complete quiz and attempt history for a student.
    
    If grade_level is provided, only returns history for that grade level.
    This allows the same student ID to have separate histories for different grades.
    
    Args:
        student_id: Student identifier
        grade_level: Optional grade level filter (if provided, only shows history for this grade)
    
    Returns:
    - List of quizzes with their attempts
    - Overall progress summary
    - Identifies practice quizzes vs full quizzes
    """
    # Get quizzes for student (filter by grade level if provided)
    query = db.query(Quiz).filter(Quiz.student_id == student_id)
    if grade_level is not None:
        query = query.filter(Quiz.grade_level == grade_level)
    
    # Order by grade level, then by grade_quiz_number (so grade-specific IDs are sequential)
    # Most recent first within each grade
    quizzes = query.order_by(Quiz.grade_level.desc(), Quiz.grade_quiz_number.desc()).all()
    
    # Get quiz IDs for this student/grade combination
    quiz_ids = [q.id for q in quizzes]
    
    # Get attempts for this student (only for quizzes in the filtered list)
    query_attempts = db.query(Attempt).filter(Attempt.student_id == student_id)
    if quiz_ids:  # Only filter by quiz_ids if we have quizzes
        query_attempts = query_attempts.filter(Attempt.quiz_id.in_(quiz_ids))
    else:
        # If no quizzes found, still filter by student_id but won't match anything
        query_attempts = query_attempts.filter(Attempt.quiz_id.in_([]))
    
    attempts = query_attempts.order_by(Attempt.submitted_at.desc()).all()
    
    # Build response with quiz type information
    quiz_history = []
    for quiz in quizzes:
        quiz_attempts = [a for a in attempts if a.quiz_id == quiz.id]
        
        # Determine if this is a practice or full quiz
        quiz_info = determine_quiz_type(quiz, db)
        quiz_dict = quiz.to_dict(db_session=db)  # Pass db session for grade_quiz_number calculation if needed
        quiz_dict.update(quiz_info)  # Add quiz_type and practice_topic
        
        quiz_history.append({
            "quiz": quiz_dict,
            "attempts": [a.to_dict() for a in quiz_attempts]
        })
    
    # Calculate summary statistics
    total_quizzes = len(quizzes)
    total_attempts = len(attempts)
    avg_score = sum(a.score_total for a in attempts) / total_attempts if total_attempts > 0 else 0.0
    
    # Count practice vs full quizzes
    full_quizzes = 0
    practice_quizzes = 0
    for quiz in quizzes:
        quiz_info = determine_quiz_type(quiz, db)
        if quiz_info["quiz_type"] == "practice":
            practice_quizzes += 1
        else:
            full_quizzes += 1
    
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
    
    # If grade_level filter was applied, include it in response
    response_data = {
        "student_id": student_id,
        "grade_level": grade_level,
        "summary": {
            "total_quizzes": total_quizzes,
            "full_quizzes": full_quizzes,
            "practice_quizzes": practice_quizzes,
            "total_attempts": total_attempts,
            "average_score": round(avg_score, 4),
            "all_weak_topics": list(all_weak_topics),
            "mastery_by_grade": mastery_by_grade
        },
        "history": quiz_history
    }
    
    return response_data

