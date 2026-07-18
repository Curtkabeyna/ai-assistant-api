# Pytest configuration and shared fixtures.
# Will contain:
#   - event_loop fixture for async tests
#   - test_client fixture (httpx AsyncClient with app)
#   - db_session fixture (test database with rollback)
#   - redis_client fixture (fakeredis or test Redis)
#   - test_user, auth_headers fixtures
#   - Factory fixtures for User, Conversation, Message
