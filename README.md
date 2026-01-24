# EOG Quiz Preparation System

Adaptive quiz application for Grade 3-5 Mathematics and Reading. Identifies weak topics and provides targeted practice using semantic search and AI-powered recommendations.

## Recent Updates

- **Vector Database**: ChromaDB integration for semantic question similarity
- **Question Review**: Enhanced results with detailed feedback and similar problems
- **Image Support**: Visual elements for mathematics questions
- **Expanded Question Bank**: Additional questions across all grades
- **Free Response**: Grade 5 Mathematics open-ended questions
- **Improved Persistence**: Enhanced question storage and retrieval

## Features

- **Multi-grade Support**: Grades 3-5, Math & Reading
- **Adaptive Quizzes**: 10 questions, balanced topic distribution
- **Targeted Practice**: Focus on weak topics (<80% score)
- **Question Review**: Detailed analysis with similar problems
- **Progress Tracking**: Mastery metrics and history
- **Semantic Search**: AI-powered question recommendations
- **Admin Dashboard**: Student statistics and analytics
- **AI Feedback**: Optional personalized tips (requires Ollama)

## Quick Start

```bash
# Backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

Access at `http://localhost:5173`

## Architecture

**Backend: FastAPI**
- High-performance async framework for API endpoints
- Automatic OpenAPI documentation
- Type hints for better code reliability

**Database Stack:**
- **Oracle DB**: Primary storage for questions, users, quiz attempts
- **Redis**: 5-minute TTL cache for history and mastery status
- **ChromaDB**: Vector embeddings for semantic question similarity

**Frontend: React**
- Component-based architecture for quiz interface
- State management for quiz flow and results
- Dynamic topic loading and question rendering

**AI Integration:**
- **Ollama**: Local LLM for personalized feedback (optional)
- **Sentence Transformers**: Text embeddings for semantic search
- **ChromaDB**: Vector similarity for finding similar questions

## ChromaDB Vector System

**Vector Embeddings Process:**
- Each question text is converted to 384-dimensional vector using `all-MiniLM-L6-v2` model
- Embeddings capture semantic meaning, not just keyword matching
- Questions with similar concepts have close vector distances regardless of exact wording

**ChromaDB Architecture:**
- 6 separate collections: `grade3_math`, `grade3_reading`, `grade4_math`, `grade4_reading`, `grade5_math`, `grade5_reading`
- Each collection stores vectors with metadata: question_id, topic, grade_level, subject, difficulty
- Persistent storage in `./chroma_db` directory
- Automatic indexing for fast similarity search

**Semantic Search Workflow:**
1. Student answers question incorrectly
2. System embeds the question text using same transformer model
3. ChromaDB queries for top 5 most similar vectors within same topic/grade
4. Similarity score calculated (1 - cosine distance)
5. Returns questions with high semantic similarity for practice

**Example Use Case:**
- Student fails "What is 15% of 80?" (fractions/percentages topic)
- Vector search finds similar questions:
  - "Calculate 25% of 120" (same concept, different numbers)
  - "Find 30% of 150" (similar percentage calculation)
  - "What fraction is equivalent to 0.75?" (related concept)

**Technical Benefits:**
- Conceptual similarity vs keyword matching
- Grade and topic-aware filtering
- Fast retrieval (<100ms for typical queries)
- Scalable to thousands of questions
- Enables AI-driven practice recommendations

## Component Architecture

**Backend Components:**
- `adaptive.py`: Question selection algorithm with balanced topic distribution
- `scoring.py`: Weighted scoring system and weak topic identification
- `vector_db.py`: ChromaDB integration for semantic question search
- `quiz.py`: Quiz generation, submission, and retake endpoints

**Frontend Components:**
- `StartQuiz.jsx`: Grade/subject selection with dynamic topic loading
- `TakeQuiz.jsx`: Question rendering with TTS and image support
- `QuizResults.jsx`: Results display with question review and similar problems

**Vector Database Flow:**
1. Questions embedded using sentence transformers
2. Stored in ChromaDB with metadata (topic, grade, subject)
3. Semantic search finds similar questions when students make mistakes
4. Results page shows similar problems for targeted practice

**Quiz Workflow:**
1. Generate 10 randomized questions (balanced across topics)
2. Track answers and calculate topic-specific scores
3. Identify weak topics (<80% accuracy)
4. Provide similar questions using vector search
5. Enable targeted practice on weak areas

## Question Bank

**300+ EOG-style questions:**
- Grade 3: Math (5 topics) + Reading (5 topics)
- Grade 4: Math + Reading + Geometry
- Grade 5: Math + Reading + Free Response

**Recent Additions:**
- Enhanced number operations (Grade 3)
- Expanded geometry and low-topic coverage (Grade 4)
- Additional vocabulary questions (Grade 5)
- Visual mathematics problems with diagrams

## API Endpoints

**Authentication & Quiz Management:**
- `POST /auth/register` - User registration with validation
- `POST /auth/login` - JWT-based authentication
- `POST /quiz/generate` - Creates quiz with balanced topic distribution
- `POST /quiz/{id}/submit` - Processes answers and calculates scores
- `POST /quiz/practice-topic` - Generates targeted practice for weak topics

**Vector Database Integration:**
- `POST /vector-db/sync` - Embeds and stores all questions in ChromaDB
- `POST /vector-db/query` - Semantic search for similar questions
- `GET /vector-db/stats` - Monitor vector database health and usage

**Data Flow:**
1. Quiz submission triggers scoring algorithm
2. Weak topics identified (<80% threshold)
3. Vector search finds semantically similar questions
4. Results page includes targeted practice recommendations

## System Workflow

**1. Quiz Generation:**
- Timestamp-based seeding ensures unique question sets
- Adaptive algorithm balances topic distribution
- No duplicate questions within single quiz

**2. Results Analysis:**
- Case-insensitive answer comparison
- Weighted topic scoring algorithm
- Weak topic identification (<80% accuracy)
- Mastery tracking (2 consecutive perfect quizzes)

**3. Vector-Powered Review:**
- Incorrect answers trigger semantic search
- ChromaDB finds conceptually similar problems
- Students practice question types they struggle with
- AI-driven recommendations improve learning efficiency

**4. Progress Tracking:**
- Redis caching for fast history retrieval
- Mastery metrics across topics and subjects
- Admin dashboard for comprehensive analytics

## Setup

**Database:**
```bash
docker-compose up -d oracle-db  # Oracle DB (port 1521)
# Create .env with DB credentials
# Auto-seeds math questions on startup

# Add reading questions
python add_reading_questions.py           # Grade 3
python add_grade4_reading_questions.py    # Grade 4
python add_grade5_reading_questions.py    # Grade 5

# Sync vector DB
curl -X POST http://localhost:8000/vector-db/sync
```

**AI Features (Optional):**
```bash
# Ollama for feedback
ollama pull llama2
export LLM_PROVIDER=ollama

# Vector search
pip install chromadb sentence-transformers
```
