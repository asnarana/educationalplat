# Prometheus & Grafana - Simple Explanation

## 🎯 What Are They?

Think of **Prometheus** and **Grafana** like a **speedometer and dashboard** for your car:

- **Prometheus** = The speedometer (collects data about how fast you're going)
- **Grafana** = The dashboard display (shows you graphs and charts of that data)

## 📊 What They Do

### Prometheus (Data Collector)
- **Job**: Collects numbers/metrics from your app every 15 seconds
- **What it collects**: How many requests, how fast responses are, how many quizzes created, etc.
- **Where it stores**: In its own database (time-series database)
- **Access**: http://localhost:9090

### Grafana (Visual Dashboard)
- **Job**: Takes data from Prometheus and shows it in pretty graphs
- **What it shows**: Charts, graphs, alerts about your app performance
- **Access**: http://localhost:3001 (username: admin, password: admin)

## 🔄 How They Work Together

```
Your App (FastAPI)
    ↓ (sends metrics every request)
Prometheus (collects and stores)
    ↓ (Grafana reads from Prometheus)
Grafana (displays graphs)
```

## 📈 What Happens in YOUR App

### Step 1: App Records Metrics
Every time someone uses your app, it records:
- **HTTP Requests**: "Someone called /quiz/generate"
- **Response Time**: "That request took 0.5 seconds"
- **Quiz Activity**: "A Grade 3 quiz was created"
- **Quiz Scores**: "Student got 85%"

### Step 2: Prometheus Collects
Every 15 seconds, Prometheus asks your app: "Hey, what are your current numbers?"
- Your app responds at: `http://localhost:8000/metrics`
- Prometheus stores these numbers with timestamps

### Step 3: Grafana Shows Charts
Grafana reads from Prometheus and displays:
- Graph of requests per minute
- Average response times
- Number of quizzes created today
- Score distributions

## 🔍 The Flow in Detail

### When a Student Takes a Quiz:

1. **Student clicks "Start Quiz"** 
   → Frontend calls `POST /quiz/generate`
   
2. **PrometheusMiddleware** (middleware.py) intercepts:
   ```python
   - Records: "POST /quiz/generate called"
   - Starts timer
   - Processes request
   - Records: "Request took 0.3 seconds, returned status 200"
   ```

3. **Quiz is generated** (quiz.py):
   ```python
   - Creates quiz in database
   - Calls: track_quiz_generated(grade_level=3, quiz_type='full')
   - Records metric: "1 quiz generated for Grade 3"
   ```

4. **Student submits quiz**:
   ```python
   - Calls: track_quiz_submitted(grade_level=3, score=0.85, passed=False)
   - Records: "1 quiz submitted, score 85%, not passed"
   ```

5. **Prometheus collects all these metrics**:
   - Every 15 seconds, scrapes: `http://localhost:8000/metrics`
   - Gets raw numbers like:
     ```
     http_requests_total{method="POST",endpoint="/quiz/generate",status_code="200"} 42
     quiz_scores{grade_level="3",quiz_type="full"} 85.0
     ```

6. **Grafana reads from Prometheus** and shows:
   - Chart: "Quizzes Generated Over Time"
   - Chart: "Average Quiz Scores by Grade"
   - Chart: "Requests per Minute"

## 📋 What Metrics Are Being Tracked?

### 1. API Performance (automatic via middleware)
- `http_requests_total`: Count of all HTTP requests
- `http_request_duration_seconds`: How long each request took

### 2. Quiz Activity (manual tracking)
- `quizzes_generated_total`: How many quizzes created (by grade, type)
- `quizzes_submitted_total`: How many quizzes submitted (by grade, passed/failed)
- `quiz_scores`: Distribution of quiz scores

### 3. Topic Performance
- `topic_weak_count`: How many times each topic was weak
- `topic_mastery_count`: How many times each topic was mastered

### 4. AI Feedback (if used)
- `llm_requests_total`: Count of AI feedback requests
- `llm_request_duration_seconds`: How long AI responses take

## 🛠️ How to Use It

### View Prometheus (Raw Data):
1. Start your app
2. Open: http://localhost:9090
3. Type a metric name (e.g., `http_requests_total`)
4. See raw numbers and graphs

### View Grafana (Pretty Dashboards):
1. Start Docker: `docker-compose up -d prometheus grafana`
2. Open: http://localhost:3001
3. Login: username `admin`, password `admin`
4. See pre-made dashboards showing your app's performance

### Check Metrics from Your App:
- Open: http://localhost:8000/metrics
- See all metrics in text format (Prometheus format)

## 🎨 Example: What You See in Grafana

**Dashboard might show:**
- 📊 **Line Chart**: "Quizzes Created Today" → Shows 15 quizzes at 10am, 23 at 2pm, etc.
- 📊 **Pie Chart**: "Pass vs Fail" → Shows 65% passed, 35% failed
- 📊 **Bar Chart**: "Average Score by Topic" → Shows Addition: 90%, Fractions: 60%
- 📊 **Number Panel**: "Total Requests Today" → Shows 1,234 requests

## 💡 Why Is This Useful?

1. **See Problems Early**: "Oh, response times are getting slow!"
2. **Understand Usage**: "Grade 3 students use the app most"
3. **Track Success**: "Quiz scores are improving over time"
4. **Debug Issues**: "We got 50 errors at 3pm - what happened?"

## 🚀 Quick Start Commands

```bash
# Start Prometheus and Grafana
docker-compose up -d prometheus grafana

# View Prometheus
# Open: http://localhost:9090

# View Grafana  
# Open: http://localhost:3001
# Login: admin / admin

# Check your app's metrics endpoint
# Open: http://localhost:8000/metrics
```

## 📝 In Simple Terms

- **Prometheus** = A notebook that writes down every number your app produces
- **Grafana** = A TV screen that shows those numbers as charts and graphs
- **Your App** = Produces numbers when students take quizzes
- **You** = Watch the graphs to see how your app is doing

That's it! 🎉

