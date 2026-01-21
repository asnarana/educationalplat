# Adaptive Quiz System

A quiz app that identifies weak topics and provides targeted practice. Built with FastAPI and React. Supports Grade 3-5 Math and Reading with 300+ EOG questions.

## Features

- **Multi-grade & Subject Support**: Grade 3, 4, 5 | Math & Reading
- **Adaptive Quizzes**: 10 questions evenly distributed across topics
- **Reading Comprehension**: Full passages with proper formatting (titles, authors, paragraph numbers)
- **Practice Mode**: Focus on weak topics (<80% score)
- **Randomized Questions**: No duplicates within same quiz
- **Progress Tracking**: Mastery = 2 perfect quizzes in a row
- **History & Analytics**: Paginated history, filterable by grade
- **Admin Dashboard**: View all students' statistics
- **AI Feedback**: Optional personalized tips (requires Ollama)

## Quick Start

### Backend
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Access at `http://localhost:5173`. Database auto-seeds 300+ questions on first run.

## Project Structure

```
educationalplat/
├── app/                    # FastAPI backend
│   ├── logic/             # adaptive.py, scoring.py, llm_provider.py
│   └── routes/            # quiz.py, auth.py, admin.py, etc.
├── frontend/              # React frontend
│   └── src/pages/         # Login, StartQuiz, TakeQuiz, QuizResults, etc.
├── add_*_reading_questions.py  # Scripts to add/update reading questions
└── docker-compose.yml     # Oracle DB, Redis, Prometheus, Grafana
```

## Key Components

**Backend:**
- `adaptive.py`: Question selection with balanced distribution, randomization, no duplicates
- `scoring.py`: Grading and topic score calculation
- `quiz.py`: Quiz generation, regeneration, submission endpoints
- `GET /quiz/topics`: Fetch topics by grade and subject

**Frontend:**
- `StartQuiz.jsx`: Grade/subject selection, dynamic topic loading
- `TakeQuiz.jsx`: Reading passage formatting, multi-part handling, TTS (question-only)
- `QuizResults.jsx`: Scores, weak topics, practice buttons, retake options

## Question Bank

**300+ questions from EOG tests:**
- **Grade 3**: Math (5 topics, 12+ each) + Reading (5 topics, 40 questions)
- **Grade 4**: Math + Reading (4 topics, 40 questions)
- **Grade 5**: Math (5 topics, 12+ each) + Reading (2 topics, 40 questions)

Questions are randomized using timestamp-based seeding. Retakes show different questions.

## API Endpoints

- `POST /auth/register` - Register student
- `POST /auth/login` - Login
- `GET /quiz/topics?grade_level=3&subject=Reading` - Get topics
- `POST /quiz/generate` - Create quiz
- `PUT /quiz/{id}/regenerate` - Retake (preserves subject)
- `POST /quiz/{id}/submit` - Submit answers
- `POST /quiz/practice-topic` - Practice weak topic
- `GET /student/{id}/history?grade_level=3` - Get history
- `POST /attempt/{id}/feedback` - AI feedback (optional)

## How It Works

1. **Take Quiz**: Select grade/subject → 10 randomized questions (evenly distributed)
2. **Get Results**: Topic breakdown, weak topics (<80%), mastery status
3. **Practice**: Focus on weak topics with targeted practice quizzes
4. **Retake**: Regenerates randomized questions, preserves subject

**Scoring:**
- Answers compared case-insensitively
- Topic score = weighted average
- Weak topic = score < 80%
- Mastery = 2 consecutive perfect quizzes

## Database & Infrastructure

- **Oracle Database**: Auto-creates tables, auto-seeds math questions
- **Redis**: Caches history, mastery status (5 min TTL)
- **Prometheus & Grafana**: Metrics at `/metrics`, dashboard at `http://localhost:3001`

### Database Setup

1. **Start Oracle DB** (Docker required):
```bash
docker-compose up -d oracle-db
# Wait ~60 seconds for Oracle to initialize
```

2. **Configure connection** (create `.env` file):
```
DB_HOST=localhost
DB_PORT=1521
DB_SERVICE=FREEPDB1
DB_USER=system
DB_PASSWORD=oracle123
```

3. **Auto-seed math questions**: Happens automatically on first backend start

4. **Add reading questions** (run once per grade):
```bash
# Activate virtual environment first
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Add reading questions for each grade
python add_reading_questions.py           # Grade 3 (40 questions)
python add_grade4_reading_questions.py    # Grade 4 (40 questions)
python add_grade5_reading_questions.py    # Grade 5 (40 questions)
```

5. **Verify questions**:
```bash
# Check question count via API
curl http://localhost:8000/quiz/topics?grade_level=5&subject=Reading
```

## AI Features 

### AI Feedback (Ollama)
```bash
# Install Ollama from ollama.ai
ollama pull llama2  # or 'phi' for smaller/faster model
export LLM_PROVIDER=ollama
export OLLAMA_MODEL=llama2  # or 'phi'
# Restart backend
```

**Model Recommendations:**
- **llama2**: Better quality, slower, needs ~8GB RAM
- **phi**: Faster, smaller, needs ~4GB RAM, good for quick feedback

### Text-to-Speech
Browser TTS (built-in) - click 🔊 button. Reads questions only for reading quizzes.

### Docker Services
```bash
# Start all services
docker-compose up -d

# Or start individually:
docker-compose up -d oracle-db    # Oracle Database (port 1521)
docker-compose up -d redis        # Redis cache (port 6379)
docker-compose up -d prometheus   # Metrics collection (port 9090)
docker-compose up -d grafana      # Dashboard (port 3001)

# Check status
docker-compose ps

# View logs
docker-compose logs oracle-db
```

## Design Decisions

1. **Randomization**: Timestamp-based seeding ensures unique question sets
2. **No Duplicates**: Same question won't appear twice in one quiz
3. **Even Distribution**: Questions spread evenly across all topics
4. **Subject Preservation**: Retakes maintain original subject (Math/Reading)
5. **Reading Formatting**: Passages with titles, authors, paragraph numbers, multi-part support
6. **Graceful Degradation**: Works without Redis, LLM, or monitoring
