# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project: GradeMaster

Adaptive remediation quiz system for grades 3–5. Students take quizzes; the system scores them by topic and biases future quizzes toward weak areas until mastery is achieved.

## Commands

### Start all infrastructure (Oracle DB, Redis, Prometheus, Grafana)
```bash
docker-compose up -d
```

### Run the backend (from repo root, with venv activated)
```bash
uvicorn app.main:app --reload
```
API runs on `http://localhost:8000`. Docs at `/docs`.

### Run the frontend
```bash
cd frontend
npm run dev
```
UI runs on `http://localhost:5173`.

### Run tests
```bash
pytest                          # all tests
pytest tests/test_scoring.py    # single file
pytest -k "test_grade_question" # single test by name
```

### Seed the question bank manually
```bash
curl -X POST http://localhost:8000/seed
```
Auto-seeding also runs on startup if the DB is empty.

## Architecture

### Backend: `app/`

**Entry point** — `app/main.py`  
Registers all routers, mounts static image dirs (`/static/grade{3,4,5}mathimages`), adds Prometheus and CORS middleware, and runs startup logic: DB init → admin user creation → question auto-seed → ChromaDB sync.

**Database** — `app/db.py`  
Oracle via `oracledb` driver + SQLAlchemy. Uses `NullPool` (no connection pooling). Connection configured via `.env`. `init_db()` also handles incremental schema migrations (adding columns) rather than using Alembic.

**Models** — `app/models.py`  
Four tables: `users`, `questions`, `quizzes`, `attempts`. Oracle has no native JSON type, so JSON fields use a custom `JSONType` (Text + serialize/deserialize). Oracle sequences are created explicitly in `init_db()` before `create_all()`.

**Auth** — `app/routes/auth.py`  
Session token auth (not JWT). Sessions stored in a Python in-memory dict (`sessions = {}`). Tokens expire after a fixed TTL. Use `get_current_user` (optional auth) or `get_current_admin` (required admin) as FastAPI dependencies.

**Adaptive quiz engine** — `app/logic/adaptive.py`  
Core logic for question selection. Rules:
- No weak topics → distribute evenly across all topics
- Some weak topics → 70% from weak topics, 30% from the rest
- All topics weak → even distribution (same as no-weak path)
- Avoids questions from the last 2 quizzes per student+grade
- Mastery = 2 consecutive attempts with zero weak topics

**Scoring** — `app/logic/scoring.py`  
Deterministic grading: string match (case/whitespace normalized), then numeric match (supports fractions). Mastery threshold per topic is 0.80 (80%).

**LLM feedback** — `app/logic/llm_provider.py`  
Calls a local Ollama instance via `langchain-ollama`. Model, URL, temperature, and token limit are all env-configurable (`OLLAMA_MODEL`, `OLLAMA_BASE_URL`, etc.). The provider validates Ollama is up and the model is pulled before calling.

**Vector DB / RAG** — `app/logic/vector_db.py`  
ChromaDB + `sentence-transformers` for semantic question search. 6 collections (one per grade×subject). Synced from Oracle on startup. Feature is optional — app works without it.

**Caching** — `app/cache.py`  
Redis (optional — app degrades gracefully if unavailable). Used for: student history, mastery status (2 min TTL), recent question IDs (1 min TTL), quiz type classification (10 min TTL). `invalidate_student_cache()` is called after every quiz submission.

**Monitoring** — `app/monitoring/`  
Prometheus metrics exposed at `GET /metrics`. Grafana dashboard at `:3001` (admin/admin).

### Frontend: `frontend/src/`

React 18 + React Router v6 + Vite. No state management library — all state is local or passed via props.

**Pages:** `Login` → `StartQuiz` → `TakeQuiz` → `QuizResults` → `StudentHistory`  
**Admin:** `AdminDashboard` (protected by `requireAdmin` in `ProtectedRoute`)  
**API client:** `frontend/src/api/client.js` — all backend calls go through this module; session token stored in `localStorage`.

### Infrastructure

| Service | Port | Notes |
|---|---|---|
| FastAPI | 8000 | Backend API |
| Vite dev server | 5173 | Frontend |
| Oracle DB | 1522 | Mapped from container's 1521 |
| Redis | 6379 | |
| Prometheus | 9090 | |
| Grafana | 3001 | admin/admin |

Oracle connection uses `.env` values. See `ACCESS_ORACLE.md` for SQL*Plus access instructions and table schema reference.

## Key Constraints

- **Oracle sequences** must be created before `Base.metadata.create_all()` — this is handled in `init_db()`, not via Alembic.
- **No Alembic** — schema changes are done by `ALTER TABLE` guards in `init_db()`. When adding a new column, add both the model field and an `ALTER TABLE ... ADD` guard there.
- **Session storage is in-memory** — sessions are lost on server restart; users must re-login.
- **Admin password resets to `"123"` on every startup** (`main.py:67–83`). Do not change admin passwords via the API expecting them to persist across restarts.
- **ChromaDB and sentence-transformers are optional** — importing `app.logic.vector_db` checks `VECTOR_DB_AVAILABLE` before any operations.
