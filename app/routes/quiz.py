"""
Routes for quiz generation and submission.
"""
import random
from typing import List, Dict, Optional, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db import get_db
from app.models import Question, Quiz, Attempt
from app.logic.scoring import compute_topic_metrics, compute_overall_score, identify_weak_topics
from app.logic.adaptive import select_questions_for_quiz, get_recent_question_ids, check_mastery_status
from app.monitoring.metrics import (
    track_quiz_generated, track_quiz_submitted, track_weak_topic
)

router = APIRouter(prefix="/quiz", tags=["quiz"])


# Request/Response models
class QuizGenerateRequest(BaseModel):
    student_id: str
    grade_level: int
    topics: List[str]
    num_questions: int = 10


class TopicPracticeRequest(BaseModel):
    student_id: str
    grade_level: int
    topic: str
    num_questions: int = 6


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
    mastery_status: Dict[str, Any]
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
    try:
        # Get student's recent attempts to determine weak topics (same grade level only)
        recent_attempt = (
            db.query(Attempt)
            .join(Quiz, Attempt.quiz_id == Quiz.id)
            .filter(
                Attempt.student_id == request.student_id,
                Quiz.grade_level == request.grade_level
            )
            .order_by(Attempt.submitted_at.desc())
            .first()
        )
        
        weak_topics = recent_attempt.weak_topics if recent_attempt else []
        
        # Get recent question IDs to avoid repeats (same grade level only)
        recent_question_ids = get_recent_question_ids(db, request.student_id, request.grade_level, num_quizzes=2)
        
        # Select questions using adaptive logic
        selected_questions = select_questions_for_quiz(
            db=db,
            grade_level=request.grade_level,
            topics=request.topics,
            num_questions=request.num_questions,
            weak_topics=weak_topics if weak_topics else None,
            exclude_question_ids=recent_question_ids
        )
        
        # If we don't have enough questions, try with less restrictive exclusions
        if len(selected_questions) < request.num_questions:
            # Try excluding only from the last 1 quiz instead of 2
            recent_question_ids = get_recent_question_ids(db, request.student_id, request.grade_level, num_quizzes=1)
            selected_questions = select_questions_for_quiz(
                db=db,
                grade_level=request.grade_level,
                topics=request.topics,
                num_questions=request.num_questions,
                weak_topics=weak_topics if weak_topics else None,
                exclude_question_ids=recent_question_ids
            )
        
        # If still not enough, allow repeats (no exclusions)
        if len(selected_questions) < request.num_questions:
            selected_questions = select_questions_for_quiz(
                db=db,
                grade_level=request.grade_level,
                topics=request.topics,
                num_questions=request.num_questions,
                weak_topics=weak_topics if weak_topics else None,
                exclude_question_ids=set()  # No exclusions - allow repeats
            )
        
        # If still not enough, use what we have (shouldn't happen with expanded bank)
        if len(selected_questions) < request.num_questions:
            # Log a warning but don't fail - use what we have
            pass
        
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
        
        # Track metrics
        track_quiz_generated(quiz.grade_level, quiz_type='full')
        
        return QuizResponse(
            quiz_id=quiz.id,
            student_id=quiz.student_id,
            grade_level=quiz.grade_level,
            questions=questions_data,
            created_at=quiz.created_at.isoformat()
        )
    except Exception as e:
        import traceback
        error_msg = f"ERROR in generate_quiz: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating quiz: {str(e)}")


@router.post("/practice-topic", response_model=QuizResponse)
def generate_topic_practice_quiz(
    request: TopicPracticeRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a focused practice quiz for a specific topic.
    
    This is used when a student wants to practice a weak topic specifically.
    """
    # For practice quizzes, get all questions for this topic
    all_topic_questions = db.query(Question).filter(
        Question.grade_level == request.grade_level,
        Question.topic == request.topic
    ).all()
    
    if len(all_topic_questions) == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No questions available for topic '{request.topic}' at grade level {request.grade_level}. Please seed the question bank first."
        )
    
    # Get recent question IDs to try to avoid repeats (but allow if needed)
    recent_question_ids = get_recent_question_ids(db, request.student_id, request.grade_level, num_quizzes=1)
    
    # Separate available questions (not recently used) and recently used questions
    available_questions = [q for q in all_topic_questions if q.id not in recent_question_ids]
    recently_used_questions = [q for q in all_topic_questions if q.id in recent_question_ids]
    
    # Shuffle to get variety
    random.shuffle(available_questions)
    random.shuffle(recently_used_questions)
    
    # Track selected question IDs to avoid duplicates
    selected_questions = []
    selected_ids = set()
    
    # First, try to fill from available (not recently used) questions
    for q in available_questions:
        if len(selected_questions) >= request.num_questions:
            break
        if q.id not in selected_ids:
            selected_questions.append(q)
            selected_ids.add(q.id)
    
    # If we need more, add from recently used questions (allow repeats for practice)
    if len(selected_questions) < request.num_questions:
        for q in recently_used_questions:
            if len(selected_questions) >= request.num_questions:
                break
            if q.id not in selected_ids:
                selected_questions.append(q)
                selected_ids.add(q.id)
    
    # If still not enough, cycle through all questions (shouldn't happen with expanded bank)
    if len(selected_questions) < request.num_questions:
        needed = request.num_questions - len(selected_questions)
        remaining = [q for q in all_topic_questions if q.id not in selected_ids]
        random.shuffle(remaining)
        for q in remaining[:needed]:
            selected_questions.append(q)
            selected_ids.add(q.id)
    
    # Final fallback: if still not enough, we should have enough with expanded bank
    # But if somehow we don't, just use what we have (better than error)
    # This should never happen with the expanded question bank
    if len(selected_questions) < request.num_questions:
        # Log that we couldn't get enough unique questions
        # But continue with what we have
        pass
    
    # Safety check: Ensure no duplicate question IDs (prevent "Some questions not found" error)
    unique_question_ids = []
    seen_ids = set()
    unique_selected_questions = []
    for q in selected_questions:
        if q.id not in seen_ids:
            unique_question_ids.append(q.id)
            unique_selected_questions.append(q)
            seen_ids.add(q.id)
    
    # Use unique lists
    selected_questions = unique_selected_questions
    
    # Create quiz
    quiz = Quiz(
        student_id=request.student_id,
        grade_level=request.grade_level,
        question_ids=unique_question_ids
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    
    # Return quiz without correct answers
    questions_data = [q.to_dict(include_answer=False) for q in selected_questions]
    
    # Track metrics for practice quiz
    track_quiz_generated(request.grade_level, quiz_type='practice')
    
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
    
    # Get questions - handle duplicates in question_ids
    # Deduplicate question_ids to avoid "Some questions not found" error when repeats are allowed
    unique_question_ids = list(dict.fromkeys(quiz.question_ids))  # Preserves order, removes duplicates
    
    questions = db.query(Question).filter(Question.id.in_(unique_question_ids)).all()
    if len(questions) != len(unique_question_ids):
        raise HTTPException(status_code=500, detail="Some questions not found")
    
    # If there were duplicates, we need to expand the questions list to match the original question_ids order
    # This allows the same question to appear multiple times in the quiz
    if len(quiz.question_ids) != len(unique_question_ids):
        # Create a mapping of question ID to Question object
        question_map = {q.id: q for q in questions}
        # Rebuild questions list in the order of quiz.question_ids (allowing repeats)
        questions = [question_map[qid] for qid in quiz.question_ids if qid in question_map]
    
    # Convert answer keys from string to int (JSON sends string keys)
    answers_int_keys = {int(k): v for k, v in request.answers.items()}
    
    # Compute scores
    topic_metrics = compute_topic_metrics(questions, answers_int_keys)
    overall_score = compute_overall_score(questions, answers_int_keys)
    weak_topics = identify_weak_topics(topic_metrics, mastery_threshold=0.80)
    passed = len(weak_topics) == 0
    
    # Determine quiz type: if quiz has questions from only one topic, it's practice
    unique_topics = set(q.topic for q in questions)
    quiz_type = 'practice' if len(unique_topics) == 1 else 'full'
    
    # Track metrics
    track_quiz_submitted(quiz.grade_level, overall_score * 100, passed, quiz_type=quiz_type)
    for topic in weak_topics:
        track_weak_topic(quiz.grade_level, topic)
    
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
    
    # Check mastery status (for this grade level)
    mastery_status = check_mastery_status(db, quiz.student_id, quiz.grade_level, mastery_threshold=0.80)
    
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

