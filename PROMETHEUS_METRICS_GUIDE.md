# Prometheus Metrics Guide - Finding Your Metrics

## 🔍 Important: Metric Name Suffixes

Prometheus client library automatically adds suffixes to metrics:
- **Counters** get `_total` suffix
- **Histograms** get `_sum`, `_count`, `_bucket` suffixes
- **Gauges** stay as-is

## 📊 Your Metrics and How to Find Them

### 1. Topic Weak Count
**In code**: `topic_weak_count`  
**In Prometheus/Grafana**: `topic_weak_count_total`

**Example query in Prometheus**:
```
topic_weak_count_total
```

**Example query by topic**:
```
topic_weak_count_total{topic="Addition"}
```

**Example query by grade**:
```
topic_weak_count_total{grade_level="3"}
```

### 2. Quiz Generated
**In code**: `quizzes_generated_total`  
**In Prometheus/Grafana**: `quizzes_generated_total` (same)

### 3. Quiz Submitted
**In code**: `quizzes_submitted_total`  
**In Prometheus/Grafana**: `quizzes_submitted_total` (same)

### 4. Quiz Scores
**In code**: `quiz_scores`  
**In Prometheus/Grafana**: 
- `quiz_scores_sum` - sum of all scores
- `quiz_scores_count` - number of scores
- `quiz_scores_bucket` - histogram buckets

**Example query for average score**:
```
quiz_scores_sum / quiz_scores_count
```

### 5. HTTP Requests
**In code**: `http_requests_total`  
**In Prometheus/Grafana**: `http_requests_total` (same)

### 6. HTTP Request Duration
**In code**: `http_request_duration_seconds`  
**In Prometheus/Grafana**:
- `http_request_duration_seconds_sum` - total time
- `http_request_duration_seconds_count` - number of requests
- `http_request_duration_seconds_bucket` - histogram buckets

**Example query for average duration**:
```
http_request_duration_seconds_sum / http_request_duration_seconds_count
```

## 🎯 How to Check Your Metrics

### Method 1: Check Metrics Endpoint
```powershell
python -c "import requests; r = requests.get('http://localhost:8000/metrics'); lines = [l for l in r.text.split('\n') if 'topic_weak' in l]; print('\n'.join(lines))"
```

### Method 2: Prometheus Web UI
1. Open: http://localhost:9090
2. In the search box, type: `topic_weak_count_total`
3. Click "Execute"
4. See the graph

### Method 3: Grafana
1. Open: http://localhost:3001
2. Create a new dashboard panel
3. Query: `topic_weak_count_total`
4. Add labels: `{topic="Addition"}` for specific topics

## 📈 Example Queries for Grafana

### Count weak topics by topic name:
```
sum by (topic) (topic_weak_count_total)
```

### Count weak topics by grade level:
```
sum by (grade_level) (topic_weak_count_total)
```

### Top 5 weak topics:
```
topk(5, sum by (topic) (topic_weak_count_total))
```

### Rate of weak topics per minute:
```
rate(topic_weak_count_total[5m])
```

## ✅ Current Status

Your `topic_weak_count` metric **IS WORKING** and has data:
- Addition: 3 times marked as weak
- Multiplication: 2 times
- Fractions: 2 times  
- Subtraction: 2 times
- Division: 2 times

Just use the metric name: **`topic_weak_count_total`** (with `_total` suffix)

