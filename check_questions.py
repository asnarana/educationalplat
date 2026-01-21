"""Check Grade 3 and Grade 4 Reading questions in database"""
from app.db import SessionLocal
from app.models import Question
from collections import Counter

db = SessionLocal()
try:
    # Grade 3 Reading questions
    grade3 = db.query(Question).filter(
        Question.grade_level == 3,
        Question.topic.in_(['Vocabulary/Word Meaning', 'Character Analysis', 'Main Idea', 'Reading Comprehension', 'Text Structure', 'Inference'])
    ).all()
    
    # Grade 4 Reading questions
    grade4 = db.query(Question).filter(
        Question.grade_level == 4,
        Question.topic.in_(['Vocabulary/Word Meaning', 'Character Analysis', 'Main Idea', 'Reading Comprehension'])
    ).all()
    
    print(f"Grade 3 Reading: {len(grade3)} questions")
    print(f"Grade 4 Reading: {len(grade4)} questions")
    
    print(f"\nGrade 3 by topic:")
    topics3 = Counter([q.topic for q in grade3])
    for topic, count in sorted(topics3.items()):
        print(f"  {topic}: {count}")
    
    print(f"\nGrade 4 by topic:")
    topics4 = Counter([q.topic for q in grade4])
    for topic, count in sorted(topics4.items()):
        print(f"  {topic}: {count}")
    
    # Expected counts
    print(f"\nExpected:")
    print(f"  Grade 3: 40 questions (from released items)")
    print(f"  Grade 4: 40 questions (from released items)")
    
    # Check for duplicates
    grade3_ids = [q.id for q in grade3]
    grade4_ids = [q.id for q in grade4]
    
    if len(grade3_ids) != len(set(grade3_ids)):
        print(f"\n⚠️  WARNING: Grade 3 has duplicate question IDs!")
    else:
        print(f"\n✓ Grade 3: No duplicate IDs")
    
    if len(grade4_ids) != len(set(grade4_ids)):
        print(f"⚠️  WARNING: Grade 4 has duplicate question IDs!")
    else:
        print(f"✓ Grade 4: No duplicate IDs")
        
finally:
    db.close()
