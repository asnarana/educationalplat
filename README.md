#  Adaptive Quiz System

A quiz app that figures out what topics you're struggling with and gives you more practice on those areas. Built with FastAPI and React.

**Note**: The AI feedback feature is totally optional and works for free with Ollama ( right now its this, we can change later on)

## What It Does

- **Take quizzes**: 10 questions covering different math topics
- **See your scores**: Get a breakdown by topic so you know what you need to work on
- **Practice weak areas**: The system automatically gives you more questions on topics you're struggling with (70% focus on weak topics)
- **Track progress**: Shows when you've mastered a grade level (2 perfect quizzes in a row)
- **AI feedback** (optional): Get personalized study tips and practice questions using AI

## Project Structure

```
educationalplat/
├── app/                      # Backend (FastAPI)
│   ├── main.py              # Main app file
│   ├── models.py            # Database models
│   ├── db.py                # Database setup
│   ├── logic/
│   │   ├── scoring.py       # How we grade quizzes
│   │   ├── adaptive.py      # Logic for picking questions based on weak topics
│   │   ├── llm_provider.py  # AI stuff (Ollama/OpenAI)
│   │   ├── feedback.py      # AI feedback generation
│   │   └── tts_provider.py  # Text-to-speech
│   └── routes/
│       ├── seed.py          # Populate question bank
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
- **`app/main.py`**: Entry point. Sets up FastAPI app, CORS, includes all route modules
- **`app/models.py`**: SQLAlchemy database models (Question, Quiz, Attempt, Student)
- **`app/db.py`**: Database connection setup (SQLite) and session management

**Logic Layer (`app/logic/`):**
- **`adaptive.py`**: The "brain" - decides which questions to show based on student performance
  - `select_questions_for_quiz()`: Picks 70% from weak topics, 30% from others
  - `check_mastery_status()`: Determines if student mastered the grade level
  - `get_recent_question_ids()`: Prevents showing same questions too soon
- **`scoring.py`**: Grades answers and calculates topic scores
  - `grade_quiz()`: Compares student answers to correct answers
  - `calculate_topic_scores()`: Groups questions by topic and calculates percentages
- **`llm_provider.py`**: Abstraction layer for AI models (Ollama, OpenAI, HuggingFace)
  - `OllamaProvider`: Uses LangChain's ChatOllama for local AI
  - `get_llm_provider()`: Factory function that picks provider based on env vars
- **`feedback.py`**: Generates personalized AI feedback
  - `generate_feedback()`: Creates prompt and calls LLM
  - `parse_llm_response()`: Parses JSON response from AI
- **`tts_provider.py`**: Text-to-speech (optional, not currently used - frontend uses browser TTS)

**Routes (`app/routes/`):**
- **`seed.py`**: Populates question bank from `expand_questions.py`
  - `POST /seed`: Adds questions to database
  - `POST /seed/clear`: Deletes all data (for reset)
- **`quiz.py`**: Main quiz logic
  - `POST /quiz/generate`: Creates new quiz (uses `adaptive.py` to pick questions)
  - `POST /quiz/{id}/submit`: Grades quiz (uses `scoring.py`), saves attempt
  - `POST /quiz/practice-topic`: Generates topic-specific practice quiz
- **`feedback.py`**: AI feedback endpoint
  - `POST /attempt/{id}/feedback`: Calls `feedback.py` to generate AI tips
- **`history.py`**: Student quiz history
  - `GET /student/{id}/history`: Returns all past quizzes and attempts
- **`tts.py`**: Text-to-speech endpoint (optional, not currently used)

### Frontend Files (React)

**Core Files:**
- **`frontend/src/main.jsx`**: React entry point, renders App component
- **`frontend/src/App.jsx`**: Main router, handles navigation between pages
- **`frontend/src/api/client.js`**: API client - all HTTP requests to backend
  - Methods like `generateQuiz()`, `submitQuiz()`, `getFeedback()`

**Pages (`frontend/src/pages/`):**
- **`StartQuiz.jsx`**: Home page
  - Student ID input, grade selection
  - "Seed Question Bank" button
  - Starts new quiz
- **`TakeQuiz.jsx`**: Quiz-taking interface
  - Displays questions, collects answers
  - Submit button sends answers to backend
  - Has 🔊 button for text-to-speech (browser API)
- **`QuizResults.jsx`**: Results page
  - Shows scores, topic breakdown, weak topics
  - "Practice [Topic]" buttons for weak topics
  - "Retake Full Test" button (70% focus on weak topics)
  - "Get AI Feedback" button (optional)

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

**3. Retaking with Focus on Weak Topics:**
```
User → QuizResults.jsx → "Retake Full Test" → client.js → POST /quiz/generate
Backend: quiz.py → adaptive.py → gets weak topics from last attempt
         → select_questions_for_quiz() → 70% from weak, 30% from others
Frontend: TakeQuiz.jsx with new questions
```

**4. Topic Practice:**
```
User → QuizResults.jsx → "Practice [Topic]" → client.js → POST /quiz/practice-topic
Backend: quiz.py → generates questions from that topic only
Frontend: TakeQuiz.jsx → submit → QuizResults.jsx → "Retake Practice" until 100%
```

**5. AI Feedback (Optional):**
```
User → QuizResults.jsx → "Get AI Feedback" → client.js → POST /attempt/{id}/feedback
Backend: feedback.py → feedback.py → llm_provider.py → Ollama/OpenAI
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
- `Question`: Stores all quiz questions
- `Quiz`: Stores quiz metadata (which questions, student, grade)
- `Attempt`: Stores student answers and scores
- `Student`: Stores student info (currently just ID)

### Key Design Decisions

1. **Adaptive Logic**: Weak topics (< 80%) get 70% focus on retakes
2. **Mastery Tracking**: 2 consecutive perfect quizzes (no weak topics) = mastery
3. **Question Selection**: Avoids recent questions, allows repeats if needed
4. **AI Feedback**: Optional feature, gracefully fails if LLM not configured
5. **TTS**: Uses browser API (free) instead of backend (simpler, no setup)

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

1. **Seed the question bank**: Click "Seed Question Bank" on the home page, or:
```bash
curl -X POST http://localhost:8000/seed
```

**Why do I need to seed?**
The database starts empty. Without seeding, there are no questions to generate quizzes from. The system needs a question bank with questions for each topic and grade level. Seeding populates the database with questions so the app can:
- Generate quizzes with all 5 topics represented (at least 2 questions per topic)
- Avoid errors when trying to create quizzes
- Ensure there are enough questions even after taking multiple quizzes (some questions get excluded to prevent repeats)

**Note**: You only need to seed once. If you want to reset everything (clear all quizzes, attempts, and questions), you can:

**Option 1: Use the frontend** - If the database already has questions, the "Seed Question Bank" button will offer to clear and reseed.

**Option 2: Clear manually via API**:
```bash
curl -X POST http://localhost:8000/seed/clear
```
This deletes all questions, quizzes, and attempts. Then seed again with:
```bash
curl -X POST http://localhost:8000/seed
```

**Option 3: Delete the database file** - You can also just delete `grademaster.db` from the project root, and it will be recreated when you seed.

2. **Start taking quizzes**: Enter a student ID, pick a grade level, and click "Start Quiz"

## How It Works

### Taking a Quiz

1. You get 10 questions covering different topics
2. Answer them all and submit
3. See your score and which topics you need to work on

### Adaptive Practice

- If you score below 80% on a topic, it's marked as "weak"
- When you retake a quiz, 70% of questions come from your weak topics
- The other 30% are from topics you're doing well on (for review)

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

After seeding, your database will contain approximately **60 questions** total:

**Grade 3** (5 topics):
- **Addition**: ~6 questions
- **Subtraction**: ~6 questions  
- **Multiplication**: ~6 questions
- **Division**: ~6 questions
- **Fractions**: ~6 questions

**Grade 5** (5 topics):
- **Algebra**: ~6 questions
- **Geometry**: ~6 questions
- **Decimals**: ~6 questions
- **Percentages**: ~6 questions
- **Word Problems**: ~6 questions

**Why this matters:**
- Each topic has enough questions to generate quizzes with all topics represented
- After taking multiple quizzes, some questions get excluded to prevent repeats
- With ~6 questions per topic, you can take several quizzes before needing to reseed
- If you see errors or missing topics, clear and reseed to get a fresh question bank

### Generate Quiz
**POST** `/quiz/generate`

Creates a new quiz. If you've taken quizzes before, it automatically focuses on your weak topics.

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
**GET** `/student/{student_id}/history`

See all your past quizzes and attempts.

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

### Using OpenAI (Costs Money)

If you want to use OpenAI instead:

1. Get an API key from [platform.openai.com](https://platform.openai.com)
2. Set environment variables:
   ```bash
   export LLM_PROVIDER=openai
   export OPENAI_API_KEY=your-key-here
   ```

**Note**: OpenAI charges per request, so this will cost money. Ollama is free.

### Using HuggingFace (Free but Limited)

1. Get a free API key from [huggingface.co](https://huggingface.co)
2. Set environment variables:
   ```bash
   export LLM_PROVIDER=huggingface
   export HUGGINGFACE_API_KEY=your-key-here
   ```

**Note**: Free tier has rate limits, so you might hit limits with heavy use.

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
2. **Next quiz**: 70% questions from weak topics, 30% from other topics
3. **Mastery**: Pass 2 quizzes in a row with no weak topics

## Database

Uses SQLite - the database file `grademaster.db` is created automatically in the project root. No setup needed.

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
- **Grafana**: http://localhost:3000 (admin/admin)
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

**Note**: Monitoring is completely optional - the app works fine without it!
