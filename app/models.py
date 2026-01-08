"""
Database models for GradeMaster adaptive remediation quiz system.
"""
import json
from datetime import datetime
from typing import Optional, Dict, List, Any
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, TypeDecorator, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class JSONType(TypeDecorator):
    """
    Custom JSON type for Oracle Database using Text/CLOB.
    Handles serialization/deserialization automatically.
    Works with Oracle by storing JSON as text.
    """
    impl = Text
    cache_ok = True

    def process_bind_param(self, value: Any, dialect) -> Optional[str]:
        """Convert Python object to JSON string for database storage."""
        if value is None:
            return None
        return json.dumps(value)

    def process_result_value(self, value: Optional[str], dialect) -> Any:
        """Convert JSON string from database to Python object."""
        if value is None:
            return None
        return json.loads(value)


class Question(Base):
    """Question model representing a quiz question."""
    __tablename__ = "questions"

    id = Column(Integer, Sequence('questions_id_seq'), primary_key=True)  # Oracle sequence for auto-increment
    grade_level = Column(Integer, nullable=False, index=True)
    topic = Column(String(100), nullable=False, index=True)
    difficulty = Column(Integer, nullable=False)  # 1-5
    weight = Column(Float, nullable=False)
    prompt = Column(Text, nullable=False)
    choices = Column(JSONType, nullable=True)  # Optional list of choices
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)

    def to_dict(self, include_answer: bool = False) -> dict:
        """Convert question to dictionary, optionally excluding correct answer."""
        result = {
            "id": self.id,
            "grade_level": self.grade_level,
            "topic": self.topic,
            "difficulty": self.difficulty,
            "weight": self.weight,
            "prompt": self.prompt,
            "choices": self.choices,
            "explanation": self.explanation if include_answer else None,
        }
        if include_answer:
            result["correct_answer"] = self.correct_answer
        return result


class Quiz(Base):
    """Quiz model representing a generated quiz."""
    __tablename__ = "quizzes"

    id = Column(Integer, Sequence('quizzes_id_seq'), primary_key=True)  # Oracle sequence for auto-increment
    student_id = Column(String(100), nullable=False, index=True)
    grade_level = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    question_ids = Column(JSONType, nullable=False)  # List of question IDs

    attempts = relationship("Attempt", back_populates="quiz", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        """Convert quiz to dictionary."""
        return {
            "id": self.id,
            "student_id": self.student_id,
            "grade_level": self.grade_level,
            "created_at": self.created_at.isoformat(),
            "question_ids": self.question_ids,
        }


class Attempt(Base):
    """Attempt model representing a student's quiz submission."""
    __tablename__ = "attempts"

    id = Column(Integer, Sequence('attempts_id_seq'), primary_key=True)  # Oracle sequence for auto-increment
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False, index=True)
    student_id = Column(String(100), nullable=False, index=True)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    answers = Column(JSONType, nullable=False)  # Dict: {question_id: answer}
    score_total = Column(Float, nullable=False)
    topic_metrics = Column(JSONType, nullable=False)  # Dict: {topic: {correct, total, weighted_score}}
    weak_topics = Column(JSONType, nullable=False)  # List of topics with score < 0.80
    passed = Column(Boolean, nullable=False)  # True if all topics mastered

    quiz = relationship("Quiz", back_populates="attempts")

    def to_dict(self) -> dict:
        """Convert attempt to dictionary."""
        return {
            "id": self.id,
            "quiz_id": self.quiz_id,
            "student_id": self.student_id,
            "submitted_at": self.submitted_at.isoformat(),
            "answers": self.answers,
            "score_total": self.score_total,
            "topic_metrics": self.topic_metrics,
            "weak_topics": self.weak_topics,
            "passed": self.passed,
        }

