"""Temporary script to drop existing tables."""
from app.db import engine
from sqlalchemy import text

def drop_tables():
    """Drop all existing tables."""
    tables = ['attempts', 'quizzes', 'questions']
    with engine.connect() as conn:
        for table in tables:
            try:
                conn.execute(text(f"DROP TABLE {table} CASCADE CONSTRAINTS"))
                print(f"Dropped table: {table}")
            except Exception as e:
                print(f"Error dropping {table}: {e}")
        conn.commit()
    print("Done!")

if __name__ == "__main__":
    drop_tables()

