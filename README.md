#  Adaptive Quiz System

A quiz app that figures out what topics you're struggling with and gives you more practice on those areas. Built with FastAPI and React.


## What It Does

- **Login/Register**: Students create accounts with username and password
- **Take quizzes**: 10 questions covering different math topics
- **See your scores**: Get a breakdown by topic so you know what you need to work on
- **Practice weak areas**: Practice quizzes focus on specific weak topics
- **Retake quizzes**: Retakes reuse the same quiz and add new attempts (different questions each time)
- **Track progress**: Shows when you've mastered a grade level (2 perfect quizzes in a row)
- **View history**: See all past quizzes with pagination support
- **Admin dashboard**: Admins can view all students' histories and statistics
- **AI feedback** : Get personalized study tips and practice questions using AI

## Project Structure

```
educationalplat/
├── app/                      # Backend (FastAPI)
│   ├── main.py              # Main app file
│   ├── models.py            # Database models
│   ├── db.py                # Database setup
│   ├── cache.py             # Redis caching utilities
│   ├── logic/
│   │   ├── scoring.py       # How we grade quizzes
│   │   ├── adaptive.py      # Logic for picking questions based on weak topics
│   │   ├── llm_provider.py  # AI stuff (Ollama via LangChain)
│   │   ├── feedback.py      # AI feedback generation
│   │   └── tts_provider.py  # Text-to-speech
│   └── routes/
│       ├── seed.py          # Populate question bank
│       ├── auth.py          # User authentication (login/register)
│       ├── admin.py         # Admin dashboard routes
│       ├── quiz.py           # Generate and submit quizzes
│       ├── history.py        # Student history
│       ├── feedback.py      # AI feedback
│       └── tts.py            # Text-to-speech
├── frontend/                 # Web UI (React)
│   ├── src/
│   │   ├── pages/           # Page components
│   │   ├── api/             # API client
│   │   └── App.jsx          # Main app
│   └── package.json
├── requirements.txt
└── README.md
```

## Architecture Overview

### Backend Files (FastAPI)

**Core Files:**
- **`app/main.py`**: Entry point. Sets up FastAPI app, CORS, includes all route modules, auto-seeds questions on startup
- **`app/models.py`**: SQLAlchemy database models (Question, Quiz, Attempt, User)
- **`app/db.py`**: Database connection setup (Oracle DB) and session management
- **`app/cache.py`**: Redis caching utilities for performance optimization

**Logic Layer (`app/logic/`):**
- **`adaptive.py`**: decides which questions to show based on student performance
  - `select_questions_for_quiz()`: Selects questions with balanced distribution (2 per topic) or single topic for practice
  - `check_mastery_status()`: Determines if student mastered the grade level
  - `get_recent_question_ids()`: Prevents showing same questions too soon
- **`scoring.py`**: Grades answers and calculates topic scores
  - `grade_quiz()`: Compares student answers to correct answers
  - `calculate_topic_scores()`: Groups questions by topic and calculates percentages
- **`llm_provider.py`**: LLM provider using LangChain ChatOllama for Ollama
  - `OllamaProvider`: Uses LangChain's ChatOllama for local AI inference
  - `get_llm_provider()`: Factory function that creates OllamaProvider instance
- **`feedback.py`**: Generates personalized AI feedback
  - `generate_feedback()`: Creates prompt and calls LLM
  - `parse_llm_response()`: Parses JSON response from AI
- **`tts_provider.py`**: Text-to-speech (optional, not currently used - frontend uses browser TTS)

**Routes (`app/routes/`):**
- **`seed.py`**: Populates question bank from `expand_questions.py`
  - `POST /seed`: Adds questions to database
  - `POST /seed/clear`: Deletes all data (for reset)
  - Auto-seeds questions on startup if database is empty
- **`auth.py`**: User authentication and authorization
  - `POST /auth/register`: Register new student account
  - `POST /auth/login`: Login with username/password
  - `POST /auth/logout`: Logout current session
  - `GET /auth/me`: Get current user info
- **`admin.py`**: Admin dashboard routes
  - `GET /admin/students`: List all students with statistics
  - `GET /admin/students/{username}/history`: View student history (admin view)
- **`quiz.py`**: Main quiz logic
  - `POST /quiz/generate`: Creates new quiz (uses `adaptive.py` to pick questions)
  - `PUT /quiz/{id}/regenerate`: Regenerates questions for existing quiz (for retakes)
  - `POST /quiz/{id}/submit`: Grades quiz (uses `scoring.py`), saves attempt
  - `POST /quiz/practice-topic`: Generates topic-specific practice quiz
- **`feedback.py`**: AI feedback endpoint
  - `POST /attempt/{id}/feedback`: Calls `feedback.py` to generate AI tips
- **`history.py`**: Student quiz history with pagination
  - `GET /student/{id}/history`: Returns paginated past quizzes and attempts
- **`tts.py`**: Text-to-speech endpoint (optional, not currently used)

### Frontend Files (React)

**Core Files:**
- **`frontend/src/main.jsx`**: React entry point, renders App component
- **`frontend/src/App.jsx`**: Main router, handles navigation between pages
- **`frontend/src/api/client.js`**: API client - all HTTP requests to backend
  - Methods like `generateQuiz()`, `submitQuiz()`, `getFeedback()`

**Pages (`frontend/src/pages/`):**
- **`Login.jsx`**: Login and registration page
  - Students can register or login with username/password
  - Admin login redirects to admin dashboard
- **`StartQuiz.jsx`**: Home page (after login)
  - Grade selection
  - Starts new quiz
  - View history button
- **`TakeQuiz.jsx`**: Quiz-taking interface
  - Displays questions, collects answers
  - Submit button sends answers to backend
  - Cancel button (for practice quizzes)
  - Has 🔊 button for text-to-speech (browser API)
- **`QuizResults.jsx`**: Results page
  - Shows scores, topic breakdown, weak topics
  - "Practice [Topic]" buttons for weak topics
  - "Retake Full Test" button (regenerates questions, adds new attempt)
  - "Retake Practice" button (regenerates practice quiz questions)
  - "Get AI Feedback" button (optional)
- **`StudentHistory.jsx`**: Student quiz history
  - Shows all quizzes with pagination
  - Separates main quizzes and practice quizzes
  - Filter by grade level
- **`AdminDashboard.jsx`**: Admin dashboard
  - Lists all students with statistics
  - View individual student histories

### How Data Flows

**1. Starting a Quiz:**
```
User → StartQuiz.jsx → client.js → POST /quiz/generate
Backend: quiz.py → adaptive.py → selects questions → returns quiz
Frontend: TakeQuiz.jsx displays questions
```

**2. Submitting a Quiz:**
```
User → TakeQuiz.jsx → client.js → POST /quiz/{id}/submit
Backend: quiz.py → scoring.py → grades answers → saves Attempt → returns results
Frontend: QuizResults.jsx displays scores and weak topics
```

**3. Retaking a Quiz:**
```
User → QuizResults.jsx → "Retake Full Test" → client.js → PUT /quiz/{id}/regenerate
Backend: quiz.py → regenerates questions for same quiz_id → updates quiz with new questions
Frontend: TakeQuiz.jsx with new questions → Submit → Adds new attempt to same quiz
```
Note: Retakes reuse the same quiz_id, so all attempts are grouped together in history.

**4. Topic Practice:**
```
User → QuizResults.jsx → "Practice [Topic]" → client.js → POST /quiz/practice-topic
Backend: quiz.py → generates questions from that topic only
Frontend: TakeQuiz.jsx → submit → QuizResults.jsx → "Retake Practice" until 100%
```

**5. AI Feedback (Optional):**
```
User → QuizResults.jsx → "Get AI Feedback" → client.js → POST /attempt/{id}/feedback
Backend: feedback.py → feedback.py → llm_provider.py → Ollama (LangChain)
         → generates JSON with tips and practice questions
Frontend: QuizResults.jsx displays AI feedback
```
 
### Component Relationships

**Backend:**
- `routes/quiz.py` depends on `logic/adaptive.py` and `logic/scoring.py`
- `routes/feedback.py` depends on `logic/feedback.py` which depends on `logic/llm_provider.py`
- All routes use `models.py` for database access via `db.py`

**Frontend:**
- All pages use `api/client.js` to talk to backend
- `App.jsx` routes between pages using React Router
- Pages store data in sessionStorage to pass between routes

**Database:**
- `Question`: Stores all quiz questions (~164 total: 20 base + 144 expanded)
- `Quiz`: Stores quiz metadata (which questions, student, grade, grade_quiz_number)
- `Attempt`: Stores student answers and scores (multiple attempts per quiz)
- `User`: Stores user accounts (username, password hash, role: student/admin)

### Key Design Decisions

1. **Authentication**: Username/password login system, admin accounts created separately
2. **Adaptive Logic**: Full tests use balanced distribution (2 per topic), practice quizzes focus on single weak topics
3. **Mastery Tracking**: 2 consecutive perfect quizzes (no weak topics) = mastery
4. **Question Selection**: Randomizes questions, avoids recent questions, allows repeats if needed
5. **Retake Logic**: Retakes regenerate questions for same quiz_id, grouping attempts together
6. **Question Bank**: ~164 questions (12+ per topic) for variety and randomization
7. **Pagination**: History uses server-side pagination for performance
8. **Caching**: Redis caches frequently accessed data (history, mastery, etc.)
9. **AI Feedback**: Optional feature, gracefully fails if LLM not configured
10. **TTS**: Uses browser API (free) instead of backend (simpler, no setup)

## Getting Started

### Backend Setup

1. **Create a virtual environment** (keeps dependencies clean):
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

2. **Install Python packages**:
```bash
pip install -r requirements.txt
```

3. **Run the backend**:
```bash
uvicorn app.main:app --reload
```

The API will be at `http://localhost:8000`

### Frontend Setup

1. **Install Node packages**:
```bash
cd frontend
npm install
```

2. **Run the frontend**:
```bash
npm run dev
```

Open `http://localhost:5173` in your browser.

### First Time Setup

1. **Question bank auto-seeds**: The database automatically seeds questions on startup if empty. No manual seeding needed!

**What gets seeded:**
- ~164 questions total (20 base + 144 expanded)
- Grade 3: 12+ questions per topic (Addition, Subtraction, Multiplication, Division, Fractions)
- Grade 5: 12+ questions per topic (Algebra, Geometry, Decimals, Percentages, Word Problems)

**Manual seeding** (if needed):
```bash
curl -X POST http://localhost:8000/seed
```

2. **Create an account**: 
   - Go to `/login` 
   - Click "Register" to create a student account
   - Or login as admin (username: `admin`, password: `123`)

3. **Start taking quizzes**: After login, pick a grade level and click "Start Quiz"

## How It Works

### Taking a Quiz

1. You get 10 questions covering different topics
2. Answer them all and submit
3. See your score and which topics you need to work on

### Adaptive Practice

- If you score below 80% on a topic, it's marked as "weak"
- Full tests use balanced distribution (2 questions per topic) for comprehensive assessment
- Practice quizzes focus on a single weak topic for targeted improvement

### Mastery

- You've "mastered" a grade level when you pass 2 quizzes in a row with no weak topics

## API Endpoints

### Seed Question Bank
**POST** `/seed`

Populates the database with questions. Do this once before using the app.

```bash
curl -X POST http://localhost:8000/seed
```

**What Gets Seeded:**

After seeding, your database will contain approximately **164 questions** total:

**Grade 3** (5 topics):
- **Addition**: 12+ questions
- **Subtraction**: 12+ questions  
- **Multiplication**: 12+ questions
- **Division**: 12+ questions
- **Fractions**: 12+ questions

**Grade 5** (5 topics):
- **Algebra**: 12+ questions
- **Geometry**: 12+ questions
- **Decimals**: 12+ questions
- **Percentages**: 12+ questions
- **Word Problems**: 12+ questions

**Why this matters:**
- Each topic has enough questions for variety and randomization
- Questions are randomized on each quiz generation
- Retakes will show different questions each time
- With 12+ questions per topic, you can take many quizzes with variety

### Authentication
**POST** `/auth/register` - Register new student account
**POST** `/auth/login` - Login with username/password
**POST** `/auth/logout` - Logout current session
**GET** `/auth/me` - Get current user info

### Generate Quiz
**POST** `/quiz/generate`

Creates a new quiz. If you've taken quizzes before, it automatically focuses on your weak topics. Questions are randomized for variety.

### Regenerate Quiz Questions
**PUT** `/quiz/{quiz_id}/regenerate`

Regenerates questions for an existing quiz (for retakes). Updates the quiz with new randomized questions while keeping the same quiz_id, so attempts are grouped together.

**Request:**
```json
{
  "student_id": "student123",
  "grade_level": 3,
  "topics": ["Addition", "Subtraction", "Multiplication", "Division", "Fractions"],
  "num_questions": 10
}
```

### Submit Quiz
**POST** `/quiz/{quiz_id}/submit`

Submit your answers and get results.

**Request:**
```json
{
  "answers": {
    "1": "8",
    "2": "27",
    "3": "6"
  }
}
```

**Response includes:**
- Overall score
- Score per topic
- List of weak topics
- Mastery status
- Recommendation for next quiz

### Get Student History
**GET** `/student/{student_id}/history?page=1&page_size=10&grade_level=3`

See all your past quizzes and attempts with pagination support. Supports filtering by grade level.

### Admin Endpoints
**GET** `/admin/students` - List all students with statistics (admin only)
**GET** `/admin/students/{username}/history` - View student history (admin only)

### Get AI Feedback (Optional)
**POST** `/attempt/{attempt_id}/feedback`

Get personalized study tips and practice questions. Requires LLM setup 

### Using Ollama (Free, Recommended)  - This is not working here , I need help properly integrating this LLM or any type of LLM for results(areas student should be able to improve on).

Ollama runs AI models on your computer - no API keys, no costs, completely free.

1. **Download Ollama**: Get it from [ollama.ai](https://ollama.ai)

2. **Start Ollama**: On Windows, it starts automatically after install. On Mac/Linux, run:
   ```bash
   ollama serve
   ```

3. **Download a model** (this downloads to your computer):
   ```bash
   ollama pull phi
   # or for better quality (but slower): ollama pull llama2
   ```

4. **Set environment variables** (Windows PowerShell):
   ```powershell
   $env:LLM_PROVIDER="ollama"
   $env:OLLAMA_MODEL="phi"
   ```
   
   On Mac/Linux:
   ```bash
   export LLM_PROVIDER=ollama
   export OLLAMA_MODEL=phi
   ```

5. **Restart your backend** - that's it!

The model runs on your computer, so you need enough RAM (4-8GB recommended for smaller models like `phi`).

**Note**: The app uses Ollama via LangChain ChatOllama. For more information, see the [LangChain Ollama documentation](https://python.langchain.com/docs/integrations/chat/ollama).

## Text-to-Speech (Optional)

The TTS feature lets you listen to questions and feedback. It's completely optional - the app works fine without it.

### Browser TTS (Recommended - Already Works!)

The frontend uses your browser's built-in text-to-speech. Just click the 🔊 button next to questions - no setup needed

### Backend TTS (Optional)

If you want backend TTS (for API use), you can install Piper TTS:

```bash
pip install piper-tts 
```
I tried to use the pip install above but was not working no matter how many times I installed it. 


## How Scoring Works

- **Grading**: Answers are compared (case-insensitive, whitespace ignored)
- **Topic Score**: Weighted average of all questions in that topic
- **Overall Score**: Weighted average of all questions
- **Weak Topics**: Any topic with score < 80%

## Adaptive Rules

1. **Weak topics**: Topics where you scored < 80%
2. **Full tests**: Balanced distribution (2 questions per topic) for comprehensive assessment
3. **Practice quizzes**: Single-topic focus for targeted improvement on weak areas
4. **Mastery**: Pass 2 quizzes in a row with no weak topics

## Database

Uses Oracle Database. Connection is configured via environment variables. The database automatically creates tables and sequences on startup. Questions are auto-seeded if the database is empty.

## Redis Caching (Optional)

Redis is used to cache frequently accessed data for improved performance. The app works without Redis, but caching makes it faster for students with many quizzes.

### Cache Types Implemented

1. **Student History** - Caches quiz history by student and grade (5 min TTL)
2. **Mastery Status** - Caches mastery check results (2 min TTL)
3. **Recent Question IDs** - Caches recently used questions to avoid repeats (1 min TTL)
4. **Quiz Type** - Caches whether quiz is "practice" or "full" (10 min TTL)
5. **Admin Student List** - Caches admin dashboard student statistics (2 min TTL)

### How It Works

- Cache is checked first before database queries
- If found in cache, data is returned instantly
- If not found, database is queried and result is stored in cache
- Caches are automatically invalidated when new quizzes/attempts are created

### Setup

Redis is included in `docker-compose.yml`. Start with:
```bash
docker-compose up -d
```

Or install Redis manually and start `redis-server`. The app  falls back to database queries if Redis is unavailable.

## Monitoring with Prometheus & Grafana (Optional)

The app includes Prometheus metrics and Grafana dashboards for monitoring performance and educational metrics.

### What Gets Monitored

**API Performance:**
- HTTP request rates and response times
- Error rates by endpoint
- Request duration percentiles

**Educational Metrics:**
- Quizzes generated (full vs practice)
- Quiz submissions and pass rates
- Score distributions by grade level
- Weak topics tracking
- LLM feedback request performance

### Quick Setup

1. **Install Prometheus client** (already in requirements.txt):
```bash
pip install prometheus-client
```

2. **Start Prometheus and Grafana**:
```bash
docker-compose up -d
```

3. **Access dashboards:**
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Metrics endpoint**: http://localhost:8000/metrics

4. **View metrics**: The Grafana dashboard will automatically load showing:
   - HTTP request rates and latency
   - Quiz generation and submission rates
   - Score distributions
   - Weak topics analysis
   - LLM performance (if using AI feedback)

### Manual Setup (Without Docker)

If you prefer not to use Docker:

1. **Download Prometheus**: https://prometheus.io/download/
2. **Download Grafana**: https://grafana.com/grafana/download
3. **Configure Prometheus** to scrape `http://localhost:8000/metrics`
4. **Import the dashboard** from `monitoring/grafana/dashboards/grademaster-dashboard.json`

### Metrics Endpoint

The FastAPI app exposes metrics at `/metrics` in Prometheus format. You can view raw metrics:
```bash
curl http://localhost:8000/metrics
```

