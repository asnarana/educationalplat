"""Script to drop and recreate database tables with sequences."""
from app.db import engine, init_db
from sqlalchemy import text

def recreate_tables():
    """Drop existing tables and sequences, then recreate them."""
    with engine.connect() as conn:
        # Drop tables (this will also drop foreign key constraints)
        try:
            conn.execute(text("DROP TABLE attempts CASCADE CONSTRAINTS"))
            print("✓ Dropped attempts table")
        except Exception as e:
            print(f"⚠ attempts table: {e}")
        
        try:
            conn.execute(text("DROP TABLE quizzes CASCADE CONSTRAINTS"))
            print("✓ Dropped quizzes table")
        except Exception as e:
            print(f"⚠ quizzes table: {e}")
        
        try:
            conn.execute(text("DROP TABLE questions CASCADE CONSTRAINTS"))
            print("✓ Dropped questions table")
        except Exception as e:
            print(f"⚠ questions table: {e}")
        
        # Drop sequences (they may not exist)
        for seq_name in ['attempts_id_seq', 'quizzes_id_seq', 'questions_id_seq']:
            try:
                conn.execute(text(f"DROP SEQUENCE {seq_name}"))
                print(f"✓ Dropped sequence {seq_name}")
            except Exception as e:
                print(f"⚠ Sequence {seq_name}: {e}")
        
        conn.commit()
    
    # Recreate tables with sequences
    print("\nRecreating tables with sequences...")
    init_db()
    print("✓ Tables recreated successfully!")

if __name__ == "__main__":
    recreate_tables()

