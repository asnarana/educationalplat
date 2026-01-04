@echo off
REM Example workflow script for GradeMaster (Windows)

echo Starting GradeMaster API...
echo Make sure the server is running: uvicorn app.main:app --reload
echo.
echo 1. Seeding question bank...
curl -X POST http://localhost:8000/seed
echo.
echo.

echo 2. Generating initial quiz for student 'alice'...
curl -X POST http://localhost:8000/quiz/generate -H "Content-Type: application/json" -d "{\"student_id\": \"alice\", \"grade_level\": 3, \"topics\": [\"Addition\", \"Subtraction\", \"Multiplication\", \"Division\", \"Fractions\"], \"num_questions\": 10}"
echo.
echo.

echo 3. Submitting quiz answers (replace QUIZ_ID with actual quiz_id from step 2)...
echo Example: curl -X POST http://localhost:8000/quiz/1/submit ...
echo.
echo 4. Check student history...
curl http://localhost:8000/student/alice/history
echo.

