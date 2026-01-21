# Grafana Troubleshooting

## Fixed Issues

**Issue**: Dashboard used `topic_weak_count` but Prometheus stores `topic_weak_count_total`
**Fix**: Updated dashboard to use `topic_weak_count_total`

## Verification Steps

### 1. Check Metrics Endpoint
```powershell
docker exec prometheus wget -qO- http://host.docker.internal:8000/metrics | findstr topic_weak
```
Expected: `topic_weak_count_total{grade_level="3",topic="Addition"} 3.0`

### 2. Check Prometheus Scraping
- Open: http://localhost:9090
- Status → Targets
- Verify `grademaster-api` is UP

### 3. Verify Metric in Prometheus
- Query: `topic_weak_count_total`
- Should return data points

### 4. Check Grafana Datasource
- Configuration → Data Sources → Prometheus
- Test connection

### 5. Verify Dashboard
- Dashboards → Browse → "GradeMaster Educational Platform"
- Check "Weak Topics Count" panel

## Common Issues

### No Data in Panel
**Causes:**
- Prometheus hasn't scraped yet (wait 15-30s)
- Time range incorrect
- Wrong metric name

**Fix:**
- Verify Prometheus target is UP
- Set time range to "Last 1 hour"
- Check metric name in Prometheus UI

### Datasource Not Found
**Fix:**
- Verify both services on `monitoring` network
- Check Prometheus running: `docker ps | grep prometheus`
- Verify datasource URL: `http://prometheus:9090`

### Dashboard Shows Old Data
**Fix:**
- Restart Grafana: `docker restart grafana`
- Hard refresh browser (Ctrl+F5)
- Re-import dashboard JSON

## Alternative Queries

```
sum by (topic) (topic_weak_count_total)
sum by (grade_level, topic) (topic_weak_count_total)
rate(topic_weak_count_total[5m])
topk(5, sum by (topic) (topic_weak_count_total))
```
