# Authentication API routes.
# Will contain:
#   - POST /auth/register — user registration
#   - POST /auth/login — login, returns access + refresh tokens
#   - POST /auth/refresh — refresh access token
#   - POST /auth/logout — invalidate refresh token (Redis blacklist)
