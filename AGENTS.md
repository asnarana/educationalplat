# AGENTS.md — GradeMaster

Reference guide for AI agents working in this repository. Describes the major system components, what each does, and how to reason about changes.

---

## Project Overview

**GradeMaster** is an adaptive remediation quiz platform for grades 3–5. Students take quizzes; the system tracks performance per topic and biases future quizzes toward weak areas until mastery is achieved.

---

## Agent Responsibilities

### Backend Logic Agents

#### Adaptive Engine — `app/logic/adaptive.py`
Selects which questions to show next based on student performance history.
- 70% weak-topic questions, 30% other (when weak topics exist)
- Avoids repeating questions from the last 2 quizzes
- Mastery = 2 consecutive quiz attempts with zero weak topics
- **When to touch:** question selection bugs, bias tuning, mastery threshold changes

#### Scoring Engine — `app/logic/scoring.py`
Grades student answers deterministically.
- String match (normalized) then numeric match (supports fractions)
- Mastery threshold: 80% per topic
- **When to touch:** grading bugs, adding new answer formats, changing mastery threshold

#### LLM Feedback — `app/logic/llm_provider.py`
Generates personalized feedback via a local Ollama instance.
- Configured via env vars: `OLLAMA_MODEL`, `OLLAMA_BASE_URL`, temperature, token limit
- Validates Ollama is running and model is pulled before calling
- **When to touch:** prompt tuning, switching models, adding new feedback types

#### Vector DB / RAG — `app/logic/vector_db.py`
Semantic question search using ChromaDB + sentence-transformers.
- 6 collections: one per grade (3, 4, 5) × subject (math, reading)
- Synced from Oracle on startup; optional (app works without it)
- **When to touch:** adding semantic search features, collection structure changes

---

### Infrastructure Agents

#### Database — `app/db.py`
Oracle via `oracledb` + SQLAlchemy with `NullPool`.
- Schema migrations done with `ALTER TABLE` guards in `init_db()` — **no Alembic**
- Oracle sequences must be created before `Base.metadata.create_all()`
- **When to touch:** adding columns (add model field + ALTER TABLE guard in `init_db()`), schema changes

#### Auth — `app/routes/auth.py`
Session token auth stored in an in-memory Python dict.
- Sessions are lost on server restart — users must re-login
- Admin password resets to `"123"` on every startup
- **When to touch:** adding endpoints, TTL changes, persistent session storage

#### Cache — `app/cache.py`
Redis caching (optional — app degrades gracefully if Redis is unavailable).

| Cached data | TTL |
|---|---|
| Student history | 2 min |
| Mastery status | 2 min |
| Recent question IDs | 1 min |
| Quiz type classification | 10 min |

Call `invalidate_student_cache()` after every quiz submission.

#### Monitoring — `app/monitoring/`
- Prometheus metrics at `GET /metrics`
- Grafana dashboard at `localhost:3001` (admin/admin)

---

### Frontend Agents

All frontend code lives in `frontend/src/`. React 18 + React Router v6 + Vite. No global state library — state is local or prop-drilled.

#### Page Flow
```
Login → StartQuiz → TakeQuiz → QuizResults → StudentHistory
```
Admin route: `AdminDashboard` (protected by `requireAdmin` in `ProtectedRoute`)

#### API Client — `frontend/src/api/client.js`
All backend calls go through this module. Session token stored in `localStorage`.
- **When to touch:** adding new API calls, auth header changes

---

## Key Rules for Agents

1. **No Alembic** — schema changes must use `ALTER TABLE` guards in `app/db.py:init_db()`.
2. **Oracle sequences first** — always create sequences before `Base.metadata.create_all()`.
3. **In-memory sessions** — do not assume sessions survive restarts.
4. **ChromaDB is optional** — always check `VECTOR_DB_AVAILABLE` before calling vector DB code.
5. **Cache invalidation** — call `invalidate_student_cache()` after any quiz write.
6. **Admin password** — hardcoded reset on startup; do not rely on API-set passwords persisting.

---

## Services & Ports

| Service | Port |
|---|---|
| FastAPI backend | 8000 |
| Vite frontend | 5173 |
| Oracle DB | 1522 |
| Redis | 6379 |
| Prometheus | 9090 |
| Grafana | 3001 |
