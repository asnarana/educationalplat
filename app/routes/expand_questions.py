"""
Script to expand the question bank with more questions.
Generates additional questions for each topic and grade level.
"""
from sqlalchemy.orm import Session
from app.db import get_db, SessionLocal
from app.models import Question, Base
from app.db import engine

# Expanded question bank
EXPANDED_QUESTIONS = [
    # Grade 3 - Addition (more questions)
    {
        "grade_level": 3,
        "topic": "Addition",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 7 + 4?",
        "choices": ["10", "11", "12", "13"],
        "correct_answer": "11",
        "explanation": "Adding 7 and 4 gives 11."
    },
    {
        "grade_level": 3,
        "topic": "Addition",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 9 + 6?",
        "choices": ["14", "15", "16", "17"],
        "correct_answer": "15",
        "explanation": "Adding 9 and 6 gives 15."
    },
    {
        "grade_level": 3,
        "topic": "Addition",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 18 + 19?",
        "choices": ["35", "36", "37", "38"],
        "correct_answer": "37",
        "explanation": "Adding 18 and 19 gives 37."
    },
    {
        "grade_level": 3,
        "topic": "Addition",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 23 + 14?",
        "choices": ["36", "37", "38", "39"],
        "correct_answer": "37",
        "explanation": "Adding 23 and 14 gives 37."
    },
    
    # Grade 3 - Subtraction (more questions)
    {
        "grade_level": 3,
        "topic": "Subtraction",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 15 - 7?",
        "choices": ["7", "8", "9", "10"],
        "correct_answer": "8",
        "explanation": "Subtracting 7 from 15 gives 8."
    },
    {
        "grade_level": 3,
        "topic": "Subtraction",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 20 - 9?",
        "choices": ["10", "11", "12", "13"],
        "correct_answer": "11",
        "explanation": "Subtracting 9 from 20 gives 11."
    },
    {
        "grade_level": 3,
        "topic": "Subtraction",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 35 - 18?",
        "choices": ["16", "17", "18", "19"],
        "correct_answer": "17",
        "explanation": "Subtracting 18 from 35 gives 17."
    },
    {
        "grade_level": 3,
        "topic": "Subtraction",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 42 - 19?",
        "choices": ["22", "23", "24", "25"],
        "correct_answer": "23",
        "explanation": "Subtracting 19 from 42 gives 23."
    },
    
    # Grade 3 - Multiplication (more questions)
    {
        "grade_level": 3,
        "topic": "Multiplication",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 4 × 5?",
        "choices": ["18", "19", "20", "21"],
        "correct_answer": "20",
        "explanation": "Multiplying 4 by 5 gives 20."
    },
    {
        "grade_level": 3,
        "topic": "Multiplication",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 5 × 8?",
        "choices": ["38", "39", "40", "41"],
        "correct_answer": "40",
        "explanation": "Multiplying 5 by 8 gives 40."
    },
    {
        "grade_level": 3,
        "topic": "Multiplication",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 8 × 9?",
        "choices": ["70", "71", "72", "73"],
        "correct_answer": "72",
        "explanation": "Multiplying 8 by 9 gives 72."
    },
    {
        "grade_level": 3,
        "topic": "Multiplication",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 7 × 8?",
        "choices": ["54", "55", "56", "57"],
        "correct_answer": "56",
        "explanation": "Multiplying 7 by 8 gives 56."
    },
    
    # Grade 3 - Division (more questions)
    {
        "grade_level": 3,
        "topic": "Division",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 15 ÷ 5?",
        "choices": ["2", "3", "4", "5"],
        "correct_answer": "3",
        "explanation": "Dividing 15 by 5 gives 3."
    },
    {
        "grade_level": 3,
        "topic": "Division",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 18 ÷ 6?",
        "choices": ["2", "3", "4", "5"],
        "correct_answer": "3",
        "explanation": "Dividing 18 by 6 gives 3."
    },
    {
        "grade_level": 3,
        "topic": "Division",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 36 ÷ 6?",
        "choices": ["5", "6", "7", "8"],
        "correct_answer": "6",
        "explanation": "Dividing 36 by 6 gives 6."
    },
    {
        "grade_level": 3,
        "topic": "Division",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 42 ÷ 7?",
        "choices": ["5", "6", "7", "8"],
        "correct_answer": "6",
        "explanation": "Dividing 42 by 7 gives 6."
    },
    
    # Grade 3 - Fractions (more questions)
    {
        "grade_level": 3,
        "topic": "Fractions",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What fraction represents one quarter?",
        "choices": ["1/3", "1/4", "1/5", "2/4"],
        "correct_answer": "1/4",
        "explanation": "One quarter is represented by 1/4."
    },
    {
        "grade_level": 3,
        "topic": "Fractions",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What fraction represents three quarters?",
        "choices": ["2/4", "3/4", "4/4", "1/3"],
        "correct_answer": "3/4",
        "explanation": "Three quarters is represented by 3/4."
    },
    {
        "grade_level": 3,
        "topic": "Fractions",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "Which fraction is smaller: 1/3 or 1/5?",
        "choices": ["1/3", "1/5", "They are equal", "Cannot compare"],
        "correct_answer": "1/5",
        "explanation": "1/5 is smaller than 1/3 because it represents a smaller portion of the whole."
    },
    {
        "grade_level": 3,
        "topic": "Fractions",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "If you have 2/4 of a pizza, how much do you have?",
        "choices": ["Half", "Quarter", "Three quarters", "Whole"],
        "correct_answer": "Half",
        "explanation": "2/4 is equal to 1/2, which is half."
    },
    
    # Grade 5 - Algebra (more questions)
    {
        "grade_level": 5,
        "topic": "Algebra",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "If x + 3 = 8, what is x?",
        "choices": ["4", "5", "6", "7"],
        "correct_answer": "5",
        "explanation": "If x + 3 = 8, then x = 8 - 3 = 5."
    },
    {
        "grade_level": 5,
        "topic": "Algebra",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "If x - 4 = 6, what is x?",
        "choices": ["8", "9", "10", "11"],
        "correct_answer": "10",
        "explanation": "If x - 4 = 6, then x = 6 + 4 = 10."
    },
    {
        "grade_level": 5,
        "topic": "Algebra",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "If 3x = 21, what is x?",
        "choices": ["6", "7", "8", "9"],
        "correct_answer": "7",
        "explanation": "If 3x = 21, then x = 21 ÷ 3 = 7."
    },
    {
        "grade_level": 5,
        "topic": "Algebra",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "If x ÷ 4 = 5, what is x?",
        "choices": ["18", "19", "20", "21"],
        "correct_answer": "20",
        "explanation": "If x ÷ 4 = 5, then x = 5 × 4 = 20."
    },
    
    # Grade 5 - Geometry (more questions)
    {
        "grade_level": 5,
        "topic": "Geometry",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "How many sides does a square have?",
        "choices": ["3", "4", "5", "6"],
        "correct_answer": "4",
        "explanation": "A square has 4 sides."
    },
    {
        "grade_level": 5,
        "topic": "Geometry",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is the perimeter of a square with side length 5?",
        "choices": ["15", "20", "25", "30"],
        "correct_answer": "20",
        "explanation": "Perimeter of a square = 4 × side = 4 × 5 = 20."
    },
    {
        "grade_level": 5,
        "topic": "Geometry",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is the area of a rectangle with length 6 and width 5?",
        "choices": ["28", "29", "30", "31"],
        "correct_answer": "30",
        "explanation": "Area of rectangle = length × width = 6 × 5 = 30."
    },
    {
        "grade_level": 5,
        "topic": "Geometry",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is the perimeter of a rectangle with length 8 and width 5?",
        "choices": ["24", "25", "26", "27"],
        "correct_answer": "26",
        "explanation": "Perimeter = 2 × (length + width) = 2 × (8 + 5) = 2 × 13 = 26."
    },
    
    # Grade 5 - Decimals (more questions)
    {
        "grade_level": 5,
        "topic": "Decimals",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 0.7 + 0.2?",
        "choices": ["0.8", "0.9", "1.0", "1.1"],
        "correct_answer": "0.9",
        "explanation": "Adding 0.7 and 0.2 gives 0.9."
    },
    {
        "grade_level": 5,
        "topic": "Decimals",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 1.5 - 0.8?",
        "choices": ["0.6", "0.7", "0.8", "0.9"],
        "correct_answer": "0.7",
        "explanation": "Subtracting 0.8 from 1.5 gives 0.7."
    },
    {
        "grade_level": 5,
        "topic": "Decimals",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 3.2 × 2?",
        "choices": ["6.2", "6.3", "6.4", "6.5"],
        "correct_answer": "6.4",
        "explanation": "Multiplying 3.2 by 2 gives 6.4."
    },
    {
        "grade_level": 5,
        "topic": "Decimals",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 4.8 ÷ 2?",
        "choices": ["2.3", "2.4", "2.5", "2.6"],
        "correct_answer": "2.4",
        "explanation": "Dividing 4.8 by 2 gives 2.4."
    },
    
    # Grade 5 - Percentages (more questions)
    {
        "grade_level": 5,
        "topic": "Percentages",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 25% of 80?",
        "choices": ["18", "20", "22", "24"],
        "correct_answer": "20",
        "explanation": "25% of 80 = 0.25 × 80 = 20."
    },
    {
        "grade_level": 5,
        "topic": "Percentages",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "What is 10% of 50?",
        "choices": ["4", "5", "6", "7"],
        "correct_answer": "5",
        "explanation": "10% of 50 = 0.10 × 50 = 5."
    },
    {
        "grade_level": 5,
        "topic": "Percentages",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 75% of 120?",
        "choices": ["88", "89", "90", "91"],
        "correct_answer": "90",
        "explanation": "75% of 120 = 0.75 × 120 = 90."
    },
    {
        "grade_level": 5,
        "topic": "Percentages",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "What is 20% of 150?",
        "choices": ["28", "29", "30", "31"],
        "correct_answer": "30",
        "explanation": "20% of 150 = 0.20 × 150 = 30."
    },
    
    # Grade 5 - Word Problems (more questions)
    {
        "grade_level": 5,
        "topic": "Word Problems",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "Tom has 20 marbles. He gives away 8. How many does he have left?",
        "choices": ["10", "11", "12", "13"],
        "correct_answer": "12",
        "explanation": "20 - 8 = 12 marbles remaining."
    },
    {
        "grade_level": 5,
        "topic": "Word Problems",
        "difficulty": 1,
        "weight": 1.0,
        "prompt": "A box has 30 pencils. If 5 students share them equally, how many pencils does each student get?",
        "choices": ["5", "6", "7", "8"],
        "correct_answer": "6",
        "explanation": "30 ÷ 5 = 6 pencils per student."
    },
    {
        "grade_level": 5,
        "topic": "Word Problems",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "Emma saves $5 each week. How much will she save in 8 weeks?",
        "choices": ["38", "39", "40", "41"],
        "correct_answer": "40",
        "explanation": "$5 × 8 weeks = $40."
    },
    {
        "grade_level": 5,
        "topic": "Word Problems",
        "difficulty": 2,
        "weight": 1.5,
        "prompt": "A store has 48 apples. They sell 3/4 of them. How many apples are left?",
        "choices": ["10", "11", "12", "13"],
        "correct_answer": "12",
        "explanation": "3/4 of 48 = 36 sold. 48 - 36 = 12 apples left."
    },
]


def expand_question_bank():
    """Add expanded questions to the database."""
    db = SessionLocal()
    try:
        # Initialize database tables
        Base.metadata.create_all(bind=engine)
        
        # Check existing questions
        existing_count = db.query(Question).count()
        print(f"Current questions in database: {existing_count}")
        
        # Add new questions
        new_questions = []
        for q_data in EXPANDED_QUESTIONS:
            # Check if question already exists (by prompt and grade_level)
            existing = db.query(Question).filter(
                Question.prompt == q_data["prompt"],
                Question.grade_level == q_data["grade_level"]
            ).first()
            
            if not existing:
                question = Question(**q_data)
                new_questions.append(question)
        
        if new_questions:
            db.add_all(new_questions)
            db.commit()
            print(f"✅ Added {len(new_questions)} new questions to the database!")
            print(f"Total questions now: {existing_count + len(new_questions)}")
        else:
            print("ℹ️  All questions already exist in the database.")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    expand_question_bank()

