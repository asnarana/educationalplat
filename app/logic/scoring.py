"""
Scoring logic for quiz submissions.
Deterministic grading based on answer key matching.
"""
from typing import Dict, List
from app.models import Question


def grade_question(student_answer: str, correct_answer: str) -> int:
    """
    Grade a single question deterministically.
    
    Args:
        student_answer: The answer provided by the student
        correct_answer: The correct answer from the question
        
    Returns:
        1 if correct, 0 if incorrect
    """
    # Normalize answers for comparison (strip whitespace, case-insensitive)
    student_normalized = str(student_answer).strip().lower()
    correct_normalized = str(correct_answer).strip().lower()
    
    return 1 if student_normalized == correct_normalized else 0


def compute_topic_metrics(
    questions: List[Question],
    answers: Dict[int, str]
) -> Dict[str, Dict[str, float]]:
    """
    Compute weighted scores per topic.
    
    Args:
        questions: List of Question objects
        answers: Dictionary mapping question_id to student answer
        
    Returns:
        Dictionary mapping topic to metrics:
        {
            topic: {
                "correct": int,  # Number of correct answers
                "total": int,     # Total number of questions
                "weighted_score": float  # Sum(weight * correct) / Sum(weight)
            }
        }
    """
    topic_data: Dict[str, Dict[str, float]] = {}
    
    for question in questions:
        topic = question.topic
        if topic not in topic_data:
            topic_data[topic] = {
                "correct": 0,
                "total": 0,
                "weighted_sum": 0.0,
                "total_weight": 0.0
            }
        
        student_answer = answers.get(question.id, "")
        is_correct = grade_question(student_answer, question.correct_answer)
        
        topic_data[topic]["correct"] += is_correct
        topic_data[topic]["total"] += 1
        topic_data[topic]["weighted_sum"] += question.weight * is_correct
        topic_data[topic]["total_weight"] += question.weight
    
    # Calculate weighted scores
    topic_metrics: Dict[str, Dict[str, float]] = {}
    for topic, data in topic_data.items():
        weighted_score = (
            data["weighted_sum"] / data["total_weight"]
            if data["total_weight"] > 0
            else 0.0
        )
        topic_metrics[topic] = {
            "correct": int(data["correct"]),
            "total": int(data["total"]),
            "weighted_score": round(weighted_score, 4)
        }
    
    return topic_metrics


def compute_overall_score(
    questions: List[Question],
    answers: Dict[int, str]
) -> float:
    """
    Compute overall weighted score for the quiz.
    
    Args:
        questions: List of Question objects
        answers: Dictionary mapping question_id to student answer
        
    Returns:
        Overall weighted score (0.0 to 1.0)
    """
    total_weighted_sum = 0.0
    total_weight = 0.0
    
    for question in questions:
        student_answer = answers.get(question.id, "")
        is_correct = grade_question(student_answer, question.correct_answer)
        total_weighted_sum += question.weight * is_correct
        total_weight += question.weight
    
    if total_weight == 0:
        return 0.0
    
    return round(total_weighted_sum / total_weight, 4)


def identify_weak_topics(
    topic_metrics: Dict[str, Dict[str, float]],
    mastery_threshold: float = 0.80
) -> List[str]:
    """
    Identify topics with weighted_score below mastery threshold.
    
    Args:
        topic_metrics: Dictionary of topic metrics from compute_topic_metrics
        mastery_threshold: Minimum score to be considered mastered (default 0.80)
        
    Returns:
        List of topic names with weighted_score < mastery_threshold
    """
    weak_topics = []
    for topic, metrics in topic_metrics.items():
        if metrics["weighted_score"] < mastery_threshold:
            weak_topics.append(topic)
    return weak_topics

