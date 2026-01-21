import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';

function AdminDashboard() {
  const navigate = useNavigate();
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [studentHistory, setStudentHistory] = useState(null);
  const [loadingHistory, setLoadingHistory] = useState(false);

  useEffect(() => {
    loadStudents();
    // Check if user is admin
    const user = api.getCurrentUserFromStorage();
    if (!user || user.role !== 'admin') {
      navigate('/login');
    }
  }, [navigate]);

  const loadStudents = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.request('/admin/students');
      setStudents(data.students || []);
    } catch (err) {
      setError(err.message || 'Failed to load students');
      if (err.message.includes('401') || err.message.includes('403')) {
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  const loadStudentHistory = async (username, gradeLevel = null) => {
    setLoadingHistory(true);
    setError(null);
    try {
      let url = `/admin/students/${username}/history`;
      if (gradeLevel) {
        url += `?grade_level=${gradeLevel}`;
      }
      const data = await api.request(url);
      setStudentHistory(data);
      setSelectedStudent(username);
    } catch (err) {
      setError(err.message || 'Failed to load student history');
    } finally {
      setLoadingHistory(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const formatScore = (score) => {
    return (score * 100).toFixed(1) + '%';
  };

  if (loading) {
    return (
      <div style={{ maxWidth: '1800px', margin: '2rem auto', padding: '2rem' }}>
        <div className="loading">Loading students...</div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '1800px', margin: '2rem auto', padding: '2rem' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1>Admin Dashboard</h1>
      </div>

      {error && <div className="error">{error}</div>}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '2rem' }}>
        {/* Students List */}
        <div className="card">
          <h2>All Students ({students.length})</h2>
          <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
            {students.length === 0 ? (
              <p>No students found.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {students.map((student) => (
                  <div
                    key={student.id}
                    onClick={() => loadStudentHistory(student.username)}
                    style={{
                      padding: '1rem',
                      border: selectedStudent === student.username ? '2px solid #007bff' : '1px solid #dee2e6',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      backgroundColor: selectedStudent === student.username ? '#f0f7ff' : 'white',
                    }}
                  >
                    <div style={{ fontWeight: 'bold', marginBottom: '0.5rem' }}>
                      {student.username}
                    </div>
                    <div style={{ fontSize: '0.9rem', color: '#666' }}>
                      <div>Quizzes: {student.stats.total_quizzes}</div>
                      <div>Attempts: {student.stats.total_attempts}</div>
                      <div>Avg Score: {student.stats.average_score}%</div>
                      <div>Grades: {student.stats.grade_levels.join(', ') || 'None'}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Student History */}
        <div className="card">
          {!selectedStudent ? (
            <div style={{ textAlign: 'center', color: '#666', padding: '2rem' }}>
              Select a student to view their history
            </div>
          ) : loadingHistory ? (
            <div className="loading">Loading history...</div>
          ) : studentHistory ? (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h2>History: {selectedStudent}</h2>
                <button
                  className="btn btn-secondary"
                  onClick={() => {
                    setSelectedStudent(null);
                    setStudentHistory(null);
                  }}
                >
                  Close
                </button>
              </div>

              {/* Summary */}
              <div style={{
                backgroundColor: '#f8f9fa',
                padding: '1rem',
                borderRadius: '8px',
                marginBottom: '1rem',
              }}>
                <h3>Summary</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.5rem' }}>
                  <div><strong>Total Quizzes:</strong> {studentHistory.summary.total_quizzes}</div>
                  <div><strong>Total Attempts:</strong> {studentHistory.summary.total_attempts}</div>
                  <div><strong>Average Score:</strong> {formatScore(studentHistory.summary.average_score)}</div>
                  <div><strong>Full Quizzes:</strong> {studentHistory.summary.full_quizzes}</div>
                  <div><strong>Practice Quizzes:</strong> {studentHistory.summary.practice_quizzes}</div>
                </div>

                {/* Mastery Status */}
                {Object.keys(studentHistory.summary.mastery_by_grade).length > 0 && (
                  <div style={{ marginTop: '1rem' }}>
                    <h4>Mastery Status:</h4>
                    {Object.entries(studentHistory.summary.mastery_by_grade).map(([grade, mastery]) => (
                      <div key={grade} style={{ marginTop: '0.5rem' }}>
                        <strong>Grade {grade}:</strong> {mastery.mastered ? '✅ Mastered' : `In Progress (${mastery.consecutive_passes}/${mastery.required})`}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Quiz History */}
              <h3>Quiz History</h3>
              <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
                {studentHistory.history.length === 0 ? (
                  <p>No quiz history found.</p>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {studentHistory.history.map((item) => {
                      const { quiz, attempts } = item;
                      return (
                        <div
                          key={quiz.id}
                          style={{
                            border: '1px solid #dee2e6',
                            borderRadius: '8px',
                            padding: '1rem',
                            backgroundColor: 'white'
                          }}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                            <div>
                              <strong>Quiz #{quiz.grade_quiz_number || quiz.id}</strong>
                              <span style={{ marginLeft: '1rem', padding: '0.25rem 0.5rem', backgroundColor: '#e3f2fd', borderRadius: '4px', fontSize: '0.85rem' }}>
                                Grade {quiz.grade_level} • {quiz.quiz_type === 'practice' ? `Practice: ${quiz.practice_topic}` : 'Full Quiz'}
                              </span>
                            </div>
                            <div style={{ fontSize: '0.9rem', color: '#666' }}>
                              {formatDate(quiz.created_at)}
                            </div>
                          </div>

                          {attempts.length > 0 ? (
                            <div>
                              {attempts.map((attempt) => (
                                <div
                                  key={attempt.id}
                                  style={{
                                    padding: '0.75rem',
                                    backgroundColor: attempt.passed ? '#d4edda' : '#fff3cd',
                                    borderRadius: '6px',
                                    marginTop: '0.5rem',
                                  }}
                                >
                                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                    <span><strong>Attempt #{attempt.id}</strong></span>
                                    <span style={{ fontWeight: 'bold', color: attempt.passed ? '#155724' : '#856404' }}>
                                      {formatScore(attempt.score_total)} {attempt.passed && '✓'}
                                    </span>
                                  </div>
                                  {attempt.weak_topics && attempt.weak_topics.length > 0 && (
                                    <div style={{ marginTop: '0.5rem', fontSize: '0.9rem' }}>
                                      Weak Topics: {attempt.weak_topics.join(', ')}
                                    </div>
                                  )}
                                </div>
                              ))}
                            </div>
                          ) : (
                            <div style={{ color: '#666', fontStyle: 'italic' }}>No attempts yet</div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}

export default AdminDashboard;
