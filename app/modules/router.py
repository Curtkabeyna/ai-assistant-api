# Central router aggregator — registers all feature module routers.
# Will contain:
#   - api_router = APIRouter(prefix="/api/v1")
#   - Include routers: health, auth, users, conversations, messages, ai
#   - Export api_router for main.py registration
