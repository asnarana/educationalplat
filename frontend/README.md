# GradeMaster Frontend

Minimal React + Vite web UI for the GradeMaster adaptive quiz system.

## Features

- **Start Quiz**: Enter student ID and grade level to generate a quiz
- **Take Quiz**: Answer questions with multiple choice or text input
- **View Results**: See topic metrics, weak topics, and mastery status
- **Generate Next Quiz**: Automatically generate next quiz focused on weak topics

## Setup

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**:
   ```bash
   npm run dev
   ```

   The UI will be available at `http://localhost:3000`

3. **Make sure the FastAPI backend is running**:
   ```bash
   # In the project root
   uvicorn app.main:app --reload
   ```

   Backend should be at `http://localhost:8000`

## Configuration

The frontend is configured to proxy API requests to the backend. If your backend runs on a different port, update `vite.config.js`:

```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8000',  // Change this
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, '')
  }
}
```

Or set the `VITE_API_URL` environment variable:

```bash
VITE_API_URL=http://localhost:8000 npm run dev
```

## Usage Flow

1. **Start Quiz Page** (`/`):
   - Enter student ID
   - Select grade level (3 or 5)
   - Click "Start Quiz" or "Seed Question Bank" first

2. **Take Quiz Page** (`/quiz/:quizId`):
   - Answer all questions
   - Click "Submit Quiz" when done

3. **Results Page** (`/results/:attemptId`):
   - View overall score and topic metrics
   - See weak topics that need improvement
   - Click "Generate Next Quiz" to continue with adaptive remediation

## Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── client.js          # API client for FastAPI endpoints
│   ├── pages/
│   │   ├── StartQuiz.jsx       # Start quiz page
│   │   ├── TakeQuiz.jsx        # Quiz taking page
│   │   └── QuizResults.jsx     # Results page
│   ├── App.jsx                 # Main app with routing
│   ├── main.jsx                # Entry point
│   └── index.css               # Minimal styling
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

## Notes

- Uses sessionStorage to persist quiz and results data between pages
- Minimal styling focused on functionality
- No external UI libraries - pure React + CSS
- Responsive design for desktop and mobile

