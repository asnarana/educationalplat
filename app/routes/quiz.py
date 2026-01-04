"""
Routes for quiz generation and submission.
"""
from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db import get_db
from app.models import Question, Quiz, Attempt
from app.logic.scoring import compute_topic_metrics, compute_overall_score, identify_weak_topics
from app.logic.adaptive import select_questions_for_quiz, get_recent_question_ids, check_mastery_status

router = APIRouter(prefix="/quiz", tags=["quiz"])


# Request/Response models
class QuizGenerateRequest(BaseModel):
    student_id: str
    grade_level: int
    topics: List[str]
    num_questions: int = 10


class QuizSubmitRequest(BaseModel):
    answers: Dict[str, str]  # {question_id: answer} - keys may be strings from JSON


class QuizResponse(BaseModel):
    quiz_id: int
    student_id: str
    grade_level: int
    questions: List[Dict]
    created_at: str


class SubmissionResponse(BaseModel):
    attempt_id: int
    quiz_id: int
    score_total: float
    topic_metrics: Dict[str, Dict[str, float]]
    weak_topics: List[str]
    passed: bool
    mastery_status: Dict[str, any]
    next_quiz_recommendation: Optional[Dict] = None


@router.post("/generate", response_model=QuizResponse)
def generate_quiz(
    request: QuizGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a new quiz for a student.
    
    If student has previous attempts, uses adaptive logic to focus on weak topics.
    Otherwise, generates a balanced quiz across all topics.
    """
    # Get student's recent attempts to determine weak topics
    recent_attempt = (
        db.query(Attempt)
        .filter(Attempt.student_id == request.student_id)
        .order_by(Attempt.submitted_at.desc())
        .first()
    )
    
    weak_topics = recent_attempt.weak_topics if recent_attempt else []
    
    # Get recent question IDs to avoid repeats
    recent_question_ids = get_recent_question_ids(db, request.student_id, num_quizzes=2)
    
    # Select questions using adaptive logic
    selected_questions = select_questions_for_quiz(
        db=db,
        grade_level=request.grade_level,
        topics=request.topics,
        num_questions=request.num_questions,
        weak_topics=weak_topics if weak_topics else None,
        exclude_question_ids=recent_question_ids
    )
    
    if len(selected_questions) < request.num_questions:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough questions available. Found {len(selected_questions)} questions, requested {request.num_questions}."
        )
    
    # Create quiz
    quiz = Quiz(
        student_id=request.student_id,
        grade_level=request.grade_level,
        question_ids=[q.id for q in selected_questions]
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    
    # Return quiz without correct answers
    questions_data = [q.to_dict(include_answer=False) for q in selected_questions]
    
    return QuizResponse(
        quiz_id=quiz.id,
        student_id=quiz.student_id,
        grade_level=quiz.grade_level,
        questions=questions_data,
        created_at=quiz.created_at.isoformat()
    )


@router.post("/{quiz_id}/submit", response_model=SubmissionResponse)
def submit_quiz(
    quiz_id: int,
    request: QuizSubmitRequest,
    db: Session = Depends(get_db)
):
    """
    Submit answers for a quiz and get scoring results.
    
    Returns:
    - Overall score
    - Topic-level metrics
    - Weak topics (score < 0.80)
    - Mastery status
    - Next quiz recommendation
    """
    # Get quiz
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Get questions
    questions = db.query(Question).filter(Question.id.in_(quiz.question_ids)).all()
    if len(questions) != len(quiz.question_ids):
        raise HTTPException(status_code=500, detail="Some questions not found")
    
    # Convert answer keys from string to int (JSON sends string keys)
    answers_int_keys = {int(k): v for k, v in request.answers.items()}
    
    # Compute scores
    topic_metrics = compute_topic_metrics(questions, answers_int_keys)
    overall_score = compute_overall_score(questions, answers_int_keys)
    weak_topics = identify_weak_topics(topic_metrics, mastery_threshold=0.80)
    passed = len(weak_topics) == 0
    
    # Create attempt record (store with int keys)
    attempt = Attempt(
        quiz_id=quiz_id,
        student_id=quiz.student_id,
        answers=answers_int_keys,
        score_total=overall_score,
        topic_metrics=topic_metrics,
        weak_topics=weak_topics,
        passed=passed
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    
    # Check mastery status
    mastery_status = check_mastery_status(db, quiz.student_id, mastery_threshold=0.80)
    
    # Generate next quiz recommendation
    next_quiz_recommendation = None
    if not mastery_status["mastered"]:
        next_quiz_recommendation = {
            "student_id": quiz.student_id,
            "grade_level": quiz.grade_level,
            "topics": list(set([q.topic for q in questions])),  # All topics from current quiz
            "num_questions": 10,
            "focus": "weak_topics" if weak_topics else "review",
            "weak_topics": weak_topics
        }
    
    return SubmissionResponse(
        attempt_id=attempt.id,
        quiz_id=quiz_id,
        score_total=overall_score,
        topic_metrics=topic_metrics,
        weak_topics=weak_topics,
        passed=passed,
        mastery_status=mastery_status,
        next_quiz_recommendation=next_quiz_recommendation
    )

