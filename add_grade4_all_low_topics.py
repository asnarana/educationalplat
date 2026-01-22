"""
Add more Grade 4 Math questions for ALL low-count topics to reach 10+.
- Geometry: currently 3, need 7 more
- Operations: currently 6, need 4 more  
- Measurement: currently 7, need 3 more
"""
from app.db import SessionLocal
from app.models import Question

# 7 more Geometry questions
GEOMETRY_QUESTIONS = [
    {
        "grade_level": 4,
        "topic": "Geometry",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "Which figure is a quadrilateral with exactly one pair of parallel sides?",
        "choices": ["Square", "Rectangle", "Rhombus", "Trapezoid"],
        "correct_answer": "Trapezoid",
        "explanation": "A trapezoid is a quadrilateral with exactly one pair of parallel sides.",
        "calculator_active": False
    },
    {
        "grade_level": 4,
        "topic": "Geometry",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "How many degrees are in a right angle?",
        "choices": ["45 degrees", "90 degrees", "180 degrees", "360 degrees"],
        "correct_answer": "90 degrees",
        "explanation": "A right angle measures exactly 90 degrees.",
        "calculator_active": False
    },
    {
        "grade_level": 4,
        "topic": "Geometry",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "A triangle has angles measuring 60 degrees and 70 degrees. What is the measure of the third angle?",
        "choices": ["40 degrees", "50 degrees", "60 degrees", "70 degrees"],
        "correct_answer": "50 degrees",
        "explanation": "The sum of angles in a triangle is 180 degrees. 180 - 60 - 70 = 50 degrees.",
        "calculator_active": True
    },
    {
        "grade_level": 4,
        "topic": "Geometry",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "Which shape has exactly 4 lines of symmetry?",
        "choices": ["Rectangle", "Square", "Trapezoid", "Parallelogram"],
        "correct_answer": "Square",
        "explanation": "A square has 4 lines of symmetry - 2 through opposite corners and 2 through midpoints of opposite sides.",
        "calculator_active": False
    },
    {
        "grade_level": 4,
        "topic": "Geometry",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "Two angles are supplementary. One angle measures 125 degrees. What is the measure of the other angle?",
        "choices": ["45 degrees", "55 degrees", "65 degrees", "75 degrees"],
        "correct_answer": "55 degrees",
        "explanation": "Supplementary angles add up to 180 degrees. 180 - 125 = 55 degrees.",
        "calculator_active": True
    },
    {
        "grade_level": 4,
        "topic": "Geometry",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "Which type of angle measures less than 90 degrees?",
        "choices": ["Right angle", "Obtuse angle", "Acute angle", "Straight angle"],
        "correct_answer": "Acute angle",
        "explanation": "An acute angle measures less than 90 degrees.",
        "calculator_active": False
    },
    {
        "grade_level": 4,
        "topic": "Geometry",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "A parallelogram has one angle that measures 70 degrees. What are the measures of the other three angles?",
        "choices": ["70, 110, 110 degrees", "70, 70, 150 degrees", "110, 110, 70 degrees", "80, 80, 130 degrees"],
        "correct_answer": "70, 110, 110 degrees",
        "explanation": "In a parallelogram, opposite angles are equal, and adjacent angles are supplementary (add to 180). So angles are 70, 110, 70, 110.",
        "calculator_active": True
    },
]

# 4 more Operations questions
OPERATIONS_QUESTIONS = [
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

# 3 more Measurement questions
MEASUREMENT_QUESTIONS = [
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


def add_questions():
    """Add more questions for ALL low-count Grade 4 topics."""
    db = SessionLocal()
    
    try:
        all_questions = GEOMETRY_QUESTIONS + OPERATIONS_QUESTIONS + MEASUREMENT_QUESTIONS
        
        added = 0
        for q_data in all_questions:
            question = Question(**q_data)
            db.add(question)
            added += 1
        
        db.commit()
        
        print(f"Successfully added {added} questions:")
        print(f"  - Geometry: +{len(GEOMETRY_QUESTIONS)} (3 -> 10)")
        print(f"  - Operations: +{len(OPERATIONS_QUESTIONS)} (6 -> 10)")
        print(f"  - Measurement: +{len(MEASUREMENT_QUESTIONS)} (7 -> 10)")
        
        return {"added": added}
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Adding Grade 4 Math questions for all low-count topics...")
    print("=" * 50)
    result = add_questions()
    print("=" * 50)
    print(f"Done! Added {result['added']} total questions.")
