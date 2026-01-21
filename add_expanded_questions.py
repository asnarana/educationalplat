"""
Script to add expanded questions to the existing database.
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.db import SessionLocal
from app.routes.seed import add_expanded_questions_to_existing_db

if __name__ == "__main__":
    db = SessionLocal()
    try:
        result = add_expanded_questions_to_existing_db(db)
        print(f"SUCCESS: {result['message']}")
        print(f"   Questions added: {result['questions_added']}")
        print(f"   Previous count: {result['previous_count']}")
        print(f"   New total: {result['new_total']}")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
