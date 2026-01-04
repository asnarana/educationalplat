# Getting Started with GradeMaster

## What is GradeMaster?

**GradeMaster** is an adaptive quiz system that helps students learn by:
- Creating personalized quizzes based on their weak areas
- Tracking progress across different topics
- Providing feedback and recommendations
- Automatically focusing on topics that need improvement

Think of it like a smart tutor that identifies what you're struggling with and gives you more practice in those areas!

---

## Quick Start Guide

### Step 1: Set Up the Backend (Python API)

1. **Open a terminal/PowerShell** in the project folder (`C:\Users\amris\educationalplat`)

2. **Create a virtual environment** (keeps dependencies organized):
   ```powershell
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   (You should see `(venv)` appear in your terminal)

4. **Install Python dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

5. **Start the backend server**:
   ```powershell
   uvicorn app.main:app --reload
   ```
   
   You should see:
   ```
   INFO:     Uvicorn running on http://127.0.0.1:8000
   ```
   
   **Keep this terminal window open!** The server needs to keep running.

6. **Test the API** (open a NEW terminal window):
   - Visit `http://localhost:8000` in your browser - you should see API info
   - Visit `http://localhost:8000/docs` - you'll see interactive API documentation

---

### Step 2: Set Up the Frontend (Web Interface)

1. **Open a NEW terminal/PowerShell** (keep the backend running in the first one!)

2. **Navigate to the frontend folder**:
   ```powershell
   cd frontend
   ```

3. **Install Node.js dependencies**:
   ```powershell
   npm install
   ```
   (Make sure you have Node.js installed - download from nodejs.org if needed)

4. **Start the frontend development server**:
   ```powershell
   npm run dev
   ```
   
   You should see:
   ```
   VITE ready in XXX ms
   ➜  Local:   http://localhost:5173/
   ```

5. **Open your browser** and go to `http://localhost:5173`

---

### Step 3: Use the Application

1. **Seed the Question Bank** (first time only):
   - In the web interface, click "Seed Question Bank" button
   - OR use the API: `POST http://localhost:8000/seed`
   - This loads sample questions into the database

2. **Start a Quiz**:
   - Enter a student ID (e.g., "alice" or "student123")
   - Select a grade level (3 or 5)
   - Click "Start Quiz"

3. **Take the Quiz**:
   - Answer all 10 questions
   - Click "Submit Quiz" when done

4. **View Results**:
   - See your score and which topics you did well/poorly on
   - Topics with scores below 80% are marked as "weak topics"

5. **Generate Next Quiz**:
   - Click "Generate Next Quiz" to get a new quiz
   - The system automatically focuses 70% of questions on your weak topics!

---

## How Everything Works

### The System Architecture

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Browser   │  ←→     │   Frontend  │  ←→     │   Backend   │
│  (You!)     │         │  (React)    │         │  (FastAPI)  │
└─────────────┘         └─────────────┘         └─────────────┘
                                                         │
                                                         ↓
                                                  ┌─────────────┐
                                                  │  Database   │
                                                  │  (SQLite)   │
                                                  └─────────────┘
```

### Key Components

1. **Backend (FastAPI)** - `app/` folder
   - Handles all quiz logic, scoring, and data storage
   - Provides REST API endpoints
   - Runs on port 8000

2. **Frontend (React)** - `frontend/` folder
   - Web interface for students
   - Communicates with backend via API
   - Runs on port 5173 (Vite default)

3. **Database (SQLite)** - `grademaster.db`
   - Stores questions, quizzes, student attempts
   - Created automatically on first run

### How Adaptive Learning Works

1. **First Quiz**: Diagnostic quiz covering all topics (5 topics × 2 questions each)

2. **Scoring**: 
   - Each answer is graded (correct/incorrect)
   - Scores are calculated per topic
   - Topics with < 80% score are marked as "weak"

3. **Next Quiz Generation**:
   - 70% of questions come from weak topics
   - 30% from other topics (for review)
   - Avoids repeating questions from recent quizzes

4. **Mastery Tracking**:
   - Student "masters" a grade level when they pass 2 consecutive quizzes with no weak topics

### API Endpoints (What the Backend Does)

- `POST /seed` - Loads sample questions into database
- `POST /quiz/generate` - Creates a new quiz for a student
- `POST /quiz/{id}/submit` - Submits answers and gets results
- `GET /student/{id}/history` - Shows all quiz history for a student
- `POST /attempt/{id}/feedback` - Gets personalized feedback (optional, needs LLM)

---

## Optional Features

### Feedback Coach (LLM-Powered Feedback)

Want personalized study recommendations? Set up an LLM provider:

**Option 1: Ollama (FREE, runs locally)**
1. Download from [ollama.ai](https://ollama.ai)
2. Install and run Ollama
3. Pull a model: `ollama pull llama2`
4. Set environment variable: `$env:LLM_PROVIDER="ollama"`
5. Restart your backend server

**Option 2: Skip it!**
- The quiz system works perfectly without LLM feedback
- All core features (quizzes, scoring, adaptive learning) work without it

### Text-to-Speech (TTS)

Want to hear questions read aloud?

1. Install: `pip install piper-tts`
2. Set: `$env:TTS_PROVIDER="piper"`
3. Restart backend

---

## Troubleshooting

### Backend won't start
- Make sure you activated the virtual environment
- Check if port 8000 is already in use
- Try: `pip install -r requirements.txt` again

### Frontend won't start
- Make sure Node.js is installed: `node --version`
- Delete `node_modules` folder and run `npm install` again
- Check if port 5173 is already in use

### Can't connect frontend to backend
- Make sure backend is running on port 8000
- Check browser console for errors (F12)
- Verify API URL in `frontend/src/api/client.js`

### Database issues
- Delete `grademaster.db` file and restart backend (it will recreate)
- Make sure you have write permissions in the project folder

---

## Testing the API Directly

You can test the API without the frontend using curl or Postman:

```powershell
# Seed questions
curl -X POST http://localhost:8000/seed

# Generate quiz
curl -X POST http://localhost:8000/quiz/generate `
  -H "Content-Type: application/json" `
  -d '{\"student_id\": \"alice\", \"grade_level\": 3, \"topics\": [\"Addition\", \"Subtraction\", \"Multiplication\", \"Division\", \"Fractions\"], \"num_questions\": 10}'

# Submit quiz (replace 1 with actual quiz_id)
curl -X POST http://localhost:8000/quiz/1/submit `
  -H "Content-Type: application/json" `
  -d '{\"answers\": {\"1\": \"8\", \"2\": \"27\", \"3\": \"6\"}}'
```

---

## Summary

**To run the application:**
1. Terminal 1: `uvicorn app.main:app --reload` (backend)
2. Terminal 2: `cd frontend && npm run dev` (frontend)
3. Browser: `http://localhost:5173`

**What it does:**
- Creates adaptive quizzes that focus on weak topics
- Tracks student progress and mastery
- Provides personalized learning paths

**Everything works out of the box!** The core quiz system doesn't need any API keys or external services. Optional features (LLM feedback, TTS) can be added later if needed.

---

## Need Help?

- Check the main `README.md` for detailed API documentation
- Visit `http://localhost:8000/docs` for interactive API docs
- Check browser console (F12) for frontend errors
- Check backend terminal for Python errors

Happy learning! 🎓

