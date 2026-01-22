"""
Add more Grade 4 Math questions for low-count topics.
- Measurement: currently 7, need 3 more
- Operations: currently 6, need 4 more
"""
from app.db import SessionLocal
from app.models import Question

# Additional Measurement questions for Grade 4
GRADE4_MEASUREMENT_ADDITIONS = [
    {
        "grade_level": 4,
        "topic": "Measurement",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "How many centimeters are in 1 meter?",
        "choices": ["10 centimeters", "100 centimeters", "1,000 centimeters", "10,000 centimeters"],
        "correct_answer": "100 centimeters",
        "explanation": "1 meter = 100 centimeters.",
        "calculator_active": False
    },
    {
        "grade_level": 4,
        "topic": "Measurement",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "A rectangle has a length of 12 cm and a width of 5 cm. What is the perimeter of the rectangle?",
        "choices": ["17 cm", "34 cm", "60 cm", "120 cm"],
        "correct_answer": "34 cm",
        "explanation": "Perimeter = 2 × (length + width) = 2 × (12 + 5) = 2 × 17 = 34 cm.",
        "calculator_active": True
    },
    {
        "grade_level": 4,
        "topic": "Measurement",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "A square has sides that are each 8 inches long. What is the area of the square?",
        "choices": ["16 square inches", "32 square inches", "64 square inches", "128 square inches"],
        "correct_answer": "64 square inches",
        "explanation": "Area of square = side × side = 8 × 8 = 64 square inches.",
        "calculator_active": True
    },
]

# Additional Operations questions for Grade 4
GRADE4_OPERATIONS_ADDITIONS = [
    {
        "grade_level": 4,
        "topic": "Operations",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "Which number is a multiple of both 4 and 6?",
        "choices": ["8", "10", "12", "14"],
        "correct_answer": "12",
        "explanation": "12 is divisible by both 4 (12÷4=3) and 6 (12÷6=2).",
        "calculator_active": False
    },
    {
        "grade_level": 4,
        "topic": "Operations",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What are all the factors of 12?",
        "choices": ["1, 2, 3, 4, 6, 12", "1, 2, 4, 12", "2, 3, 4, 6", "1, 12"],
        "correct_answer": "1, 2, 3, 4, 6, 12",
        "explanation": "The factors of 12 are all numbers that divide evenly into 12: 1, 2, 3, 4, 6, and 12.",
        "calculator_active": False
    },
    {
        "grade_level": 4,
        "topic": "Operations",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "If n × 7 = 56, what is the value of n?",
        "choices": ["6", "7", "8", "9"],
        "correct_answer": "8",
        "explanation": "n × 7 = 56, so n = 56 ÷ 7 = 8.",
        "calculator_active": True
    },
    {
        "grade_level": 4,
        "topic": "Operations",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "A store has 84 apples to put into bags. Each bag holds 7 apples. How many bags can be filled?",
        "choices": ["10 bags", "11 bags", "12 bags", "13 bags"],
        "correct_answer": "12 bags",
        "explanation": "84 ÷ 7 = 12 bags.",
        "calculator_active": True
    },
]


def add_questions():
    """Add more questions for low-count Grade 4 topics."""
    db = SessionLocal()
    
    try:
        all_questions = GRADE4_MEASUREMENT_ADDITIONS + GRADE4_OPERATIONS_ADDITIONS
        
        added = 0
        for q_data in all_questions:
            question = Question(**q_data)
            db.add(question)
            added += 1
        
        db.commit()
        
        print(f"Successfully added {added} questions:")
        print(f"  - Measurement: {len(GRADE4_MEASUREMENT_ADDITIONS)} (now should be 10)")
        print(f"  - Operations: {len(GRADE4_OPERATIONS_ADDITIONS)} (now should be 10)")
        
        return {"added": added}
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Adding more Grade 4 Math questions for low-count topics...")
    result = add_questions()
    print(f"\nDone! Added {result['added']} questions.")
