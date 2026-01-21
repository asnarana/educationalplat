"""
Database models for GradeMaster adaptive remediation quiz system.
"""
import json
from datetime import datetime
from typing import Optional, Dict, List, Any
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Sequence, TypeDecorator
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from passlib.context import CryptContext

Base = declarative_base()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Custom JSON type for Oracle compatibility
# Oracle doesn't have native JSON type, so we use Text and handle serialization
class JSONType(TypeDecorator):
    """JSON type that stores data as Text for Oracle compatibility."""
    impl = Text
    cache_ok = True

    def process_bind_param(self, value: Any, dialect) -> Optional[str]:
        """Convert Python object to JSON string for storage."""
        if value is None:
            return None
        return json.dumps(value)

    def process_result_value(self, value: Optional[str], dialect) -> Optional[Any]:
        """Convert JSON string back to Python object."""
        if value is None:
            return None
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return value


class User(Base):
    """User model for authentication (students and admins)."""
    __tablename__ = "users"

    id = Column(Integer, Sequence('user_id_seq'), server_default=Sequence('user_id_seq').next_value(), primary_key=True)
    username = Column(String(100), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="student")  # "student" or "admin"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def verify_password(self, password: str) -> bool:
        """Verify a password against the stored hash."""
        return pwd_context.verify(password, self.password_hash)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password."""
        # Ensure password is not None and is a string
        if not password:
            raise ValueError("Password cannot be empty")
        if not isinstance(password, str):
            password = str(password)
        # Bcrypt has a 72-byte limit, but this should only affect very long passwords
        # For normal passwords, this won't be an issue
        return pwd_context.hash(password)
    
    def to_dict(self) -> dict:
        """Convert user to dictionary (without password)."""
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
        }


class Question(Base):
    """Question model representing a quiz question."""
    __tablename__ = "questions"

    id = Column(Integer, Sequence('question_id_seq'), server_default=Sequence('question_id_seq').next_value(), primary_key=True)
    grade_level = Column(Integer, nullable=False, index=True)
    topic = Column(String(100), nullable=False, index=True)
    difficulty = Column(Integer, nullable=False)  # 1-5
    weight = Column(Float, nullable=False)
    prompt = Column(Text, nullable=False)
    choices = Column(JSONType, nullable=True)  # Optional list of choices (JSON stored as Text)
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

    id = Column(Integer, Sequence('quiz_id_seq'), server_default=Sequence('quiz_id_seq').next_value(), primary_key=True)
    student_id = Column(String(100), nullable=False, index=True)
    grade_level = Column(Integer, nullable=False, index=True)
    grade_quiz_number = Column(Integer, nullable=True)  # Unique ID within this student+grade combination (starts at 1). Nullable for migration compatibility.
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    question_ids = Column(JSONType, nullable=False)  # List of question IDs (JSON stored as Text)

    attempts = relationship("Attempt", back_populates="quiz", cascade="all, delete-orphan")

    @staticmethod
    def get_next_grade_quiz_number(db_session, student_id: str, grade_level: int) -> int:
        """
        Get the next grade_quiz_number for a student+grade combination.
        This ensures each grade level starts at 1 and increments independently.
        
        Args:
            db_session: Database session
            student_id: Student identifier
            grade_level: Grade level
            
        Returns:
            Next grade_quiz_number (starts at 1 for first quiz in this grade)
        """
        from sqlalchemy import func
        max_number = db_session.query(func.max(Quiz.grade_quiz_number)).filter(
            Quiz.student_id == student_id,
            Quiz.grade_level == grade_level
        ).scalar()
        
        return (max_number or 0) + 1
    
    @staticmethod
    def backfill_grade_quiz_numbers(db_session):
        """
        Backfill grade_quiz_number for existing quizzes that don't have it set.
        This is a migration helper function.
        
        Args:
            db_session: Database session
        """
        # Get all quizzes without grade_quiz_number, ordered by student_id, grade_level, and created_at
        quizzes_to_update = db_session.query(Quiz).filter(
            Quiz.grade_quiz_number.is_(None)
        ).order_by(Quiz.student_id, Quiz.grade_level, Quiz.created_at).all()
        
        if not quizzes_to_update:
            return 0
        
        # Group by student_id and grade_level, then assign sequential numbers
        current_student = None
        current_grade = None
        current_number = 0
        updated_count = 0
        
        for quiz in quizzes_to_update:
            if quiz.student_id != current_student or quiz.grade_level != current_grade:
                # New student+grade combination, reset counter
                current_student = quiz.student_id
                current_grade = quiz.grade_level
                current_number = 1
            else:
                # Same student+grade, increment
                current_number += 1
            
            quiz.grade_quiz_number = current_number
            updated_count += 1
        
        db_session.commit()
        return updated_count

    def to_dict(self, db_session=None) -> dict:
        """
        Convert quiz to dictionary.
        
        Args:
            db_session: Optional database session (needed if grade_quiz_number is None and needs calculation)
        """
        grade_quiz_number = self.grade_quiz_number
        # If grade_quiz_number is None (for old quizzes), calculate it based on position
        if grade_quiz_number is None and db_session is not None:
            # Count how many quizzes exist for this student+grade before this one (by created_at)
            from sqlalchemy import and_
            earlier_count = db_session.query(Quiz).filter(
                and_(
                    Quiz.student_id == self.student_id,
                    Quiz.grade_level == self.grade_level,
                    Quiz.created_at < self.created_at
                )
            ).count()
            grade_quiz_number = earlier_count + 1
        
        return {
            "id": self.id,
            "grade_quiz_number": grade_quiz_number,  # Grade-specific ID
            "student_id": self.student_id,
            "grade_level": self.grade_level,
            "created_at": self.created_at.isoformat(),
            "question_ids": self.question_ids,
        }


class Attempt(Base):
    """Attempt model representing a student's quiz submission."""
    __tablename__ = "attempts"

    id = Column(Integer, Sequence('attempt_id_seq'), server_default=Sequence('attempt_id_seq').next_value(), primary_key=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False, index=True)
    student_id = Column(String(100), nullable=False, index=True)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    answers = Column(JSONType, nullable=False)  # Dict: {question_id: answer} (JSON stored as Text)
    score_total = Column(Float, nullable=False)
    topic_metrics = Column(JSONType, nullable=False)  # Dict: {topic: {correct, total, weighted_score}} (JSON stored as Text)
    weak_topics = Column(JSONType, nullable=False)  # List of topics with score < 0.80 (JSON stored as Text)
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

