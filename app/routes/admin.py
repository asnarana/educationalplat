"""
Admin routes for viewing all students and their histories.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from app.db import get_db
from app.models import User, Quiz, Attempt, Question
from app.routes.auth import get_current_admin, SessionUser
from app.routes.history import determine_quiz_type
from app.cache import get_cache_key, get_from_cache, set_cache

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/students")
def list_all_students(
    current_admin: SessionUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    List all students in the system with their statistics.
    
    Uses Redis caching to improve performance when there are many students.
    """
    # Try to get from cache first
    cache_key = "admin:students:list"
    cached_result = get_from_cache(cache_key)
    if cached_result is not None:
        return cached_result
    
    students = db.query(User).filter(User.role == "student").order_by(User.username).all()
    
    student_list = []
    for student in students:
        # Get quiz statistics
        quizzes = db.query(Quiz).filter(Quiz.student_id == student.username).all()
        attempts = db.query(Attempt).filter(Attempt.student_id == student.username).all()
        
        # Calculate stats
        total_quizzes = len(quizzes)
        total_attempts = len(attempts)
        avg_score = sum(a.score_total for a in attempts) / total_attempts if total_attempts > 0 else 0.0
        
        # Get grade levels this student has worked on
        grade_levels = list(set([q.grade_level for q in quizzes]))
        
        student_list.append({
            "id": student.id,
            "username": student.username,
            "created_at": student.created_at.isoformat(),
            "stats": {
                "total_quizzes": total_quizzes,
                "total_attempts": total_attempts,
                "average_score": round(avg_score * 100, 2),
                "grade_levels": sorted(grade_levels)
            }
        })
    
    response_data = {
        "total_students": len(student_list),
        "students": student_list
    }
    
    # Cache the result (2 minutes TTL - shorter than history since stats change more frequently)
    set_cache(cache_key, response_data, ttl=120)
    
    return response_data


@router.get("/students/{student_username}/history")
def get_student_history_admin(
    student_username: str,
    grade_level: Optional[int] = Query(None, description="Filter history by grade level"),
    current_admin: SessionUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get complete quiz and attempt history for any student (admin view).
    
    Uses Redis caching to improve performance for students with many quizzes.
    """
    # Verify student exists
    student = db.query(User).filter(
        User.username == student_username,
        User.role == "student"
    ).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Try to get from cache first
    cache_key = get_cache_key(student_username, grade_level, prefix="admin_history")
    cached_result = get_from_cache(cache_key)
    if cached_result is not None:
        return cached_result
    
    # Get quizzes for student (filter by grade level if provided)
    query = db.query(Quiz).filter(Quiz.student_id == student_username)
    if grade_level is not None:
        query = query.filter(Quiz.grade_level == grade_level)
    
    # Order by grade level, then by grade_quiz_number
    quizzes = query.order_by(Quiz.grade_level.desc(), Quiz.grade_quiz_number.desc()).all()
    
    # Get quiz IDs for this student/grade combination
    quiz_ids = [q.id for q in quizzes]
    
    # Get attempts for this student
    query_attempts = db.query(Attempt).filter(Attempt.student_id == student_username)
    if quiz_ids:
        query_attempts = query_attempts.filter(Attempt.quiz_id.in_(quiz_ids))
    else:
        query_attempts = query_attempts.filter(Attempt.quiz_id.in_([]))
    
    attempts = query_attempts.order_by(Attempt.submitted_at.desc()).all()
    
    # Build response with quiz type information
    quiz_history = []
    for quiz in quizzes:
        quiz_attempts = [a for a in attempts if a.quiz_id == quiz.id]
        
        # Determine if this is a practice or full quiz
        quiz_info = determine_quiz_type(quiz, db)
        quiz_dict = quiz.to_dict(db_session=db)
        quiz_dict.update(quiz_info)
        
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
        mastery_by_grade[grade] = check_mastery_status(db, student_username, grade, mastery_threshold=0.80)
    
    response_data = {
        "student": student.to_dict(),
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
    
    # Cache the result (5 minutes TTL)
    set_cache(cache_key, response_data, ttl=300)
    
    return response_data
