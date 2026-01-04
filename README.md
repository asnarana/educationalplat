# GradeMaster - Adaptive Remediation Quiz System

A FastAPI-based POC for adaptive remediation quizzes that identifies weak topics and generates personalized follow-up quizzes.

**💡 Free LLM Option**: The Feedback Coach feature works completely free using Ollama (local, no API costs). See [Feedback Coach Setup](#feedback-coach-setup) for details.

## Features

- **Diagnostic Quizzes**: 10 questions covering multiple topics (5 topics × 2 questions each)
- **Deterministic Scoring**: Answer key-based grading with weighted scores per topic
- **Adaptive Remediation**: Automatically identifies weak topics and generates focused quizzes
- **Mastery Tracking**: Tracks student progress and determines mastery (2 consecutive attempts with no weak topics)
- **Question Bank**: Pre-seeded with sample questions for Grade 3 and Grade 5
- **Feedback Coach** (Optional): LLM-powered personalized feedback with study recommendations and practice questions

## Project Structure

```
educationalplat/
├── app/                      # FastAPI backend
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # SQLAlchemy models
│   ├── db.py                # Database setup
│   ├── logic/
│   │   ├── __init__.py
│   │   ├── scoring.py       # Scoring and grading logic
│   │   ├── adaptive.py      # Adaptive quiz generation
│   │   ├── llm_provider.py  # LLM provider abstraction (Ollama/OpenAI/HF)
│   │   ├── feedback.py      # Feedback generation logic
│   │   └── tts_provider.py  # TTS provider abstraction
│   ├── prompts/
│   │   └── feedback_prompt.txt  # LLM prompt template
│   └── routes/
│       ├── __init__.py
│       ├── seed.py          # Question bank seeding
│       ├── quiz.py           # Quiz generation and submission
│       ├── history.py        # Student history
│       ├── feedback.py      # LLM feedback generation
│       └── tts.py            # Text-to-speech
├── frontend/                 # React + Vite web UI
│   ├── src/
│   │   ├── pages/           # Page components
│   │   ├── api/             # API client
│   │   └── App.jsx          # Main app
│   └── package.json
├── tests/
│   ├── __init__.py
│   ├── test_scoring.py      # Scoring logic tests
│   └── test_adaptive.py     # Adaptive logic tests
├── requirements.txt
└── README.md
```

## Installation

1. **Create a virtual environment** (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

   **For Feedback Coach feature**, install additional dependencies based on your LLM provider:
   - **Ollama** (local): `pip install requests` (already included)
   - **OpenAI**: `pip install openai`
   - **HuggingFace**: `pip install huggingface-hub`

3. **Run the application**:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### 1. Seed Question Bank
**POST** `/seed`

Seeds the database with sample questions for Grade 3 and Grade 5.

**Example:**
```bash
curl -X POST http://localhost:8000/seed
```

**Response:**
```json
{
  "message": "Successfully seeded 20 questions",
  "questions_created": 20,
  "grade_levels": [3, 5],
  "topics_per_grade": 5
}
```

### 2. Generate Quiz
**POST** `/quiz/generate`

Generates a new quiz for a student. Uses adaptive logic if the student has previous attempts.

**Request Body:**
```json
{
  "student_id": "student123",
  "grade_level": 3,
  "topics": ["Addition", "Subtraction", "Multiplication", "Division", "Fractions"],
  "num_questions": 10
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/quiz/generate \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student123",
    "grade_level": 3,
    "topics": ["Addition", "Subtraction", "Multiplication", "Division", "Fractions"],
    "num_questions": 10
  }'
```

**Response:**
```json
{
  "quiz_id": 1,
  "student_id": "student123",
  "grade_level": 3,
  "questions": [
    {
      "id": 1,
      "grade_level": 3,
      "topic": "Addition",
      "difficulty": 1,
      "weight": 1.0,
      "prompt": "What is 5 + 3?",
      "choices": ["6", "7", "8", "9"],
      "explanation": null
    },
    ...
  ],
  "created_at": "2024-01-15T10:30:00"
}
```

### 3. Submit Quiz
**POST** `/quiz/{quiz_id}/submit`

Submits answers for a quiz and receives scoring results.

**Request Body:**
```json
{
  "answers": {
    "1": "8",
    "2": "27",
    "3": "6",
    ...
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/quiz/1/submit \
  -H "Content-Type: application/json" \
  -d '{
    "answers": {
      "1": "8",
      "2": "27",
      "3": "6",
      "4": "12",
      "5": "12",
      "6": "42",
      "7": "4",
      "8": "7",
      "9": "1/2",
      "10": "1/2"
    }
  }'
```

**Response:**
```json
{
  "attempt_id": 1,
  "quiz_id": 1,
  "score_total": 0.85,
  "topic_metrics": {
    "Addition": {
      "correct": 2,
      "total": 2,
      "weighted_score": 1.0
    },
    "Subtraction": {
      "correct": 1,
      "total": 2,
      "weighted_score": 0.6
    },
    ...
  },
  "weak_topics": ["Subtraction", "Division"],
  "passed": false,
  "mastery_status": {
    "mastered": false,
    "consecutive_passes": 0,
    "required": 2
  },
  "next_quiz_recommendation": {
    "student_id": "student123",
    "grade_level": 3,
    "topics": ["Addition", "Subtraction", "Multiplication", "Division", "Fractions"],
    "num_questions": 10,
    "focus": "weak_topics",
    "weak_topics": ["Subtraction", "Division"]
  }
}
```

### 4. Get Student History
**GET** `/student/{student_id}/history`

Retrieves complete quiz and attempt history for a student.

**Example:**
```bash
curl http://localhost:8000/student/student123/history
```

**Response:**
```json
{
  "student_id": "student123",
  "summary": {
    "total_quizzes": 3,
    "total_attempts": 3,
    "average_score": 0.7833,
    "all_weak_topics": ["Subtraction", "Division"],
    "mastery_status": {
      "mastered": false,
      "consecutive_passes": 0,
      "required": 2
    }
  },
  "history": [
    {
      "quiz": {
        "id": 1,
        "student_id": "student123",
        "grade_level": 3,
        "created_at": "2024-01-15T10:30:00",
        "question_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
      },
      "attempts": [
        {
          "id": 1,
          "quiz_id": 1,
          "student_id": "student123",
          "submitted_at": "2024-01-15T10:35:00",
          "answers": {"1": "8", "2": "27", ...},
          "score_total": 0.85,
          "topic_metrics": {...},
          "weak_topics": ["Subtraction", "Division"],
          "passed": false
        }
      ]
    },
    ...
  ]
}
```

### 5. Get Feedback (Feedback Coach)
**POST** `/attempt/{attempt_id}/feedback`

Generates personalized feedback using an LLM. Provides study recommendations and practice questions for weak topics.

**Note**: This endpoint requires an LLM provider to be configured (see [Feedback Coach Setup](#feedback-coach-setup) below).

**Example:**
```bash
curl -X POST http://localhost:8000/attempt/1/feedback
```

**Response:**
```json
{
  "summary": "You did well on Addition and Multiplication! Focus on improving Subtraction and Division. Keep practicing and you'll master these topics soon.",
  "topics": {
    "Subtraction": {
      "actions": [
        "Practice subtracting two-digit numbers using number lines",
        "Review borrowing/regrouping techniques with visual examples",
        "Complete 10 subtraction problems daily focusing on accuracy"
      ],
      "practice": [
        {
          "q": "What is 45 - 18?",
          "answer": "27",
          "explanation": "Start with 45, subtract 8 to get 37, then subtract 10 more to get 27. You can also think: 45 - 18 = (45 - 10) - 8 = 35 - 8 = 27."
        },
        {
          "q": "Sarah has 32 stickers. She gives away 15. How many does she have left?",
          "answer": "17",
          "explanation": "Subtract 15 from 32: 32 - 15 = 17. You can check by adding: 17 + 15 = 32."
        }
      ]
    },
    "Division": {
      "actions": [
        "Practice division facts using flashcards",
        "Use visual aids like arrays to understand division concepts",
        "Solve word problems involving division to build real-world connections"
      ],
      "practice": [
        {
          "q": "If you have 24 cookies and want to share them equally among 6 friends, how many cookies does each friend get?",
          "answer": "4",
          "explanation": "Divide 24 by 6: 24 ÷ 6 = 4. Each friend gets 4 cookies. You can verify: 4 × 6 = 24."
        },
        {
          "q": "What is 35 ÷ 5?",
          "answer": "7",
          "explanation": "35 divided by 5 equals 7. Think: how many times does 5 go into 35? 5 × 7 = 35, so the answer is 7."
        }
      ]
    }
  }
}
```

**Important**: The LLM does NOT grade answers. Grading remains deterministic and is handled by the scoring system.

## Feedback Coach Setup

The Feedback Coach feature is optional and requires an LLM provider. Configure it using environment variables:

### Option 1: Ollama (Local - FREE & Recommended for POC) ⭐

**✅ 100% FREE - No API costs, runs entirely on your local machine**

This is the best option if you have no funding. Ollama runs models locally on your computer with zero API costs.

1. **Install Ollama**: Download from [ollama.ai](https://ollama.ai) (Windows/Mac/Linux)

2. **Start Ollama** (it runs as a local service):
   ```bash
   # On Windows, just run the installer - it starts automatically
   # On Mac/Linux, run: ollama serve
   ```

3. **Pull a free model** (downloads to your computer):
   ```bash
   ollama pull llama2
   # or for smaller/faster: ollama pull mistral
   # or for even smaller: ollama pull phi
   ```

4. **Set environment variables** (Windows PowerShell):
   ```powershell
   $env:LLM_PROVIDER="ollama"
   $env:OLLAMA_MODEL="llama2"  # Optional, defaults to "llama2"
   ```
   
   Or on Mac/Linux:
   ```bash
   export LLM_PROVIDER=ollama
   export OLLAMA_MODEL=llama2
   ```

**That's it!** No API keys, no costs, everything runs locally. The model runs on your computer's CPU/GPU.

### Option 2: OpenAI (💰 Paid - Not Recommended for POC)

**⚠️ COSTS MONEY** - Pay-per-use API (typically $0.001-0.01 per request)

1. **Get API key** from [platform.openai.com](https://platform.openai.com)

2. **Set environment variables**:
   ```bash
   export LLM_PROVIDER=openai
   export OPENAI_API_KEY=your-api-key-here
   export OPENAI_MODEL=gpt-3.5-turbo  # Optional, defaults to "gpt-3.5-turbo"
   ```

### Option 3: HuggingFace (🆓 Limited Free Tier)

**⚠️ Free tier has rate limits** - May hit limits with heavy usage

1. **Get free API key** from [huggingface.co](https://huggingface.co) (free account)

2. **Set environment variables**:
   ```bash
   export LLM_PROVIDER=huggingface
   export HUGGINGFACE_API_KEY=your-api-key-here
   export HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.1  # Optional
   ```

---

**💡 Recommendation for POC with no funding**: Use **Ollama** (Option 1). It's completely free, runs locally, and has no usage limits. The only requirement is having enough RAM (4-8GB recommended for smaller models like `phi` or `mistral`).

**Note**: If no LLM provider is configured, the feedback endpoint will return a 503 error. The rest of the API works perfectly without it - you can use all quiz features without any LLM setup.

## Text-to-Speech (TTS) Setup

The TTS feature is **completely optional** and allows you to convert quiz questions and feedback to audio. The core quiz functionality works perfectly without TTS.

### Option 1: Piper TTS (🆓 FREE - Recommended) ⭐

**✅ 100% FREE - Lightweight, fast, runs locally**

Piper is the recommended TTS option - it's lightweight, fast, and completely free.

1. **Install Piper TTS**:
   ```bash
   pip install piper-tts
   ```

2. **That's it!** Piper will automatically download voices on first use.

3. **Optional - Set environment variables**:
   ```bash
   export TTS_PROVIDER=piper
   export PIPER_VOICE=en_US-lessac-medium  # Optional, defaults to this
   ```

**Available voices** (Piper will download automatically):
- `en_US-lessac-medium` (default) - US English, medium quality
- `en_US-lessac-low` - US English, faster/lower quality
- `en_GB-alba-medium` - UK English
- Many more available - see [Piper voices](https://github.com/rhasspy/piper/blob/master/voices.md)

### Option 2: Coqui TTS (🆓 FREE - Alternative)

**✅ FREE but larger download** - Alternative option if Piper doesn't work

1. **Install Coqui TTS**:
   ```bash
   pip install TTS soundfile
   ```

2. **Set environment variables**:
   ```bash
   export TTS_PROVIDER=coqui
   export COQUI_MODEL=tts_models/en/ljspeech/tacotron2-DDC  # Optional
   ```

**Note**: Coqui TTS downloads models on first use (can be several GB).

---

**💡 Recommendation**: Use **Piper TTS** (Option 1). It's lighter, faster, and easier to set up.

**Note**: If no TTS provider is installed, the `/tts` endpoint will return a 503 error. All other quiz features work perfectly without TTS.

## TTS API Endpoint

### POST /tts

Convert text to speech audio.

**Request Body:**
```json
{
  "text": "What is 5 + 3?",
  "voice": "default"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "What is 5 + 3?", "voice": "default"}' \
  --output speech.wav
```

**Response:**
- Returns WAV audio file as binary response
- Content-Type: `audio/wav`
- Maximum text length: 5000 characters

**Status Check:**
```bash
curl http://localhost:8000/tts/status
```

Returns:
```json
{
  "available": true,
  "provider": "Piper",
  "message": "TTS is ready"
}
```

**Usage Example - Convert Quiz Question to Speech:**
```bash
# Get a quiz question
QUIZ_RESPONSE=$(curl -X POST http://localhost:8000/quiz/generate \
  -H "Content-Type: application/json" \
  -d '{"student_id": "alice", "grade_level": 3, "topics": ["Addition"], "num_questions": 1}')

# Extract question text (example)
QUESTION_TEXT="What is 5 + 3?"

# Convert to speech
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"$QUESTION_TEXT\", \"voice\": \"default\"}" \
  --output question.wav

# Play the audio file
# On Windows: start question.wav
# On Mac: afplay question.wav
# On Linux: aplay question.wav
```

## Scoring Logic

- **Question Grading**: 1 if answer matches (case-insensitive, whitespace-normalized), 0 otherwise
- **Topic Weighted Score**: `sum(weight × correct) / sum(weight)` for all questions in that topic
- **Overall Score**: `sum(weight × correct) / sum(weight)` for all questions
- **Weak Topics**: Topics with weighted_score < 0.80 (mastery threshold)

## Adaptive Rules

1. **Weak Topic Identification**: Topics with weighted_score < 0.80 are considered weak
2. **Next Quiz Generation**:
   - 70% of questions from weak topics
   - 30% from remaining topics (review)
   - Avoids repeating questions from the last 2 quizzes
3. **Mastery**: Student is considered "mastered" when they have 2 consecutive attempts with no weak topics

## Running Tests

```bash
pytest tests/
```

## Database

The application uses SQLite with the database file `grademaster.db` created in the project root. The database is automatically initialized on first startup.

## Sample Workflow

1. **Seed the question bank**:
   ```bash
   curl -X POST http://localhost:8000/seed
   ```

2. **Generate initial diagnostic quiz**:
   ```bash
   curl -X POST http://localhost:8000/quiz/generate \
     -H "Content-Type: application/json" \
     -d '{"student_id": "alice", "grade_level": 3, "topics": ["Addition", "Subtraction", "Multiplication", "Division", "Fractions"], "num_questions": 10}'
   ```

3. **Submit quiz answers**:
   ```bash
   curl -X POST http://localhost:8000/quiz/1/submit \
     -H "Content-Type: application/json" \
     -d '{"answers": {"1": "8", "2": "27", ...}}'
   ```

4. **Generate next adaptive quiz** (using recommendation from step 3):
   ```bash
   curl -X POST http://localhost:8000/quiz/generate \
     -H "Content-Type: application/json" \
     -d '{"student_id": "alice", "grade_level": 3, "topics": ["Addition", "Subtraction", "Multiplication", "Division", "Fractions"], "num_questions": 10}'
   ```

5. **Check student history**:
   ```bash
   curl http://localhost:8000/student/alice/history
   ```

6. **Get personalized feedback** (requires LLM provider):
   ```bash
   curl -X POST http://localhost:8000/attempt/1/feedback
   ```

## Web UI

A minimal React + Vite web interface is available in the `frontend/` directory. See [frontend/README.md](frontend/README.md) for setup instructions.

**Quick Start**:
```bash
cd frontend
npm install
npm run dev
```

Then open `http://localhost:5173` in your browser.

The UI provides:
- Start Quiz page to begin a new quiz
- Interactive quiz taking interface
- Results page with topic metrics and weak topics
- One-click next quiz generation

## Web UI

A minimal React + Vite web interface is available in the `frontend/` directory. See [frontend/README.md](frontend/README.md) for detailed setup instructions.

**Quick Start**:
```bash
cd frontend
npm install
npm run dev
```

Then open `http://localhost:5173` in your browser.

The UI provides:
- **Start Quiz** page to begin a new quiz
- **Interactive quiz taking** interface with multiple choice and text input
- **Results page** with topic metrics, weak topics, and mastery status
- **One-click next quiz generation** for adaptive remediation

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

