# PrometheusMiddleware Flow - Where It Runs

## 📍 Where It's Used

### File: `app/main.py`

**Line 9**: Import
```python
from app.monitoring.middleware import PrometheusMiddleware
```

**Line 20**: Added to FastAPI app
```python
app.add_middleware(PrometheusMiddleware)
```

---

## 🔄 How It Works (The Flow)

### Every HTTP Request Goes Through This:

```
1. Client makes request
   ↓
   POST /quiz/generate
   ↓
2. PrometheusMiddleware.dispatch() is called FIRST (line 14)
   ↓
   - Skips /metrics endpoint (line 16)
   - Starts timer (line 19)
   ↓
3. Your actual endpoint runs (e.g., quiz.py generate_quiz)
   ↓
   - Processes request
   - Returns response
   ↓
4. PrometheusMiddleware finishes (line 27-48)
   ↓
   - Calculates duration (line 28)
   - Records metrics (line 39-48)
   ↓
5. Response sent back to client
```

---

## 📊 What Gets Tracked

### For EVERY Request (except /metrics):

**1. Request Counter** (line 39-43):
```python
http_requests_total.labels(
    method=request.method,        # "GET", "POST", etc.
    endpoint=request.url.path,    # "/quiz/generate", etc.
    status_code=str(status_code)  # "200", "404", "500", etc.
).inc()
```

**2. Request Duration** (line 45-48):
```python
http_request_duration_seconds.labels(
    method=request.method,
    endpoint=request.url.path
).observe(duration)
```

---

## 🎯 Example: What Happens When Student Starts Quiz

### Request Flow:

```
1. Frontend: POST http://localhost:8000/quiz/generate
   ↓
2. PrometheusMiddleware intercepts:
   - Start time: 10:00:00.000
   - Endpoint: "/quiz/generate"
   - Method: "POST"
   ↓
3. Your code runs (app/routes/quiz.py):
   - generate_quiz() function executes
   - Creates quiz in database
   - Returns quiz data
   - Status code: 200
   ↓
4. PrometheusMiddleware finishes:
   - Duration: 0.35 seconds
   - Records: http_requests_total{method="POST", endpoint="/quiz/generate", status_code="200"} +1
   - Records: http_request_duration_seconds{method="POST", endpoint="/quiz/generate"} = 0.35
   ↓
5. Response sent to frontend
```

---

## 🚫 What Gets Skipped

### Line 16: `/metrics` endpoint is skipped
```python
if request.url.path == "/metrics":
    return await call_next(request)
```

**Why?** To prevent infinite loop:
- `/metrics` endpoint is read by Prometheus
- If we tracked `/metrics` requests, Prometheus would keep requesting `/metrics`
- This would create endless tracking loop

---

## 📈 Where You See The Data

### 1. Prometheus (http://localhost:9090)
Query: `http_requests_total`
- Shows: Total count of all requests
- Labels: method, endpoint, status_code

Query: `http_request_duration_seconds`
- Shows: How long each request took
- Labels: method, endpoint

### 2. Grafana Dashboard
Panel: "HTTP Requests Rate"
- Query: `rate(http_requests_total[5m])`
- Shows: Requests per second over time

Panel: "HTTP Request Duration (p95)"
- Query: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`
- Shows: 95% of requests are faster than X seconds

---

## 🔍 Special Processing (Line 31-36)

### Endpoint Normalization
```python
endpoint = request.url.path
if "/quiz/" in endpoint and endpoint.count("/") >= 3:
    parts = endpoint.split("/")
    if parts[-1].isdigit():
        endpoint = "/".join(parts[:-1]) + "/{id}"
```

**What it does:**
- Changes `/quiz/123` → `/quiz/{id}`
- Changes `/quiz/456` → `/quiz/{id}`

**Why?** To group similar requests:
- Without this: `/quiz/123`, `/quiz/456`, `/quiz/789` = 3 separate metrics
- With this: `/quiz/{id}` = 1 metric (all quiz requests grouped)

**Example:**
- Request 1: `POST /quiz/1/submit` → tracked as `/quiz/{id}/submit`
- Request 2: `POST /quiz/2/submit` → tracked as `/quiz/{id}/submit`
- Both count toward same metric!

---

## 💡 In Simple Terms

**PrometheusMiddleware** is like a **bouncer at a club**:

1. **Every person (request) enters** → Bouncer notes time
2. **Person goes inside** → Does their thing (your code runs)
3. **Person leaves** → Bouncer notes time again, records:
   - Who came in (method, endpoint)
   - How long they stayed (duration)
   - Status (left happy/angry = status code)

**Result**: You have a log of everyone who came, how long they stayed, and when!

---

## 📂 File Locations

| File | Purpose | Used Where |
|------|---------|------------|
| `app/monitoring/middleware.py` | Middleware code (lines 14-50) | **`app/main.py` line 20** |
| `app/monitoring/metrics.py` | Metrics definitions | Imported by middleware |
| `app/main.py` | FastAPI app setup | **Where middleware is added** |

---

## ✅ Summary

**Where middleware runs:**
- **File**: `app/monitoring/middleware.py` (lines 14-50)
- **Added in**: `app/main.py` (line 20)
- **Runs on**: **EVERY HTTP request** (except `/metrics`)
- **Tracks**: Request count, duration, method, endpoint, status code

**Flow:**
```
Request → PrometheusMiddleware (tracks) → Your Code → Response
```

That's it! 🎉

