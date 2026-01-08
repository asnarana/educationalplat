# Prometheus Metric Names

## Suffix Rules

Prometheus client adds suffixes:
- **Counters**: `_total`
- **Histograms**: `_sum`, `_count`, `_bucket`
- **Gauges**: No suffix

## Metric Mappings

| Code Name | Prometheus Name | Type |
|-----------|----------------|------|
| `topic_weak_count` | `topic_weak_count_total` | Counter |
| `quizzes_generated_total` | `quizzes_generated_total` | Counter |
| `quizzes_submitted_total` | `quizzes_submitted_total` | Counter |
| `quiz_scores` | `quiz_scores_sum`, `quiz_scores_count`, `quiz_scores_bucket` | Histogram |
| `http_requests_total` | `http_requests_total` | Counter |
| `http_request_duration_seconds` | `http_request_duration_seconds_sum`, `_count`, `_bucket` | Histogram |

## Example Queries

**By topic:**
```
topic_weak_count_total{topic="Addition"}
```

**By grade:**
```
topic_weak_count_total{grade_level="3"}
```

**Average score:**
```
quiz_scores_sum / quiz_scores_count
```

**Average duration:**
```
http_request_duration_seconds_sum / http_request_duration_seconds_count
```

## Verification

**Check endpoint:**
```powershell
curl http://localhost:8000/metrics | findstr topic_weak_count_total
```

**Prometheus UI:**
- http://localhost:9090
- Query: `topic_weak_count_total`

**Grafana:**
- Query: `sum by (topic) (topic_weak_count_total)`
