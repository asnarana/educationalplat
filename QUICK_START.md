# Quick Start - GradeMaster

## 🚀 Run in 3 Steps

### 1. Backend (Terminal 1)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```
✅ Backend running at `http://localhost:8000`

### 2. Frontend (Terminal 2 - NEW WINDOW)
```powershell
cd frontend
npm install
npm run dev
```
✅ Frontend running at `http://localhost:5173`

### 3. Use It!
- Open browser: `http://localhost:5173`
- Click "Seed Question Bank" (first time only)
- Enter student ID and grade level
- Click "Start Quiz"
- Answer questions and submit!

---

## 📋 What It Does

**GradeMaster** = Smart Quiz System

1. **Takes a quiz** → Identifies weak topics
2. **Generates next quiz** → Focuses 70% on weak topics
3. **Tracks progress** → Shows mastery status
4. **Adapts automatically** → Personalizes learning path

---

## 🏗️ Architecture

```
Browser → React Frontend (port 5173) → FastAPI Backend (port 8000) → SQLite Database
```

---

## ✅ Everything Works!

- ✅ Quiz generation
- ✅ Answer submission & scoring
- ✅ Adaptive learning (weak topic focus)
- ✅ Progress tracking
- ✅ Mastery detection

**Optional (not required):**
- LLM feedback (needs Ollama/OpenAI setup)
- Text-to-speech (needs piper-tts)

---

## 🆘 Quick Fixes

**Backend error?**
- Activate venv: `.\venv\Scripts\Activate.ps1`
- Reinstall: `pip install -r requirements.txt`

**Frontend error?**
- Check Node.js: `node --version`
- Reinstall: `cd frontend && npm install`

**Can't connect?**
- Backend must be running on port 8000
- Frontend must be running on port 5173
- Check both terminal windows!

---

## 📚 More Info

See `GETTING_STARTED.md` for detailed instructions.
See `README.md` for API documentation.


