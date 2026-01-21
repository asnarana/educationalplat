"""
Script to update Grade 4 Reading questions by deleting old ones and adding updated ones.
This ensures passage text updates are reflected.
"""
from app.db import SessionLocal
from app.models import Question

def update_grade4_reading_questions():
    """Delete existing Grade 4 Reading questions and re-add them with updated passages."""
    db = SessionLocal()
    try:
        # Delete all existing Grade 4 Reading questions
        deleted = db.query(Question).filter(
            Question.grade_level == 4,
            Question.topic.in_([
                "Vocabulary/Word Meaning",
                "Reading Comprehension", 
                "Character Analysis",
                "Main Idea",
                "Text Structure"
            ])
        ).delete(synchronize_session=False)
        
        db.commit()
        print(f"Deleted {deleted} existing Grade 4 Reading questions")
        
        # Now import and run the add function
        from add_grade4_reading_questions import add_grade4_reading_questions
        result = add_grade4_reading_questions()
        
        added_count = result.get('added', 0) if result else 0
        
        print(f"\nUpdate complete!")
        print(f"Deleted: {deleted} questions")
        print(f"Added: {added_count} questions")
        
        return {
            "deleted": deleted,
            "added": added_count
        }
    except Exception as e:
        db.rollback()
        print(f"Error updating questions: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_grade4_reading_questions()
