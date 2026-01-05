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
    grade_level: int,
    num_quizzes: int = 2
) -> Set[int]:
    """
    Get question IDs from the last N quizzes for a student at a specific grade level.
    
    Args:
        db: Database session
        student_id: Student identifier
        grade_level: Grade level to filter quizzes by
        num_quizzes: Number of recent quizzes to check (default 2)
        
    Returns:
        Set of question IDs that should be avoided
    """
    recent_quizzes = (
        db.query(Quiz)
        .filter(
            Quiz.student_id == student_id,
            Quiz.grade_level == grade_level
        )
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
    
    # Step 1: Select questions from weak topics (70% focus)
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
        
        # Prioritize weak topics: try to get all num_weak questions from weak topics
        # If single weak topic, get all from it; if multiple, distribute evenly but ensure we get all num_weak
        if len(weak_topics) == 1:
            # Single weak topic: get all num_weak questions from it
            topic_questions = [q for q in available_weak if q.topic == weak_topics[0]]
            for q in topic_questions[:num_weak]:
                if len(selected_questions) < num_weak:
                    selected_questions.append(q)
                    selected_ids.add(q.id)
        else:
            # Multiple weak topics: distribute evenly, but ensure we get ALL num_weak questions
            # First pass: distribute evenly
            questions_per_weak_topic = max(1, num_weak // len(weak_topics))
            for topic in weak_topics:
                topic_questions = [q for q in available_weak if q.topic == topic]
                needed = min(questions_per_weak_topic, len(topic_questions))
                for q in topic_questions[:needed]:
                    if len(selected_questions) < num_weak:
                        selected_questions.append(q)
                        selected_ids.add(q.id)
            
            # Second pass: if we didn't get all num_weak questions, fill from any weak topic
            if len(selected_questions) < num_weak:
                for q in available_weak:
                    if q.id not in selected_ids and len(selected_questions) < num_weak:
                        selected_questions.append(q)
                        selected_ids.add(q.id)
    
    # Step 2: Fill remaining slots from review topics (non-weak topics)
    # BUT ONLY if we've already filled all num_weak slots from weak topics
    # If we haven't filled all weak topic slots, we'll fill them in Step 3 first
    # This ensures we always prioritize weak topics before filling review slots
    if num_review > 0 and len(selected_questions) >= num_weak:
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
    
    # Step 3: If we still need more questions, prioritize weak topics first, then fill from any available topic
    if len(selected_questions) < num_questions:
        remaining_needed = num_questions - len(selected_questions)
        
        # CRITICAL: First, try to fill remaining slots from weak topics (if we didn't get enough)
        # This ensures we always get 70% from weak topics before filling review slots
        if weak_topics and len(selected_questions) < num_weak:
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
            # Fill up to num_weak from weak topics
            for q in available_weak:
                if len(selected_questions) < num_weak:
                    selected_questions.append(q)
                    selected_ids.add(q.id)
        
        # Only fill review slots (from non-weak topics) if we've filled all weak topic slots
        # AND we still need more questions to reach num_questions
        if len(selected_questions) >= num_weak and len(selected_questions) < num_questions:
            # Fill remaining slots from review topics (non-weak topics)
            review_topics = [t for t in topics if t not in weak_topics]
            if not review_topics:
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
            for q in available_review:
                if len(selected_questions) < num_questions:
                    selected_questions.append(q)
                    selected_ids.add(q.id)
        
        # If we still need more and haven't filled weak slots, try any topic (but prioritize weak)
        if len(selected_questions) < num_questions:
            all_available = (
                db.query(Question)
                .filter(
                    Question.grade_level == grade_level,
                    Question.topic.in_(topics),
                    ~Question.id.in_(exclude_question_ids)
                )
                .all()
            )
            
            # Prioritize weak topics even in this fallback
            weak_questions = [q for q in all_available if q.topic in weak_topics and q.id not in selected_ids]
            other_questions = [q for q in all_available if q.topic not in weak_topics and q.id not in selected_ids]
            
            # First fill from weak topics if we haven't reached num_weak
            for q in weak_questions:
                if len(selected_questions) < num_weak:
                    selected_questions.append(q)
                    selected_ids.add(q.id)
            
            # Then fill remaining from any topic
            for q in weak_questions + other_questions:
                if q.id not in selected_ids and len(selected_questions) < num_questions:
                    selected_questions.append(q)
                    selected_ids.add(q.id)
    
    # Step 4: If still not enough and exclusions are preventing us, try without exclusions (prioritize weak topics)
    if len(selected_questions) < num_questions and exclude_question_ids:
        remaining_needed = num_questions - len(selected_questions)
        
        # First, try to get more from weak topics (without exclusions)
        if weak_topics and len(selected_questions) < num_weak:
            weak_query_no_exclusions = (
                db.query(Question)
                .filter(
                    Question.grade_level == grade_level,
                    Question.topic.in_(weak_topics)
                )
            )
            available_weak_no_exclusions = [
                q for q in weak_query_no_exclusions.all()
                if q.id not in selected_ids
            ]
            for q in available_weak_no_exclusions:
                if len(selected_questions) < num_weak:
                    selected_questions.append(q)
                    selected_ids.add(q.id)
        
        # Then fill from any topic (without exclusions)
        if len(selected_questions) < num_questions:
            all_available_no_exclusions = (
                db.query(Question)
                .filter(
                    Question.grade_level == grade_level,
                    Question.topic.in_(topics)
                )
                .all()
            )
            
            for q in all_available_no_exclusions:
                if q.id not in selected_ids and len(selected_questions) < num_questions:
                    selected_questions.append(q)
                    selected_ids.add(q.id)
    
    return selected_questions[:num_questions]


def check_mastery_status(
    db: Session,
    student_id: str,
    grade_level: int,
    mastery_threshold: float = 0.80
) -> Dict[str, any]:
    """
    Check if student has achieved mastery (2 consecutive attempts with no weak topics) for a specific grade level.
    
    Args:
        db: Database session
        student_id: Student identifier
        grade_level: Grade level to check mastery for
        mastery_threshold: Mastery threshold (default 0.80)
        
    Returns:
        Dictionary with mastery status and details
    """
    recent_attempts = (
        db.query(Attempt)
        .join(Quiz, Attempt.quiz_id == Quiz.id)
        .filter(
            Attempt.student_id == student_id,
            Quiz.grade_level == grade_level
        )
        .order_by(Attempt.submitted_at.desc())
        .limit(2)
        .all()
    )
    
    # Count consecutive perfect attempts (no weak topics)
    consecutive_passes = 0
    for attempt in recent_attempts:
        if len(attempt.weak_topics) == 0:
            consecutive_passes += 1
        else:
            # If we hit an attempt with weak topics, break the streak
            break
    
    # Mastery requires 2 consecutive perfect attempts
    mastered = consecutive_passes >= 2
    
    return {
        "mastered": mastered,
        "consecutive_passes": consecutive_passes,
        "required": 2
    }

