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
  const [playingAudioId, setPlayingAudioId] = useState(null); // Track which question is playing

  useEffect(() => {
    loadQuiz();
    
    // Load voices for Web Speech API (needed for some browsers)
    if ('speechSynthesis' in window) {
      const loadVoices = () => {
        window.speechSynthesis.getVoices();
      };
      loadVoices();
      if (window.speechSynthesis.onvoiceschanged !== undefined) {
        window.speechSynthesis.onvoiceschanged = loadVoices;
      }
    }
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

  const handlePlayQuestion = async (questionText, questionId) => {
    // If this specific question is already playing, stop it
    if (playingAudioId === questionId) {
      // Stop current speech
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
      setPlayingAudioId(null);
      return;
    }

    // Stop any other playing audio first
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }

    // Use browser's built-in Web Speech API (free, no backend needed)
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(questionText);
      
      // Configure voice settings
      utterance.rate = 1.2; // Slightly faster speed
      utterance.pitch = 1.0; // Normal pitch
      utterance.volume = 1.0; // Full volume
      
      // Try to use a natural-sounding voice
      const voices = window.speechSynthesis.getVoices();
      const preferredVoice = voices.find(v => 
        v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Premium') || v.name.includes('Neural'))
      ) || voices.find(v => v.lang.startsWith('en')) || voices[0];
      
      if (preferredVoice) {
        utterance.voice = preferredVoice;
      }
      
      utterance.onend = () => {
        setPlayingAudioId(null);
      };
      
      utterance.onerror = (e) => {
        // Ignore 'interrupted' errors (happens when stopping speech)
        if (e.error !== 'interrupted') {
          console.error('Speech synthesis error:', e);
          setPlayingAudioId(null);
          // Only alert for non-interrupted errors
          if (e.error !== 'canceled') {
            alert('Failed to speak text. Please try again.');
          }
        } else {
          setPlayingAudioId(null);
        }
      };
      
      setPlayingAudioId(questionId);
      window.speechSynthesis.speak(utterance);
    } else {
      alert('Text-to-speech is not supported in your browser. Please use a modern browser like Chrome, Edge, or Firefox.');
    }
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
      // Check if this is a practice quiz (single topic)
      const topics = [...new Set(quiz.questions.map(q => q.topic))];
      const isPracticeQuiz = topics.length === 1;
      const practiceTopic = isPracticeQuiz ? topics[0] : null;
      
      // Get the original main test attempt_id (don't clear it yet - we need it for retakes)
      const originalMainAttemptId = sessionStorage.getItem('current_practice_original_attempt');
      
      // Store results in sessionStorage for QuizResults to access
      sessionStorage.setItem(`attempt_${response.attempt_id}`, JSON.stringify({
        ...response,
        student_id: quiz.student_id,
        grade_level: quiz.grade_level,
        is_practice_quiz: isPracticeQuiz,
        practice_topic: practiceTopic,
        original_attempt_id: isPracticeQuiz ? originalMainAttemptId : null,
      }));
      
      // Don't clear the practice original attempt marker - we need it for retakes
      // It will be cleared when user goes back to main results or starts a new main test
      
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
        {quiz.questions && (
          <div style={{ 
            marginBottom: '20px', 
            textAlign: 'right'
          }}>
            <div style={{
              display: 'inline-block',
              backgroundColor: '#007bff',
              color: 'white',
              padding: '8px 15px',
              borderRadius: '6px',
              fontWeight: 'bold',
              fontSize: '16px'
            }}>
              Total: {quiz.questions.reduce((sum, q) => sum + (q.weight || 1.0), 0).toFixed(1)} points
            </div>
          </div>
        )}

        {error && <div className="error">{error}</div>}

        {quiz.questions.map((question, index) => {
          // Convert weight to points (weight 1.0 = 1 point, 1.5 = 1.5 points, etc.)
          const points = question.weight || 1.0;
          const isHighValue = points > 1.0;
          
          return (
          <div key={`${question.id}-${index}`} className="question-card">
            <div className="question-header">
              <span>Question {index + 1} of {quiz.questions.length}</span>
              <span className="question-topic">{question.topic}</span>
              <span style={{
                backgroundColor: isHighValue ? '#ffc107' : '#6c757d',
                color: 'white',
                padding: '4px 10px',
                borderRadius: '12px',
                fontSize: '13px',
                fontWeight: 'bold'
              }}>
                ⭐ {points} {points === 1 ? 'point' : 'points'}
              </span>
            </div>
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '10px', 
              marginBottom: '10px' 
            }}>
              <div className="question-prompt" style={{ flex: 1 }}>{question.prompt}</div>
              <button
                onClick={() => handlePlayQuestion(question.prompt, question.id)}
                style={{
                  padding: '8px 12px',
                  backgroundColor: playingAudioId === question.id ? '#dc3545' : '#007bff',
                  color: 'white',
                  border: 'none',
                  borderRadius: '5px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
                title="Listen to question"
              >
                {playingAudioId === question.id ? '⏸️ Stop' : '🔊 Listen'}
              </button>
            </div>
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
          );
        })}

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

