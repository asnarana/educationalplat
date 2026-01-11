"""
Routes for retrieving student history.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from app.db import get_db
from app.models import Quiz, Attempt, Question
from app.routes.auth import get_current_user, get_current_admin, SessionUser
from app.cache import get_cache_key, get_from_cache, set_cache, invalidate_student_cache
from typing import Optional as Opt

router = APIRouter(prefix="/student", tags=["history"])


def determine_quiz_type(quiz: Quiz, db: Session) -> Dict[str, any]:
    """
    Determine if a quiz is a practice quiz (single topic) or full quiz (multiple topics).
    
    This determination is based on:
    1. The actual questions in the quiz (ensuring consistency)
    2. The number of questions (quizzes with 6 or fewer questions are typically practice)
    3. Whether all questions are from the same topic
    
    Uses Redis caching to improve performance when processing many quizzes.
    
    Returns a dictionary with quiz_type and practice_topic (if applicable).
    """
    # Handle case where question_ids might be None or empty
    if not quiz.question_ids:
        return {"quiz_type": "full", "practice_topic": None}
    
    # Try to get from cache first (cache key based on quiz ID and question IDs hash)
    cache_key = f"quiz_type:{quiz.id}:{hash(tuple(sorted(quiz.question_ids)))}"
    cached_result = get_from_cache(cache_key)
    if cached_result is not None:
        return cached_result
    
    # Get unique question IDs (handle duplicates)
    unique_question_ids = list(dict.fromkeys(quiz.question_ids))
    num_questions = len(unique_question_ids)
    
    # Get questions for this quiz
    questions = db.query(Question).filter(
        Question.id.in_(unique_question_ids)
    ).all()
    
    # If no questions found (e.g., questions were deleted), try to determine from question_ids count
    # This handles the case where questions were cleared but quizzes remain
    if not questions:
        # If we have question_ids but can't find the questions, use count as fallback
        # Quizzes with 6 or fewer questions are typically practice quizzes
        if num_questions <= 6:
            result = {
                "quiz_type": "practice",
                "practice_topic": None  # Can't determine topic without questions
            }
            set_cache(cache_key, result, ttl=600)
            return result
        else:
            result = {"quiz_type": "full", "practice_topic": None}
            set_cache(cache_key, result, ttl=600)
            return result
    
    # Get unique topics from questions
    unique_topics = set(q.topic for q in questions)
    
    # Determine quiz type:
    # 1. If all questions are from the same topic, it's a practice quiz
    # 2. If quiz has 6 or fewer questions, it's likely a practice quiz (even if multiple topics somehow)
    #    This handles edge cases where practice quizzes might have been misclassified
    if len(unique_topics) == 1:
        practice_topic = list(unique_topics)[0]
        result = {
            "quiz_type": "practice",
            "practice_topic": practice_topic
        }
        # Cache the result (10 minutes TTL - quiz type doesn't change)
        set_cache(cache_key, result, ttl=600)
        return result
    elif num_questions <= 6:
        # Quizzes with 6 or fewer questions should be practice quizzes
        # Use the most common topic as the practice topic
        topic_counts = {}
        for q in questions:
            topic_counts[q.topic] = topic_counts.get(q.topic, 0) + 1
        practice_topic = max(topic_counts.items(), key=lambda x: x[1])[0] if topic_counts else None
        result = {
            "quiz_type": "practice",
            "practice_topic": practice_topic
        }
        # Cache the result (10 minutes TTL - quiz type doesn't change)
        set_cache(cache_key, result, ttl=600)
        return result
    else:
        result = {
            "quiz_type": "full",
            "practice_topic": None
        }
        # Cache the result (10 minutes TTL - quiz type doesn't change)
        set_cache(cache_key, result, ttl=600)
        return result


@router.get("/{student_id}/history")
def get_student_history(
    student_id: str,
    grade_level: Optional[int] = Query(None, description="Filter history by grade level"),
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    page_size: int = Query(10, ge=1, le=50, description="Number of quizzes per page (max 50)"),
    db: Session = Depends(get_db),
    current_user: Opt[SessionUser] = Depends(get_current_user)
):
    """
    Get complete quiz and attempt history for a student.
    
    If grade_level is provided, only returns history for that grade level.
    This allows the same student ID to have separate histories for different grades.
    
    Students can only view their own history unless they are an admin.
    
    Uses Redis caching to improve performance for students with many quizzes.
    
    Args:
        student_id: Student identifier
        grade_level: Optional grade level filter (if provided, only shows history for this grade)
        current_user: Authenticated user (optional)
    
    Returns:
    - List of quizzes with their attempts
    - Overall progress summary
    - Identifies practice quizzes vs full quizzes
    """
    # Check authorization: students can only view their own history, admins can view any
    if current_user:
        if current_user.role != "admin" and current_user.username != student_id:
            raise HTTPException(
                status_code=403,
                detail="You can only view your own history"
            )
    
    # Try to get from cache first (cache key includes pagination)
    cache_key = f"history:{student_id}:grade:{grade_level or 'all'}:page:{page}:size:{page_size}"
    cached_result = get_from_cache(cache_key)
    if cached_result is not None:
        return cached_result
    
    # Get quizzes for student (filter by grade level if provided)
    query = db.query(Quiz).filter(Quiz.student_id == student_id)
    if grade_level is not None:
        query = query.filter(Quiz.grade_level == grade_level)
    
    # Get total count for pagination
    total_quizzes_count = query.count()
    
    # Calculate pagination
    offset = (page - 1) * page_size
    
    # Order by grade level, then by grade_quiz_number (so grade-specific IDs are sequential)
    # Most recent first within each grade
    quizzes = query.order_by(Quiz.grade_level.desc(), Quiz.grade_quiz_number.desc()).offset(offset).limit(page_size).all()
    
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
    
    # Build response with quiz type information (only for current page)
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
    
    # Calculate summary statistics from ALL quizzes (not just current page)
    # Get all quizzes for accurate summary
    all_quizzes_query = db.query(Quiz).filter(Quiz.student_id == student_id)
    if grade_level is not None:
        all_quizzes_query = all_quizzes_query.filter(Quiz.grade_level == grade_level)
    all_quizzes = all_quizzes_query.all()
    all_quiz_ids = [q.id for q in all_quizzes]
    
    # Get all attempts for summary
    all_attempts_query = db.query(Attempt).filter(Attempt.student_id == student_id)
    if all_quiz_ids:
        all_attempts_query = all_attempts_query.filter(Attempt.quiz_id.in_(all_quiz_ids))
    else:
        all_attempts_query = all_attempts_query.filter(Attempt.quiz_id.in_([]))
    all_attempts = all_attempts_query.all()
    
    total_attempts = len(all_attempts)
    avg_score = sum(a.score_total for a in all_attempts) / total_attempts if total_attempts > 0 else 0.0
    
    # Count practice vs full quizzes (from all quizzes)
    full_quizzes = 0
    practice_quizzes = 0
    for quiz in all_quizzes:
        quiz_info = determine_quiz_type(quiz, db)
        if quiz_info["quiz_type"] == "practice":
            practice_quizzes += 1
        else:
            full_quizzes += 1
    
    # Get unique weak topics across all attempts
    all_weak_topics = set()
    for attempt in all_attempts:
        all_weak_topics.update(attempt.weak_topics)
    
    # Group mastery status by grade level
    from app.logic.adaptive import check_mastery_status
    grade_levels = list(set([q.grade_level for q in all_quizzes]))
    mastery_by_grade = {}
    for grade in grade_levels:
        mastery_by_grade[grade] = check_mastery_status(db, student_id, grade, mastery_threshold=0.80)
    
    # Calculate pagination info
    total_pages = (total_quizzes_count + page_size - 1) // page_size if total_quizzes_count > 0 else 1
    
    # If grade_level filter was applied, include it in response
    response_data = {
        "student_id": student_id,
        "grade_level": grade_level,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_quizzes": total_quizzes_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1
        },
        "summary": {
            "total_quizzes": total_quizzes_count,  # Use total count, not just current page
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

