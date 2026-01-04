import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';

function StartQuiz() {
  const navigate = useNavigate();
  const [studentId, setStudentId] = useState('');
  const [gradeLevel, setGradeLevel] = useState(3);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [seeding, setSeeding] = useState(false);

  const topics = {
    3: ['Addition', 'Subtraction', 'Multiplication', 'Division', 'Fractions'],
    5: ['Algebra', 'Geometry', 'Decimals', 'Percentages', 'Word Problems'],
  };

  const handleSeed = async () => {
    setSeeding(true);
    setError(null);
    try {
      await api.seedQuestions();
      alert('Question bank seeded successfully!');
    } catch (err) {
      setError(err.message);
    } finally {
      setSeeding(false);
    }
  };

  const handleStartQuiz = async (e) => {
    e.preventDefault();
    if (!studentId.trim()) {
      setError('Please enter a student ID');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await api.generateQuiz(
        studentId.trim(),
        gradeLevel,
        topics[gradeLevel],
        10
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
        <p style={{ marginBottom: '20px', color: '#666' }}>
          Enter your student ID and grade level to begin an adaptive quiz.
        </p>

        {error && <div className="error">{error}</div>}

        <form onSubmit={handleStartQuiz}>
          <div className="form-group">
            <label htmlFor="studentId">Student ID</label>
            <input
              id="studentId"
              type="text"
              value={studentId}
              onChange={(e) => setStudentId(e.target.value)}
              placeholder="Enter your student ID"
              required
            />
          </div>

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
              onClick={handleSeed}
              disabled={seeding}
            >
              {seeding ? 'Seeding...' : 'Seed Question Bank'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default StartQuiz;

