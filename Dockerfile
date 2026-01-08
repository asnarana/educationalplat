# Backend Dockerfile (FastAPI)
FROM python:3.11-slim

WORKDIR /app

# Note: Oracle client libraries not needed - Oracle DB runs on host machine
# The oracledb Python package will connect via network

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY expand_questions.py ./
COPY en_US-lessac-medium.onnx* ./

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

