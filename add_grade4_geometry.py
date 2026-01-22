"""
Add more Grade 4 Geometry questions to balance the topics.
Currently has only 3, need at least 6-8.
"""
from app.db import SessionLocal
from app.models import Question

GRADE4_GEOMETRY_ADDITIONS = [
    {
        "grade_level": 4,
        "topic": "Geometry",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "Which shape has exactly 4 sides and 4 right angles?",
        "choices": ["triangle", "pentagon", "rectangle", "hexagon"],
        "correct_answer": "rectangle",
        "explanation": "A rectangle has 4 sides and 4 right angles (90° each).",
        "calculator_active": False
    },
    {
        "grade_level": 4,
        "topic": "Geometry",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "How many degrees are in a right angle?",
        "choices": ["45°", "90°", "180°", "360°"],
        "correct_answer": "90°",
        "explanation": "A right angle measures exactly 90 degrees.",
        "calculator_active": False
    },
    {
        "grade_level": 4,
        "topic": "Geometry",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "A straight line measures how many degrees?",
        "choices": ["90°", "120°", "180°", "360°"],
        "correct_answer": "180°",
        "explanation": "A straight line (straight angle) measures 180 degrees.",
        "calculator_active": True
    },
    {
        "grade_level": 4,
        "topic": "Geometry",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "Which type of angle measures less than 90 degrees?",
        "choices": ["right angle", "acute angle", "obtuse angle", "straight angle"],
        "correct_answer": "acute angle",
        "explanation": "An acute angle measures less than 90 degrees.",
        "calculator_active": False
    },
    {
        "grade_level": 4,
        "topic": "Geometry",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "Which type of angle measures more than 90 degrees but less than 180 degrees?",
        "choices": ["right angle", "acute angle", "obtuse angle", "straight angle"],
        "correct_answer": "obtuse angle",
        "explanation": "An obtuse angle measures between 90 and 180 degrees.",
        "calculator_active": True
    },
    {
        "grade_level": 4,
        "topic": "Geometry",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "Two lines that cross at a right angle are called:",
        "choices": ["parallel lines", "perpendicular lines", "curved lines", "diagonal lines"],
        "correct_answer": "perpendicular lines",
        "explanation": "Perpendicular lines intersect at a 90-degree (right) angle.",
        "calculator_active": True
    },
]


def add_questions():
    """Add more Geometry questions for Grade 4."""
    db = SessionLocal()
    
    try:
        added = 0
        for q_data in GRADE4_GEOMETRY_ADDITIONS:
            question = Question(**q_data)
            db.add(question)
            added += 1
        
        db.commit()
        print(f"Successfully added {added} Grade 4 Geometry questions")
        return {"added": added}
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Adding Grade 4 Geometry questions...")
    result = add_questions()
    print(f"Done! Added {result['added']} questions.")
