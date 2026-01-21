"""
Prometheus middleware for FastAPI to track HTTP requests.
"""
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.monitoring.metrics import http_requests_total, http_request_duration_seconds


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to track HTTP requests for Prometheus."""
    
    async def dispatch(self, request: Request, call_next):
        # Skip metrics endpoint to avoid infinite loops
        if request.url.path == "/metrics":
            return await call_next(request)
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            raise
        finally:
            duration = time.time() - start_time
            
            # Extract endpoint (remove query params and IDs for better grouping)
            endpoint = request.url.path
            # Replace IDs with {id} for better metric grouping
            if "/quiz/" in endpoint and endpoint.count("/") >= 3:
                parts = endpoint.split("/")
                if parts[-1].isdigit():
                    endpoint = "/".join(parts[:-1]) + "/{id}"
            
            # Track metrics
            http_requests_total.labels(
                method=request.method,
                endpoint=endpoint,
                status_code=str(status_code)
            ).inc()
            
            http_request_duration_seconds.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(duration)
        
        return response

