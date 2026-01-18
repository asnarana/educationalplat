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

    // Normalize text for speech: replace math symbols with spoken words
    let normalizedText = questionText
      .replace(/\s*-\s*/g, ' minus ')  // Replace "-" with "minus" (handles spaces around minus)
      .replace(/\s*\+\s*/g, ' plus ')   // Replace "+" with "plus"
      .replace(/\s*×\s*/g, ' times ')    // Replace "×" with "times"
      // Replace "x" with "times" ONLY when it's between numbers (multiplication), not when it's a variable
      // Pattern: number-space-x-space-number (like "5 x 3" or "2 x 5")
      .replace(/(\d+)\s+x\s+(\d+)/g, '$1 times $2')
      .replace(/\s*÷\s*/g, ' divided by ') // Replace "÷" with "divided by"
      .replace(/\s*\/\s*/g, ' divided by ') // Replace "/" with "divided by"
      .replace(/\s*=\s*/g, ' equals ')   // Replace "=" with "equals"
      .replace(/\s+/g, ' ')              // Normalize multiple spaces to single space
      .trim();

    // Use browser's built-in Web Speech API (free, no backend needed)
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(normalizedText);
      
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

  // Load quiz from sessionStorage or fetch from backend
  useEffect(() => {
    const loadQuizData = async () => {
      // First try sessionStorage
      const storedQuiz = sessionStorage.getItem(`quiz_${quizId}`);
      if (storedQuiz) {
        setQuiz(JSON.parse(storedQuiz));
        setLoading(false);
        return;
      }
      
      // If not in sessionStorage, try to fetch from backend
      try {
        const response = await api.getQuiz(quizId);
        setQuiz(response);
        // Store it in sessionStorage for future use
        sessionStorage.setItem(`quiz_${quizId}`, JSON.stringify(response));
        setLoading(false);
      } catch (err) {
        console.error('Error loading quiz:', err);
        setError('Quiz not found. Please start a new quiz.');
        setLoading(false);
        // Don't redirect immediately - let user see the error
      }
    };
    
    loadQuizData();
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
          
          // Parse reading passages from prompt
          // The question is ALWAYS the last part after double newlines
          const parseReadingPrompt = (prompt) => {
            if (!prompt) return { passage: null, question: prompt, hasPassage: false };
            
            // Normalize line breaks
            const normalizedPrompt = prompt.replace(/\r\n/g, '\n');
            
            // Check if it starts with "Read" - indicates a reading passage
            if (!normalizedPrompt.startsWith('Read')) {
              return {
                passage: null,
                question: prompt,
                hasPassage: false
              };
            }
            
            // Remove the "Read..." prefix to get just the content
            const contentMatch = normalizedPrompt.match(/^Read (?:the passage|both parts(?: of the story)?):\s*\n\n(.+)$/s);
            if (!contentMatch) {
              return {
                passage: null,
                question: prompt,
                hasPassage: false
              };
            }
            
            const content = contentMatch[1];
            
            // Check if this is a "both parts" question
            const isBothParts = normalizedPrompt.includes('Read both parts') || normalizedPrompt.includes('Use both parts');
            
            let question, passage, passageParts;
            
            if (isBothParts) {
              // For "both parts" questions, the structure is:
              // PART1\n\nPART2\n\nQUESTION
              // We need to find where the question starts (it's usually short and at the end)
              // Split by double newlines
              const parts = content.split(/\n\n+/);
              
              if (parts.length < 3) {
                // Not enough parts, treat last as question
                question = parts[parts.length - 1].trim();
                passageParts = parts.slice(0, -1);
              } else {
                // Find the question: it's the last part that's relatively short (< 300 chars)
                // and doesn't look like part of a passage
                let questionIdx = parts.length - 1;
                for (let i = parts.length - 1; i >= 0; i--) {
                  const part = parts[i].trim();
                  // Question is typically short and doesn't start with paragraph numbers
                  if (part.length < 300 && !part.match(/^\d+\s/)) {
                    questionIdx = i;
                    break;
                  }
                }
                
                question = parts[questionIdx].trim();
                passageParts = parts.slice(0, questionIdx);
              }
              
              // Join all passage parts back together to preserve full text
              passage = passageParts.join('\n\n').trim();
            } else {
              // Single passage: split by double newlines, last part is question
              const parts = content.split(/\n\n+/);
              
              if (parts.length < 2) {
                return {
                  passage: null,
                  question: prompt,
                  hasPassage: false
                };
              }
              
              question = parts[parts.length - 1].trim();
              passageParts = parts.slice(0, -1);
              passage = passageParts.join('\n\n').trim();
            }
            
            // Validate: question should be relatively short (typically < 300 chars)
            // and passage should be longer
            if (question.length < 300 && passage.length > question.length) {
              return {
                passage: passage,
                question: question,
                hasPassage: true,
                isBothParts: isBothParts,
                passageParts: isBothParts && passageParts.length >= 2 ? passageParts : null
              };
            }
            
            // Fallback: if validation fails, still try to separate
            return {
              passage: passage,
              question: question,
              hasPassage: true,
              isBothParts: isBothParts,
              passageParts: isBothParts && passageParts.length >= 2 ? passageParts : null
            };
          };
          
          const { passage, question: questionText, hasPassage, isBothParts, passageParts } = parseReadingPrompt(question.prompt);
          
          // Extract passage titles/names based on content
          const extractPassageTitle = (passageText, partIndex = 0) => {
            if (!passageText) return null;
            
            // Detect passage by key phrases/content
            // Part 2 may have different keywords, so we check for both parts
            const passageDetectors = [
              {
                keywords: partIndex === 0 
                  ? ['Rhode Island Red', 'rooster', 'poultry tent', 'county fairgrounds']
                  : ['Rhode Island Red', 'boy', 'oats', 'midway', 'cages'],
                title: 'The Great Escape',
                part: partIndex === 0 ? '(Part 1)' : '(Part 2)'
              },
              {
                keywords: partIndex === 0
                  ? ['Lois Ehlert', 'Growing Vegetable Soup', 'handmade books', 'Milwaukee', 'circus parade']
                  : ['dummy book', 'thumbnail sketches', 'typewriter', 'sunroom', 'collage', 'Milwaukee'],
                title: 'Excerpt from Under My Nose',
                part: partIndex === 0 ? '(Part 1)' : '(Part 2)'
              },
              {
                keywords: partIndex === 0
                  ? ['Grandfather Frog', 'Billy Mink', 'Little Joe Otter', 'Smiling Pool']
                  : ['Grandfather Frog', 'Jerry', 'pounded the water', 'Little Joe Otter', 'Longlegs'],
                title: 'Adapted from The Adventures of Grandfather Frog: "Billy Mink Finds Little Joe Otter"',
                part: partIndex === 0 ? '(Part 1)' : '(Part 2)'
              },
              {
                keywords: partIndex === 0
                  ? ['beaver', 'dam', 'sticks and logs', 'foundation']
                  : ['beaver', 'village', 'winter homes', 'Frenchman', 'Louisiana', 'hole'],
                title: 'Adapted from "Beavers at Home"',
                part: partIndex === 0 ? '(Part 1)' : '(Part 2)'
              },
              {
                keywords: partIndex === 0
                  ? ['Velvet', 'Mount Hood', 'climbers', 'German shepherd', 'transmitter']
                  : ['Velvet', 'rescue team', 'White River Canyon', 'forest ranger station', 'extra treats'],
                title: 'Excerpt from "Dog a Hero on Mount Hood"',
                part: partIndex === 0 ? '(Part 1)' : '(Part 2)'
              }
            ];
            
            // Check passage content for keywords
            const passageLower = passageText.toLowerCase();
            for (const detector of passageDetectors) {
              const matchCount = detector.keywords.filter(keyword => 
                passageLower.includes(keyword.toLowerCase())
              ).length;
              
              // If at least 2 keywords match (or 1 for Part 2 if we're being lenient), it's likely this passage
              const threshold = partIndex === 1 ? 1 : 2; // More lenient for Part 2
              if (matchCount >= threshold) {
                return `${detector.title} ${detector.part}`;
              }
            }
            
            return null;
          };
          
          // Get titles for each part
          const passageTitles = passageParts && passageParts.length > 0 
            ? passageParts.map((part, idx) => extractPassageTitle(part, idx))
            : passage ? [extractPassageTitle(passage, 0)] : [null];
          
          // Debug: log if passage was detected
          if (hasPassage) {
            console.log('Found passage for question', index + 1, 'Passage length:', passage?.length, 'Both parts:', isBothParts, 'Titles:', passageTitles);
          }
          
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
            
            {hasPassage && passage && (() => {
              // Always show the FULL passage text
              // The `passage` variable already contains the complete text
              // For "both parts" questions, try to split into Part 1 and Part 2 for visual separation
              let displayParts = [];
              
              if (isBothParts && passageParts && passageParts.length >= 2) {
                // For "both parts", we need to split the full passage into Part 1 and Part 2
                // The passageParts array contains all paragraphs separated by double newlines
                // We need to find where Part 1 ends and Part 2 begins
                // Strategy: if we have exactly 2 large parts, use them; otherwise split by content length
                
                if (passageParts.length === 2 && 
                    passageParts[0].length > 200 && 
                    passageParts[1].length > 200) {
                  // Likely already split correctly into Part 1 and Part 2
                  displayParts = passageParts;
                } else {
                  // Multiple smaller parts - need to combine and split intelligently
                  // Split the full passage roughly in half, looking for a natural break
                  const fullPassage = passage; // This already has all text joined
                  const midPoint = Math.floor(fullPassage.length / 2);
                  
                  // Look backwards from midpoint for a double newline (natural paragraph break)
                  const beforeMid = fullPassage.substring(0, midPoint);
                  const splitPoint = beforeMid.lastIndexOf('\n\n');
                  
                  if (splitPoint > midPoint * 0.4) {
                    // Found a reasonable split point
                    displayParts = [
                      fullPassage.substring(0, splitPoint).trim(),
                      fullPassage.substring(splitPoint).trim()
                    ];
                  } else {
                    // No good split point found - show as single passage with full text
                    displayParts = [passage];
                  }
                }
              } else {
                // Single passage - show full text, no part labels
                displayParts = [passage];
              }
              
              // Compute titles for displayParts (may differ from passageParts if we split)
              // CRITICAL: For "both parts", if Part 1 is detected, use same title for Part 2
              let displayTitles = displayParts.map((part, idx) => extractPassageTitle(part, idx));
              
              if (isBothParts && displayParts.length >= 2) {
                // If Part 1 has a title but Part 2 doesn't, extract the title from Part 1 and apply to Part 2
                const part1Title = displayTitles[0];
                if (part1Title && !displayTitles[1]) {
                  // Extract the base title (without Part number) and add Part 2
                  const baseTitleMatch = part1Title.match(/^(.+?)\s*\(Part\s+1\)$/i);
                  if (baseTitleMatch) {
                    displayTitles[1] = `${baseTitleMatch[1]} (Part 2)`;
                  } else {
                    // If no Part 1 in title, try to detect Part 2 separately
                    displayTitles[1] = extractPassageTitle(displayParts[1], 1);
                    // If still no title, use same as Part 1 but change to Part 2
                    if (!displayTitles[1] && part1Title) {
                      displayTitles[1] = part1Title.replace(/\(Part\s+1\)/i, '(Part 2)');
                    }
                  }
                }
                // If Part 2 has a title but Part 1 doesn't, do the reverse
                const part2Title = displayTitles[1];
                if (part2Title && !displayTitles[0]) {
                  const baseTitleMatch = part2Title.match(/^(.+?)\s*\(Part\s+2\)$/i);
                  if (baseTitleMatch) {
                    displayTitles[0] = `${baseTitleMatch[1]} (Part 1)`;
                  }
                }
              }
              
              return (
                <div style={{
                  backgroundColor: '#f8f9fa',
                  border: '2px solid #007bff',
                  borderRadius: '8px',
                  padding: '20px',
                  marginBottom: '25px',
                  maxHeight: '500px',
                  overflowY: 'auto',
                  lineHeight: '1.8',
                  fontSize: '15px',
                  color: '#212529'
                }}>
                  <div style={{
                    fontWeight: 'bold',
                    marginBottom: '12px',
                    color: '#007bff',
                    fontSize: '14px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px'
                  }}>
                    📖 Reading Passage{isBothParts ? ' (Part 1 & Part 2)' : ''}
                  </div>
                  {displayParts.map((part, partIdx) => {
                    const passageTitle = displayTitles[partIdx] || null;
                    return (
                      <div key={partIdx}>
                        {/* Show passage title if available */}
                        {passageTitle && (
                          <div style={{
                            marginBottom: partIdx > 0 ? '20px' : '15px',
                            marginTop: partIdx > 0 ? '20px' : '0',
                            padding: '12px 20px',
                            backgroundColor: '#e7f3ff',
                            border: '2px solid #007bff',
                            borderRadius: '8px',
                            textAlign: 'center',
                            fontWeight: 'bold',
                            color: '#0056b3',
                            fontSize: '18px',
                            fontStyle: 'italic'
                          }}>
                            {passageTitle}
                          </div>
                        )}
                      <div style={{ 
                        whiteSpace: 'pre-wrap',
                        fontFamily: 'Georgia, serif',
                        textAlign: 'left'
                      }}>
                        {part.split('\n').map((line, idx) => {
                          // Check if line is a paragraph number (just a number on its own line)
                          // Paragraph numbers are NOT parts - they're just paragraph markers
                          // CRITICAL: Trim whitespace before checking
                          const trimmedLine = line.trim();
                          const paragraphMatch = trimmedLine.match(/^(\d+)$/);
                          if (paragraphMatch) {
                            return (
                              <div key={`${partIdx}-${idx}`} style={{
                                fontWeight: 'bold',
                                fontSize: '18px',
                                color: '#007bff',
                                marginTop: idx > 0 ? '20px' : '0',
                                marginBottom: '8px',
                                paddingLeft: '5px',
                                borderLeft: '4px solid #007bff',
                                backgroundColor: '#e7f3ff',
                                padding: '5px 10px',
                                borderRadius: '4px',
                                display: 'inline-block',
                                minWidth: '40px',
                                textAlign: 'center'
                              }}>
                                {paragraphMatch[1]}
                              </div>
                            );
                          }
                          // Regular text line - skip empty lines (they're just spacing)
                          if (!trimmedLine) {
                            return <div key={`${partIdx}-${idx}`} style={{ marginBottom: '4px' }}>{'\u00A0'}</div>;
                          }
                          return <div key={`${partIdx}-${idx}`} style={{ marginBottom: '8px' }}>{line}</div>;
                        })}
                      </div>
                      </div>
                    );
                  })}
                </div>
              );
            })()}
            
            {/* Question Section - Clearly Separated */}
            <div style={{ 
              marginBottom: '20px',
              marginTop: hasPassage ? '30px' : '10px',
              paddingTop: hasPassage ? '25px' : '0',
              borderTop: hasPassage ? '4px solid #28a745' : 'none',
              backgroundColor: hasPassage ? '#f0f8f0' : 'transparent',
              padding: hasPassage ? '20px' : '0',
              borderRadius: hasPassage ? '8px' : '0'
            }}>
              {hasPassage && (
                <div style={{
                  fontWeight: 'bold',
                  marginBottom: '15px',
                  color: '#28a745',
                  fontSize: '15px',
                  textTransform: 'uppercase',
                  letterSpacing: '1px'
                }}>
                  ❓ Question
                </div>
              )}
              <div style={{ 
                display: 'flex', 
                alignItems: 'flex-start', 
                gap: '10px'
              }}>
                <div className="question-prompt" style={{ 
                  flex: 1,
                  fontSize: hasPassage ? '18px' : '16px',
                  fontWeight: '600',
                  lineHeight: '1.7',
                  color: '#212529',
                  backgroundColor: hasPassage ? '#ffffff' : 'transparent',
                  padding: hasPassage ? '18px' : '0',
                  borderRadius: hasPassage ? '8px' : '0',
                  border: hasPassage ? '2px solid #28a745' : 'none',
                  boxShadow: hasPassage ? '0 2px 4px rgba(0,0,0,0.1)' : 'none'
                }}>
                  {hasPassage ? questionText : question.prompt}
                </div>
                <button
                  onClick={() => handlePlayQuestion(hasPassage ? questionText : question.prompt, question.id)}
                  style={{
                    padding: '8px 12px',
                    backgroundColor: playingAudioId === question.id ? '#dc3545' : '#007bff',
                    color: 'white',
                    border: 'none',
                    borderRadius: '5px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    flexShrink: 0
                  }}
                  title="Listen to question"
                >
                  {playingAudioId === question.id ? '⏸️ Stop' : '🔊 Listen'}
                </button>
              </div>
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
            onClick={() => {
              // Check if this is a practice quiz - if so, go back to results
              const originalMainAttemptId = sessionStorage.getItem('current_practice_original_attempt');
              if (originalMainAttemptId) {
                // Navigate back to the original main test results
                navigate(`/results/${originalMainAttemptId}`);
              } else {
                // Otherwise, go to home
                navigate('/');
              }
            }}
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

