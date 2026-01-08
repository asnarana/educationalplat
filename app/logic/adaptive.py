"""
Adaptive quiz generation logic.
Selects questions based on weak topics and avoids recent repeats.
Uses Redis caching for performance optimization.
"""
import random
from typing import List, Set, Dict
from sqlalchemy.orm import Session
from app.models import Question, Quiz, Attempt
from app.redis_client import (
    cache_get, cache_set, cache_delete, CACHE_KEYS, is_redis_available
)


def get_recent_question_ids(
    db: Session,
    student_id: str,
    grade_level: int,
    num_quizzes: int = 2
) -> Set[int]:
    """
    Get question IDs from the last N quizzes for a student at a specific grade level.
    Uses Redis cache for faster retrieval.
    
    Args:
        db: Database session
        student_id: Student identifier
        grade_level: Grade level to filter quizzes by
        num_quizzes: Number of recent quizzes to check (default 2)
        
    Returns:
        Set of question IDs that should be avoided
    """
    # Try to get from Redis cache first
    cache_key = CACHE_KEYS["recent_question_ids"].format(
        student_id=student_id,
        grade_level=grade_level
    )
    
    cached_ids = cache_get(cache_key)
    if cached_ids is not None:
        # Convert list back to set
        return set(cached_ids)
    
    # Cache miss - query database
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
    
    # Cache the result (TTL: 30 minutes)
    cache_set(cache_key, list(recent_question_ids), ttl=1800)
    
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
    
    # IMPORTANT: Distinguish between weak_topics=None (don't use adaptive) vs weak_topics=[] (use adaptive but no weak topics)
    # If weak_topics is None, use 2-per-topic logic. If it's [] (empty list), still use 70/30 logic (which will handle empty case)
    use_adaptive_mode = weak_topics is not None
    
    # Handle non-adaptive mode (weak_topics=None) - always 2 per topic
    if not use_adaptive_mode:
        # Non-adaptive mode: exactly 2 questions per topic
        questions_per_topic = num_questions // len(topics)  # Should be 2 for 10 questions, 5 topics
        
        # Shuffle topics for randomization
        shuffled_topics = topics.copy()
        random.shuffle(shuffled_topics)
        
        selected_questions: List[Question] = []
        selected_ids: Set[int] = set()
        
        # First pass: Try to get questions_per_topic (2) from each topic without repeats
        for topic in shuffled_topics:
            topic_questions = (
                db.query(Question)
                .filter(
                    Question.grade_level == grade_level,
                    Question.topic == topic,
                    ~Question.id.in_(exclude_question_ids)
                )
                .all()
            )
            
            # Shuffle questions for randomization - get different questions each time
            random.shuffle(topic_questions)
            
            # Filter out already selected in this quiz
            available = [q for q in topic_questions if q.id not in selected_ids]
            
            # Get exactly questions_per_topic (2) from this topic (randomized)
            for q in available[:questions_per_topic]:
                if len(selected_questions) < num_questions:
                    selected_questions.append(q)
                    selected_ids.add(q.id)
        
        # Second pass: If any topic didn't get enough questions, fill from all available questions
        # Count how many we have per topic
        topic_counts = {}
        for q in selected_questions:
            topic_counts[q.topic] = topic_counts.get(q.topic, 0) + 1
        
        # Shuffle topics again for randomization
        shuffled_topics_fill = [t for t in shuffled_topics if topic_counts.get(t, 0) < questions_per_topic]
        random.shuffle(shuffled_topics_fill)
        
        # Fill missing questions per topic
        for topic in shuffled_topics_fill:
            current_count = topic_counts.get(topic, 0)
            needed = questions_per_topic - current_count
            
            if needed > 0:
                # Try to get from excluded questions (allow repeats from previous quizzes)
                topic_questions_excluded = (
                    db.query(Question)
                    .filter(
                        Question.grade_level == grade_level,
                        Question.topic == topic,
                        Question.id.in_(exclude_question_ids)
                    )
                    .all()
                )
                
                # Shuffle for randomization
                random.shuffle(topic_questions_excluded)
                
                available_excluded = [q for q in topic_questions_excluded if q.id not in selected_ids]
                for q in available_excluded[:needed]:
                    if len(selected_questions) < num_questions:
                        selected_questions.append(q)
                        selected_ids.add(q.id)
                        needed -= 1
        
        # Third pass: If still not enough, try ALL questions from this topic (even if excluded)
        topic_counts = {}
        for q in selected_questions:
            topic_counts[q.topic] = topic_counts.get(q.topic, 0) + 1
        
        # Shuffle topics for randomization
        topics_needing_more = [t for t in shuffled_topics if topic_counts.get(t, 0) < questions_per_topic]
        random.shuffle(topics_needing_more)
        
        for topic in topics_needing_more:
            current_count = topic_counts.get(topic, 0)
            needed = questions_per_topic - current_count
            
            if needed > 0:
                # Get ALL questions from this topic (excluding those already selected in this quiz)
                all_topic_questions = (
                    db.query(Question)
                    .filter(
                        Question.grade_level == grade_level,
                        Question.topic == topic
                    )
                    .all()
                )
                
                # Shuffle for randomization - different questions each time
                random.shuffle(all_topic_questions)
                
                # Filter to only questions not already in this quiz
                available_unique = [q for q in all_topic_questions if q.id not in selected_ids]
                
                # Add unique questions first (randomized)
                for q in available_unique[:needed]:
                    if len(selected_questions) < num_questions:
                        selected_questions.append(q)
                        selected_ids.add(q.id)
                        needed -= 1
                
                # Final fallback: If we still need more and have run out of unique questions,
                # allow repeats from this topic (same question twice in quiz)
                if needed > 0 and all_topic_questions:
                    # Use randomized questions, but allow same question if necessary
                    for _ in range(needed):
                        if len(selected_questions) < num_questions:
                            # Use shuffled questions (may repeat same question if no other option)
                            selected_questions.append(all_topic_questions[0])
                            # Note: Not adding to selected_ids allows same question ID multiple times
        
        # Final shuffle to randomize the order of questions in the quiz
        random.shuffle(selected_questions)
        return selected_questions[:num_questions]
    
    if weak_topics is None:
        weak_topics = []
    
    # Special case: If ALL topics are weak, ensure exactly 2 questions per topic (same as no weak topics)
    # This ensures consistent behavior: always 2 per topic
    if weak_topics and set(weak_topics) == set(topics):
        # All topics are weak - get exactly 2 per topic (same logic as no weak topics)
        import sys
        print(f"DEBUG: All topics are weak, using 2 per topic logic", file=sys.stderr, flush=True)
        questions_per_topic = num_questions // len(topics)  # Should be 2 for 10 questions, 5 topics
        
        # Shuffle topics for randomization
        shuffled_topics = topics.copy()
        random.shuffle(shuffled_topics)
        
        selected_questions: List[Question] = []
        selected_ids: Set[int] = set()
        
        # First pass: Try to get questions_per_topic (2) from each topic without repeats
        for topic in shuffled_topics:
            topic_questions = (
                db.query(Question)
                .filter(
                    Question.grade_level == grade_level,
                    Question.topic == topic,
                    ~Question.id.in_(exclude_question_ids)
                )
                .all()
            )
            
            # Shuffle questions for randomization - get different questions each time
            random.shuffle(topic_questions)
            
            # Filter out already selected in this quiz
            available = [q for q in topic_questions if q.id not in selected_ids]
            
            # Get exactly questions_per_topic (2) from this topic (randomized)
            for q in available[:questions_per_topic]:
                if len(selected_questions) < num_questions:
                    selected_questions.append(q)
                    selected_ids.add(q.id)
        
        # Second pass: If any topic didn't get enough questions, fill from all available questions
        # Count how many we have per topic
        topic_counts = {}
        for q in selected_questions:
            topic_counts[q.topic] = topic_counts.get(q.topic, 0) + 1
        
        # Shuffle topics again for randomization
        shuffled_topics_fill = [t for t in shuffled_topics if topic_counts.get(t, 0) < questions_per_topic]
        random.shuffle(shuffled_topics_fill)
        
        # Fill missing questions per topic
        for topic in shuffled_topics_fill:
            current_count = topic_counts.get(topic, 0)
            needed = questions_per_topic - current_count
            
            if needed > 0:
                # Try to get from excluded questions (allow repeats from previous quizzes)
                topic_questions_excluded = (
                    db.query(Question)
                    .filter(
                        Question.grade_level == grade_level,
                        Question.topic == topic,
                        Question.id.in_(exclude_question_ids)
                    )
                    .all()
                )
                
                # Shuffle for randomization
                random.shuffle(topic_questions_excluded)
                
                available_excluded = [q for q in topic_questions_excluded if q.id not in selected_ids]
                for q in available_excluded[:needed]:
                    if len(selected_questions) < num_questions:
                        selected_questions.append(q)
                        selected_ids.add(q.id)
                        needed -= 1
        
        # Third pass: If still not enough, try ALL questions from this topic (even if excluded)
        topic_counts = {}
        for q in selected_questions:
            topic_counts[q.topic] = topic_counts.get(q.topic, 0) + 1
        
        # Shuffle topics for randomization
        topics_needing_more = [t for t in shuffled_topics if topic_counts.get(t, 0) < questions_per_topic]
        random.shuffle(topics_needing_more)
        
        for topic in topics_needing_more:
            current_count = topic_counts.get(topic, 0)
            needed = questions_per_topic - current_count
            
            if needed > 0:
                # Get ALL questions from this topic (excluding those already selected in this quiz)
                all_topic_questions = (
                    db.query(Question)
                    .filter(
                        Question.grade_level == grade_level,
                        Question.topic == topic
                    )
                    .all()
                )
                
                # Shuffle for randomization - different questions each time
                random.shuffle(all_topic_questions)
                
                # Filter to only questions not already in this quiz
                available_unique = [q for q in all_topic_questions if q.id not in selected_ids]
                
                # Add unique questions first (randomized)
                for q in available_unique[:needed]:
                    if len(selected_questions) < num_questions:
                        selected_questions.append(q)
                        selected_ids.add(q.id)
                        needed -= 1
                
                # Final fallback: If we still need more and have run out of unique questions,
                # allow repeats from this topic (same question twice in quiz)
                if needed > 0 and all_topic_questions:
                    # Use randomized questions, but allow same question if necessary
                    for _ in range(needed):
                        if len(selected_questions) < num_questions:
                            # Use shuffled questions (may repeat same question if no other option)
                            selected_questions.append(all_topic_questions[0])
                            # Note: Not adding to selected_ids allows same question ID multiple times
        
        # Final shuffle to randomize the order of questions in the quiz
        random.shuffle(selected_questions)
        return selected_questions[:num_questions]
    
    # Normal case: In adaptive mode with weak topics - use 70/30 split
    # If not in adaptive mode, already handled above with 2 per topic
    # Calculate distribution for 70/30 split
    # IMPORTANT: Check if weak_topics is truthy (non-empty list) to ensure 70/30 split
    import sys
    print(f"DEBUG: use_adaptive_mode={use_adaptive_mode}, weak_topics={weak_topics}, len(weak_topics)={len(weak_topics) if weak_topics else 0}", file=sys.stderr, flush=True)
    if use_adaptive_mode and weak_topics and len(weak_topics) > 0:
        # In adaptive mode with weak topics: 70/30 split
        print(f"DEBUG: Entering 70/30 split logic with {len(weak_topics)} weak topics: {weak_topics}", file=sys.stderr, flush=True)
        num_weak = int(num_questions * 0.7)
        num_review = num_questions - num_weak
        print(f"DEBUG: 70/30 split - num_weak={num_weak}, num_review={num_review}", file=sys.stderr, flush=True)
        
        # Initialize for 70/30 split logic
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
            
            # Shuffle available questions for randomization
            random.shuffle(available_weak)
            
            # Shuffle weak topics for randomization
            shuffled_weak_topics = weak_topics.copy()
            random.shuffle(shuffled_weak_topics)
            
            # Prioritize weak topics: try to get all num_weak questions from weak topics
            # If single weak topic, get all from it; if multiple, distribute evenly but ensure we get all num_weak
            if len(shuffled_weak_topics) == 1:
                # Single weak topic: get all num_weak questions from it (randomized)
                topic_questions = [q for q in available_weak if q.topic == shuffled_weak_topics[0]]
                # Shuffle again for this specific topic
                random.shuffle(topic_questions)
                for q in topic_questions[:num_weak]:
                    if len(selected_questions) < num_weak:
                        selected_questions.append(q)
                        selected_ids.add(q.id)
            else:
                # Multiple weak topics: distribute evenly among weak topics (randomized)
                # Calculate how many per topic (with remainder distributed)
                questions_per_weak_topic = num_weak // len(shuffled_weak_topics)
                remainder_weak = num_weak % len(shuffled_weak_topics)
                
                # First pass: distribute base amount evenly (with shuffled topics)
                for i, topic in enumerate(shuffled_weak_topics):
                    # Add one extra question to first 'remainder_weak' topics if needed
                    needed = questions_per_weak_topic + (1 if i < remainder_weak else 0)
                    
                    topic_questions = [q for q in available_weak if q.topic == topic]
                    # Shuffle questions for this topic to get different ones each time
                    random.shuffle(topic_questions)
                    for q in topic_questions[:needed]:
                        if len(selected_questions) < num_weak:
                            selected_questions.append(q)
                            selected_ids.add(q.id)
                
                # Second pass: if we didn't get all num_weak questions, fill from any weak topic (shuffled)
                if len(selected_questions) < num_weak:
                    # Shuffle again to get different questions
                    random.shuffle(available_weak)
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
            
            # Shuffle review topics for randomization
            random.shuffle(review_topics)
            
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
            
            # Shuffle available review questions for randomization
            random.shuffle(available_review)
            
            # Distribute across review topics
            questions_per_review_topic = max(1, num_review // len(review_topics)) if review_topics else 0
            for topic in review_topics:
                topic_questions = [q for q in available_review if q.topic == topic]
                # Shuffle questions for this specific topic
                random.shuffle(topic_questions)
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
        
        # Final shuffle to randomize the order of questions in the quiz (for weak topics case too)
        random.shuffle(selected_questions)
        return selected_questions[:num_questions]
    elif use_adaptive_mode and not weak_topics:
        # In adaptive mode but no weak topics yet: use 2 per topic (fallback)
        questions_per_topic = num_questions // len(topics)
        selected_questions: List[Question] = []
        selected_ids: Set[int] = set()
        shuffled_topics = topics.copy()
        random.shuffle(shuffled_topics)
        # Same 2-per-topic logic as non-adaptive mode
        for topic in shuffled_topics:
            topic_questions = (
                db.query(Question)
                .filter(
                    Question.grade_level == grade_level,
                    Question.topic == topic,
                    ~Question.id.in_(exclude_question_ids)
                )
                .all()
            )
            random.shuffle(topic_questions)
            available = [q for q in topic_questions if q.id not in selected_ids]
            for q in available[:questions_per_topic]:
                if len(selected_questions) < num_questions:
                    selected_questions.append(q)
                    selected_ids.add(q.id)
        random.shuffle(selected_questions)
        return selected_questions[:num_questions]
    else:
        # Should not reach here - non-adaptive mode handled above
        return []


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

