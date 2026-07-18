# Request/response logging middleware.
# Will contain:
#   - LoggingMiddleware class (ASGI or BaseHTTPMiddleware)
#   - Request ID generation and propagation
#   - Log method, path, status_code, duration_ms
#   - Skip health check endpoints from verbose logging
