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
- Keep practicing until you get there!

## API Endpoints

### Seed Question Bank
**POST** `/seed`

Populates the database with questions. Do this once before using the app.

```bash
curl -X POST http://localhost:8000/seed
```

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

Get personalized study tips and practice questions. Requires LLM setup (see below).

## AI Feedback Setup (Optional)

The AI feedback feature is completely optional. Everything else works fine without it.

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
