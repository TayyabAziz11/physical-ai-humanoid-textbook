# RAG Backend & Study Assistant API

Backend API for the Physical AI & Humanoid Robotics Textbook Study Assistant.

## Features

- FastAPI-based REST API
- RAG (Retrieval-Augmented Generation) for Q&A
- Vector search with Qdrant
- Session persistence with Neon Postgres
- OpenAI integration for embeddings and chat

## Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Qdrant Cloud account (Free Tier)
- Neon Postgres account (Free Tier)
- OpenAI API key

## Quick Start

### 1. Install Dependencies

```bash
cd backend
uv sync
```

This will create a virtual environment and install all dependencies from `pyproject.toml`.

### 2. Environment Setup

Copy the example environment file and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env` and provide:
- `OPENAI_API_KEY` - Your OpenAI API key
- `QDRANT_URL` - Your Qdrant Cloud cluster URL
- `QDRANT_API_KEY` - Your Qdrant API key
- `DATABASE_URL` - Your Neon Postgres connection string

### 3. Run Development Server

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

### 4. Test Health Endpoint

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2025-12-07T12:00:00.000Z"
}
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entrypoint
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py          # API router aggregator
│   │       └── health.py          # Health check endpoint
│   ├── core/                      # Config, logging, security (Phase 2)
│   ├── models/                    # Database and Pydantic models (Phase 3)
│   ├── services/                  # Business logic (RAG, embeddings, etc.)
│   └── db/                        # Database session management (Phase 3)
├── scripts/
│   └── index_docs.py              # Indexing script (Phase 5)
├── tests/                         # Pytest tests (Phase 9)
├── pyproject.toml                 # Dependencies and project config
├── .env.example                   # Example environment variables
└── README.md                      # This file
```

## Development

### Installing Additional Dependencies

```bash
cd backend
uv add <package-name>
```

### Installing Dev Dependencies

```bash
cd backend
uv add --dev pytest pytest-asyncio pytest-cov
```

### Running Tests (Phase 9)

```bash
cd backend
uv run pytest tests/ -v
```

## API Endpoints

### Current Endpoints

- `GET /` - Root endpoint with API info
- `GET /api/v1/health` - Health check

### Upcoming Endpoints (Future Phases)

- `POST /api/v1/chat` - Chat with the Study Assistant (Phase 6)
- `GET /api/v1/sessions` - List chat sessions (Phase 8)
- `GET /api/v1/sessions/{id}/messages` - Retrieve session messages (Phase 8)

## Deployment

Deployment instructions will be added in Phase 9. Recommended platforms:
- Railway
- Render
- Fly.io

## Contributing

This backend is part of the Physical AI & Humanoid Robotics Textbook project.

## License

[Add license information]
