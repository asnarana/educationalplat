"""
Add more Grade 3 Number Operations questions.
Currently has 5, need at least 8-10 for balanced quizzes.
Based on NC.3.NBT standards (Numbers and Operations in Base Ten).
"""
from app.db import SessionLocal
from app.models import Question

# Additional Number Operations questions for Grade 3
GRADE3_NUMBER_OPERATIONS = [
    {
        "grade_level": 3,
        "topic": "Number Operations",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "A library has 456 books on the first floor and 328 books on the second floor. How many books are in the library?",
        "choices": ["784", "774", "684", "674"],
        "correct_answer": "784",
        "explanation": "456 + 328 = 784 books total in the library."
    },
    {
        "grade_level": 3,
        "topic": "Number Operations",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "Maria had 425 stickers. She gave 178 stickers to her friend. How many stickers does Maria have now?",
        "choices": ["247", "257", "347", "357"],
        "correct_answer": "247",
        "explanation": "425 - 178 = 247 stickers remaining."
    },
    {
        "grade_level": 3,
        "topic": "Number Operations",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "The school store sold 312 pencils on Monday and 489 pencils on Tuesday. About how many pencils were sold in all?",
        "choices": ["700", "800", "900", "1,000"],
        "correct_answer": "800",
        "explanation": "312 + 489 = 801 pencils. Rounded to the nearest hundred, this is about 800 pencils."
    },
    {
        "grade_level": 3,
        "topic": "Number Operations",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "A bakery made 600 cookies. They sold 437 cookies. How many cookies are left?",
        "choices": ["163", "173", "237", "263"],
        "correct_answer": "163",
        "explanation": "600 - 437 = 163 cookies left."
    },
    {
        "grade_level": 3,
        "topic": "Number Operations",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "There are 8 rows of desks in a classroom. Each row has 4 desks. How many desks are in the classroom?",
        "choices": ["12", "24", "32", "36"],
        "correct_answer": "32",
        "explanation": "8 rows × 4 desks = 32 desks in the classroom."
    },
    {
        "grade_level": 3,
        "topic": "Number Operations",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "A store had 752 apples. They received 248 more apples. About how many apples does the store have now?",
        "choices": ["900", "1,000", "1,100", "1,200"],
        "correct_answer": "1,000",
        "explanation": "752 + 248 = 1,000 apples exactly."
    },
]


def add_questions():
    """Add the additional Number Operations questions."""
    db = SessionLocal()
    
    try:
        added = 0
        for q_data in GRADE3_NUMBER_OPERATIONS:
            question = Question(**q_data)
            db.add(question)
            added += 1
        
        db.commit()
        print(f"Successfully added {added} Grade 3 Number Operations questions")
        return {"added": added}
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Adding Grade 3 Number Operations questions...")
    result = add_questions()
    print(f"Done! Added {result['added']} questions.")
