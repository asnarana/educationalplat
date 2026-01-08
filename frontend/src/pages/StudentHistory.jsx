import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../api/client';

function StudentHistory() {
  const { studentId, gradeLevel } = useParams();
  const navigate = useNavigate();
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [inputStudentId, setInputStudentId] = useState(studentId || '');
  const [inputGradeLevel, setInputGradeLevel] = useState(gradeLevel ? parseInt(gradeLevel) : 3);

  useEffect(() => {
    if (studentId && gradeLevel) {
      loadHistory(studentId, parseInt(gradeLevel));
    } else {
      setLoading(false);
    }
  }, [studentId, gradeLevel]);

  const loadHistory = async (sid, grade) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getStudentHistory(sid, grade);
      setHistory(data);
    } catch (err) {
      setError(err.message || 'Failed to load student history');
      console.error('Error loading history:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleViewHistory = (e) => {
    e.preventDefault();
    if (inputStudentId.trim() && inputGradeLevel) {
      navigate(`/history/${inputStudentId}/${inputGradeLevel}`);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const formatScore = (score) => {
    return (score * 100).toFixed(1) + '%';
  };

  if (!studentId) {
    return (
      <div style={{ maxWidth: '800px', margin: '2rem auto', padding: '2rem' }}>
        <h1>View Student History</h1>
        <p style={{ marginBottom: '1rem', color: '#666' }}>
          Enter student ID and grade level to view history. The same student ID can have separate histories for different grade levels.
        </p>
        <form onSubmit={handleViewHistory} style={{ marginBottom: '2rem' }}>
          <div style={{ marginBottom: '1rem' }}>
            <label htmlFor="studentId" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
              Student ID:
            </label>
            <input
              id="studentId"
              type="text"
              value={inputStudentId}
              onChange={(e) => setInputStudentId(e.target.value)}
              placeholder="Enter student ID"
              style={{
                padding: '0.5rem',
                fontSize: '1rem',
                width: '100%',
                maxWidth: '300px',
                border: '1px solid #ccc',
                borderRadius: '4px'
              }}
              required
            />
          </div>
          <div style={{ marginBottom: '1rem' }}>
            <label htmlFor="gradeLevel" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
              Grade Level:
            </label>
            <select
              id="gradeLevel"
              value={inputGradeLevel}
              onChange={(e) => setInputGradeLevel(Number(e.target.value))}
              style={{
                padding: '0.5rem',
                fontSize: '1rem',
                width: '100%',
                maxWidth: '300px',
                border: '1px solid #ccc',
                borderRadius: '4px'
              }}
              required
            >
              <option value={3}>Grade 3</option>
              <option value={5}>Grade 5</option>
            </select>
          </div>
          <button
            type="submit"
            style={{
              padding: '0.5rem 1.5rem',
              fontSize: '1rem',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            View History
          </button>
        </form>
        <button
          onClick={() => navigate('/')}
          style={{
            padding: '0.5rem 1rem',
            fontSize: '0.9rem',
            backgroundColor: '#6c757d',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Back to Home
        </button>
      </div>
    );
  }

  if (loading) {
    return (
      <div style={{ maxWidth: '1200px', margin: '2rem auto', padding: '2rem', textAlign: 'center' }}>
        <p>Loading history...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ maxWidth: '1200px', margin: '2rem auto', padding: '2rem' }}>
        <div style={{ padding: '1rem', backgroundColor: '#f8d7da', color: '#721c24', borderRadius: '4px', marginBottom: '1rem' }}>
          <strong>Error:</strong> {error}
        </div>
        <button
          onClick={() => navigate('/')}
          style={{
            padding: '0.5rem 1rem',
            fontSize: '0.9rem',
            backgroundColor: '#6c757d',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Back to Home
        </button>
      </div>
    );
  }

  if (!history || !history.history || history.history.length === 0) {
    return (
      <div style={{ maxWidth: '1200px', margin: '2rem auto', padding: '2rem' }}>
        <h1>Student History: {studentId} (Grade {gradeLevel})</h1>
        <p style={{ fontSize: '1.1rem', marginBottom: '2rem' }}>
          No quiz history found for this student at Grade {gradeLevel}.
        </p>
        <button
          onClick={() => navigate('/')}
          style={{
            padding: '0.5rem 1rem',
            fontSize: '0.9rem',
            backgroundColor: '#6c757d',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Back to Home
        </button>
      </div>
    );
  }

  const { summary, history: quizHistory } = history;

  return (
      <div style={{ maxWidth: '1200px', margin: '2rem auto', padding: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <h1>Student History: {studentId} (Grade {gradeLevel})</h1>
        <button
          onClick={() => navigate('/')}
          style={{
            padding: '0.5rem 1rem',
            fontSize: '0.9rem',
            backgroundColor: '#6c757d',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Back to Home
        </button>
      </div>

      {/* Summary Section */}
      <div style={{
        backgroundColor: '#f8f9fa',
        padding: '1.5rem',
        borderRadius: '8px',
        marginBottom: '2rem',
        border: '1px solid #dee2e6'
      }}>
        <h2 style={{ marginTop: 0, marginBottom: '1rem' }}>Summary</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <div>
            <strong>Total Quizzes:</strong> {summary.total_quizzes}
          </div>
          <div>
            <strong>Full Quizzes:</strong> {summary.full_quizzes || 0}
          </div>
          <div>
            <strong>Practice Quizzes:</strong> {summary.practice_quizzes || 0}
          </div>
          <div>
            <strong>Total Attempts:</strong> {summary.total_attempts}
          </div>
          <div>
            <strong>Average Score:</strong> {formatScore(summary.average_score)}
          </div>
          <div>
            <strong>All Weak Topics:</strong> {summary.all_weak_topics.length > 0 
              ? summary.all_weak_topics.join(', ')
              : 'None (all mastered!)'}
          </div>
        </div>

        {/* Mastery Status by Grade */}
        {Object.keys(summary.mastery_by_grade).length > 0 && (
          <div style={{ marginTop: '1.5rem' }}>
            <h3 style={{ marginBottom: '0.5rem' }}>Mastery Status by Grade Level:</h3>
            {Object.entries(summary.mastery_by_grade).map(([grade, mastery]) => (
              <div key={grade} style={{ marginBottom: '0.5rem', padding: '0.5rem', backgroundColor: mastery.mastered ? '#d4edda' : '#fff3cd', borderRadius: '4px' }}>
                <strong>Grade {grade}:</strong> {mastery.mastered ? (
                  <span style={{ color: '#155724' }}>✓ Mastered ({mastery.consecutive_passes}/{mastery.required} perfect quizzes)</span>
                ) : (
                  <span style={{ color: '#856404' }}>In Progress ({mastery.consecutive_passes}/{mastery.required} perfect quizzes)</span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Quiz History */}
      <h2 style={{ marginBottom: '1rem' }}>Quiz History</h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        {quizHistory.map((item, idx) => {
          const { quiz, attempts } = item;
          return (
            <div
              key={quiz.id}
              style={{
                border: '1px solid #dee2e6',
                borderRadius: '8px',
                padding: '1.5rem',
                backgroundColor: 'white'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                    <h3 style={{ margin: 0 }}>Quiz #{quiz.id}</h3>
                    {quiz.quiz_type === 'practice' ? (
                      <span style={{
                        padding: '0.25rem 0.5rem',
                        backgroundColor: '#e3f2fd',
                        color: '#1565c0',
                        borderRadius: '4px',
                        fontSize: '0.85rem',
                        fontWeight: 'bold'
                      }}>
                        PRACTICE: {quiz.practice_topic}
                      </span>
                    ) : (
                      <span style={{
                        padding: '0.25rem 0.5rem',
                        backgroundColor: '#f3e5f5',
                        color: '#6a1b9a',
                        borderRadius: '4px',
                        fontSize: '0.85rem',
                        fontWeight: 'bold'
                      }}>
                        FULL QUIZ
                      </span>
                    )}
                  </div>
                  <p style={{ margin: 0, color: '#6c757d' }}>
                    Grade {quiz.grade_level} • Created: {formatDate(quiz.created_at)}
                  </p>
                  <p style={{ margin: '0.5rem 0 0 0', color: '#6c757d' }}>
                    Questions: {quiz.question_ids.length}
                    {quiz.quiz_type === 'practice' && quiz.practice_topic && (
                      <span> • Topic: <strong>{quiz.practice_topic}</strong></span>
                    )}
                  </p>
                </div>
              </div>

              {attempts.length > 0 ? (
                <div>
                  <h4 style={{ marginBottom: '0.75rem' }}>Attempts ({attempts.length}):</h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {attempts.map((attempt) => (
                      <div
                        key={attempt.id}
                        style={{
                          padding: '1rem',
                          backgroundColor: attempt.passed ? '#d4edda' : '#fff3cd',
                          borderRadius: '6px',
                          border: `1px solid ${attempt.passed ? '#c3e6cb' : '#ffeaa7'}`,
                          cursor: 'pointer'
                        }}
                        onClick={() => navigate(`/results/${attempt.id}`)}
                        onMouseEnter={(e) => e.currentTarget.style.opacity = '0.9'}
                        onMouseLeave={(e) => e.currentTarget.style.opacity = '1'}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                          <div>
                            <strong>Attempt #{attempt.id}</strong>
                            <span style={{ marginLeft: '1rem', color: '#6c757d' }}>
                              Submitted: {formatDate(attempt.submitted_at)}
                            </span>
                          </div>
                          <div style={{
                            fontSize: '1.2rem',
                            fontWeight: 'bold',
                            color: attempt.passed ? '#155724' : '#856404'
                          }}>
                            {formatScore(attempt.score_total)}
                            {attempt.passed && ' ✓ Passed'}
                          </div>
                        </div>
                        
                        {attempt.weak_topics && attempt.weak_topics.length > 0 && (
                          <div style={{ marginTop: '0.5rem' }}>
                            <strong>Weak Topics:</strong>{' '}
                            <span style={{ color: '#856404' }}>
                              {attempt.weak_topics.join(', ')}
                            </span>
                          </div>
                        )}

                        {attempt.topic_metrics && (
                          <div style={{ marginTop: '0.5rem', fontSize: '0.9rem', color: '#6c757d' }}>
                            <strong>Topic Scores:</strong>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '0.25rem', marginTop: '0.25rem' }}>
                              {Object.entries(attempt.topic_metrics).map(([topic, metrics]) => (
                                <div key={topic}>
                                  {topic}: {formatScore(metrics.weighted_score)} ({metrics.correct}/{metrics.total})
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        <div style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: '#6c757d', fontStyle: 'italic' }}>
                          Click to view detailed results
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <p style={{ color: '#6c757d', fontStyle: 'italic' }}>No attempts yet</p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default StudentHistory;
