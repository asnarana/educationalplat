"""
Routes for seeding the question bank.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Question, Base
from app.db import engine
# Import expanded questions from root directory
import importlib.util
import os
# Get the project root directory (two levels up from app/routes/seed.py)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
expand_questions_path = os.path.join(project_root, "expand_questions.py")
spec = importlib.util.spec_from_file_location("expand_questions", expand_questions_path)
expand_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(expand_module)
EXPANDED_QUESTIONS = expand_module.EXPANDED_QUESTIONS

router = APIRouter(prefix="/seed", tags=["seed"])


@router.post("", status_code=201)
def seed_questions(db: Session = Depends(get_db)):
    """
    Seed the database with sample questions for 2 grade levels and 5 topics each.
    
    Creates questions for:
    - Grade 3: Addition, Subtraction, Multiplication, Division, Fractions
    - Grade 5: Algebra, Geometry, Decimals, Percentages, Word Problems
    """
    # Check if questions already exist
    existing_count = db.query(Question).count()
    if existing_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Database already contains {existing_count} questions. Use POST /seed/clear to clear the database first, then seed again."
        )
    
    # Initialize database tables
    Base.metadata.create_all(bind=engine)
    
    # Start with base questions
    questions_data = [
        # Grade 3 Questions
        {
            "grade_level": 3,
            "topic": "Addition",
            "difficulty": 1,
            "weight": 1.0,
            "prompt": "What is 5 + 3?",
            "choices": ["6", "7", "8", "9"],
            "correct_answer": "8",
            "explanation": "Adding 5 and 3 gives 8."
        },
        {
            "grade_level": 3,
            "topic": "Addition",
            "difficulty": 2,
            "weight": 1.5,
            "prompt": "What is 12 + 15?",
            "choices": ["25", "26", "27", "28"],
            "correct_answer": "27",
            "explanation": "Adding 12 and 15 gives 27."
        },
        {
            "grade_level": 3,
            "topic": "Subtraction",
            "difficulty": 1,
            "weight": 1.0,
            "prompt": "What is 10 - 4?",
            "choices": ["5", "6", "7", "8"],
            "correct_answer": "6",
            "explanation": "Subtracting 4 from 10 gives 6."
        },
        {
            "grade_level": 3,
            "topic": "Subtraction",
            "difficulty": 2,
            "weight": 1.5,
            "prompt": "What is 25 - 13?",
            "choices": ["11", "12", "13", "14"],
            "correct_answer": "12",
            "explanation": "Subtracting 13 from 25 gives 12."
        },
        {
            "grade_level": 3,
            "topic": "Multiplication",
            "difficulty": 1,
            "weight": 1.0,
            "prompt": "What is 3 × 4?",
            "choices": ["10", "11", "12", "13"],
            "correct_answer": "12",
            "explanation": "Multiplying 3 by 4 gives 12."
        },
        {
            "grade_level": 3,
            "topic": "Multiplication",
            "difficulty": 2,
            "weight": 1.5,
            "prompt": "What is 6 × 7?",
            "choices": ["40", "41", "42", "43"],
            "correct_answer": "42",
            "explanation": "Multiplying 6 by 7 gives 42."
        },
        {
            "grade_level": 3,
            "topic": "Division",
            "difficulty": 1,
            "weight": 1.0,
            "prompt": "What is 12 ÷ 3?",
            "choices": ["3", "4", "5", "6"],
            "correct_answer": "4",
            "explanation": "Dividing 12 by 3 gives 4."
        },
        {
            "grade_level": 3,
            "topic": "Division",
            "difficulty": 2,
            "weight": 1.5,
            "prompt": "What is 28 ÷ 4?",
            "choices": ["6", "7", "8", "9"],
            "correct_answer": "7",
            "explanation": "Dividing 28 by 4 gives 7."
        },
        {
            "grade_level": 3,
            "topic": "Fractions",
            "difficulty": 1,
            "weight": 1.0,
            "prompt": "What fraction represents half of a whole?",
            "choices": ["1/3", "1/2", "1/4", "2/3"],
            "correct_answer": "1/2",
            "explanation": "Half of a whole is represented by 1/2."
        },
        {
            "grade_level": 3,
            "topic": "Fractions",
            "difficulty": 2,
            "weight": 1.5,
            "prompt": "Which fraction is larger: 1/4 or 1/2?",
            "choices": ["1/4", "1/2", "They are equal", "Cannot compare"],
            "correct_answer": "1/2",
            "explanation": "1/2 is larger than 1/4 because it represents a bigger portion."
        },
        
        # Grade 5 Questions
        {
            "grade_level": 5,
            "topic": "Algebra",
            "difficulty": 1,
            "weight": 1.0,
            "prompt": "If x + 5 = 10, what is x?",
            "choices": ["3", "4", "5", "6"],
            "correct_answer": "5",
            "explanation": "If x + 5 = 10, then x = 10 - 5 = 5."
        },
        {
            "grade_level": 5,
            "topic": "Algebra",
            "difficulty": 2,
            "weight": 1.5,
            "prompt": "If 2x = 14, what is x?",
            "choices": ["6", "7", "8", "9"],
            "correct_answer": "7",
            "explanation": "If 2x = 14, then x = 14 ÷ 2 = 7."
        },
        {
            "grade_level": 5,
            "topic": "Geometry",
            "difficulty": 1,
            "weight": 1.0,
            "prompt": "How many sides does a triangle have?",
            "choices": ["2", "3", "4", "5"],
            "correct_answer": "3",
            "explanation": "A triangle has 3 sides."
        },
        {
            "grade_level": 5,
            "topic": "Geometry",
            "difficulty": 2,
            "weight": 1.5,
            "prompt": "What is the area of a rectangle with length 5 and width 4?",
            "choices": ["18", "19", "20", "21"],
            "correct_answer": "20",
            "explanation": "Area of rectangle = length × width = 5 × 4 = 20."
        },
        {
            "grade_level": 5,
            "topic": "Decimals",
            "difficulty": 1,
            "weight": 1.0,
            "prompt": "What is 0.5 + 0.3?",
            "choices": ["0.7", "0.8", "0.9", "1.0"],
            "correct_answer": "0.8",
            "explanation": "Adding 0.5 and 0.3 gives 0.8."
        },
        {
            "grade_level": 5,
            "topic": "Decimals",
            "difficulty": 2,
            "weight": 1.5,
            "prompt": "What is 2.5 × 4?",
            "choices": ["9", "10", "11", "12"],
            "correct_answer": "10",
            "explanation": "Multiplying 2.5 by 4 gives 10."
        },
        {
            "grade_level": 5,
            "topic": "Percentages",
            "difficulty": 1,
            "weight": 1.0,
            "prompt": "What is 50% of 100?",
            "choices": ["40", "50", "60", "70"],
            "correct_answer": "50",
            "explanation": "50% of 100 is 50."
        },
        {
            "grade_level": 5,
            "topic": "Percentages",
            "difficulty": 2,
            "weight": 1.5,
            "prompt": "What is 25% of 80?",
            "choices": ["18", "20", "22", "24"],
            "correct_answer": "20",
            "explanation": "25% of 80 = 0.25 × 80 = 20."
        },
        {
            "grade_level": 5,
            "topic": "Word Problems",
            "difficulty": 1,
            "weight": 1.0,
            "prompt": "Sarah has 15 apples. She gives away 6. How many does she have left?",
            "choices": ["8", "9", "10", "11"],
            "correct_answer": "9",
            "explanation": "15 - 6 = 9 apples remaining."
        },
        {
            "grade_level": 5,
            "topic": "Word Problems",
            "difficulty": 2,
            "weight": 1.5,
            "prompt": "A box contains 24 cookies. If 6 children share them equally, how many cookies does each child get?",
            "choices": ["3", "4", "5", "6"],
            "correct_answer": "4",
            "explanation": "24 ÷ 6 = 4 cookies per child."
        },
    ]
    
    # Automatically include expanded questions
    questions_data.extend(EXPANDED_QUESTIONS)
    
    questions = [Question(**q_data) for q_data in questions_data]
    db.add_all(questions)
    db.commit()
    
    return {
        "message": f"Successfully seeded {len(questions)} questions (including expanded question bank)",
        "questions_created": len(questions),
        "grade_levels": [3, 5],
        "topics_per_grade": 5,
        "includes_expanded": True
    }


@router.post("/clear", status_code=200)
def clear_database(db: Session = Depends(get_db)):
    """
    Clear only questions from the database, preserving student history (quizzes and attempts).
    
    This allows reseeding the question bank without losing student progress.
    Note: Quizzes and attempts that reference deleted questions will still exist,
    but those questions won't be available for new quizzes.
    """
    from app.models import Question
    
    try:
        # Only delete questions, preserve student history
        deleted_count = db.query(Question).count()
        db.query(Question).delete()
        db.commit()
        
        return {
            "message": f"Successfully cleared {deleted_count} questions from database",
            "note": "Student history (quizzes and attempts) has been preserved. You can now seed the question bank again with /seed endpoint."
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error clearing questions: {str(e)}")


@router.post("/clear-all", status_code=200)
def clear_all_database(db: Session = Depends(get_db)):
    """
    Clear ALL data from the database (questions, quizzes, attempts).
    
    WARNING: This will delete ALL student history! Use with extreme caution.
    Use /seed/clear instead if you only want to clear questions.
    """
    from app.models import Attempt, Quiz, Question
    
    try:
        # Delete all attempts first (due to foreign key constraints)
        attempts_count = db.query(Attempt).count()
        db.query(Attempt).delete()
        # Delete all quizzes
        quizzes_count = db.query(Quiz).count()
        db.query(Quiz).delete()
        # Delete all questions
        questions_count = db.query(Question).count()
        db.query(Question).delete()
        db.commit()
        
        return {
            "message": "Database cleared completely",
            "deleted": {
                "attempts": attempts_count,
                "quizzes": quizzes_count,
                "questions": questions_count
            },
            "warning": "All student history has been deleted!",
            "note": "You can now seed the question bank again with /seed endpoint"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error clearing database: {str(e)}")


# Note: The /expand endpoint has been removed.
# Expanded questions are now automatically included when seeding via /seed endpoint.

