# Health check service layer.
# Will contain:
#   - HealthService.check_liveness() -> bool
#   - HealthService.check_readiness(db, redis) -> ReadinessResponse
#   - Ping PostgreSQL and Redis connections
