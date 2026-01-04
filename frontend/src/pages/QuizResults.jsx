import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/client';

function QuizResults() {
  const { attemptId } = useParams();
  const navigate = useNavigate();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [generatingNext, setGeneratingNext] = useState(false);
  const [studentId, setStudentId] = useState(null);
  const [gradeLevel, setGradeLevel] = useState(null);

  useEffect(() => {
    loadResults();
  }, [attemptId]);

  const loadResults = async () => {
    try {
      // Get results from sessionStorage (stored when quiz was submitted)
      const storedResults = sessionStorage.getItem(`attempt_${attemptId}`);
      if (storedResults) {
        const data = JSON.parse(storedResults);
        setResults(data);
        setStudentId(data.student_id || data.next_quiz_recommendation?.student_id);
        setGradeLevel(data.grade_level || data.next_quiz_recommendation?.grade_level);
      } else {
        setError('Results not found. Please submit a quiz first.');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleNextQuiz = async () => {
    if (!studentId || !results?.next_quiz_recommendation) {
      alert('Cannot generate next quiz. Please start a new quiz from the home page.');
      return;
    }

    setGeneratingNext(true);
    setError(null);

    try {
      const rec = results.next_quiz_recommendation;
      const response = await api.generateQuiz(
        studentId,
        gradeLevel || rec.grade_level,
        rec.topics,
        rec.num_questions
      );
      
      // Store quiz in sessionStorage
      sessionStorage.setItem(`quiz_${response.quiz_id}`, JSON.stringify(response));
      navigate(`/quiz/${response.quiz_id}`);
    } catch (err) {
      setError(err.message || 'Failed to generate next quiz');
    } finally {
      setGeneratingNext(false);
    }
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Loading results...</div>
      </div>
    );
  }

  if (error || !results) {
    return (
      <div className="container">
        <div className="error">{error || 'Results not found'}</div>
        <button className="btn" onClick={() => navigate('/')}>
          Go Home
        </button>
      </div>
    );
  }

  const overallScore = (results.score_total * 100).toFixed(1);
  const passed = results.passed;
  const weakTopics = results.weak_topics || [];

  return (
    <div className="container">
      <div className="card">
        <h2>Quiz Results</h2>
        
        <div style={{ textAlign: 'center', marginBottom: '30px' }}>
          <div style={{ fontSize: '48px', fontWeight: 'bold', color: passed ? '#28a745' : '#dc3545' }}>
            {overallScore}%
          </div>
          <div style={{ fontSize: '18px', color: '#666', marginTop: '10px' }}>
            {passed ? '🎉 All topics mastered!' : 'Keep practicing to improve!'}
          </div>
        </div>

        <h3 style={{ marginBottom: '15px' }}>Topic Performance</h3>
        <div className="metrics-grid">
          {Object.entries(results.topic_metrics || {}).map(([topic, metrics]) => {
            const score = (metrics.weighted_score * 100).toFixed(1);
            const isWeak = weakTopics.includes(topic);
            const isStrong = metrics.weighted_score >= 0.80;
            
            return (
              <div
                key={topic}
                className={`metric-card ${isWeak ? 'weak' : isStrong ? 'strong' : ''}`}
              >
                <div className="metric-topic">{topic}</div>
                <div className="metric-score">{score}%</div>
                <div className="metric-details">
                  {metrics.correct}/{metrics.total} correct
                </div>
              </div>
            );
          })}
        </div>

        {weakTopics.length > 0 && (
          <div className="weak-topics-list">
            <h3>Topics Needing Improvement</h3>
            <ul>
              {weakTopics.map((topic) => (
                <li key={topic}>{topic}</li>
              ))}
            </ul>
          </div>
        )}

        {results.mastery_status && (
          <div style={{ marginTop: '20px', padding: '15px', background: '#f0f7ff', borderRadius: '8px' }}>
            <strong>Mastery Status:</strong> {results.mastery_status.mastered 
              ? '✅ Mastered!' 
              : `${results.mastery_status.consecutive_passes}/${results.mastery_status.required} consecutive perfect attempts needed`}
          </div>
        )}

        {results.next_quiz_recommendation && (
          <div style={{ marginTop: '20px', padding: '15px', background: '#fff5f5', borderRadius: '8px' }}>
            <strong>Next Quiz Focus:</strong> {results.next_quiz_recommendation.focus === 'weak_topics' 
              ? `70% questions from weak topics: ${weakTopics.join(', ')}`
              : 'Review all topics'}
          </div>
        )}

        <div className="actions">
          {results.next_quiz_recommendation && !results.mastery_status?.mastered && (
            <button
              className="btn"
              onClick={handleNextQuiz}
              disabled={generatingNext}
            >
              {generatingNext ? 'Generating...' : 'Generate Next Quiz'}
            </button>
          )}
          <button className="btn btn-secondary" onClick={() => navigate('/')}>
            {results.mastery_status?.mastered ? 'Start New Quiz' : 'Back to Home'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default QuizResults;

