# PrometheusMiddleware Implementation

## Location

**File:** `app/monitoring/middleware.py`  
**Registered:** `app/main.py` line 20

## Request Flow

```
Request → PrometheusMiddleware.dispatch() → Handler → Response
         ↓                                    ↓
    Start timer                          Calculate duration
                                         Record metrics
```

## Implementation

**Code:** `app/monitoring/middleware.py:14-50`

**Process:**
1. Skip `/metrics` endpoint (prevents recursive tracking)
2. Record start time
3. Execute handler via `call_next()`
4. Calculate duration
5. Record `http_requests_total` and `http_request_duration_seconds`

## Metrics Recorded

**Per request:**
- `http_requests_total`: Counter with labels `method`, `endpoint`, `status_code`
- `http_request_duration_seconds`: Histogram with labels `method`, `endpoint`

## Endpoint Normalization

**Code:** `app/monitoring/middleware.py:31-36`

Normalizes paths with IDs:
- `/quiz/123` → `/quiz/{id}`
- `/quiz/456/submit` → `/quiz/{id}/submit`

**Purpose:** Groups similar requests into single metric series

## Accessing Data

**Prometheus:**
- Query: `http_requests_total`
- Query: `http_request_duration_seconds`

**Grafana:**
- `rate(http_requests_total[5m])`: Requests per second
- `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`: p95 latency
