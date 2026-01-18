"""
Routes for quiz generation and submission.
"""
import random
import time
from typing import List, Dict, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db import get_db
from app.models import Question, Quiz, Attempt
from app.logic.scoring import compute_topic_metrics, compute_overall_score, identify_weak_topics
from app.logic.adaptive import select_questions_for_quiz, get_recent_question_ids, check_mastery_status
from app.monitoring.metrics import (
    track_quiz_generated, track_quiz_submitted, track_weak_topic
)
from app.routes.auth import get_current_user, SessionUser
from app.cache import invalidate_student_cache
from typing import Optional

router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.get("/topics")
def get_topics(
    grade_level: int = Query(..., description="Grade level (3, 4, or 5)"),
    subject: Optional[str] = Query(None, description="Subject filter: 'Math' or 'Reading'"),
    db: Session = Depends(get_db)
):
    """
    Get available topics for a given grade level and subject.
    If subject is not provided, returns all topics for the grade level.
    """
    query = db.query(Question.topic).filter(
        Question.grade_level == grade_level
    ).distinct()
    
    topics = [row[0] for row in query.all()]
    
    # Filter by subject if provided
    if subject:
        # Determine subject based on topic names
        # Math topics: Addition, Subtraction, Multiplication, Division, Fractions, Algebra, Geometry, etc.
        # Reading topics: Vocabulary, Reading Comprehension, Character Analysis, Main Idea, etc.
        math_keywords = ['addition', 'subtraction', 'multiplication', 'division', 'fraction', 
                        'algebra', 'geometry', 'decimal', 'percentage', 'word problem']
        reading_keywords = ['vocabulary', 'reading', 'comprehension', 'character', 'main idea', 
                           'text structure', 'inference', 'word meaning']
        
        if subject.lower() == 'math':
            topics = [t for t in topics if any(keyword in t.lower() for keyword in math_keywords)]
        elif subject.lower() == 'reading':
            topics = [t for t in topics if any(keyword in t.lower() for keyword in reading_keywords)]
    
    return {
        "grade_level": grade_level,
        "subject": subject,
        "topics": sorted(topics)
    }


# Request/Response models
class QuizGenerateRequest(BaseModel):
    student_id: Optional[str] = None  # Optional if user is authenticated
    grade_level: int
    topics: List[str]
    num_questions: int = 10


class TopicPracticeRequest(BaseModel):
    student_id: Optional[str] = None  # Optional if user is authenticated
    grade_level: int
    topic: str
    num_questions: int = 6


class QuizSubmitRequest(BaseModel):
    answers: Dict[str, str]  # {question_id: answer} - keys may be strings from JSON


class QuizResponse(BaseModel):
    quiz_id: int
    grade_quiz_number: int  # Grade-specific ID (starts at 1 for each grade)
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
    next_grade_level: Optional[int] = None  # Next grade level available if current grade is mastered


@router.post("/generate", response_model=QuizResponse)
def generate_quiz(
    request: QuizGenerateRequest,
    db: Session = Depends(get_db),
    current_user: Optional[SessionUser] = Depends(get_current_user)
):
    """
    Generate a new quiz for a student.
    
    If student has previous attempts, uses adaptive logic to focus on weak topics.
    Otherwise, generates a balanced quiz across all topics.
    """
    # Use authenticated user's username if available, otherwise use provided student_id
    student_id = current_user.username if current_user else request.student_id
    if not student_id:
        raise HTTPException(status_code=400, detail="Student ID required. Please login or provide student_id.")
    
    try:
        # For full test retakes: Use balanced distribution (2 per topic)
        # Students already have practice quizzes for weak topics, so full tests should assess all topics equally
        # This ensures mastery means comprehensive knowledge, not just improvement in weak areas
        
        # Get recent question IDs to avoid repeats (same grade level only)
        # Exclude from last 3 quizzes to ensure more variety (increased from 2)
        recent_question_ids = get_recent_question_ids(db, student_id, request.grade_level, num_quizzes=3)
        
        # Also get the MOST recent quiz's questions to ensure current quiz is definitely excluded
        most_recent_quiz = (
            db.query(Quiz)
            .filter(
                Quiz.student_id == student_id,
                Quiz.grade_level == request.grade_level
            )
            .order_by(Quiz.created_at.desc())
            .first()
        )
        
        # Add the most recent quiz's questions to exclusion set
        if most_recent_quiz and most_recent_quiz.question_ids:
            recent_question_ids.update(most_recent_quiz.question_ids)
        
        # CRITICAL: Seed random number generator with current time to ensure different questions each time
        random.seed(int(time.time() * 1000))
        
        # Select questions using balanced distribution (no weak topic focus for full tests)
        # Pass weak_topics=None to get even distribution across all topics
        # Exclude octopus sample question
        selected_questions = select_questions_for_quiz(
            db=db,
            grade_level=request.grade_level,
            topics=request.topics,
            num_questions=request.num_questions,
            weak_topics=None,  # No adaptive focus - balanced quiz for comprehensive assessment
            exclude_question_ids=recent_question_ids,
            exclude_prompt_keywords=['octopus']  # Exclude octopus sample question
        )
        
        # If we don't have enough questions, try with less restrictive exclusions
        if len(selected_questions) < request.num_questions:
            # Try excluding only from the last 2 quizzes instead of 3
            recent_question_ids = get_recent_question_ids(db, student_id, request.grade_level, num_quizzes=2)
            if most_recent_quiz and most_recent_quiz.question_ids:
                recent_question_ids.update(most_recent_quiz.question_ids)
            selected_questions = select_questions_for_quiz(
                db=db,
                grade_level=request.grade_level,
                topics=request.topics,
                num_questions=request.num_questions,
                weak_topics=None,  # Balanced distribution for full tests
                exclude_question_ids=recent_question_ids,
                exclude_prompt_keywords=['octopus']
            )
        
        # If still not enough, try excluding only the most recent quiz
        if len(selected_questions) < request.num_questions:
            recent_question_ids = set()
            if most_recent_quiz and most_recent_quiz.question_ids:
                recent_question_ids.update(most_recent_quiz.question_ids)
            selected_questions = select_questions_for_quiz(
                db=db,
                grade_level=request.grade_level,
                topics=request.topics,
                num_questions=request.num_questions,
                weak_topics=None,  # Balanced distribution for full tests
                exclude_question_ids=recent_question_ids,
                exclude_prompt_keywords=['octopus']
            )
        
        # If still not enough, allow repeats (no exclusions) - but this should be rare with expanded bank
        if len(selected_questions) < request.num_questions:
            selected_questions = select_questions_for_quiz(
                db=db,
                grade_level=request.grade_level,
                topics=request.topics,
                num_questions=request.num_questions,
                weak_topics=None,  # Balanced distribution for full tests
                exclude_question_ids=set(),  # No exclusions - allow repeats
                exclude_prompt_keywords=['octopus']  # Still exclude octopus
            )
        
        # If still not enough, use what we have (shouldn't happen with expanded bank)
        if len(selected_questions) < request.num_questions:
            # Log a warning but don't fail - use what we have
            pass
        
        # Get next grade-specific quiz number for this student+grade combination
        grade_quiz_number = Quiz.get_next_grade_quiz_number(db, student_id, request.grade_level)
        
        # Create quiz
        quiz = Quiz(
            student_id=student_id,
            grade_level=request.grade_level,
            grade_quiz_number=grade_quiz_number,
            question_ids=[q.id for q in selected_questions]
        )
        db.add(quiz)
        db.commit()
        db.refresh(quiz)
        
        # Invalidate cache for this student (new quiz created)
        invalidate_student_cache(student_id)
        
        # Return quiz without correct answers
        questions_data = [q.to_dict(include_answer=False) for q in selected_questions]
        
        # Track metrics
        track_quiz_generated(quiz.grade_level, quiz_type='full')
        
        return QuizResponse(
            quiz_id=quiz.id,
            grade_quiz_number=quiz.grade_quiz_number,
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


@router.put("/{quiz_id}/regenerate", response_model=QuizResponse)
def regenerate_quiz_questions(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[SessionUser] = Depends(get_current_user)
):
    """
    Regenerate questions for an existing quiz (for retakes).
    Updates the quiz with new questions while keeping the same quiz_id.
    This allows retakes to show up as attempts under the same quiz entry.
    """
    # Get the existing quiz
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Verify ownership
    student_id = current_user.username if current_user else None
    if student_id and quiz.student_id != student_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this quiz")
    
    # Determine if this is a practice quiz (single topic) or full quiz (multiple topics)
    # Check existing questions to determine topic
    existing_questions = db.query(Question).filter(Question.id.in_(quiz.question_ids)).all() if quiz.question_ids else []
    existing_topics = set(q.topic for q in existing_questions) if existing_questions else set()
    
    is_practice_quiz = len(existing_topics) == 1
    
    try:
        if is_practice_quiz:
            # Practice quiz: regenerate questions for the same topic
            practice_topic = list(existing_topics)[0] if existing_topics else None
            if not practice_topic:
                raise HTTPException(status_code=400, detail="Cannot determine practice topic")
            
            # Get all questions for this topic
            all_topic_questions = db.query(Question).filter(
                Question.grade_level == quiz.grade_level,
                Question.topic == practice_topic
            ).all()
            
            if len(all_topic_questions) == 0:
                raise HTTPException(status_code=404, detail=f"No questions available for topic '{practice_topic}'")
            
            # Get recent question IDs (exclude this quiz's current questions)
            recent_question_ids = get_recent_question_ids(db, quiz.student_id, quiz.grade_level, num_quizzes=1)
            if quiz.question_ids:
                recent_question_ids.update(quiz.question_ids)
            
            # Separate available and recently used questions (exclude octopus sample question)
            available_questions = [
                q for q in all_topic_questions 
                if q.id not in recent_question_ids 
                and 'octopus' not in q.prompt.lower()
            ]
            recently_used_questions = [
                q for q in all_topic_questions 
                if q.id in recent_question_ids 
                and 'octopus' not in q.prompt.lower()
            ]
            
            # CRITICAL: Seed random number generator with current time to ensure different questions each retake
            random.seed(int(time.time() * 1000))
            
            # Shuffle for variety
            random.shuffle(available_questions)
            random.shuffle(recently_used_questions)
            
            # Select questions (same count as original)
            num_needed = len(quiz.question_ids) if quiz.question_ids else 6
            selected_questions = []
            selected_ids = set()
            
            # First try available questions
            for q in available_questions:
                if len(selected_questions) >= num_needed:
                    break
                if q.id not in selected_ids:
                    selected_questions.append(q)
                    selected_ids.add(q.id)
            
            # If needed, add from recently used
            if len(selected_questions) < num_needed:
                for q in recently_used_questions:
                    if len(selected_questions) >= num_needed:
                        break
                    if q.id not in selected_ids:
                        selected_questions.append(q)
                        selected_ids.add(q.id)
            
            # Final fallback: use any questions (but still exclude octopus and current quiz)
            if len(selected_questions) < num_needed:
                remaining = [
                    q for q in all_topic_questions 
                    if q.id not in selected_ids 
                    and q.id not in (quiz.question_ids or [])
                    and 'octopus' not in q.prompt.lower()
                ]
                random.shuffle(remaining)
                for q in remaining[:num_needed - len(selected_questions)]:
                    selected_questions.append(q)
        else:
            # Full quiz: regenerate with balanced distribution across the SAME topics as original quiz
            # Use topics from existing questions to preserve subject (Math vs Reading)
            if not existing_topics:
                raise HTTPException(status_code=400, detail="Cannot determine quiz topics from existing questions")
            
            grade_topics = list(existing_topics)
            
            # Get recent question IDs to avoid repeats
            recent_question_ids = get_recent_question_ids(db, quiz.student_id, quiz.grade_level, num_quizzes=3)
            
            # Always exclude this quiz's current questions
            if quiz.question_ids:
                recent_question_ids.update(quiz.question_ids)
            
            num_needed = len(quiz.question_ids) if quiz.question_ids else 10
            
            # CRITICAL: Always exclude current quiz's questions to ensure different questions on retake
            current_quiz_question_ids = set(quiz.question_ids) if quiz.question_ids else set()
            
            # CRITICAL: Seed random number generator with current time to ensure different questions each retake
            random.seed(int(time.time() * 1000))
            
            # Select new questions using balanced distribution across the SAME topics
            # Always exclude current quiz questions AND octopus sample question
            selected_questions = select_questions_for_quiz(
                db=db,
                grade_level=quiz.grade_level,
                topics=grade_topics,
                num_questions=num_needed,
                weak_topics=None,  # Balanced distribution for full tests
                exclude_question_ids=recent_question_ids | current_quiz_question_ids,
                exclude_prompt_keywords=['octopus']  # Exclude octopus sample question
            )
            
            # If we don't have enough questions, try with less restrictive exclusions (but still exclude current quiz)
            if len(selected_questions) < num_needed:
                selected_questions = select_questions_for_quiz(
                    db=db,
                    grade_level=quiz.grade_level,
                    topics=grade_topics,
                    num_questions=num_needed,
                    weak_topics=None,
                    exclude_question_ids=current_quiz_question_ids,  # Still exclude current quiz
                    exclude_prompt_keywords=['octopus']
                )
            
            # If still not enough, allow repeats from other quizzes but NEVER from current quiz
            if len(selected_questions) < num_needed:
                selected_questions = select_questions_for_quiz(
                    db=db,
                    grade_level=quiz.grade_level,
                    topics=grade_topics,
                    num_questions=num_needed,
                    weak_topics=None,
                    exclude_question_ids=current_quiz_question_ids,  # ALWAYS exclude current quiz
                    exclude_prompt_keywords=['octopus']
                )
        
        # Update the quiz with new questions
        quiz.question_ids = [q.id for q in selected_questions]
        db.commit()
        db.refresh(quiz)
        
        # Invalidate cache
        invalidate_student_cache(quiz.student_id)
        
        # Return quiz without correct answers
        questions_data = [q.to_dict(include_answer=False) for q in selected_questions]
        
        return QuizResponse(
            quiz_id=quiz.id,
            grade_quiz_number=quiz.grade_quiz_number,
            student_id=quiz.student_id,
            grade_level=quiz.grade_level,
            questions=questions_data,
            created_at=quiz.created_at.isoformat()
        )
    except Exception as e:
        import traceback
        error_msg = f"ERROR in regenerate_quiz_questions: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error regenerating quiz questions: {str(e)}")


@router.post("/practice-topic", response_model=QuizResponse)
def generate_topic_practice_quiz(
    request: TopicPracticeRequest,
    db: Session = Depends(get_db),
    current_user: Optional[SessionUser] = Depends(get_current_user)
):
    """
    Generate a focused practice quiz for a specific topic.
    
    This is used when a student wants to practice a weak topic specifically.
    """
    # Use authenticated user's username if available, otherwise use provided student_id
    student_id = current_user.username if current_user else request.student_id
    if not student_id:
        raise HTTPException(status_code=400, detail="Student ID required. Please login or provide student_id.")
    
    # For practice quizzes, get all questions for this topic ONLY
    # This ensures practice quizzes always have questions from a single topic
    # Exclude octopus sample question
    all_topic_questions = [
        q for q in db.query(Question).filter(
            Question.grade_level == request.grade_level,
            Question.topic == request.topic
        ).all()
        if 'octopus' not in q.prompt.lower()
    ]
    
    # Verify we're only getting questions from the requested topic
    # This is a safeguard to ensure practice quizzes are always single-topic
    for q in all_topic_questions:
        if q.topic != request.topic:
            raise HTTPException(
                status_code=500,
                detail=f"Data integrity error: Question {q.id} has topic '{q.topic}' but expected '{request.topic}'"
            )
    
    if len(all_topic_questions) == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No questions available for topic '{request.topic}' at grade level {request.grade_level}. Please seed the question bank first."
        )
    
    # Get recent question IDs to try to avoid repeats (but allow if needed)
    recent_question_ids = get_recent_question_ids(db, student_id, request.grade_level, num_quizzes=1)
    
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
    
    # Final verification: Ensure all selected questions are from the requested topic
    # This guarantees practice quizzes are always single-topic
    for q in selected_questions:
        if q.topic != request.topic:
            raise HTTPException(
                status_code=500,
                detail=f"Data integrity error: Selected question {q.id} has topic '{q.topic}' but practice quiz requires '{request.topic}'"
            )
    
    # Get next grade-specific quiz number for this student+grade combination
    grade_quiz_number = Quiz.get_next_grade_quiz_number(db, student_id, request.grade_level)
    
    # Create quiz
    quiz = Quiz(
        student_id=student_id,
        grade_level=request.grade_level,
        grade_quiz_number=grade_quiz_number,
        question_ids=unique_question_ids
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    
    # Invalidate cache for this student (new practice quiz created)
    invalidate_student_cache(student_id)
    
    # Return quiz without correct answers
    questions_data = [q.to_dict(include_answer=False) for q in selected_questions]
    
    # Track metrics for practice quiz
    track_quiz_generated(request.grade_level, quiz_type='practice')
    
    return QuizResponse(
        quiz_id=quiz.id,
        grade_quiz_number=quiz.grade_quiz_number,
        student_id=quiz.student_id,
        grade_level=quiz.grade_level,
        questions=questions_data,
        created_at=quiz.created_at.isoformat()
    )


@router.get("/{quiz_id}", response_model=QuizResponse)
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    """Get a quiz by ID (without correct answers)."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Get questions
    unique_question_ids = list(dict.fromkeys(quiz.question_ids))
    questions = db.query(Question).filter(Question.id.in_(unique_question_ids)).all()
    
    if len(questions) != len(unique_question_ids):
        raise HTTPException(status_code=500, detail="Some questions not found")
    
    # Handle duplicates in question_ids
    if len(quiz.question_ids) != len(unique_question_ids):
        question_map = {q.id: q for q in questions}
        questions = [question_map[qid] for qid in quiz.question_ids if qid in question_map]
    
    # Return quiz without correct answers
    questions_data = [q.to_dict(include_answer=False) for q in questions]
    
    return QuizResponse(
        quiz_id=quiz.id,
        grade_quiz_number=quiz.grade_quiz_number,
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
    try:
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
        
        # Invalidate cache for this student (new attempt submitted)
        invalidate_student_cache(quiz.student_id)
        
        # Check mastery status (for this grade level)
        mastery_status = check_mastery_status(db, quiz.student_id, quiz.grade_level, mastery_threshold=0.80)
        
        # Generate next quiz recommendation
        next_quiz_recommendation = None
        next_grade_level = None
        
        if mastery_status["mastered"]:
            # If mastered, check if there's a next grade level available
            # Grade 3 -> Grade 5, Grade 5 -> None (highest level)
            if quiz.grade_level == 3:
                next_grade_level = 5
            elif quiz.grade_level == 5:
                next_grade_level = None  # Already at highest level
        else:
            # Not mastered yet, recommend retake at same grade level
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
            next_quiz_recommendation=next_quiz_recommendation,
            next_grade_level=next_grade_level  # Available next grade level if mastered
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_msg = f"Error submitting quiz: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error submitting quiz: {str(e)}")


@router.get("/attempt/{attempt_id}", response_model=dict)
def get_attempt_results(
    attempt_id: int,
    db: Session = Depends(get_db)
):
    """Get attempt results by attempt ID."""
    attempt = db.query(Attempt).filter(Attempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    
    # Get quiz
    quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found for this attempt")
    
    # Get questions to determine quiz type (consistent with history endpoint)
    if not quiz.question_ids:
        is_practice_quiz = False
        practice_topic = None
    else:
        unique_question_ids = list(dict.fromkeys(quiz.question_ids))
        num_questions = len(unique_question_ids)
        questions = db.query(Question).filter(Question.id.in_(unique_question_ids)).all()
        
        # Determine quiz type based on:
        # 1. Actual question topics (if all same topic, it's practice)
        # 2. Number of questions (6 or fewer = practice quiz)
        unique_topics = set(q.topic for q in questions) if questions else set()
        
        if len(unique_topics) == 1:
            # All questions from same topic = practice quiz
            is_practice_quiz = True
            practice_topic = list(unique_topics)[0]
        elif num_questions <= 6:
            # Quizzes with 6 or fewer questions should be practice quizzes
            is_practice_quiz = True
            # Use the most common topic as practice topic
            topic_counts = {}
            for q in questions:
                topic_counts[q.topic] = topic_counts.get(q.topic, 0) + 1
            practice_topic = max(topic_counts.items(), key=lambda x: x[1])[0] if topic_counts else None
        else:
            is_practice_quiz = False
            practice_topic = None
    
    # Check mastery status
    from app.logic.adaptive import check_mastery_status
    mastery_status = check_mastery_status(db, quiz.student_id, quiz.grade_level, mastery_threshold=0.80)
    
    # Generate next quiz recommendation
    next_quiz_recommendation = None
    next_grade_level = None
    
    if mastery_status["mastered"]:
        if quiz.grade_level == 3:
            next_grade_level = 5
        elif quiz.grade_level == 5:
            next_grade_level = None
    else:
        next_quiz_recommendation = {
            "student_id": quiz.student_id,
            "grade_level": quiz.grade_level,
            "topics": list(unique_topics),
            "num_questions": 10,
            "focus": "weak_topics" if attempt.weak_topics else "review",
            "weak_topics": attempt.weak_topics
        }
    
    return {
        "attempt_id": attempt.id,
        "quiz_id": quiz.id,
        "student_id": quiz.student_id,
        "grade_level": quiz.grade_level,
        "score_total": attempt.score_total,
        "topic_metrics": attempt.topic_metrics,
        "weak_topics": attempt.weak_topics,
        "passed": attempt.passed,
        "mastery_status": mastery_status,
        "next_quiz_recommendation": next_quiz_recommendation,
        "next_grade_level": next_grade_level,
        "is_practice_quiz": is_practice_quiz,
        "practice_topic": practice_topic
    }

