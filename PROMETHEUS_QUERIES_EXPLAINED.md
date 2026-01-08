# Prometheus Queries Explained - Simple Guide

## 🎯 What is `rate()`?

### Simple Explanation
**`rate()`** = "How fast is something happening per second?"

Think of it like a speedometer:
- **Counter (total count)**: "I've driven 1000 miles total"
- **Rate (per second)**: "I'm driving 60 miles per hour"

### Example
```
topic_weak_count_total = 100  (total times Addition was weak)
rate(topic_weak_count_total[5m]) = 0.5  (Addition is being marked weak 0.5 times per second)
```

**`[5m]`** = Look at last 5 minutes to calculate the rate

## 📊 Common Prometheus Functions

### 1. `rate()` - Speed Per Second
**What it does**: Calculates how fast a counter is increasing per second

**Example**:
```
rate(topic_weak_count_total[5m])
```
**Meaning**: How many times per second are topics being marked as weak (over last 5 minutes)

**Use when**: You want to see "activity level" or "requests per second"

---

### 2. `sum()` - Add Everything Together
**What it does**: Adds up all values

**Example**:
```
sum(topic_weak_count_total)
```
**Meaning**: Total count of all weak topics (across all grades, all topics)

**With `by`**:
```
sum by (topic) (topic_weak_count_total)
```
**Meaning**: Total count per topic (Addition: 10, Multiplication: 5, etc.)

**Use when**: You want totals

---

### 3. `count()` - Count Items
**What it does**: Counts how many series (data points) exist

**Example**:
```
count(topic_weak_count_total)
```
**Meaning**: How many different weak topic combinations exist (e.g., 5 topics × 2 grades = 10)

**Use when**: You want to know "how many unique things"

---

### 4. `avg()` / `mean()` - Average
**What it does**: Calculates average value

**Example**:
```
avg(quiz_scores_sum / quiz_scores_count)
```
**Meaning**: Average quiz score across all quizzes

**Use when**: You want average value

---

### 5. `max()` / `min()` - Highest/Lowest
**What it does**: Gets maximum or minimum value

**Example**:
```
max(quiz_scores_sum / quiz_scores_count)
```
**Meaning**: Highest quiz score ever

**Use when**: You want best/worst performance

---

### 6. `histogram_quantile()` - Percentile
**What it does**: Calculates percentile (like "95% of requests are faster than X")

**Example**:
```
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```
**Meaning**: 95% of requests are faster than this time (p95)

**Common percentiles**:
- `0.50` = Median (50th percentile) - half are faster, half are slower
- `0.95` = p95 - 95% are faster
- `0.99` = p99 - 99% are faster

**Use when**: You want "most requests are faster than X"

---

### 7. `topk()` - Top N Values
**What it does**: Shows top N highest values

**Example**:
```
topk(5, sum by (topic) (topic_weak_count_total))
```
**Meaning**: Top 5 topics with most weak counts

**Use when**: You want "top performers" or "worst performers"

---

### 8. `increase()` - Total Increase
**What it does**: How much a counter increased (not per second, but total)

**Example**:
```
increase(topic_weak_count_total[1h])
```
**Meaning**: How many times topics were marked as weak in the last hour (total)

**Difference from `rate()`**:
- `rate()` = per second
- `increase()` = total increase

**Use when**: You want "how many in the last hour" (not "per second")

---

## 📈 Time Windows: `[5m]`, `[1h]`, etc.

These tell Prometheus "look at the last X time":

- `[5m]` = Last 5 minutes
- `[15m]` = Last 15 minutes
- `[1h]` = Last 1 hour
- `[6h]` = Last 6 hours
- `[1d]` = Last 1 day

**Why use time windows?**
- For `rate()`: Longer window = smoother graph (less spikes)
- For counters: Shows "increase in this time period"

---

## 🔍 Queries in Your Dashboard

### 1. HTTP Requests Rate
```
rate(http_requests_total[5m])
```
**What it shows**: How many HTTP requests per second

**Example**: `2.5` = 2.5 requests per second (or 150 requests per minute)

---

### 2. Quiz Scores Distribution
```
histogram_quantile(0.50, rate(quiz_scores_bucket[5m]))
```
**What it shows**: Median quiz score (50th percentile)

**Example**: `85.0` = Half of quizzes scored 85 or above, half scored below

---

### 3. Weak Topics Count (Fixed!)
```
rate(topic_weak_count_total[5m])
```
**What it shows**: How fast topics are being marked as weak per second

**Example**: `0.1` = Topics are being marked as weak 0.1 times per second (6 times per minute)

```
sum by (topic) (topic_weak_count_total)
```
**What it shows**: Total count of weak topics per topic

**Example**: 
- Addition: 10 total
- Multiplication: 5 total

---

## 💡 When to Use What?

### Use `rate()` when:
- ✅ You want "requests per second"
- ✅ You want "how fast is something happening"
- ✅ You want to see activity level over time
- ✅ Graph shows smooth lines (rate over time)

### Use `sum()` when:
- ✅ You want total count
- ✅ You want to combine multiple metrics
- ✅ You want "how many total"

### Use `histogram_quantile()` when:
- ✅ You want "most requests are faster than X"
- ✅ You want p50, p95, p99 percentiles
- ✅ You're measuring response times or scores

### Use `topk()` when:
- ✅ You want "top 5 worst topics"
- ✅ You want "top 10 slowest endpoints"
- ✅ You want ranking

### Use `increase()` when:
- ✅ You want "how many in the last hour" (total)
- ✅ You want to see growth over time period
- ✅ Not "per second", but "total in this period"

---

## 📊 Real Examples from Your App

### Example 1: How many quizzes generated per minute?
```
rate(quizzes_generated_total[5m]) * 60
```
**Result**: `5.0` = 5 quizzes per minute

---

### Example 2: Total weak topics count by topic
```
sum by (topic) (topic_weak_count_total)
```
**Result**:
- Addition: 10
- Multiplication: 5
- Fractions: 8

---

### Example 3: Average quiz score
```
quiz_scores_sum / quiz_scores_count
```
**Result**: `85.5` = Average score is 85.5%

---

### Example 4: 95% of requests are faster than...
```
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```
**Result**: `0.5` = 95% of requests take less than 0.5 seconds

---

### Example 5: Top 3 weak topics
```
topk(3, sum by (topic) (topic_weak_count_total))
```
**Result**: Shows only the 3 topics with highest weak counts

---

## 🎯 Quick Reference

| Function | What It Does | Use For |
|----------|-------------|---------|
| `rate()` | Speed per second | Activity level, requests/sec |
| `sum()` | Add together | Totals |
| `count()` | Count items | How many unique things |
| `avg()` | Average | Average value |
| `max()` / `min()` | Highest/Lowest | Best/worst performance |
| `histogram_quantile()` | Percentile | "Most requests are faster than X" |
| `topk()` | Top N | Rankings |
| `increase()` | Total increase | Growth in time period |

---

## ✅ Summary

**`rate()`** = "How fast per second" (like speedometer)  
**`sum()`** = "Total count" (like odometer)  
**`histogram_quantile()`** = "95% are faster than X"  
**`topk()`** = "Top 5 worst/best"  
**`increase()`** = "Total in last hour" (not per second)

That's it! 🎉

