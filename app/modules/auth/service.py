# Authentication business logic.
# Will contain:
#   - AuthService.register() — create user, return tokens
#   - AuthService.login() — verify credentials, return tokens
#   - AuthService.refresh() — validate refresh token, issue new access token
#   - AuthService.logout() — blacklist refresh token in Redis
