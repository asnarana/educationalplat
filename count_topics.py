import re

# Grade 3
with open('add_reading_questions.py', 'r', encoding='utf-8') as f:
    content = f.read()
    topics = sorted(set(re.findall(r'"topic":\s*"([^"]+)"', content)))
    print(f'Grade 3 Reading Topics: {len(topics)}')
    for t in topics:
        print(f'  - {t}')

print()

# Grade 4
with open('add_grade4_reading_questions.py', 'r', encoding='utf-8') as f:
    content = f.read()
    topics = sorted(set(re.findall(r'"topic":\s*"([^"]+)"', content)))
    print(f'Grade 4 Reading Topics: {len(topics)}')
    for t in topics:
        print(f'  - {t}')

print()

# Grade 5
with open('add_grade5_reading_questions.py', 'r', encoding='utf-8') as f:
    content = f.read()
    topics = sorted(set(re.findall(r'"topic":\s*"([^"]+)"', content)))
    print(f'Grade 5 Reading Topics: {len(topics)}')
    for t in topics:
        print(f'  - {t}')
