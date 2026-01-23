"""
Add more Grade 5 Math questions for low-count topics to reach 10+.
- Geometry: currently 2, need 8 more
- Operations: currently 5, need 5 more
- Measurement: currently 6, need 4 more
"""
from app.db import SessionLocal
from app.models import Question

# 8 more Geometry questions
GEOMETRY_QUESTIONS = [
    {
        "grade_level": 5,
        "topic": "Geometry",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "Which point on the coordinate plane is located at (4, 2)?",
        "choices": ["Point A at x=4, y=2", "Point B at x=2, y=4", "Point C at x=4, y=4", "Point D at x=2, y=2"],
        "correct_answer": "Point A at x=4, y=2",
        "explanation": "The point (4, 2) means x=4 and y=2.",
        "calculator_active": True
    },
    {
        "grade_level": 5,
        "topic": "Geometry",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "A rectangle has vertices at (1, 1), (1, 5), (6, 5), and (6, 1). What is the perimeter of the rectangle?",
        "choices": ["18 units", "20 units", "22 units", "24 units"],
        "correct_answer": "18 units",
        "explanation": "Length = 6-1 = 5, Width = 5-1 = 4. Perimeter = 2(5+4) = 18 units.",
        "calculator_active": True
    },
    {
        "grade_level": 5,
        "topic": "Geometry",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "Which ordered pair is located in Quadrant I of the coordinate plane?",
        "choices": ["(-3, 4)", "(3, -4)", "(3, 4)", "(-3, -4)"],
        "correct_answer": "(3, 4)",
        "explanation": "Quadrant I has positive x and positive y values. (3, 4) is in Quadrant I.",
        "calculator_active": True
    },
    {
        "grade_level": 5,
        "topic": "Geometry",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "A triangle has vertices at (0, 0), (4, 0), and (2, 3). Which type of triangle is this?",
        "choices": ["Right triangle", "Isosceles triangle", "Equilateral triangle", "Scalene triangle"],
        "correct_answer": "Isosceles triangle",
        "explanation": "The two sides from (2,3) to the base vertices are equal in length, making it isosceles.",
        "calculator_active": True
    },
    {
        "grade_level": 5,
        "topic": "Geometry",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is the distance between points (1, 3) and (1, 8) on a coordinate plane?",
        "choices": ["3 units", "4 units", "5 units", "8 units"],
        "correct_answer": "5 units",
        "explanation": "Since x-coordinates are the same, distance = |8-3| = 5 units.",
        "calculator_active": True
    },
    {
        "grade_level": 5,
        "topic": "Geometry",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "A parallelogram has vertices at (2, 1), (5, 1), (6, 4), and (3, 4). What is the length of the base?",
        "choices": ["2 units", "3 units", "4 units", "5 units"],
        "correct_answer": "3 units",
        "explanation": "The base goes from (2,1) to (5,1), so length = 5-2 = 3 units.",
        "calculator_active": True
    },
    {
        "grade_level": 5,
        "topic": "Geometry",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "Which shape always has 4 right angles?",
        "choices": ["Trapezoid", "Rhombus", "Rectangle", "Parallelogram"],
        "correct_answer": "Rectangle",
        "explanation": "A rectangle always has 4 right angles (90 degrees each).",
        "calculator_active": False
    },
    {
        "grade_level": 5,
        "topic": "Geometry",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "Point A is at (2, 5). Point B is 4 units to the right and 3 units down from Point A. What are the coordinates of Point B?",
        "choices": ["(6, 2)", "(6, 8)", "(-2, 2)", "(-2, 8)"],
        "correct_answer": "(6, 2)",
        "explanation": "4 units right: 2+4=6. 3 units down: 5-3=2. Point B is at (6, 2).",
        "calculator_active": True
    },
]

# 5 more Operations questions
OPERATIONS_QUESTIONS = [
    {
        "grade_level": 5,
        "topic": "Operations",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "Which expression is equivalent to 4 × (3 + 7)?",
        "choices": ["4 × 3 + 7", "4 × 3 + 4 × 7", "4 + 3 × 7", "4 × 3 × 7"],
        "correct_answer": "4 × 3 + 4 × 7",
        "explanation": "Using the distributive property: 4 × (3 + 7) = 4 × 3 + 4 × 7.",
        "calculator_active": False
    },
    {
        "grade_level": 5,
        "topic": "Operations",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is the value of 24 ÷ (4 + 2)?",
        "choices": ["2", "4", "6", "8"],
        "correct_answer": "4",
        "explanation": "First solve parentheses: 4 + 2 = 6. Then 24 ÷ 6 = 4.",
        "calculator_active": False
    },
    {
        "grade_level": 5,
        "topic": "Operations",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "A pattern starts with 2 and each term is multiplied by 3. What is the 5th term?",
        "choices": ["54", "81", "162", "243"],
        "correct_answer": "162",
        "explanation": "1st: 2, 2nd: 6, 3rd: 18, 4th: 54, 5th: 162.",
        "calculator_active": True
    },
    {
        "grade_level": 5,
        "topic": "Operations",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "Which expression represents 'five times the sum of a number n and 8'?",
        "choices": ["5n + 8", "5 + n × 8", "5 × (n + 8)", "5 × n × 8"],
        "correct_answer": "5 × (n + 8)",
        "explanation": "'The sum of n and 8' is (n + 8). 'Five times' that is 5 × (n + 8).",
        "calculator_active": False
    },
    {
        "grade_level": 5,
        "topic": "Operations",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is the value of 3² + 4²?",
        "choices": ["14", "25", "49", "144"],
        "correct_answer": "25",
        "explanation": "3² = 9, 4² = 16. 9 + 16 = 25.",
        "calculator_active": True
    },
]

# 4 more Measurement questions
MEASUREMENT_QUESTIONS = [
    {
        "grade_level": 5,
        "topic": "Measurement",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "A rectangular prism has dimensions 5 cm × 4 cm × 3 cm. What is its volume?",
        "choices": ["12 cubic cm", "47 cubic cm", "60 cubic cm", "120 cubic cm"],
        "correct_answer": "60 cubic cm",
        "explanation": "Volume = length × width × height = 5 × 4 × 3 = 60 cubic cm.",
        "calculator_active": True
    },
    {
        "grade_level": 5,
        "topic": "Measurement",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "How many milliliters are in 3.5 liters?",
        "choices": ["35 mL", "350 mL", "3,500 mL", "35,000 mL"],
        "correct_answer": "3,500 mL",
        "explanation": "1 liter = 1,000 mL. 3.5 × 1,000 = 3,500 mL.",
        "calculator_active": True
    },
    {
        "grade_level": 5,
        "topic": "Measurement",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "A cube has edges of 6 cm each. What is the volume of the cube?",
        "choices": ["36 cubic cm", "72 cubic cm", "108 cubic cm", "216 cubic cm"],
        "correct_answer": "216 cubic cm",
        "explanation": "Volume of cube = edge³ = 6³ = 216 cubic cm.",
        "calculator_active": True
    },
    {
        "grade_level": 5,
        "topic": "Measurement",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "A box is 10 inches long, 8 inches wide, and 4 inches tall. How many 1-inch cubes can fit inside?",
        "choices": ["22 cubes", "88 cubes", "320 cubes", "1,280 cubes"],
        "correct_answer": "320 cubes",
        "explanation": "Volume = 10 × 8 × 4 = 320 cubic inches = 320 one-inch cubes.",
        "calculator_active": True
    },
]


def add_questions():
    """Add more questions for low-count Grade 5 topics."""
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
        print(f"  - Geometry: +{len(GEOMETRY_QUESTIONS)} (2 -> 10)")
        print(f"  - Operations: +{len(OPERATIONS_QUESTIONS)} (5 -> 10)")
        print(f"  - Measurement: +{len(MEASUREMENT_QUESTIONS)} (6 -> 10)")
        
        return {"added": added}
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Adding Grade 5 Math questions for low-count topics...")
    print("=" * 50)
    result = add_questions()
    print("=" * 50)
    print(f"Done! Added {result['added']} total questions.")
