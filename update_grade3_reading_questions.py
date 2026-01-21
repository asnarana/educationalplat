"""
Script to update Grade 3 Reading questions by deleting old ones and adding updated ones.
This ensures passage text updates (like adding titles to Part 2) are reflected.
"""
from app.db import SessionLocal
from app.models import Question

def update_grade3_reading_questions():
    """Delete existing Grade 3 Reading questions and re-add them with updated passages."""
    db = SessionLocal()
    try:
        # Delete all existing Grade 3 Reading questions
        deleted = db.query(Question).filter(
            Question.grade_level == 3,
            Question.topic.in_([
                "Vocabulary/Word Meaning",
                "Reading Comprehension", 
                "Character Analysis",
                "Main Idea",
                "Text Structure"
            ])
        ).delete(synchronize_session=False)
        
        db.commit()
        print(f"Deleted {deleted} existing Grade 3 Reading questions")
        
        # Now import and run the add function
        from add_reading_questions import add_reading_questions
        result = add_reading_questions()
        
        print(f"\nUpdate complete!")
        print(f"Deleted: {deleted} questions")
        print(f"Added: {result['added']} questions")
        
        return {
            "deleted": deleted,
            "added": result['added']
        }
    except Exception as e:
        db.rollback()
        print(f"Error updating questions: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_grade3_reading_questions()
