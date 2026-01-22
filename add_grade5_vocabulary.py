"""
Add more Grade 5 Vocabulary questions.
Currently has 9, need at least 15 for proper quiz retakes.
"""
from app.db import SessionLocal
from app.models import Question

# Import passages from the Grade 5 reading file
from add_grade5_reading_questions import (
    LIFE_WITHOUT_GRAVITY,
    MAKING_WORLDS_RAREST_SYRUP,
    WORLD_IN_A_BOTTLE
)

# Additional Vocabulary questions for Grade 5
GRADE5_VOCABULARY_ADDITIONS = [
    {
        "grade_level": 5,
        "topic": "Vocabulary",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{LIFE_WITHOUT_GRAVITY}\n\nWhat does the word 'adapted' mean in paragraph 4?",
        "choices": ["changed to fit", "moved quickly", "grew larger", "became weaker"],
        "correct_answer": "changed to fit",
        "explanation": "Adapted means adjusted or changed to fit a particular environment or condition."
    },
    {
        "grade_level": 5,
        "topic": "Vocabulary",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{LIFE_WITHOUT_GRAVITY}\n\nWhat does the word 'feeble' mean in paragraph 8?",
        "choices": ["strong", "flexible", "weak", "healthy"],
        "correct_answer": "weak",
        "explanation": "Feeble means lacking strength or weak."
    },
    {
        "grade_level": 5,
        "topic": "Vocabulary",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{LIFE_WITHOUT_GRAVITY}\n\nWhat does the word 'nauseous' mean in paragraph 9?",
        "choices": ["excited", "hungry", "sick to the stomach", "tired"],
        "correct_answer": "sick to the stomach",
        "explanation": "Nauseous means feeling sick to the stomach, like you might throw up."
    },
    {
        "grade_level": 5,
        "topic": "Vocabulary",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{MAKING_WORLDS_RAREST_SYRUP}\n\nWhat does the word 'mature' mean in paragraph 2?",
        "choices": ["young", "fully grown", "small", "colorful"],
        "correct_answer": "fully grown",
        "explanation": "Mature means fully grown or developed."
    },
    {
        "grade_level": 5,
        "topic": "Vocabulary",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{MAKING_WORLDS_RAREST_SYRUP}\n\nWhat does the word 'strain' mean in paragraph 10?",
        "choices": ["to cook quickly", "to separate liquid from solids", "to mix together", "to cool down"],
        "correct_answer": "to separate liquid from solids",
        "explanation": "Strain means to pour through a filter to separate liquid from solid pieces."
    },
    {
        "grade_level": 5,
        "topic": "Vocabulary",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{WORLD_IN_A_BOTTLE}\n\nWhat does the word 'transparent' mean in paragraph 5?",
        "choices": ["dark", "see-through", "colorful", "thick"],
        "correct_answer": "see-through",
        "explanation": "Transparent means clear or see-through, allowing light to pass through."
    },
    {
        "grade_level": 5,
        "topic": "Vocabulary",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{WORLD_IN_A_BOTTLE}\n\nWhat does the word 'thrived' mean in paragraph 6?",
        "choices": ["died quickly", "grew well", "stayed the same", "became smaller"],
        "correct_answer": "grew well",
        "explanation": "Thrived means grew strong and healthy, or prospered."
    },
    {
        "grade_level": 5,
        "topic": "Vocabulary",
        "difficulty": 2,
        "weight": 1.0,
        "prompt": f"Read the passage:\n\n{LIFE_WITHOUT_GRAVITY}\n\nWhat does the word 'blander' mean in paragraph 10?",
        "choices": ["more colorful", "less tasty", "more delicious", "hotter"],
        "correct_answer": "less tasty",
        "explanation": "Blander means having less flavor or being more plain and boring in taste."
    },
]


def add_questions():
    """Add the additional Vocabulary questions."""
    db = SessionLocal()
    
    try:
        added = 0
        for q_data in GRADE5_VOCABULARY_ADDITIONS:
            question = Question(**q_data)
            db.add(question)
            added += 1
        
        db.commit()
        print(f"Successfully added {added} Grade 5 Vocabulary questions")
        return {"added": added}
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Adding Grade 5 Vocabulary questions...")
    result = add_questions()
    print(f"Done! Added {result['added']} questions.")
