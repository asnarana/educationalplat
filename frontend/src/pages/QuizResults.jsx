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
  const [feedback, setFeedback] = useState(null);
  const [loadingFeedback, setLoadingFeedback] = useState(false);
  const [feedbackError, setFeedbackError] = useState(null);
  const [playingAudio, setPlayingAudio] = useState(null);

  useEffect(() => {
    loadResults();
    
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

  const handlePracticeTopic = async (topic) => {
    if (!studentId || !gradeLevel) {
      alert('Cannot generate practice quiz. Please start a new quiz from the home page.');
      return;
    }

    setGeneratingNext(true);
    setError(null);

    try {
      const response = await api.generateTopicPractice(
        studentId,
        gradeLevel,
        topic,
        7  // Number of practice questions
      );
      
      // Store the original main test attempt_id so we can navigate back
      // If this is called from main results, use current attemptId
      // If this is called from practice results, preserve the original_attempt_id
      const originalMainAttemptId = results?.original_attempt_id || attemptId;
      sessionStorage.setItem('current_practice_original_attempt', originalMainAttemptId);
      
      // Store quiz in sessionStorage
      sessionStorage.setItem(`quiz_${response.quiz_id}`, JSON.stringify(response));
      navigate(`/quiz/${response.quiz_id}`);
    } catch (err) {
      setError(err.message || `Failed to generate practice quiz for ${topic}`);
    } finally {
      setGeneratingNext(false);
    }
  };

  const handleRetakePractice = async () => {
    if (!results.practice_topic || !studentId || !gradeLevel) {
      return;
    }
    
    // Preserve the original main test attempt_id (not the current practice attempt_id)
    const originalMainAttemptId = results.original_attempt_id || attemptId;
    sessionStorage.setItem('current_practice_original_attempt', originalMainAttemptId);
    
    await handlePracticeTopic(results.practice_topic);
  };

  const handleBackToMainResults = () => {
    const originalAttemptId = results.original_attempt_id;
    // Clear the practice marker when going back to main results
    sessionStorage.removeItem('current_practice_original_attempt');
    if (originalAttemptId) {
      navigate(`/results/${originalAttemptId}`);
    } else {
      navigate('/');
    }
  };

  const handleRetakeFullTest = async () => {
    if (!studentId || !gradeLevel || !results.next_quiz_recommendation) {
      alert('Cannot generate quiz. Please start a new quiz from the home page.');
      return;
    }

    setGeneratingNext(true);
    setError(null);

    try {
      const rec = results.next_quiz_recommendation;
      const response = await api.generateQuiz(
        studentId,
        gradeLevel,
        rec.topics,
        rec.num_questions
      );
      
      // Store quiz in sessionStorage
      sessionStorage.setItem(`quiz_${response.quiz_id}`, JSON.stringify(response));
      navigate(`/quiz/${response.quiz_id}`);
    } catch (err) {
      setError(err.message || 'Failed to generate quiz');
    } finally {
      setGeneratingNext(false);
    }
  };

  const handleGetFeedback = async () => {
    if (!attemptId) return;

    setLoadingFeedback(true);
    setFeedbackError(null);

    try {
      const feedbackData = await api.getFeedback(Number(attemptId));
      setFeedback(feedbackData);
    } catch (err) {
      setFeedbackError(err.message || 'Failed to generate feedback. Make sure Ollama is running and Langchain packages are installed.');
    } finally {
      setLoadingFeedback(false);
    }
  };

  const handlePlayText = async (text) => {
    if (playingAudio) {
      // Stop current speech
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
      setPlayingAudio(null);
      return;
    }

    // Use browser's built-in Web Speech API (free, no backend needed)
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      
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
        setPlayingAudio(null);
      };
      
      utterance.onerror = (e) => {
        // Ignore 'interrupted' errors (happens when stopping speech)
        if (e.error !== 'interrupted') {
          console.error('Speech synthesis error:', e);
          setPlayingAudio(null);
          // Only alert for non-interrupted errors
          if (e.error !== 'canceled') {
            alert('Failed to speak text. Please try again.');
          }
        } else {
          setPlayingAudio(null);
        }
      };
      
      setPlayingAudio(utterance);
      window.speechSynthesis.speak(utterance);
    } else {
      alert('Text-to-speech is not supported in your browser. Please use a modern browser like Chrome, Edge, or Firefox.');
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
  const isPracticeQuiz = results.is_practice_quiz || false;
  const practiceTopic = results.practice_topic || null;
  // Use weighted_score (consistent with backend) instead of simple percentage
  const topicScore = practiceTopic && results.topic_metrics?.[practiceTopic] 
    ? (results.topic_metrics[practiceTopic].weighted_score 
        ? (results.topic_metrics[practiceTopic].weighted_score * 100).toFixed(1)
        : '0.0')
    : null;
  const isTopicMastered = topicScore && parseFloat(topicScore) >= 100;

  return (
    <div className="container">
      <div className="card">
        <h2>{isPracticeQuiz ? `Practice Results: ${practiceTopic}` : 'Quiz Results'}</h2>
        
        {isPracticeQuiz && (
          <div style={{ marginBottom: '20px', padding: '15px', background: '#e8f5e9', borderRadius: '8px' }}>
            <strong>Practice Topic:</strong> {practiceTopic}
            {topicScore && (
              <div style={{ marginTop: '10px', fontSize: '24px', fontWeight: 'bold', color: isTopicMastered ? '#28a745' : '#ff6b6b' }}>
                {topicScore}% {isTopicMastered ? '✅ Mastered!' : 'Keep practicing!'}
              </div>
            )}
          </div>
        )}
        
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
            // Use weighted_score (consistent with backend logic for determining weak topics)
            const score = metrics.weighted_score 
              ? (metrics.weighted_score * 100).toFixed(1) 
              : (metrics.total > 0 ? ((metrics.correct / metrics.total) * 100).toFixed(1) : '0.0');
            const isWeak = weakTopics.includes(topic);
            // Check if strong using weighted_score (consistent with weak topic logic)
            const isStrong = metrics.weighted_score ? metrics.weighted_score >= 0.80 : (metrics.correct / metrics.total) >= 0.80;
            
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

        {weakTopics.length > 0 && !isPracticeQuiz && (
          <div className="weak-topics-list">
            <h3>Topics Needing Improvement</h3>
            <p style={{ marginBottom: '15px', color: '#666' }}>
              Practice these topics with focused quizzes. Practice until you reach 100%:
            </p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
              {weakTopics.map((topic) => (
                <button
                  key={topic}
                  className="btn"
                  onClick={() => handlePracticeTopic(topic)}
                  disabled={generatingNext}
                  style={{ 
                    minWidth: '150px',
                    backgroundColor: '#ff6b6b',
                    color: 'white'
                  }}
                >
                  {generatingNext ? 'Loading...' : `Practice ${topic}`}
                </button>
              ))}
            </div>
          </div>
        )}

        {results.mastery_status && !isPracticeQuiz && (
          <div style={{ marginTop: '20px', padding: '15px', background: '#f0f7ff', borderRadius: '8px' }}>
            <strong>Grade Level Mastery Status:</strong>
            {results.mastery_status.mastered ? (
              <div style={{ marginTop: '10px', color: '#28a745', fontWeight: 'bold' }}>
                ✅ Grade Level Mastered! You've passed 2 consecutive full tests with no weak topics.
              </div>
            ) : (
              <div style={{ marginTop: '10px' }}>
                <p style={{ marginBottom: '5px' }}>
                  To master this grade level, you need to pass <strong>2 consecutive full tests</strong> with no weak topics (all topics ≥ 80%).
                </p>
                <p style={{ margin: 0, color: '#666' }}>
                  Progress: <strong>{results.mastery_status.consecutive_passes}/{results.mastery_status.required}</strong> consecutive perfect attempts
                </p>
                {results.mastery_status.consecutive_passes === 1 && (
                  <p style={{ marginTop: '5px', color: '#28a745', fontSize: '14px' }}>
                    💡 You're halfway there! Pass one more full test with no weak topics to achieve mastery.
                  </p>
                )}
              </div>
            )}
          </div>
        )}

        {results.next_quiz_recommendation && !isPracticeQuiz && (
          <div style={{ marginTop: '20px', padding: '15px', background: '#fff5f5', borderRadius: '8px' }}>
            <strong>Next Quiz Focus:</strong> {results.next_quiz_recommendation.focus === 'weak_topics' 
              ? `70% questions from weak topics: ${weakTopics.join(', ')}`
              : 'Review all topics'}
          </div>
        )}

        {/* LLM Feedback Section */}
        <div style={{ marginTop: '30px', padding: '20px', background: '#f8f9fa', borderRadius: '8px', border: '1px solid #dee2e6' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
            <h3 style={{ margin: 0 }}>🤖 Personalized Feedback (AI-Powered)</h3>
            {!feedback && (
              <button
                className="btn"
                onClick={handleGetFeedback}
                disabled={loadingFeedback}
                style={{ backgroundColor: '#007bff', color: 'white' }}
              >
                {loadingFeedback ? 'Generating...' : 'Get AI Feedback'}
              </button>
            )}
          </div>

          {feedbackError && (
            <div style={{ padding: '15px', background: '#f8d7da', color: '#721c24', borderRadius: '5px', marginBottom: '15px' }}>
              <strong>Error:</strong> {feedbackError}
              <div style={{ marginTop: '10px', fontSize: '14px' }}>
                <p>Make sure:</p>
                <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
                  <li>Ollama is running (check with: <code>ollama list</code>)</li>
                  <li>Langchain packages are installed: <code>pip install langchain langchain-community</code></li>
                  <li>You have a model pulled: <code>ollama pull phi</code> or <code>ollama pull llama2</code></li>
                </ul>
              </div>
            </div>
          )}

          {loadingFeedback && (
            <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
              <div>🔄 Generating personalized feedback with AI...</div>
              <div style={{ marginTop: '10px', fontSize: '14px' }}>This may take 10-30 seconds</div>
            </div>
          )}

          {feedback && (
            <div>
              {feedback.summary && (
                <div style={{ marginBottom: '20px', padding: '15px', background: '#e7f3ff', borderRadius: '5px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                    <strong style={{ fontSize: '16px' }}>📝 Summary:</strong>
                    <button
                      onClick={() => handlePlayText(feedback.summary)}
                      style={{
                        padding: '6px 12px',
                        backgroundColor: playingAudio ? '#dc3545' : '#28a745',
                        color: 'white',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: 'pointer',
                        fontSize: '12px'
                      }}
                      title="Listen to summary"
                    >
                      {playingAudio ? '⏸️ Stop' : '🔊 Listen'}
                    </button>
                  </div>
                  <p style={{ marginTop: '10px', marginBottom: 0, lineHeight: '1.6' }}>{feedback.summary}</p>
                </div>
              )}

              {feedback.topics && Object.keys(feedback.topics).length > 0 && (
                <div>
                  <h4 style={{ marginBottom: '15px' }}>Study Recommendations:</h4>
                  {Object.entries(feedback.topics).map(([topic, topicData]) => (
                    <div key={topic} style={{ marginBottom: '25px', padding: '15px', background: 'white', borderRadius: '5px', border: '1px solid #dee2e6' }}>
                      <h5 style={{ marginTop: 0, marginBottom: '15px', color: '#007bff' }}>{topic}</h5>
                      
                      {topicData.actions && topicData.actions.length > 0 && (
                        <div style={{ marginBottom: '20px' }}>
                          <strong>💡 Study Actions:</strong>
                          <ul style={{ marginTop: '10px', marginBottom: 0, paddingLeft: '20px' }}>
                            {topicData.actions.map((action, idx) => (
                              <li key={idx} style={{ marginBottom: '8px', lineHeight: '1.5' }}>{action}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {topicData.practice && topicData.practice.length > 0 && (
                        <div>
                          <strong>📚 Practice Questions:</strong>
                          {topicData.practice.map((practiceQ, idx) => (
                            <div key={idx} style={{ marginTop: '15px', padding: '15px', background: '#f8f9fa', borderRadius: '5px' }}>
                              <div style={{ marginBottom: '10px' }}>
                                <strong>Q{idx + 1}:</strong> {practiceQ.q}
                              </div>
                              <div style={{ marginBottom: '10px', paddingLeft: '15px' }}>
                                <strong>Answer:</strong> {practiceQ.answer}
                              </div>
                              {practiceQ.explanation && (
                                <div style={{ paddingLeft: '15px', color: '#666', fontStyle: 'italic' }}>
                                  <strong>Explanation:</strong> {practiceQ.explanation}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}

              <button
                className="btn btn-secondary"
                onClick={() => setFeedback(null)}
                style={{ marginTop: '15px' }}
              >
                Hide Feedback
              </button>
            </div>
          )}
        </div>

        <div className="actions">
          {isPracticeQuiz ? (
            // Practice quiz actions
            <>
              {!isTopicMastered && (
                <button
                  className="btn"
                  onClick={handleRetakePractice}
                  disabled={generatingNext}
                  style={{ backgroundColor: '#ff6b6b', color: 'white' }}
                >
                  {generatingNext ? 'Loading...' : 'Retake Practice (Until 100%)'}
                </button>
              )}
              {results.original_attempt_id && (
                <button
                  className="btn btn-secondary"
                  onClick={handleBackToMainResults}
                >
                  Back to Main Results
                </button>
              )}
              <button className="btn btn-secondary" onClick={() => navigate('/')}>
                Home
              </button>
              {studentId && gradeLevel && (
                <button className="btn btn-secondary" onClick={() => navigate(`/history/${studentId}/${gradeLevel}`)}>
                  View History
                </button>
              )}
            </>
          ) : (
            // Full quiz actions
            <>
          {results.next_quiz_recommendation && !results.mastery_status?.mastered && (
            <button
              className="btn"
                  onClick={handleRetakeFullTest}
              disabled={generatingNext}
            >
                  {generatingNext ? 'Generating...' : 'Retake Full Test (70% Focus on Weak Topics)'}
            </button>
          )}
          <button className="btn btn-secondary" onClick={() => navigate('/')}>
            {results.mastery_status?.mastered ? 'Start New Quiz' : 'Back to Home'}
          </button>
          {studentId && gradeLevel && (
            <button className="btn btn-secondary" onClick={() => navigate(`/history/${studentId}/${gradeLevel}`)}>
              View History
            </button>
          )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default QuizResults;

