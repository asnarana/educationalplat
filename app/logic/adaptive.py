"""
Adaptive quiz generation logic.
Selects questions based on weak topics and avoids recent repeats.
"""
import random
import time
from typing import List, Set, Dict
from sqlalchemy.orm import Session
from app.models import Question, Quiz, Attempt
from app.cache import get_from_cache, set_cache, get_cache_key


def get_recent_question_ids(
    db: Session,
    student_id: str,
    grade_level: int,
    num_quizzes: int = 2
) -> Set[int]:
    """
    Get question IDs from the last N quizzes for a student at a specific grade level.
    
    Uses Redis caching to improve performance during quiz generation.
    
    Args:
        db: Database session
        student_id: Student identifier
        grade_level: Grade level to filter quizzes by
        num_quizzes: Number of recent quizzes to check (default 2)
        
    Returns:
        Set of question IDs that should be avoided
    """
    # Try to get from cache first
    cache_key = f"recent_questions:{student_id}:grade:{grade_level}:num:{num_quizzes}"
    cached_result = get_from_cache(cache_key)
    if cached_result is not None:
        return set(cached_result)  # Convert list back to set
    
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
    
    # Cache the result (1 minute TTL - short because this changes when new quizzes are created)
    set_cache(cache_key, list(recent_question_ids), ttl=60)
    
    return recent_question_ids


def select_questions_for_quiz(
    db: Session,
    grade_level: int,
    topics: List[str],
    num_questions: int,
    weak_topics: List[str] = None,
    exclude_question_ids: Set[int] = None,
    exclude_prompt_keywords: List[str] = None
) -> List[Question]:
    """
    Select questions for a quiz based on adaptive rules.
    
    Rules:
    - If weak_topics provided: 70% from weak_topics, 30% from remaining topics
    - Ensure topic coverage
    - Avoid questions in exclude_question_ids
    - CRITICAL: No duplicate questions within the same quiz
    - CRITICAL: Questions are randomized for each call
    
    Args:
        db: Database session
        grade_level: Grade level for questions
        topics: List of available topics
        num_questions: Total number of questions needed
        weak_topics: List of weak topics (if None, distribute evenly)
        exclude_question_ids: Set of question IDs to exclude
        
    Returns:
        List of selected Question objects (no duplicates, randomized order)
    """
    # CRITICAL: Seed random number generator with current time to ensure different questions each time
    random.seed(int(time.time() * 1000))
    
    if exclude_question_ids is None:
        exclude_question_ids = set()
    
    if weak_topics is None:
        weak_topics = []
    
    if exclude_prompt_keywords is None:
        exclude_prompt_keywords = []
    
    # Helper function to filter questions by keywords
    def filter_by_keywords(questions):
        if not exclude_prompt_keywords:
            return questions
        return [
            q for q in questions 
            if not any(keyword.lower() in q.prompt.lower() for keyword in exclude_prompt_keywords)
        ]
    
    # Special case: If ALL topics are weak, distribute evenly across all topics
    # This prevents uneven distribution when student struggles with everything
    if weak_topics and set(weak_topics) == set(topics):
        # All topics are weak - distribute evenly with strict equal distribution
        questions_per_topic = num_questions // len(topics)
        remainder = num_questions % len(topics)
        
        selected_questions: List[Question] = []
        selected_ids: Set[int] = set()
        
        # Track how many questions each topic should get
        topic_targets = {}
        for i, topic in enumerate(topics):
            # First 'remainder' topics get one extra question
            topic_targets[topic] = questions_per_topic + (1 if i < remainder else 0)
        
        # Track how many questions each topic has actually received
        topic_counts = {topic: 0 for topic in topics}
        
        # Fill each topic to its target, ensuring equal distribution
        for topic in topics:
            target = topic_targets[topic]
            while topic_counts[topic] < target and len(selected_questions) < num_questions:
                topic_questions = (
                    db.query(Question)
                    .filter(
                        Question.grade_level == grade_level,
                        Question.topic == topic,
                        ~Question.id.in_(exclude_question_ids)
                    )
                    .all()
                )
                
                # Filter out already selected, exclude keywords, and randomize
                available = filter_by_keywords([
                    q for q in topic_questions if q.id not in selected_ids
                ])
                random.shuffle(available)  # Randomize to ensure different questions each time
                
                # Select one question from this topic
                found = False
                for q in available:
                    if q.id not in selected_ids and topic_counts[topic] < target:
                        selected_questions.append(q)
                        selected_ids.add(q.id)
                        topic_counts[topic] += 1
                        found = True
                        break
                
                # If no more questions available for this topic, break
                if not found:
                    break
        
        # If we still haven't filled all slots, redistribute remaining slots evenly
        remaining_needed = num_questions - len(selected_questions)
        if remaining_needed > 0:
            # Find topics that haven't reached their target yet
            under_target_topics = [
                topic for topic in topics 
                if topic_counts[topic] < topic_targets[topic]
            ]
            
            # If all topics are at target but we still need more, distribute evenly
            if not under_target_topics:
                under_target_topics = topics
            
            # Distribute remaining questions evenly among under-target topics
            for i in range(remaining_needed):
                if not under_target_topics:
                    break
                
                # Cycle through topics to distribute evenly
                topic = under_target_topics[i % len(under_target_topics)]
                
                topic_questions = (
                    db.query(Question)
                    .filter(
                        Question.grade_level == grade_level,
                        Question.topic == topic,
                        ~Question.id.in_(exclude_question_ids)
                    )
                    .all()
                )
                
                available = filter_by_keywords([
                    q for q in topic_questions if q.id not in selected_ids
                ])
                random.shuffle(available)
                
                if available:
                    selected_questions.append(available[0])
                    selected_ids.add(available[0].id)
                    topic_counts[topic] += 1
        
        # CRITICAL: Final shuffle to randomize order of selected questions
        # This ensures questions appear in different order each time
        random.shuffle(selected_questions)
        
        # Final check: Ensure no duplicates (shouldn't happen, but double-check)
        seen_ids = set()
        unique_questions = []
        for q in selected_questions:
            if q.id not in seen_ids:
                unique_questions.append(q)
                seen_ids.add(q.id)
        
        return unique_questions[:num_questions]
    
    # Normal case: Some topics are weak, some are not - use 70/30 split
    # OR: No weak topics - distribute evenly across all topics
    # Calculate distribution
    num_weak = int(num_questions * 0.7) if weak_topics else 0
    num_review = num_questions - num_weak
    
    selected_questions: List[Question] = []
    selected_ids: Set[int] = set()
    
    # Special case: If no weak topics, ensure STRICT equal distribution across all topics
    if not weak_topics:
        # Calculate strict distribution: questions_per_topic + remainder distributed to first topics
        questions_per_topic = num_questions // len(topics)
        remainder = num_questions % len(topics)
        
        # Track how many questions each topic should get
        topic_targets = {}
        for i, topic in enumerate(topics):
            # First 'remainder' topics get one extra question
            topic_targets[topic] = questions_per_topic + (1 if i < remainder else 0)
        
        # Track how many questions each topic has actually received
        topic_counts = {topic: 0 for topic in topics}
        
        # First pass: Fill each topic to its target, ensuring equal distribution
        for topic in topics:
            target = topic_targets[topic]
            while topic_counts[topic] < target and len(selected_questions) < num_questions:
                topic_questions = (
                    db.query(Question)
                    .filter(
                        Question.grade_level == grade_level,
                        Question.topic == topic,
                        ~Question.id.in_(exclude_question_ids)
                    )
                    .all()
                )
                
                # Filter out already selected, exclude keywords, and randomize
                available = filter_by_keywords([
                    q for q in topic_questions if q.id not in selected_ids
                ])
                random.shuffle(available)  # Randomize BEFORE selecting
                
                # Select one question from this topic
                found = False
                for q in available:
                    if q.id not in selected_ids and topic_counts[topic] < target:
                        selected_questions.append(q)
                        selected_ids.add(q.id)
                        topic_counts[topic] += 1
                        found = True
                        break
                
                # If no more questions available for this topic, break
                if not found:
                    break
        
        # If we still haven't filled all slots, redistribute remaining slots evenly
        # This handles cases where some topics don't have enough questions
        remaining_needed = num_questions - len(selected_questions)
        if remaining_needed > 0:
            # Find topics that haven't reached their target yet
            under_target_topics = [
                topic for topic in topics 
                if topic_counts[topic] < topic_targets[topic]
            ]
            
            # If all topics are at target but we still need more, distribute evenly
            if not under_target_topics:
                under_target_topics = topics
            
            # Distribute remaining questions evenly among under-target topics
            for i in range(remaining_needed):
                if not under_target_topics:
                    break
                
                # Cycle through topics to distribute evenly
                topic = under_target_topics[i % len(under_target_topics)]
                
                topic_questions = (
                    db.query(Question)
                    .filter(
                        Question.grade_level == grade_level,
                        Question.topic == topic,
                        ~Question.id.in_(exclude_question_ids)
                    )
                    .all()
                )
                
                available = filter_by_keywords([
                    q for q in topic_questions if q.id not in selected_ids
                ])
                random.shuffle(available)
                
                if available:
                    selected_questions.append(available[0])
                    selected_ids.add(available[0].id)
                    topic_counts[topic] += 1
        
        # Final shuffle to randomize order
        random.shuffle(selected_questions)
        
        # Final check: Ensure no duplicates
        seen_ids = set()
        unique_questions = []
        for q in selected_questions:
            if q.id not in seen_ids:
                unique_questions.append(q)
                seen_ids.add(q.id)
        
        return unique_questions[:num_questions]
    
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
        
        available_weak = filter_by_keywords([
            q for q in weak_query.all()
            if q.id not in selected_ids
        ])
        random.shuffle(available_weak)  # Randomize to ensure different questions each time
        
        # Prioritize weak topics: try to get all num_weak questions from weak topics
        # If single weak topic, get all from it; if multiple, distribute evenly but ensure we get all num_weak
        if len(weak_topics) == 1:
            # Single weak topic: get all num_weak questions from it
            topic_questions = [q for q in available_weak if q.topic == weak_topics[0]]
            random.shuffle(topic_questions)  # Randomize
            for q in topic_questions[:num_weak]:
                if len(selected_questions) < num_weak:
                    selected_questions.append(q)
                    selected_ids.add(q.id)
        else:
            # Multiple weak topics: distribute evenly among weak topics
            # Calculate how many per topic (with remainder distributed)
            questions_per_weak_topic = num_weak // len(weak_topics)
            remainder_weak = num_weak % len(weak_topics)
            
            # First pass: distribute base amount evenly
            for i, topic in enumerate(weak_topics):
                # Add one extra question to first 'remainder_weak' topics if needed
                needed = questions_per_weak_topic + (1 if i < remainder_weak else 0)
                
                topic_questions = [q for q in available_weak if q.topic == topic]
                random.shuffle(topic_questions)  # Randomize
                for q in topic_questions[:needed]:
                    if len(selected_questions) < num_weak:
                        selected_questions.append(q)
                        selected_ids.add(q.id)
            
            # Second pass: if we didn't get all num_weak questions, fill from any weak topic
            if len(selected_questions) < num_weak:
                random.shuffle(available_weak)  # Randomize before filling
                for q in available_weak:
                    if q.id not in selected_ids and len(selected_questions) < num_weak:
                        selected_questions.append(q)
                        selected_ids.add(q.id)
    
    # Step 2: Fill remaining slots from review topics (non-weak topics)
    # BUT ONLY if we've already filled all num_weak slots from weak topics
    # If we haven't filled all weak topic slots, we'll fill them in Step 3 first
    # This ensures we always prioritize weak topics before filling review slots
    # CRITICAL: Check weak topic count specifically, not total count
    weak_topic_count_step2 = sum(1 for q in selected_questions if q.topic in weak_topics)
    if num_review > 0 and weak_topic_count_step2 >= num_weak:
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
        
        available_review = filter_by_keywords([
            q for q in review_query.all()
            if q.id not in selected_ids
        ])
        random.shuffle(available_review)  # Randomize to ensure different questions each time
        
        # Distribute across review topics
        questions_per_review_topic = max(1, num_review // len(review_topics)) if review_topics else 0
        for topic in review_topics:
            topic_questions = [q for q in available_review if q.topic == topic]
            random.shuffle(topic_questions)  # Randomize
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
            # First try with exclusions
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
            
            # If we still haven't reached num_weak, allow repeats from weak topics (remove exclusions)
            if len(selected_questions) < num_weak:
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
                random.shuffle(available_weak_no_exclusions)  # Randomize
                # Fill up to num_weak from weak topics (allowing repeats if needed)
                for q in available_weak_no_exclusions:
                    if len(selected_questions) < num_weak:
                        selected_questions.append(q)
                        selected_ids.add(q.id)
                
                # Final fallback: if still not enough, allow actual repeats (same question ID)
                if len(selected_questions) < num_weak:
                    all_weak_questions = (
                        db.query(Question)
                        .filter(
                            Question.grade_level == grade_level,
                            Question.topic.in_(weak_topics)
                        )
                        .all()
                    )
                    random.shuffle(all_weak_questions)  # Randomize
                    for q in all_weak_questions:
                        if len(selected_questions) < num_weak:
                            selected_questions.append(q)
                            # Don't add to selected_ids to allow repeats
        
        # CRITICAL: Only fill review slots (from non-weak topics) if we've filled ALL weak topic slots
        # This ensures we get the full 70% from weak topics before any review questions
        # Check: Have we reached num_weak from weak topics specifically? If not, don't fill review slots yet
        weak_topic_count = sum(1 for q in selected_questions if q.topic in weak_topics)
        if weak_topic_count >= num_weak and len(selected_questions) < num_questions:
            # Fill remaining slots from review topics (non-weak topics) - this is the 30%
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
            available_review = filter_by_keywords([
                q for q in review_query.all()
                if q.id not in selected_ids
            ])
            random.shuffle(available_review)  # Randomize
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
            
            # Prioritize weak topics even in this fallback (filter by keywords)
            weak_questions = filter_by_keywords([
                q for q in all_available if q.topic in weak_topics and q.id not in selected_ids
            ])
            other_questions = filter_by_keywords([
                q for q in all_available if q.topic not in weak_topics and q.id not in selected_ids
            ])
            
            # Randomize both lists
            random.shuffle(weak_questions)
            random.shuffle(other_questions)
            
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
            available_weak_no_exclusions = filter_by_keywords([
                q for q in weak_query_no_exclusions.all()
                if q.id not in selected_ids
            ])
            random.shuffle(available_weak_no_exclusions)  # Randomize
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
            
            # Randomize before selecting
            available_list = [q for q in all_available_no_exclusions if q.id not in selected_ids]
            random.shuffle(available_list)
            
            for q in available_list:
                if len(selected_questions) < num_questions:
                    selected_questions.append(q)
                    selected_ids.add(q.id)
    
    # CRITICAL: Final shuffle to randomize order of selected questions
    # This ensures questions appear in different order each time
    random.shuffle(selected_questions)
    
    # Final check: Ensure no duplicates (shouldn't happen, but double-check)
    seen_ids = set()
    unique_questions = []
    for q in selected_questions:
        if q.id not in seen_ids:
            unique_questions.append(q)
            seen_ids.add(q.id)
    
    return unique_questions[:num_questions]


def check_mastery_status(
    db: Session,
    student_id: str,
    grade_level: int,
    mastery_threshold: float = 0.80
) -> Dict[str, any]:
    """
    Check if student has achieved mastery (2 consecutive attempts with no weak topics) for a specific grade level.
    
    Uses Redis caching to improve performance when checking mastery status frequently.
    
    Args:
        db: Database session
        student_id: Student identifier
        grade_level: Grade level to check mastery for
        mastery_threshold: Mastery threshold (default 0.80)
        
    Returns:
        Dictionary with mastery status and details
    """
    # Try to get from cache first
    cache_key = f"mastery:{student_id}:grade:{grade_level}"
    cached_result = get_from_cache(cache_key)
    if cached_result is not None:
        return cached_result
    
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
    
    result = {
        "mastered": mastered,
        "consecutive_passes": consecutive_passes,
        "required": 2
    }
    
    # Cache the result (2 minutes TTL - shorter than history cache since mastery changes with new attempts)
    set_cache(cache_key, result, ttl=120)
    
    return result

