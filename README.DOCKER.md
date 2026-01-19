# Docker Setup Guide

This project is now fully containerized! You can run everything with a single command.

## Quick Start

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## Services

- **Backend**: FastAPI application on port 8000
- **Frontend**: React/Vite application on port 5173 (served via Nginx)
- **Oracle DB**: Database on port 1522
- **Redis**: Cache on port 6379
- **Prometheus**: Metrics on port 9090
- **Grafana**: Dashboards on port 3001

## Access Points

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Grafana: http://localhost:3001 (admin/admin)
- Prometheus: http://localhost:9090

## Environment Variables

The backend uses these environment variables (set in docker-compose.yml):

- `ORACLE_HOST`: Database host (default: oracle-db)
- `ORACLE_PORT`: Database port (default: 1521)
- `ORACLE_USER`: Database user (default: system)
- `ORACLE_PASSWORD`: Database password (default: Oracle123)
- `ORACLE_SERVICE`: Service name (default: FREEPDB1)
- `REDIS_HOST`: Redis host (default: redis)
- `REDIS_PORT`: Redis port (default: 6379)

## Building Images

```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build frontend
```

## Development Mode

For development with hot-reload, create `docker-compose.override.yml`:

```yaml
version: '3.8'

services:
  backend:
    volumes:
      - ./app:/app/app
    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

## Troubleshooting

### Oracle Instant Client Issues

If Oracle Instant Client fails to download in the Docker build, you can:

1. Download manually and mount it as a volume
2. Use an Oracle Linux base image
3. Build the image on a machine with Oracle Instant Client pre-installed

### Port Conflicts

If ports are already in use, modify `docker-compose.yml` to use different ports.

### Database Connection

The backend connects to `oracle-db` service name (not localhost). This is handled automatically by Docker networking.

### Frontend API Calls

The frontend uses `/api` proxy in production (via Nginx) or `http://localhost:8000` in development.

## Volumes

- `oracle_data`: Oracle database data (persistent)
- `prometheus_data`: Prometheus metrics (persistent)
- `grafana_data`: Grafana dashboards (persistent)
- `redis_data`: Redis cache (persistent)

## Math Images

Math question images are mounted from:
- `./grade3mathimages` → `/usr/share/nginx/html/images/math/grade3`
- `./grade4mathimages` → `/usr/share/nginx/html/images/math/grade4`
- `./grade5mathimages` → `/usr/share/nginx/html/images/math/grade5`

These are accessible at `/images/math/grade3/q38.png` etc. in the frontend.
