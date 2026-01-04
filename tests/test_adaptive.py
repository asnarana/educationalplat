"""
Unit tests for adaptive quiz generation logic.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Question, Quiz
from app.logic.adaptive import (
    get_recent_question_ids,
    select_questions_for_quiz,
    check_mastery_status
)


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def sample_questions(db_session):
    """Create sample questions for testing."""
    questions = [
        Question(
            id=i,
            grade_level=3,
            topic=f"Topic{(i % 5) + 1}",
            difficulty=1 + (i % 3),
            weight=1.0 + (i % 2) * 0.5,
            prompt=f"Question {i}",
            correct_answer=f"Answer{i}"
        )
        for i in range(1, 21)  # 20 questions across 5 topics
    ]
    db_session.add_all(questions)
    db_session.commit()
    return questions


def test_get_recent_question_ids(db_session, sample_questions):
    """Test getting recent question IDs."""
    # Create some quizzes
    quiz1 = Quiz(
        student_id="student1",
        grade_level=3,
        question_ids=[1, 2, 3, 4, 5]
    )
    quiz2 = Quiz(
        student_id="student1",
        grade_level=3,
        question_ids=[6, 7, 8, 9, 10]
    )
    db_session.add_all([quiz1, quiz2])
    db_session.commit()
    
    recent_ids = get_recent_question_ids(db_session, "student1", grade_level=3, num_quizzes=2)
    assert len(recent_ids) == 10
    assert all(i in recent_ids for i in range(1, 11))


def test_select_questions_for_quiz(db_session, sample_questions):
    """Test selecting questions for a quiz."""
    topics = [f"Topic{i}" for i in range(1, 6)]
    weak_topics = ["Topic1", "Topic2"]
    
    selected = select_questions_for_quiz(
        db=db_session,
        grade_level=3,
        topics=topics,
        num_questions=10,
        weak_topics=weak_topics,
        exclude_question_ids=set()
    )
    
    assert len(selected) == 10
    
    # Check that we have questions from weak topics (70%)
    weak_topic_questions = [q for q in selected if q.topic in weak_topics]
    assert len(weak_topic_questions) >= 6  # At least 70%


def test_select_questions_excludes_recent(db_session, sample_questions):
    """Test that selected questions exclude recent ones."""
    topics = [f"Topic{i}" for i in range(1, 6)]
    exclude_ids = {1, 2, 3, 4, 5}
    
    selected = select_questions_for_quiz(
        db=db_session,
        grade_level=3,
        topics=topics,
        num_questions=10,
        weak_topics=None,
        exclude_question_ids=exclude_ids
    )
    
    selected_ids = {q.id for q in selected}
    assert not selected_ids.intersection(exclude_ids)


def test_check_mastery_status(db_session):
    """Test checking mastery status."""
    from app.models import Attempt
    
    # Create quizzes first (attempts need quiz_id to exist)
    quiz1 = Quiz(
        student_id="student1",
        grade_level=3,
        question_ids=[1, 2, 3]
    )
    quiz2 = Quiz(
        student_id="student1",
        grade_level=3,
        question_ids=[4, 5, 6]
    )
    db_session.add_all([quiz1, quiz2])
    db_session.commit()
    
    # Create attempts with no weak topics (mastered)
    attempt1 = Attempt(
        quiz_id=quiz1.id,
        student_id="student1",
        answers={},
        score_total=0.9,
        topic_metrics={},
        weak_topics=[],
        passed=True
    )
    attempt2 = Attempt(
        quiz_id=quiz2.id,
        student_id="student1",
        answers={},
        score_total=0.95,
        topic_metrics={},
        weak_topics=[],
        passed=True
    )
    db_session.add_all([attempt1, attempt2])
    db_session.commit()
    
    status = check_mastery_status(db_session, "student1", grade_level=3)
    assert status["mastered"] is True
    assert status["consecutive_passes"] == 2

