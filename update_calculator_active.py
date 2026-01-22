"""
Update Grade 3 Math questions with calculator_active field.
Questions 1-20 = Calculator Inactive (False)
Questions 21-40+ = Calculator Active (True)

This is based on NC EOG format where first 20 questions are non-calculator.
"""
from app.db import SessionLocal, engine
from app.models import Question
from sqlalchemy import text, inspect

def ensure_calculator_active_column():
    """Add calculator_active column if it doesn't exist."""
    inspector = inspect(engine)
    columns = [col['name'].upper() for col in inspector.get_columns('questions')]
    
    if 'CALCULATOR_ACTIVE' not in columns:
        with engine.connect() as conn:
            add_column = text("ALTER TABLE questions ADD calculator_active NUMBER(1)")
            conn.execute(add_column)
            conn.commit()
            print("[OK] Added calculator_active column")
    else:
        print("[OK] calculator_active column already exists")


def update_calculator_active():
    """
    Update Grade 3 Math questions with calculator_active based on prompt patterns.
    Since we don't have question_num stored, we'll identify questions by their content.
    
    For now, we'll use a simpler approach:
    - Questions with certain keywords/patterns get calculator_active = True
    - All Grade 3 Math questions before Q21 patterns get False
    """
    ensure_calculator_active_column()
    
    db = SessionLocal()
    
    try:
        # Get all Grade 3 Math questions
        math_keywords = ['geometry', 'fractions', 'operations', 'number operations', 'measurement']
        
        questions = db.query(Question).filter(
            Question.grade_level == 3
        ).all()
        
        # Questions that are calculator active (Q21-40) based on their prompts
        # These are identifiable by specific question content from EOG
        calculator_active_prompts = [
            "A fraction of this circle is shaded",  # Q21
            "What fraction is represented by point L",  # Q22
            "Carlos and his friends collected 72 rocks",  # Q23
            "Jasmine wrote 2 pages in her journal",  # Q24
            "What fraction of the area of this figure is shaded",  # Q25
            "A truck rental company charges",  # Q26
            "Which circle is 3/4 shaded",  # Q27
            "third-grade class voted for their favorite subject",  # Q28
            "Which letter has a value of 3/4",  # Q29
            "Sarah drew a shape",  # Q30
            "A train makes 9 stops each day",  # Q31
            "Four friends were playing a game",  # Q32
            "school collects canned food for charity",  # Q33
            "expression can be used to find the missing number",  # Q34
            "Donna shaded this rectangle",  # Q35
            "Ellen is comparing two rectangles",  # Q36
            "Lacey has a bookcase with 6 shelves",  # Q37
            "shows a pencil and a ruler",  # Q38
            "Tanya baked 125 cookies",  # Q39
            "shows two correct ways to arrange 21 pennies",  # Q40
        ]
        
        updated_active = 0
        updated_inactive = 0
        
        for q in questions:
            # Check if it's a math question
            is_math = any(kw in q.topic.lower() for kw in math_keywords)
            if not is_math:
                continue
            
            # Check if this question's prompt matches any calculator active pattern
            is_active = any(pattern.lower() in q.prompt.lower() for pattern in calculator_active_prompts)
            
            if is_active:
                q.calculator_active = True
                updated_active += 1
            else:
                q.calculator_active = False
                updated_inactive += 1
        
        db.commit()
        
        print(f"\nUpdated Grade 3 Math questions:")
        print(f"  Calculator Active (True): {updated_active}")
        print(f"  Calculator Inactive (False): {updated_inactive}")
        
        return {
            "active": updated_active,
            "inactive": updated_inactive
        }
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Updating Grade 3 Math questions with calculator_active field...")
    result = update_calculator_active()
    print(f"\nDone!")
