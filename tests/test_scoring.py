"""
Unit tests for scoring logic.
"""
import pytest
from app.models import Question
from app.logic.scoring import (
    grade_question,
    compute_topic_metrics,
    compute_overall_score,
    identify_weak_topics
)


def test_grade_question_correct():
    """Test grading a correct answer."""
    assert grade_question("8", "8") == 1
    assert grade_question(" 8 ", "8") == 1  # Whitespace handling
    assert grade_question("Eight", "eight") == 1  # Case insensitive


def test_grade_question_incorrect():
    """Test grading an incorrect answer."""
    assert grade_question("7", "8") == 0
    assert grade_question("wrong", "correct") == 0


def test_compute_topic_metrics():
    """Test computing topic-level metrics."""
    questions = [
        Question(
            id=1,
            grade_level=3,
            topic="Addition",
            difficulty=1,
            weight=1.0,
            prompt="Test",
            correct_answer="8"
        ),
        Question(
            id=2,
            grade_level=3,
            topic="Addition",
            difficulty=2,
            weight=1.5,
            prompt="Test",
            correct_answer="27"
        ),
        Question(
            id=3,
            grade_level=3,
            topic="Subtraction",
            difficulty=1,
            weight=1.0,
            prompt="Test",
            correct_answer="6"
        ),
    ]
    
    answers = {
        1: "8",   # Correct
        2: "26",  # Incorrect (should be 27)
        3: "6"    # Correct
    }
    
    metrics = compute_topic_metrics(questions, answers)
    
    assert "Addition" in metrics
    assert "Subtraction" in metrics
    
    # Addition: 1 correct out of 2, weighted: (1.0*1 + 1.5*0) / (1.0 + 1.5) = 1.0 / 2.5 = 0.4
    assert metrics["Addition"]["correct"] == 1
    assert metrics["Addition"]["total"] == 2
    assert abs(metrics["Addition"]["weighted_score"] - 0.4) < 0.001
    
    # Subtraction: 1 correct out of 1, weighted: 1.0*1 / 1.0 = 1.0
    assert metrics["Subtraction"]["correct"] == 1
    assert metrics["Subtraction"]["total"] == 1
    assert abs(metrics["Subtraction"]["weighted_score"] - 1.0) < 0.001


def test_compute_overall_score():
    """Test computing overall weighted score."""
    questions = [
        Question(
            id=1,
            grade_level=3,
            topic="Addition",
            difficulty=1,
            weight=1.0,
            prompt="Test",
            correct_answer="8"
        ),
        Question(
            id=2,
            grade_level=3,
            topic="Addition",
            difficulty=2,
            weight=2.0,
            prompt="Test",
            correct_answer="27"
        ),
    ]
    
    answers = {
        1: "8",   # Correct
        2: "26",  # Incorrect
    }
    
    score = compute_overall_score(questions, answers)
    # (1.0*1 + 2.0*0) / (1.0 + 2.0) = 1.0 / 3.0 = 0.3333...
    assert abs(score - 0.3333) < 0.001


def test_identify_weak_topics():
    """Test identifying weak topics below mastery threshold."""
    topic_metrics = {
        "Addition": {"correct": 1, "total": 2, "weighted_score": 0.5},
        "Subtraction": {"correct": 2, "total": 2, "weighted_score": 0.9},
        "Multiplication": {"correct": 1, "total": 2, "weighted_score": 0.75},
    }
    
    weak_topics = identify_weak_topics(topic_metrics, mastery_threshold=0.80)
    
    assert "Addition" in weak_topics
    assert "Multiplication" in weak_topics
    assert "Subtraction" not in weak_topics

