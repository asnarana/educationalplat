# Prometheus & Grafana Overview

## Components

**Prometheus**: Time-series database that scrapes metrics from applications
**Grafana**: Visualization tool that queries Prometheus and displays dashboards

## Flow

```
FastAPI App → Metrics endpoint → Prometheus (scrapes every 15s) → Grafana (queries) → Dashboard
```

## Metrics Tracked

### Automatic (via middleware)
- `http_requests_total`: Request count by method, endpoint, status
- `http_request_duration_seconds`: Request latency distribution

### Manual (application code)
- `quizzes_generated_total`: Quiz creation count by grade, type
- `quizzes_submitted_total`: Quiz submission count by grade, pass/fail
- `quiz_scores`: Score distribution histogram
- `topic_weak_count_total`: Weak topic identification count

## Access

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)
- Metrics endpoint: http://localhost:8000/metrics

## Setup

```bash
docker-compose up -d prometheus grafana
```

## Usage

1. App exposes metrics at `/metrics` endpoint
2. Prometheus scrapes every 15 seconds
3. Grafana queries Prometheus using PromQL
4. Dashboards display time-series graphs
