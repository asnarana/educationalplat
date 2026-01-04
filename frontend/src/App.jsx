import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import StartQuiz from './pages/StartQuiz';
import TakeQuiz from './pages/TakeQuiz';
import QuizResults from './pages/QuizResults';

function App() {
  return (
    <Router>
      <div className="app">
        <div className="header">
          <h1>GradeMaster</h1>
          <p>Adaptive Remediation Quiz System</p>
        </div>
        <Routes>
          <Route path="/" element={<StartQuiz />} />
          <Route path="/quiz/:quizId" element={<TakeQuiz />} />
          <Route path="/results/:attemptId" element={<QuizResults />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

