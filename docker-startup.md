# Docker Setup Guide

This guide will help you run the entire application stack using Docker Compose.

## Prerequisites

1. **Docker Desktop** installed and running
   - Download: https://www.docker.com/products/docker-desktop/
   
2. **Oracle Container Registry Account** (free)
   - Sign up: https://container-registry.oracle.com/
   - Login: `docker login container-registry.oracle.com`

3. **Ollama** (for AI feedback) - can run locally or in Docker
   - Download: https://ollama.ai/
   - Pull model: `ollama pull phi` (or your preferred model)

## Quick Start

### 1. Login to Oracle Container Registry

```powershell
docker login container-registry.oracle.com
# Enter your Oracle account credentials
```

### 2. Pull Oracle Database Image (first time only)

```powershell
docker pull container-registry.oracle.com/database/free:latest
```

This is a large download (~6GB), so it may take a while.

### 3. Update Environment Variables (Optional)

Create a `.env` file from `.env.example` if you want to customize settings:

```powershell
copy .env.example .env
# Edit .env with your preferred settings
```

**Important**: Update the Oracle password in both `.env` and `docker-compose.yml` if you change it!

### 4. Start All Services

```powershell
docker-compose up -d
```

This will start:
- ✅ Oracle Database (port 1521)
- ✅ Redis (port 6379)
- ✅ Backend API (port 8000)
- ✅ Frontend (port 3000)
- ✅ Prometheus (port 9090)
- ✅ Grafana (port 3001)

### 5. Wait for Oracle Database to Initialize

Oracle Database takes 2-3 minutes to start up. Check status:

```powershell
docker-compose logs oracle-db
```

Wait until you see: `DATABASE IS READY TO USE!`

### 6. Initialize Database Tables

Once Oracle is ready, initialize the database:

```powershell
docker-compose exec backend python -c "from app.db import init_db; init_db()"
```

Or access the API:
```
POST http://localhost:8000/seed
```

### 7. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)

## Common Commands

### View Logs

```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f oracle-db
```

### Stop Services

```powershell
docker-compose down
```

### Stop and Remove Volumes (⚠️ deletes data)

```powershell
docker-compose down -v
```

### Rebuild Services

```powershell
# Rebuild specific service
docker-compose build backend

# Rebuild all services
docker-compose build

# Rebuild and restart
docker-compose up -d --build
```

### Restart Service

```powershell
docker-compose restart backend
```

### Access Container Shell

```powershell
# Backend
docker-compose exec backend bash

# Oracle Database
docker-compose exec oracle-db bash
```

## Oracle Database Connection

### From Host Machine

```powershell
sqlplus system/YourPassword123!@localhost:1521/FREEPDB1
```

### From Another Container

Use `oracle-db:1521` as the host.

### Default Credentials

- **Username**: `system`
- **Password**: `YourPassword123!` (change in docker-compose.yml)
- **Service Name**: `FREEPDB1`
- **Port**: `1521`

## Troubleshooting

### Oracle Database Won't Start

1. Check logs: `docker-compose logs oracle-db`
2. Ensure you've logged into Oracle Container Registry
3. Wait 2-3 minutes for initialization
4. Check disk space (Oracle needs ~10GB)

### Backend Can't Connect to Oracle

1. Wait for Oracle to be healthy: `docker-compose ps`
2. Check Oracle logs: `docker-compose logs oracle-db`
3. Verify connection string in backend logs

### Frontend Can't Connect to Backend

1. Check backend is running: `docker-compose ps backend`
2. Check backend logs: `docker-compose logs backend`
3. Verify CORS settings in `app/main.py`

### Ollama Connection Issues

If Ollama runs on your host machine, the backend uses `host.docker.internal:11434` to connect.

For Docker Ollama, add to docker-compose.yml:
```yaml
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    networks:
      - app-network
```

Then update backend environment:
```yaml
OLLAMA_BASE_URL: http://ollama:11434
```

### Redis Connection Issues

Redis should auto-connect. Check:
```powershell
docker-compose exec redis redis-cli ping
# Should return: PONG
```

## Production Considerations

For production:

1. **Change Default Passwords** in docker-compose.yml
2. **Use Secrets** for sensitive data (don't hardcode passwords)
3. **Configure SSL/TLS** for frontend and backend
4. **Set Resource Limits** for containers
5. **Use External Database** (managed Oracle DB service)
6. **Enable Backups** for Oracle data volume
7. **Configure Logging** to external service
8. **Use Docker Secrets** or environment files for credentials

## Service URLs Summary

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | - |
| Backend API | http://localhost:8000 | - |
| API Docs | http://localhost:8000/docs | - |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3001 | admin/admin |
| Oracle DB | localhost:1521 | system/YourPassword123! |
| Redis | localhost:6379 | - |

