import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/client';

function TakeQuiz() {
  const { quizId } = useParams();
  const navigate = useNavigate();
  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadQuiz();
  }, [quizId]);

  const loadQuiz = async () => {
    try {
      // For demo, we'll generate a quiz if quizId is provided
      // In a real app, you'd have a GET /quiz/{quizId} endpoint
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionId, answer) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: answer,
    }));
  };

  const handleSubmit = async () => {
    const unanswered = quiz.questions.filter(
      (q) => !answers[q.id] || answers[q.id].trim() === ''
    );

    if (unanswered.length > 0) {
      if (!confirm(`You have ${unanswered.length} unanswered questions. Submit anyway?`)) {
        return;
      }
    }

    setSubmitting(true);
    setError(null);

    try {
      const response = await api.submitQuiz(Number(quizId), answers);
      // Store results in sessionStorage for QuizResults to access
      sessionStorage.setItem(`attempt_${response.attempt_id}`, JSON.stringify({
        ...response,
        student_id: quiz.student_id,
        grade_level: quiz.grade_level,
      }));
      navigate(`/results/${response.attempt_id}`);
    } catch (err) {
      setError(err.message || 'Failed to submit quiz');
    } finally {
      setSubmitting(false);
    }
  };

  // For demo: if quiz is not loaded, try to get it from sessionStorage or generate
  useEffect(() => {
    const storedQuiz = sessionStorage.getItem(`quiz_${quizId}`);
    if (storedQuiz) {
      setQuiz(JSON.parse(storedQuiz));
      setLoading(false);
    } else {
      // If no stored quiz, redirect to start
      navigate('/');
    }
  }, [quizId, navigate]);

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Loading quiz...</div>
      </div>
    );
  }

  if (!quiz) {
    return (
      <div className="container">
        <div className="error">Quiz not found</div>
      </div>
    );
  }

  const allAnswered = quiz.questions.every((q) => answers[q.id] && answers[q.id].trim() !== '');

  return (
    <div className="container">
      <div className="card">
        <h2>Quiz Questions</h2>
        <p style={{ marginBottom: '20px', color: '#666' }}>
          Answer all questions and click Submit when done.
        </p>

        {error && <div className="error">{error}</div>}

        {quiz.questions.map((question, index) => (
          <div key={question.id} className="question-card">
            <div className="question-header">
              <span>Question {index + 1} of {quiz.questions.length}</span>
              <span className="question-topic">{question.topic}</span>
            </div>
            <div className="question-prompt">{question.prompt}</div>
            {question.choices && question.choices.length > 0 ? (
              <ul className="choices">
                {question.choices.map((choice, idx) => (
                  <li
                    key={idx}
                    className={`choice-item ${
                      answers[question.id] === choice ? 'selected' : ''
                    }`}
                    onClick={() => handleAnswerChange(question.id, choice)}
                  >
                    {choice}
                  </li>
                ))}
              </ul>
            ) : (
              <input
                type="text"
                value={answers[question.id] || ''}
                onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                placeholder="Enter your answer"
                style={{ width: '100%', padding: '10px', fontSize: '16px' }}
              />
            )}
          </div>
        ))}

        <div className="actions">
          <button
            className="btn btn-success"
            onClick={handleSubmit}
            disabled={submitting}
          >
            {submitting ? 'Submitting...' : 'Submit Quiz'}
          </button>
          <button
            className="btn btn-secondary"
            onClick={() => navigate('/')}
          >
            Cancel
          </button>
        </div>

        {!allAnswered && (
          <div style={{ marginTop: '15px', color: '#666', fontSize: '14px' }}>
            {quiz.questions.length - Object.keys(answers).filter(k => answers[k]?.trim()).length} questions unanswered
          </div>
        )}
      </div>
    </div>
  );
}

export default TakeQuiz;

