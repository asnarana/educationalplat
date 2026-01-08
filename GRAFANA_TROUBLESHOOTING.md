# Grafana Dashboard Troubleshooting Guide

## ✅ Fixed Issues

### Issue 1: Weak Topics Count Not Showing
**Problem**: Dashboard was using `topic_weak_count` but Prometheus stores it as `topic_weak_count_total`

**Fix**: Updated dashboard JSON to use `topic_weak_count_total` (with `_total` suffix)

## 🔍 How to Verify Dashboard is Working

### Step 1: Check Prometheus Can Reach Your App
```powershell
# From inside Prometheus container
docker exec prometheus wget -qO- http://host.docker.internal:8000/metrics | findstr topic_weak
```

Should show:
```
topic_weak_count_total{grade_level="3",topic="Addition"} 3.0
```

### Step 2: Check Prometheus is Scraping
1. Open: http://localhost:9090
2. Go to: Status → Targets
3. Check if `grademaster-api` target is **UP** (green)

### Step 3: Verify Metric in Prometheus
1. Open: http://localhost:9090
2. Type in query box: `topic_weak_count_total`
3. Click "Execute"
4. Should see data points

### Step 4: Check Grafana Datasource
1. Open: http://localhost:3001
2. Login: admin / admin
3. Go to: Configuration → Data Sources
4. Click on "Prometheus"
5. Click "Test" button
6. Should see "Data source is working"

### Step 5: Check Dashboard is Loaded
1. Open: http://localhost:3001
2. Go to: Dashboards → Browse
3. Look for: "GradeMaster Educational Platform"
4. Open it
5. Check if "Weak Topics Count" panel shows data

## 🛠️ If Dashboard Still Not Showing Data

### Option 1: Reload Dashboard
1. In Grafana, open the dashboard
2. Click the refresh button (top right)
3. Wait 10-15 seconds for Prometheus to scrape new data

### Option 2: Check Time Range
1. In Grafana dashboard, check time range (top right)
2. Set to: "Last 1 hour" or "Last 6 hours"
3. Prometheus only stores recent data

### Option 3: Restart Grafana
```powershell
docker restart grafana
```

Wait 30 seconds, then reload the dashboard in browser

### Option 4: Re-import Dashboard
1. In Grafana, go to: Dashboards → Import
2. Click "Upload JSON file"
3. Select: `monitoring/grafana/dashboards/grademaster-dashboard.json`
4. Click "Import"

### Option 5: Create Panel Manually
1. In Grafana, open any dashboard
2. Click "Add panel" → "Add visualization"
3. Select datasource: "Prometheus"
4. In query box, type:
   ```
   topic_weak_count_total
   ```
5. Click "Run query"
6. Should see data!

## 📊 Alternative Queries to Try

### Total Weak Topics Count (not rate):
```
sum by (topic) (topic_weak_count_total)
```

### Weak Topics by Grade:
```
sum by (grade_level, topic) (topic_weak_count_total)
```

### Rate of Weak Topics:
```
rate(topic_weak_count_total[5m])
```

### Top 5 Weak Topics:
```
topk(5, sum by (topic) (topic_weak_count_total))
```

## 🚨 Common Issues

### Issue: "No data" in panel
**Cause**: 
- Prometheus hasn't scraped data yet (wait 15-30 seconds)
- Time range too short/too long
- Metric name wrong

**Fix**: 
- Check Prometheus targets are UP
- Expand time range to "Last 1 hour"
- Verify metric name in Prometheus UI

### Issue: "Datasource not found"
**Cause**: Grafana can't connect to Prometheus

**Fix**:
1. Check `docker-compose.yml` - both should be on `monitoring` network
2. Check Prometheus is running: `docker ps | grep prometheus`
3. Check Grafana datasource URL: `http://prometheus:9090` (not `localhost`)

### Issue: Dashboard shows old/empty data
**Cause**: Dashboard JSON not reloaded

**Fix**:
1. Restart Grafana: `docker restart grafana`
2. Hard refresh browser (Ctrl+F5)
3. Check if dashboard file was saved correctly

## ✅ Current Status

After fixing the metric name, you should see:
- Panel: "Weak Topics Count"
- Shows: Rate and total count of weak topics
- Data: Addition (3), Multiplication (2), Fractions (2), etc.

## 🎯 Quick Test

Run this to verify everything is working:
```powershell
# 1. Check metric exists in app
python -c "import requests; r = requests.get('http://localhost:8000/metrics'); print('topic_weak_count_total' in r.text)"

# 2. Check Prometheus can see it
docker exec prometheus wget -qO- http://host.docker.internal:8000/metrics | findstr topic_weak_count_total

# 3. Open Grafana and check dashboard
# http://localhost:3001 → Dashboards → GradeMaster Educational Platform
```

