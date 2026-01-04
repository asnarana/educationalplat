"""
Adaptive quiz generation logic.
Selects questions based on weak topics and avoids recent repeats.
"""
from typing import List, Set, Dict
from sqlalchemy.orm import Session
from app.models import Question, Quiz, Attempt


def get_recent_question_ids(
    db: Session,
    student_id: str,
    num_quizzes: int = 2
) -> Set[int]:
    """
    Get question IDs from the last N quizzes for a student.
    
    Args:
        db: Database session
        student_id: Student identifier
        num_quizzes: Number of recent quizzes to check (default 2)
        
    Returns:
        Set of question IDs that should be avoided
    """
    recent_quizzes = (
        db.query(Quiz)
        .filter(Quiz.student_id == student_id)
        .order_by(Quiz.created_at.desc())
        .limit(num_quizzes)
        .all()
    )
    
    recent_question_ids = set()
    for quiz in recent_quizzes:
        recent_question_ids.update(quiz.question_ids)
    
    return recent_question_ids


def select_questions_for_quiz(
    db: Session,
    grade_level: int,
    topics: List[str],
    num_questions: int,
    weak_topics: List[str] = None,
    exclude_question_ids: Set[int] = None
) -> List[Question]:
    """
    Select questions for a quiz based on adaptive rules.
    
    Rules:
    - If weak_topics provided: 70% from weak_topics, 30% from remaining topics
    - Ensure topic coverage
    - Avoid questions in exclude_question_ids
    
    Args:
        db: Database session
        grade_level: Grade level for questions
        topics: List of available topics
        num_questions: Total number of questions needed
        weak_topics: List of weak topics (if None, distribute evenly)
        exclude_question_ids: Set of question IDs to exclude
        
    Returns:
        List of selected Question objects
    """
    if exclude_question_ids is None:
        exclude_question_ids = set()
    
    if weak_topics is None:
        weak_topics = []
    
    # Calculate distribution
    num_weak = int(num_questions * 0.7) if weak_topics else 0
    num_review = num_questions - num_weak
    
    selected_questions: List[Question] = []
    selected_ids: Set[int] = set()
    
    # Step 1: Select questions from weak topics
    if weak_topics and num_weak > 0:
        weak_query = (
            db.query(Question)
            .filter(
                Question.grade_level == grade_level,
                Question.topic.in_(weak_topics),
                ~Question.id.in_(exclude_question_ids)
            )
        )
        
        available_weak = [
            q for q in weak_query.all()
            if q.id not in selected_ids
        ]
        
        # Distribute across weak topics
        questions_per_weak_topic = max(1, num_weak // len(weak_topics)) if weak_topics else 0
        for topic in weak_topics:
            topic_questions = [q for q in available_weak if q.topic == topic]
            needed = min(questions_per_weak_topic, len(topic_questions))
            for q in topic_questions[:needed]:
                if len(selected_questions) < num_weak:
                    selected_questions.append(q)
                    selected_ids.add(q.id)
    
    # Step 2: Fill remaining slots from review topics (non-weak topics)
    if num_review > 0:
        review_topics = [t for t in topics if t not in weak_topics]
        
        if not review_topics:
            # If no review topics, use all topics
            review_topics = topics
        
        review_query = (
            db.query(Question)
            .filter(
                Question.grade_level == grade_level,
                Question.topic.in_(review_topics),
                ~Question.id.in_(exclude_question_ids)
            )
        )
        
        available_review = [
            q for q in review_query.all()
            if q.id not in selected_ids
        ]
        
        # Distribute across review topics
        questions_per_review_topic = max(1, num_review // len(review_topics)) if review_topics else 0
        for topic in review_topics:
            topic_questions = [q for q in available_review if q.topic == topic]
            needed = min(questions_per_review_topic, len(topic_questions))
            for q in topic_questions[:needed]:
                if len(selected_questions) < num_questions:
                    selected_questions.append(q)
                    selected_ids.add(q.id)
    
    # Step 3: If we still need more questions, fill from any available topic
    if len(selected_questions) < num_questions:
        remaining_needed = num_questions - len(selected_questions)
        all_available = (
            db.query(Question)
            .filter(
                Question.grade_level == grade_level,
                Question.topic.in_(topics),
                ~Question.id.in_(exclude_question_ids)
            )
            .all()
        )
        
        for q in all_available:
            if q.id not in selected_ids and len(selected_questions) < num_questions:
                selected_questions.append(q)
                selected_ids.add(q.id)
    
    return selected_questions[:num_questions]


def check_mastery_status(
    db: Session,
    student_id: str,
    mastery_threshold: float = 0.80
) -> Dict[str, any]:
    """
    Check if student has achieved mastery (2 consecutive attempts with no weak topics).
    
    Args:
        db: Database session
        student_id: Student identifier
        mastery_threshold: Mastery threshold (default 0.80)
        
    Returns:
        Dictionary with mastery status and details
    """
    recent_attempts = (
        db.query(Attempt)
        .filter(Attempt.student_id == student_id)
        .order_by(Attempt.submitted_at.desc())
        .limit(2)
        .all()
    )
    
    if len(recent_attempts) < 2:
        return {
            "mastered": False,
            "consecutive_passes": len(recent_attempts),
            "required": 2
        }
    
    # Check if last 2 attempts have no weak topics
    all_passed = all(
        len(attempt.weak_topics) == 0
        for attempt in recent_attempts[:2]
    )
    
    return {
        "mastered": all_passed,
        "consecutive_passes": 2 if all_passed else 0,
        "required": 2
    }

