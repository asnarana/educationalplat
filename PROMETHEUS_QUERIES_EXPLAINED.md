# PromQL Functions Reference

## Core Functions

### `rate(metric[time_window])`
Calculates per-second rate of counter increase.

**Example:**
```
rate(http_requests_total[5m])
```
Returns: Requests per second over last 5 minutes

### `sum(metric)` / `sum by (label) (metric)`
Aggregates values. Use `by` to group by label.

**Example:**
```
sum by (topic) (topic_weak_count_total)
```
Returns: Total weak count per topic

### `histogram_quantile(quantile, metric)`
Calculates percentile from histogram buckets.

**Example:**
```
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```
Returns: 95th percentile latency

**Common quantiles:**
- `0.50`: Median
- `0.95`: p95
- `0.99`: p99

### `increase(metric[time_window])`
Total increase over time period (not per-second).

**Example:**
```
increase(quizzes_generated_total[1h])
```
Returns: Total quizzes generated in last hour

### `topk(n, metric)`
Returns top N highest values.

**Example:**
```
topk(5, sum by (topic) (topic_weak_count_total))
```
Returns: Top 5 topics by weak count

### `avg()`, `max()`, `min()`, `count()`
Standard aggregation functions.

## Time Windows

- `[5m]`: Last 5 minutes
- `[15m]`: Last 15 minutes
- `[1h]`: Last hour
- `[6h]`: Last 6 hours
- `[1d]`: Last day

## Common Patterns

**Average score:**
```
quiz_scores_sum / quiz_scores_count
```

**Requests per minute:**
```
rate(http_requests_total[5m]) * 60
```

**Total weak topics by topic:**
```
sum by (topic) (topic_weak_count_total)
```
