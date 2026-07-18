# Rate limiting middleware using Redis.
# Will contain:
#   - RateLimitMiddleware class
#   - Sliding window or fixed window counter in Redis
#   - Configurable limits per IP/user from settings
#   - 429 Too Many Requests response with Retry-After header
