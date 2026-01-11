import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';

function StartQuiz() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [gradeLevel, setGradeLevel] = useState(3);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const currentUser = api.getCurrentUserFromStorage();
    if (!currentUser) {
      navigate('/login');
    } else {
      setUser(currentUser);
    }
  }, [navigate]);

  const topics = {
    3: ['Addition', 'Subtraction', 'Multiplication', 'Division', 'Fractions'],
    5: ['Algebra', 'Geometry', 'Decimals', 'Percentages', 'Word Problems'],
  };

  const handleStartQuiz = async (e) => {
    e.preventDefault();
    if (!user) {
      navigate('/login');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Clear any practice markers when starting a new main test
      sessionStorage.removeItem('current_practice_original_attempt');
      
      const response = await api.generateQuiz(
        gradeLevel,
        topics[gradeLevel],
        10
        // studentId not needed - will use authenticated user's username automatically
      );
      // Store quiz in sessionStorage for TakeQuiz to access
      sessionStorage.setItem(`quiz_${response.quiz_id}`, JSON.stringify(response));
      navigate(`/quiz/${response.quiz_id}`);
    } catch (err) {
      setError(err.message || 'Failed to generate quiz');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h2>Start New Quiz</h2>
        {user && (
          <p style={{ marginBottom: '20px', color: '#666' }}>
            Welcome, <strong>{user.username}</strong>! Select a grade level to begin an adaptive quiz.
          </p>
        )}

        {error && <div className="error">{error}</div>}

        <form onSubmit={handleStartQuiz}>
          <div className="form-group">
            <label htmlFor="gradeLevel">Grade Level</label>
            <select
              id="gradeLevel"
              value={gradeLevel}
              onChange={(e) => setGradeLevel(Number(e.target.value))}
            >
              <option value={3}>Grade 3</option>
              <option value={5}>Grade 5</option>
            </select>
          </div>

          <div className="form-group">
            <label>Topics</label>
            <div style={{ padding: '10px', background: '#f5f5f5', borderRadius: '4px' }}>
              {topics[gradeLevel].join(', ')}
            </div>
          </div>

          <div className="actions">
            <button type="submit" className="btn" disabled={loading}>
              {loading ? 'Generating Quiz...' : 'Start Quiz'}
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => {
                if (!user || !user.username) {
                  alert('Please login first before viewing history');
                  navigate('/login');
                  return;
                }
                navigate(`/history/${user.username}`);
              }}
            >
              View Student History
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default StartQuiz;

