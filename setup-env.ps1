# PowerShell script to set environment variables for Docker Compose
# Run this script: .\setup-env.ps1
# Or copy these commands to your PowerShell session

Write-Host "Setting up environment variables for Docker Compose..." -ForegroundColor Green

# Oracle Database Configuration (Local Installation)
$env:ORACLE_USER = "system"
$env:ORACLE_PASSWORD = "admin"
$env:ORACLE_HOST = "host.docker.internal"  # For Docker containers to access host
$env:ORACLE_PORT = "1521"
$env:ORACLE_SERVICE_NAME = "orclpdb"

# Redis Configuration (Local Windows Service)
$env:REDIS_HOST = "host.docker.internal"  # For Docker containers to access host
$env:REDIS_PORT = "6379"
$env:REDIS_DB = "0"
$env:REDIS_PASSWORD = ""

# Ollama Configuration (Local Installation)
$env:OLLAMA_MODEL = "llama2"
$env:OLLAMA_BASE_URL = "http://host.docker.internal:11434"
$env:OLLAMA_TEMPERATURE = "0.7"

# Frontend Configuration
$env:VITE_API_URL = "/api"

Write-Host "✅ Environment variables set!" -ForegroundColor Green
Write-Host ""
Write-Host "Current values:" -ForegroundColor Yellow
Write-Host "  ORACLE_USER: $env:ORACLE_USER"
Write-Host "  ORACLE_HOST: $env:ORACLE_HOST"
Write-Host "  ORACLE_SERVICE_NAME: $env:ORACLE_SERVICE_NAME"
Write-Host "  REDIS_HOST: $env:REDIS_HOST"
Write-Host "  OLLAMA_BASE_URL: $env:OLLAMA_BASE_URL"
Write-Host ""
Write-Host "You can now run: docker-compose up -d" -ForegroundColor Cyan

