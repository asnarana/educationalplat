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
          
          // Extract passage title and author from text
          const extractTitleAndAuthor = (passageText) => {
            if (!passageText) return { title: null, author: null };
            
            // Filter out empty lines and "Part X" lines, but keep order
            const allLines = passageText.split('\n');
            const lines = [];
            for (const line of allLines) {
              const trimmed = line.trim();
              // Skip empty lines and "Part X" standalone lines
              if (trimmed && !trimmed.match(/^Part\s+[12]$/i)) {
                lines.push(trimmed);
              }
            }
            
            // Look for title on first line and "by Author" on second line
            let title = null;
            let author = null;
            
            if (lines.length > 0) {
              // Check if first line looks like a title (not a paragraph number, not starting with lowercase)
              const firstLine = lines[0];
              // Title should:
              // - Not be just a number (paragraph number)
              // - Have reasonable length (3-150 chars)
              // - Usually start with capital letter or known title patterns
              if (!firstLine.match(/^\d+$/) &&
                  firstLine.length >= 3 && firstLine.length <= 150 &&
                  (firstLine.match(/^[A-Z]/) || // Starts with capital
                   firstLine.match(/^(Excerpt|Adapted|Making|The|Antonio|Annabel|Libby|Amelia|What's|Dinos|Dinosaur)/i) ||
                   firstLine.length < 50)) { // Short lines are likely titles
                title = firstLine;
                
                // Check second line for "by Author" pattern
                if (lines.length > 1) {
                  const secondLine = lines[1];
                  const byMatch = secondLine.match(/^by\s+(.+)$/i);
                  if (byMatch) {
                    author = byMatch[1];
                  } else if (secondLine.match(/^This\s+article|^This\s+text/i)) {
                    // Skip lines like "This article was written in 2006"
                    // Check third line for author
                    if (lines.length > 2) {
                      const thirdLine = lines[2];
                      const byMatch2 = thirdLine.match(/^by\s+(.+)$/i);
                      if (byMatch2) {
                        author = byMatch2[1];
                      }
                    }
                  }
                }
              }
            }
            
            return { title, author };
          };
          
          // Extract passage titles/names based on content (fallback if title extraction fails)
          const extractPassageTitle = (passageText, partIndex = 0) => {
            if (!passageText) return null;
            
            // Detect which part this is by checking for "Part 1" or "Part 2" markers in the text
            const passageLower = passageText.toLowerCase();
            let detectedPartIndex = partIndex; // Default to passed partIndex
            
            // Check if text contains "Part 2" marker (more reliable than partIndex)
            if (passageLower.includes('part 2') && !passageLower.includes('part 1')) {
              detectedPartIndex = 1; // This is Part 2
            } else if (passageLower.includes('part 1') && !passageLower.includes('part 2')) {
              detectedPartIndex = 0; // This is Part 1
            }
            // If both are present or neither, use the passed partIndex
            
            // First try to extract title and author directly from text
            const { title, author } = extractTitleAndAuthor(passageText);
            if (title) {
              let displayTitle = title;
              if (author) {
                displayTitle = `${title}\nby ${author}`;
              }
              // Add part number if applicable
              const passageDetectors = [
                { keywords: ['Rhode Island Red', 'rooster'], hasParts: true },
                { keywords: ['Lois Ehlert', 'Under My Nose'], hasParts: true },
                { keywords: ['Grandfather Frog', 'Billy Mink'], hasParts: true },
                { keywords: ['beaver', 'dam'], hasParts: true },
                { keywords: ['Velvet', 'Mount Hood'], hasParts: true }
              ];
              
              const hasParts = passageDetectors.some(d => 
                d.keywords.some(k => passageLower.includes(k.toLowerCase()))
              );
              
              if (hasParts && detectedPartIndex >= 0) {
                // Only add Part label if not already present
                if (!displayTitle.match(/\(Part\s+[12]\)/i)) {
                  displayTitle += `\n(Part ${detectedPartIndex === 0 ? '1' : '2'})`;
                }
              }
              
              // Always return the title if we found one (even without author)
              return displayTitle;
            }
            
            // Fallback: Detect passage by key phrases/content
            const passageDetectors = [
              {
                keywords: partIndex === 0 
                  ? ['Rhode Island Red', 'rooster', 'poultry tent', 'county fairgrounds']
                  : ['Rhode Island Red', 'boy', 'oats', 'midway', 'cages'],
                title: 'The Great Escape',
                author: 'Susan Mitsch',
                part: partIndex === 0 ? '(Part 1)' : '(Part 2)'
              },
              {
                keywords: partIndex === 0
                  ? ['Lois Ehlert', 'Growing Vegetable Soup', 'handmade books', 'Milwaukee', 'circus parade']
                  : ['dummy book', 'thumbnail sketches', 'typewriter', 'sunroom', 'collage', 'Milwaukee'],
                title: 'Excerpt from Under My Nose',
                author: 'Lois Ehlert',
                part: partIndex === 0 ? '(Part 1)' : '(Part 2)'
              },
              {
                keywords: partIndex === 0
                  ? ['Grandfather Frog', 'Billy Mink', 'Little Joe Otter', 'Smiling Pool']
                  : ['Grandfather Frog', 'Jerry', 'pounded the water', 'Little Joe Otter', 'Longlegs'],
                title: 'Adapted from The Adventures of Grandfather Frog: "Billy Mink Finds Little Joe Otter"',
                author: 'Thornton W. Burgess',
                part: partIndex === 0 ? '(Part 1)' : '(Part 2)'
              },
              {
                keywords: partIndex === 0
                  ? ['beaver', 'dam', 'sticks and logs', 'foundation']
                  : ['beaver', 'village', 'winter homes', 'Frenchman', 'Louisiana', 'hole'],
                title: 'Adapted from "Beavers at Home"',
                author: 'James Baldwin',
                part: partIndex === 0 ? '(Part 1)' : '(Part 2)'
              },
              {
                keywords: partIndex === 0
                  ? ['Velvet', 'Mount Hood', 'climbers', 'German shepherd', 'transmitter']
                  : ['Velvet', 'rescue team', 'White River Canyon', 'forest ranger station', 'extra treats'],
                title: 'Excerpt from "Dog a Hero on Mount Hood"',
                author: 'Susan Jankowski',
                part: partIndex === 0 ? '(Part 1)' : '(Part 2)'
              },
              // Grade 4 Reading Passages
              {
                keywords: ['Libby', 'Alaskan huskies', 'sled', 'Timber and Tucker', 'dogs', 'anchor'],
                title: 'Libby Saves the Team',
                author: 'Kristine Nielsen',
                part: ''
              },
              {
                keywords: ['Amelia Earhart', 'Friendship', 'Lockheed Vega', 'Ninety-Nines', 'Fred Noonan', 'navigator'],
                title: 'Excerpt from Amelia Earhart',
                author: 'Marilyn Rosenthal and Daniel Freeman',
                part: ''
              },
              {
                keywords: ['Chef Justus', 'Hershey Lodge', 'chocolate', 'Thanksgiving', 'culinary', 'sous chef'],
                title: "What's It Like to Be a Chef?",
                author: '',
                part: ''
              },
              {
                keywords: ['Trigger', 'cocker spaniel', 'Charlie', 'railroad', 'red flag', 'switch'],
                title: 'Adapted from "A Regular Railroad Dog"',
                author: 'Avis J. Kirsch',
                part: ''
              },
              {
                keywords: ['Dinosaur Cove', 'paleontologists', 'South Pole', 'Antarctica', 'cold-blooded', 'warm-blooded', 'big eyes'],
                title: 'Dinos in the Dark',
                author: 'Stephen Whitt',
                part: ''
              },
              // Grade 5 Reading Passages
              {
                keywords: ['weightless', 'astronauts', 'gravity', 'space', 'zero gravity', 'weightlessness'],
                title: 'Excerpt from "Life without Gravity"',
                author: 'Robert Zimmerman',
                part: ''
              },
              {
                keywords: ['saguaro', 'Tohono O\'odham', 'Gina', 'kuipad', 'creosote', 'syrup', 'harvest'],
                title: 'Making the World\'s Rarest Syrup',
                author: 'David Edwards',
                part: ''
              },
              {
                keywords: ['terrarium', 'Wardian', 'Dr. Ward', 'fern case', 'ecosystem', 'greenhouse'],
                title: 'The World in a Bottle',
                author: 'Janeen R. Adil',
                part: ''
              },
              {
                keywords: ['Antonio Canova', 'sculptor', 'butter', 'lion', 'Count', 'stonecutter'],
                title: 'Antonio Canova',
                author: 'James Baldwin',
                part: ''
              },
              {
                keywords: ['Annabel Lee', 'P.I.', 'sock', 'Exhibit A', 'detective', 'John', 'dryer'],
                title: 'Annabel Lee, P.I.',
                author: 'Judy Cox',
                part: ''
              }
            ];
            
            // Check passage content for keywords (reuse passageLower from above)
            for (const detector of passageDetectors) {
              const matchCount = detector.keywords.filter(keyword => 
                passageLower.includes(keyword.toLowerCase())
              ).length;
              
              // If at least 2 keywords match (or 1 for Part 2 if we're being lenient), it's likely this passage
              const threshold = partIndex === 1 ? 1 : 2; // More lenient for Part 2
              if (matchCount >= threshold) {
                let displayTitle = detector.title;
                if (detector.author) {
                  displayTitle = `${detector.title}\nby ${detector.author}`;
                }
                if (detector.part) {
                  displayTitle += `\n${detector.part}`;
                }
                return displayTitle;
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
              // Clean passage text: remove title, author, and "Part 1" and "Part 2" headers since they're in the title box
              const cleanPassageText = (text) => {
                if (!text) return text;
                
                const lines = text.split('\n');
                let cleanedLines = [];
                let foundTitle = false;
                let foundAuthor = false;
                let isFirstContentLine = true; // Track if we're still at the beginning
                
                // Process lines
                for (let i = 0; i < lines.length; i++) {
                  const line = lines[i].trim();
                  const originalLine = lines[i]; // Keep original spacing
                  
                  // Skip empty lines at the very start
                  if (cleanedLines.length === 0 && !line) continue;
                  
                  // Skip "Part 1" or "Part 2" standalone lines (not paragraph numbers)
                  if (line.match(/^Part\s+[12]$/i) || line.match(/^\(Part\s+[12]\)$/i)) {
                    continue;
                  }
                  
                  // Detect title: check if this is the first content line we're processing
                  // and it looks like a title followed by "by Author" OR "This article/text..."
                  if (!foundTitle && isFirstContentLine && line && 
                      !line.match(/^\d+$/) && 
                      line.length >= 3 && line.length <= 150) {
                    
                    // Look ahead for "by Author" pattern OR "This article/text..." metadata (within next 6 lines, skipping empty lines)
                    let foundByAuthor = false;
                    let foundMetadata = false;
                    let emptyLinesCount = 0;
                    for (let j = i + 1; j < Math.min(i + 7, lines.length); j++) {
                      const nextLine = lines[j].trim();
                      if (!nextLine) {
                        emptyLinesCount++;
                        if (emptyLinesCount > 2) break; // Too many empty lines, probably not author/metadata
                        continue;
                      }
                      
                      // Check for "by Author" pattern
                      if (nextLine.match(/^by\s+.+$/i)) {
                        foundByAuthor = true;
                        break;
                      }
                      
                      // Check for "This article/text was written/published..." metadata
                      if (nextLine.match(/^This\s+(article|text)\s+was\s+(written|published)/i)) {
                        foundMetadata = true;
                        break;
                      }
                      
                      // If we hit actual content (starts with lowercase letter that's not a title word), stop looking
                      // But allow "This article..." metadata lines
                      if (nextLine.match(/^[a-z]/) && 
                          !nextLine.match(/^(This\s+(article|text)|by\s+)/i) &&
                          nextLine.length > 50) {
                        break; // This looks like actual passage content
                      }
                      
                      // Also stop if we hit paragraph numbers or Part markers
                      if (nextLine.match(/^\d+$/) || nextLine.match(/^Part\s+[12]$/i)) {
                        break;
                      }
                    }
                    
                    // Title is valid if followed by "by Author" OR "This article..." metadata
                    if (foundByAuthor || foundMetadata) {
                      // If we found "by Author" or metadata after this line, it's almost certainly a title
                      // Just make sure it doesn't look like passage content (doesn't start with lowercase dialogue)
                      const looksLikeTitle = !line.match(/^[a-z]/) || // Doesn't start with lowercase
                                            line.match(/^(Excerpt|Adapted|Making|The|Antonio|Annabel|Libby|Amelia|What's|Dinos)/i) ||
                                            line.length < 60;
                      
                      if (looksLikeTitle) {
                        foundTitle = true;
                        isFirstContentLine = false;
                        continue; // Skip title line
                      }
                    }
                  }
                  
                  // Mark that we've passed the first content line
                  if (line && !foundTitle) {
                    isFirstContentLine = false;
                  }
                  
                  // Skip "by Author" line (only if we found a title)
                  if (foundTitle && !foundAuthor && line.match(/^by\s+.+$/i)) {
                    foundAuthor = true;
                    continue;
                  }
                  
                  // Skip "This article/text was written/published..." lines (only after title)
                  // This handles cases where there's no author but there's metadata (like "What's It Like to Be a Chef?")
                  if (foundTitle && line.match(/^This\s+(article|text)\s+was\s+(written|published)/i)) {
                    continue;
                  }
                  
                  // Skip lines that are just "(Part 1)" or "(Part 2)" - these should only be in title box
                  if (line.match(/^\(Part\s+[12]\)$/i)) {
                    continue;
                  }
                  
                  // Keep all other lines (including passage content)
                  cleanedLines.push(originalLine); // Keep original line with spacing
                  isFirstContentLine = false; // We've added content, so we're past the title section
                }
                
                // Remove any duplicate consecutive lines
                const result = cleanedLines.join('\n').trim();
                const resultLines = result.split('\n');
                const deduplicatedLines = [];
                for (let i = 0; i < resultLines.length; i++) {
                  const current = resultLines[i].trim();
                  const previous = i > 0 ? resultLines[i - 1].trim() : '';
                  // Skip if this line is identical to the previous line (duplicate)
                  if (current && current !== previous) {
                    deduplicatedLines.push(resultLines[i]);
                  } else if (!current) {
                    // Keep empty lines
                    deduplicatedLines.push(resultLines[i]);
                  }
                }
                return deduplicatedLines.join('\n').trim();
              };
              
              // For "both parts" questions, try to split into Part 1 and Part 2 for visual separation
              let displayParts = [];
              let originalParts = []; // Keep original passage parts for title extraction
              
              if (isBothParts && passageParts && passageParts.length >= 2) {
                // For "both parts", we need to split the full passage into Part 1 and Part 2
                // CRITICAL: Look for duplicate title pattern BEFORE "Part 2" marker
                // When both parts are concatenated, Part 2 starts with: "Title\nby Author\n\nPart 2\n\nContent"
                // We need to find where the duplicate title begins and split there
                
                // First, try to find the duplicate title pattern before "Part 2"
                // Pattern: Title (e.g., "The Great Escape") followed by "by Author" then "Part 2"
                const duplicateTitlePatterns = [
                  /\n\nThe Great Escape\s*\nby Susan Mitsch\s*\n\nPart\s+2\s*\n\n/i,
                  /\n\nExcerpt from Under My Nose\s*\nby Lois Ehlert\s*\n\nPart\s+2\s*\n\n/i,
                  /\n\nAdapted from.*Grandfather Frog.*\nby.*\n\nPart\s+2\s*\n\n/i,
                  /\n\nAdapted from.*Beavers.*\nby.*\n\nPart\s+2\s*\n\n/i,
                  /\n\nExcerpt from.*Dog a Hero.*\nby.*\n\nPart\s+2\s*\n\n/i
                ];
                
                let duplicateTitleMatch = null;
                for (const pattern of duplicateTitlePatterns) {
                  duplicateTitleMatch = passage.match(pattern);
                  if (duplicateTitleMatch) break;
                }
                
                // If we found duplicate title pattern, split there
                if (duplicateTitleMatch) {
                  // Split BEFORE the duplicate title (which is the start of Part 2)
                  const part1Text = passage.substring(0, duplicateTitleMatch.index).trim();
                  
                  // Part 2 starts after the duplicate title and "Part 2" marker
                  // Find where actual Part 2 content starts (after "Part 2\n\n")
                  let part2ContentStart = duplicateTitleMatch.index + duplicateTitleMatch[0].length;
                  while (part2ContentStart < passage.length && 
                         (passage[part2ContentStart] === '\n' || passage[part2ContentStart] === ' ' || passage[part2ContentStart] === '\r')) {
                    part2ContentStart++;
                  }
                  const part2Text = passage.substring(part2ContentStart).trim();
                  
                  originalParts = [part1Text, part2Text];
                  displayParts = originalParts.map(cleanPassageText);
                } else {
                  // Fallback: Look for "Part 2" marker directly
                  const part2Match = passage.match(/\n\nPart\s+2\s*\n\n/i) || 
                                     passage.match(/\n\nPart\s+2\s*\n/i) ||
                                     passage.match(/\nPart\s+2\s*\n\n/i) ||
                                     passage.match(/\nPart\s+2\s*\n/i) || 
                                     passage.match(/^Part\s+2\s*\n/i) ||
                                     passage.match(/\n\nPart\s+2\s/i) ||
                                     passage.match(/Part\s+2\s*\n/i);
                  
                  if (part2Match) {
                    // Found Part 2 marker - split there
                    // CRITICAL: Everything BEFORE "Part 2" marker is Part 1
                    // Everything AFTER "Part 2" marker is Part 2
                    
                    // Find where Part 2 content actually starts (after "Part 2" marker and newlines)
                    let part2ContentStart = part2Match.index + part2Match[0].length;
                    // Skip any leading whitespace/newlines to find actual content start
                    while (part2ContentStart < passage.length && 
                           (passage[part2ContentStart] === '\n' || passage[part2ContentStart] === ' ' || passage[part2ContentStart] === '\r')) {
                      part2ContentStart++;
                    }
                    
                    // Part 1: Everything before "Part 2" marker (should end with Part 1 content)
                    const part1Text = passage.substring(0, part2Match.index).trim();
                    
                    // Part 2: Everything after "Part 2" marker (should start with Part 2 content)
                    const part2Text = passage.substring(part2ContentStart).trim();
                    
                    // VERIFICATION: Ensure Part 1 doesn't contain Part 2 content
                  // Part 2 typically starts with specific phrases
                  const part2StartPhrases = [
                    'red pecked open the pigpens',
                    'i like to write out rough story',
                    'jerry muskrat',
                    'the beavers build their houses',
                    'the rescue team'
                  ];
                  
                  const part1Lower = part1Text.toLowerCase();
                  const part2Lower = part2Text.toLowerCase();
                  
                  // Check if Part 1 incorrectly contains Part 2 content
                  // Look for Part 2 start phrases in Part 1 (they shouldn't be there)
                  let part2ContentInPart1 = null;
                  for (const phrase of part2StartPhrases) {
                    const phraseIndex = part1Lower.indexOf(phrase);
                    if (phraseIndex > 0) {
                      // Found Part 2 content in Part 1 - this is wrong!
                      // Find the last occurrence of Part 1 content before this phrase
                      part2ContentInPart1 = phraseIndex;
                      break;
                    }
                  }
                  
                  // Check if Part 2 correctly starts with Part 2 content
                  const part2StartsWithCorrectContent = part2StartPhrases.some(phrase => 
                    part2Lower.startsWith(phrase) || 
                    part2Lower.match(new RegExp(`^[\\s\\n]*${phrase.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`, 'i'))
                  );
                  
                  // If Part 1 has Part 2 content, we need to find a better split point
                  if (part2ContentInPart1 !== null) {
                    // Part 2 content is incorrectly in Part 1 - find where Part 1 should actually end
                    // Look backwards from the Part 2 content to find a natural break (double newline or end of sentence)
                    let actualPart1End = part2ContentInPart1;
                    
                    // Try to find a double newline before the Part 2 content
                    const lastDoubleNewline = part1Text.substring(0, part2ContentInPart1).lastIndexOf('\n\n');
                    if (lastDoubleNewline > part2ContentInPart1 * 0.5) {
                      // Found a reasonable break point
                      actualPart1End = lastDoubleNewline;
                    } else {
                      // Look for end of sentence before Part 2 content
                      const lastPeriod = part1Text.substring(0, part2ContentInPart1).lastIndexOf('.');
                      if (lastPeriod > part2ContentInPart1 * 0.7) {
                        actualPart1End = lastPeriod + 1;
                      }
                    }
                    
                    // Split at the corrected point
                    const correctedPart1 = part1Text.substring(0, actualPart1End).trim();
                    const correctedPart2 = part1Text.substring(actualPart1End).trim() + '\n\n' + part2Text;
                    
                    originalParts = [correctedPart1, correctedPart2];
                    displayParts = originalParts.map(cleanPassageText);
                  } else if (!part2StartsWithCorrectContent && part2Text.length > 0) {
                    // Part 2 doesn't start with expected content - might be missing title/header
                    // Check if Part 2 text starts with a title that should be removed
                    const part2FirstLine = part2Text.split('\n')[0].toLowerCase();
                    if (part2FirstLine.includes('the great escape') || 
                        part2FirstLine.includes('under my nose') ||
                        part2FirstLine.includes('grandfather frog') ||
                        part2FirstLine.includes('beavers') ||
                        part2FirstLine.includes('dog a hero')) {
                      // Part 2 starts with title - find where actual content starts
                      const titleEndIndex = part2Text.indexOf('\n\n');
                      if (titleEndIndex > 0) {
                        const correctedPart2 = part2Text.substring(titleEndIndex + 2).trim();
                        originalParts = [part1Text, correctedPart2];
                        displayParts = originalParts.map(cleanPassageText);
                      } else {
                        originalParts = [part1Text, part2Text];
                        displayParts = originalParts.map(cleanPassageText);
                      }
                    } else {
                      // Normal case: split is correct
                      originalParts = [part1Text, part2Text];
                      displayParts = originalParts.map(cleanPassageText);
                    }
                  } else {
                    // Normal case: split is correct
                    originalParts = [part1Text, part2Text];
                    displayParts = originalParts.map(cleanPassageText);
                  }
                  } else {
                    // No Part 2 marker found - try to find in passageParts array
                  let part1Index = -1;
                  let part2Index = -1;
                  
                  // Look for Part 1 and Part 2 markers in each part
                  for (let i = 0; i < passageParts.length; i++) {
                    const partLower = passageParts[i].toLowerCase();
                    if (partLower.includes('part 1') && !partLower.includes('part 2')) {
                      part1Index = i;
                    }
                    if (partLower.includes('part 2')) {
                      part2Index = i;
                    }
                  }
                  
                  // If we found both parts in the array, use them directly
                  if (part1Index >= 0 && part2Index > part1Index) {
                    // Combine all parts before Part 2 as Part 1, and Part 2 onwards as Part 2
                    originalParts = [
                      passageParts.slice(0, part2Index).join('\n\n'),
                      passageParts.slice(part2Index).join('\n\n')
                    ];
                    displayParts = originalParts.map(cleanPassageText);
                  } else if (part2Index > 0) {
                    // Found Part 2 but not Part 1 - split at Part 2
                    originalParts = [
                      passageParts.slice(0, part2Index).join('\n\n'),
                      passageParts.slice(part2Index).join('\n\n')
                    ];
                    displayParts = originalParts.map(cleanPassageText);
                  } else {
                    // No clear markers in passageParts - try to find in full passage text
                    const passageLower2 = passage.toLowerCase();
                    
                    // Look for Part 2 marker in full passage (most reliable indicator)
                    const part2Match2 = passage.match(/\n\nPart\s+2\s*\n\n/i) || 
                                        passage.match(/\n\nPart\s+2\s*\n/i) ||
                                        passage.match(/\nPart\s+2\s*\n\n/i) ||
                                        passage.match(/\nPart\s+2\s*\n/i) || 
                                        passage.match(/^Part\s+2\s*\n/i) ||
                                        passage.match(/\n\nPart\s+2\s/i) ||
                                        passage.match(/Part\s+2\s*\n/i);
                    
                    // Also look for duplicate title pattern (e.g., "The Great Escape" appears twice)
                    const titlePatterns = [
                      /The Great Escape/gi,
                      /Under My Nose/gi,
                      /Grandfather Frog/gi,
                      /Beavers at Home/gi,
                      /Dog a Hero on Mount Hood/gi
                    ];
                    
                    let duplicateTitleIndex = -1;
                    for (const pattern of titlePatterns) {
                      const matches = [...passage.matchAll(pattern)];
                      if (matches.length >= 2) {
                        const firstMatch = matches[0];
                        const secondMatch = matches[1];
                        const contentBetween = passage.substring(firstMatch.index + firstMatch[0].length, secondMatch.index);
                        if (contentBetween.length > 100) {
                          duplicateTitleIndex = secondMatch.index;
                          break;
                        }
                      }
                    }
                    
                    if (part2Match2) {
                      // Found Part 2 marker - split there (most reliable)
                      const splitIndex = part2Match2.index + part2Match2[0].length;
                      originalParts = [
                        passage.substring(0, part2Match2.index).trim(),
                        passage.substring(splitIndex).trim()
                      ];
                      displayParts = originalParts.map(cleanPassageText);
                    } else if (duplicateTitleIndex > 0) {
                      // Found duplicate title - split before the duplicate title
                      const beforeTitle = passage.substring(0, duplicateTitleIndex);
                      const lastDoubleNewline = beforeTitle.lastIndexOf('\n\n');
                      
                      if (lastDoubleNewline > duplicateTitleIndex * 0.3) {
                        originalParts = [
                          passage.substring(0, lastDoubleNewline).trim(),
                          passage.substring(lastDoubleNewline).trim()
                        ];
                        displayParts = originalParts.map(cleanPassageText);
                      } else {
                        originalParts = [
                          beforeTitle.trim(),
                          passage.substring(duplicateTitleIndex).trim()
                        ];
                        displayParts = originalParts.map(cleanPassageText);
                      }
                    } else {
                      // Fallback: Split the full passage roughly in half, looking for a natural break
                      const midPoint = Math.floor(passage.length / 2);
                      const beforeMid = passage.substring(0, midPoint);
                      const splitPoint = beforeMid.lastIndexOf('\n\n');
                      
                      if (splitPoint > midPoint * 0.4) {
                        // Found a reasonable split point
                        originalParts = [
                          passage.substring(0, splitPoint).trim(),
                          passage.substring(splitPoint).trim()
                        ];
                        displayParts = originalParts.map(cleanPassageText);
                      } else {
                        // No good split point found - show as single passage with full text
                        originalParts = [passage];
                        displayParts = [cleanPassageText(passage)];
                      }
                    }
                  }
                  }
                }
              } else {
                // Single passage - show full text, no part labels
                originalParts = [passage];
                displayParts = [cleanPassageText(passage)];
              }
              
              // Compute titles for displayParts using ORIGINAL passage text (before cleaning)
              // CRITICAL: Extract titles from original text, not cleaned text
              let displayTitles = originalParts.map((part, idx) => extractPassageTitle(part, idx));
              
              // CRITICAL: Ensure Part 1 comes before Part 2 by checking content
              if (isBothParts && displayParts.length >= 2) {
                // Verify order: Part 1 should contain "Part 1" marker or come first
                const part1Lower = originalParts[0].toLowerCase();
                const part2Lower = originalParts[1].toLowerCase();
                
                const part1HasPart1 = part1Lower.includes('part 1') && !part1Lower.includes('part 2');
                const part2HasPart2 = part2Lower.includes('part 2');
                const part1HasPart2 = part1Lower.includes('part 2');
                const part2HasPart1 = part2Lower.includes('part 1') && !part2Lower.includes('part 2');
                
                // Check if Part 1 starts with Part 1 content (e.g., "The county was full of farms")
                const part1StartsWithPart1Content = part1Lower.includes('the county was full of farms') || 
                                                     part1Lower.includes('i never planned to be a writer') ||
                                                     part1Lower.includes('billy mink ran around') ||
                                                     part1Lower.includes('a beaver is a wild animal') ||
                                                     part1Lower.includes('velvet was a german shepherd');
                
                // Check if Part 2 starts with Part 2 content (e.g., "Red pecked open the pigpens")
                const part2StartsWithPart2Content = part2Lower.includes('red pecked open the pigpens') ||
                                                     part2Lower.includes('i like to write out rough story') ||
                                                     part2Lower.includes('jerry muskrat') ||
                                                     part2Lower.includes('the beavers build their houses') ||
                                                     part2Lower.includes('the rescue team');
                
                // Check if Part 1 starts with Part 2 content (wrong order indicator)
                const part1StartsWithPart2Content = part1Lower.includes('red pecked open the pigpens') ||
                                                     part1Lower.includes('i like to write out rough story') ||
                                                     part1Lower.includes('jerry muskrat') ||
                                                     part1Lower.includes('the beavers build their houses') ||
                                                     part1Lower.includes('the rescue team');
                
                // Check if Part 2 starts with Part 1 content (wrong order indicator)
                const part2StartsWithPart1Content = part2Lower.includes('the county was full of farms') || 
                                                     part2Lower.includes('i never planned to be a writer') ||
                                                     part2Lower.includes('billy mink ran around') ||
                                                     part2Lower.includes('a beaver is a wild animal') ||
                                                     part2Lower.includes('velvet was a german shepherd');
                
                // If parts are swapped (Part 2 comes before Part 1), swap them
                if ((part1HasPart2 && part2HasPart1) || 
                    (!part1HasPart1 && part2HasPart1) ||
                    (part1StartsWithPart2Content && part2StartsWithPart1Content)) {
                  // Parts are swapped - swap them back
                  [originalParts[0], originalParts[1]] = [originalParts[1], originalParts[0]];
                  [displayParts[0], displayParts[1]] = [displayParts[1], displayParts[0]];
                  [displayTitles[0], displayTitles[1]] = [displayTitles[1], displayTitles[0]];
                }
              }
              
              if (isBothParts && displayParts.length >= 2) {
                // Ensure both parts have titles with proper Part labels
                const part1Title = displayTitles[0];
                const part2Title = displayTitles[1];
                
                // Helper to extract base title (without Part label)
                const getBaseTitle = (title) => {
                  if (!title) return null;
                  // Remove Part label if present (can be on same line or separate line)
                  return title.replace(/\n?\(Part\s+[12]\)/gi, '').trim();
                };
                
                // If Part 1 has a title but Part 2 doesn't
                if (part1Title && !part2Title) {
                  const baseTitle = getBaseTitle(part1Title);
                  displayTitles[0] = `${baseTitle}\n(Part 1)`;
                  displayTitles[1] = `${baseTitle}\n(Part 2)`;
                }
                // If Part 2 has a title but Part 1 doesn't
                else if (part2Title && !part1Title) {
                  const baseTitle = getBaseTitle(part2Title);
                  displayTitles[0] = `${baseTitle}\n(Part 1)`;
                  displayTitles[1] = `${baseTitle}\n(Part 2)`;
                }
                // If both have titles, ensure they have Part labels
                else if (part1Title && part2Title) {
                  // Get base titles (without Part labels)
                  const baseTitle1 = getBaseTitle(part1Title);
                  const baseTitle2 = getBaseTitle(part2Title);
                  
                  // Use the longer/more complete title as the base (likely has author)
                  const baseTitle = baseTitle1.length >= baseTitle2.length ? baseTitle1 : baseTitle2;
                  
                  // Ensure both have Part labels
                  displayTitles[0] = `${baseTitle}\n(Part 1)`;
                  displayTitles[1] = `${baseTitle}\n(Part 2)`;
                }
                // If neither has a title, try to extract from the first part
                else if (!part1Title && !part2Title && originalParts.length >= 2) {
                  const extractedTitle = extractPassageTitle(originalParts[0], 0);
                  if (extractedTitle) {
                    const baseTitle = getBaseTitle(extractedTitle);
                    displayTitles[0] = `${baseTitle}\n(Part 1)`;
                    displayTitles[1] = `${baseTitle}\n(Part 2)`;
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
                            color: '#0056b3'
                          }}>
                            {passageTitle.split('\n').map((line, lineIdx) => {
                              const isTitle = lineIdx === 0;
                              const isAuthor = line.match(/^by\s+/i);
                              const isPart = line.match(/\(Part\s+[12]\)/i);
                              
                              return (
                                <div key={lineIdx} style={{
                                  fontSize: isTitle ? '18px' : isAuthor ? '14px' : '16px',
                                  fontWeight: isTitle ? 'bold' : 'normal',
                                  fontStyle: isTitle ? 'italic' : 'normal',
                                  marginBottom: lineIdx < passageTitle.split('\n').length - 1 ? '4px' : '0'
                                }}>
                                  {line}
                                </div>
                              );
                            })}
                          </div>
                        )}
                      <div style={{ 
                        whiteSpace: 'pre-wrap',
                        fontFamily: 'Georgia, serif',
                        textAlign: 'left'
                      }}>
                        {part.split('\n').map((line, idx) => {
                          // Remove "Part 1" or "Part 2" from the passage text if it appears (redundant with title)
                          let cleanedLine = line.replace(/^\s*Part\s+[12]\s*$/i, '').trim();
                          
                          // Check if line is a paragraph number (regular number or circled number)
                          // Paragraph numbers can be: regular (2, 5, 6) or circled (②, ⑤, ⑥)
                          const trimmedLine = cleanedLine.trim();
                          
                          // Map of circled numbers to regular numbers
                          const circledToRegular = {
                            '①': '1', '②': '2', '③': '3', '④': '4', '⑤': '5',
                            '⑥': '6', '⑦': '7', '⑧': '8', '⑨': '9', '⑩': '10',
                            '⑪': '11', '⑫': '12', '⑬': '13', '⑭': '14', '⑮': '15',
                            '⑯': '16', '⑰': '17', '⑱': '18', '⑲': '19', '⑳': '20'
                          };
                          
                          // Check for regular number
                          let paragraphMatch = trimmedLine.match(/^(\d+)$/);
                          let paragraphNum = paragraphMatch ? paragraphMatch[1] : null;
                          
                          // If not regular number, check for circled number
                          if (!paragraphNum && trimmedLine.length === 1 && circledToRegular[trimmedLine]) {
                            paragraphNum = circledToRegular[trimmedLine];
                          }
                          
                          if (paragraphNum) {
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
                                {paragraphNum}
                              </div>
                            );
                          }
                          
                          // Regular text line - skip empty lines (they're just spacing)
                          if (!trimmedLine) {
                            return <div key={`${partIdx}-${idx}`} style={{ marginBottom: '4px' }}>{'\u00A0'}</div>;
                          }
                          
                          // Remove "Part 1" or "Part 2" from text lines as well
                          cleanedLine = cleanedLine.replace(/^\s*Part\s+[12]\s*$/i, '').trim();
                          if (!cleanedLine) {
                            return <div key={`${partIdx}-${idx}`} style={{ marginBottom: '4px' }}>{'\u00A0'}</div>;
                          }
                          
                          return <div key={`${partIdx}-${idx}`} style={{ marginBottom: '8px' }}>{cleanedLine}</div>;
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

