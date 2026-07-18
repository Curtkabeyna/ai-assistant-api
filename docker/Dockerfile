# Multi-stage Dockerfile for production-ready FastAPI application.
# Will contain:
#   - Stage 1 (builder): install dependencies with uv/pip
#   - Stage 2 (runtime): slim Python 3.13 image, copy app, run uvicorn
# With non-root user, health check, and optimized layer caching.
