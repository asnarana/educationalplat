# Prometheus Metrics Flow

## Architecture

```
FastAPI App → /metrics endpoint → Prometheus scrapes → Grafana queries → Dashboard
```

## Metric Calculation

### HTTP Metrics (Automatic)

**Location:** `app/monitoring/middleware.py`

Every request:
1. Records start time
2. Executes handler
3. Calculates duration
4. Records metrics

**Metrics:**
- `http_requests_total`: Counter incremented per request
- `http_request_duration_seconds`: Histogram recording request duration

### Quiz Metrics (Manual)

**Location:** `app/routes/quiz.py`

**Functions:**
- `track_quiz_generated(grade_level, quiz_type)`: Increments `quizzes_generated_total`
- `track_quiz_submitted(grade_level, score, passed, quiz_type)`: Increments `quizzes_submitted_total`, records `quiz_scores`
- `track_weak_topic(grade_level, topic)`: Increments `topic_weak_count_total`

### Metric Types

- **Counter**: Monotonically increasing (use `rate()` for per-second)
- **Histogram**: Distribution of values (use `histogram_quantile()` for percentiles)
- **Gauge**: Current value (can increase or decrease)

## Prometheus Scraping

**Config:** `monitoring/prometheus.yml`
- Scrape interval: 15s
- Target: `host.docker.internal:8000/metrics`

**Process:**
1. Prometheus GETs `/metrics` every 15s
2. Parses Prometheus text format
3. Stores time-series data with timestamps

## Grafana Visualization

**Config:** `monitoring/grafana/datasources/prometheus.yml`
- Datasource: `http://prometheus:9090`
- Queries: PromQL sent via HTTP API

**Common PromQL Functions:**
- `rate(metric[5m])`: Per-second rate over 5 minutes
- `sum(metric)`: Aggregate values
- `histogram_quantile(0.95, ...)`: 95th percentile
- `increase(metric[1h])`: Total increase over 1 hour

## Example Flow

1. Request: `POST /quiz/generate`
   - Middleware records: `http_requests_total{method="POST", endpoint="/quiz/generate"}` += 1
   - Code calls: `track_quiz_generated(grade_level=3, quiz_type='full')`

2. Prometheus scrapes (15s later):
   - GETs `/metrics`, stores `quizzes_generated_total{grade_level="3",quiz_type="full"} 1`

3. Grafana queries:
   - `rate(quizzes_generated_total[5m])` → Returns requests per second
   - Renders as time-series graph

## Summary

1. App tracks events → Metrics exposed at `/metrics`
2. Prometheus scrapes every 15s → Stores time-series data
3. Grafana queries Prometheus → Renders dashboards
