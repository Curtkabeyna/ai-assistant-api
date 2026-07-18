# AI Assistant API

Production-ready AI Assistant Backend built with FastAPI.

## Stack

- FastAPI
- Python 3.13
- SQLAlchemy 2.0 Async
- PostgreSQL
- Redis
- Alembic
- Pydantic v2
- OpenAI SDK v1
- JWT
- Docker
- pytest

## Project Structure

Feature-Based Architecture with separation into `core`, `common`, `db`, `modules`, `middleware`, and `utils`.

## Quick Start

```bash
# Copy environment variables
cp .env.example .env

# Start services with Docker
docker compose up -d

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

## Testing

```bash
pytest
```
