import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';

function StartQuiz() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [gradeLevel, setGradeLevel] = useState(3);
  const [subject, setSubject] = useState('Math'); // 'Math' or 'Reading'
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingTopics, setLoadingTopics] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const currentUser = api.getCurrentUserFromStorage();
    if (!currentUser) {
      navigate('/login');
    } else {
      setUser(currentUser);
    }
  }, [navigate]);

  // Fetch topics when grade level or subject changes
  useEffect(() => {
    const fetchTopics = async () => {
      setLoadingTopics(true);
      try {
        const data = await api.getTopics(gradeLevel, subject);
        setTopics(data.topics || []);
      } catch (err) {
        console.error('Error fetching topics:', err);
        setTopics([]);
      } finally {
        setLoadingTopics(false);
      }
    };
    
    if (user) {
      fetchTopics();
    }
  }, [gradeLevel, subject, user]);

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
      
      if (topics.length === 0) {
        setError(`No ${subject} topics available for Grade ${gradeLevel}. Please select a different grade or subject.`);
        setLoading(false);
        return;
      }

      const response = await api.generateQuiz(
        gradeLevel,
        topics,
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
              <option value={4}>Grade 4</option>
              <option value={5}>Grade 5</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="subject">Subject</label>
            <select
              id="subject"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
            >
              <option value="Math">Math</option>
              <option value="Reading">Reading</option>
            </select>
          </div>

          <div className="form-group">
            <label>Available Topics ({subject})</label>
            {loadingTopics ? (
              <div style={{ padding: '10px', background: '#f5f5f5', borderRadius: '4px' }}>
                Loading topics...
              </div>
            ) : topics.length > 0 ? (
              <div style={{ padding: '10px', background: '#f5f5f5', borderRadius: '4px' }}>
                {topics.map((topic, index) => (
                  <span key={topic} style={{ 
                    display: 'inline-block', 
                    margin: '4px 8px 4px 0',
                    padding: '4px 8px',
                    background: '#fff',
                    border: '1px solid #ddd',
                    borderRadius: '4px'
                  }}>
                    {topic}
                  </span>
                ))}
              </div>
            ) : (
              <div style={{ padding: '10px', background: '#fff3cd', borderRadius: '4px', color: '#856404' }}>
                No {subject} topics available for Grade {gradeLevel}
              </div>
            )}
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

