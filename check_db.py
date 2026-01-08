"""
Simple script to check if Oracle database is working and has entries.
Run with: python check_db.py
"""
from app.db import engine, SessionLocal
from app.models import Question, Quiz, Attempt
from sqlalchemy import text, inspect

def check_database():
    """Check database connection and show table entries."""
    try:
        # Test connection
        print("[*] Checking database connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 FROM DUAL"))
            print("[OK] Database connection successful!")
        
        # Get a database session
        db = SessionLocal()
        try:
            # Check if tables exist
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            print(f"\n[*] Tables found: {tables}")
            
            # Check Questions table
            print("\n[*] Questions table:")
            question_count = db.query(Question).count()
            print(f"    Total questions: {question_count}")
            if question_count > 0:
                sample_question = db.query(Question).first()
                print(f"    Sample question: ID={sample_question.id}, Topic={sample_question.topic}, Grade={sample_question.grade_level}")
            
            # Check Quizzes table
            print("\n[*] Quizzes table:")
            quiz_count = db.query(Quiz).count()
            print(f"    Total quizzes: {quiz_count}")
            if quiz_count > 0:
                sample_quiz = db.query(Quiz).first()
                print(f"    Sample quiz: ID={sample_quiz.id}, Student={sample_quiz.student_id}, Grade={sample_quiz.grade_level}")
            
            # Check Attempts table
            print("\n[*] Attempts table:")
            attempt_count = db.query(Attempt).count()
            print(f"    Total attempts: {attempt_count}")
            if attempt_count > 0:
                sample_attempt = db.query(Attempt).first()
                print(f"    Sample attempt: ID={sample_attempt.id}, Score={sample_attempt.score_total}, Passed={sample_attempt.passed}")
            
            # Check sequences
            print("\n[*] Sequences:")
            with engine.connect() as conn:
                seq_result = conn.execute(text("""
                    SELECT sequence_name, last_number 
                    FROM user_sequences 
                    ORDER BY sequence_name
                """))
                sequences = seq_result.fetchall()
                if sequences:
                    for seq_name, last_num in sequences:
                        print(f"    {seq_name}: last_number={last_num}")
                else:
                    print("    No sequences found")
            
            print("\n[OK] Database check complete!")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database()
