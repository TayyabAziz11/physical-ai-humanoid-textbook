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

Edit `.env` and provide the following required values:

**Required API Keys:**
- `OPENAI_API_KEY` - Your OpenAI API key (get from https://platform.openai.com/api-keys)
- `QDRANT_URL` - Your Qdrant Cloud cluster URL (e.g., `https://xyz.qdrant.io`)
- `QDRANT_API_KEY` - Your Qdrant API key (from Qdrant Cloud dashboard)
- `DATABASE_URL` - Your Neon Postgres connection string (format: `postgresql+asyncpg://user:password@host:5432/database`)

**Optional Configuration:**
- `LOG_LEVEL` - Set to `DEBUG` for verbose logging (default: `INFO`)
- `CORS_ORIGINS` - JSON array of allowed origins (default: `["http://localhost:3000","http://localhost:8000"]`)
- `RAG_TOP_K_CHUNKS` - Number of chunks to retrieve (default: `7`)
- `MAX_QUESTION_TOKENS` - Max question length (default: `2000`)

**Note:** For initial development, you can use placeholder values for `QDRANT_URL`, `QDRANT_API_KEY`, and `DATABASE_URL` if you haven't set up these services yet. The application will start but RAG features won't work until real credentials are provided.

### 3. Initialize Database

Create the database tables (chat_sessions, chat_messages):

```bash
cd backend
uv run python scripts/init_db.py
```

Expected output:
```
2025-12-07 12:00:00 - rag_backend - INFO - Initializing database...
2025-12-07 12:00:00 - rag_backend - INFO - Database URL: host:5432/database
2025-12-07 12:00:00 - rag_backend - INFO - Creating database tables...
2025-12-07 12:00:00 - rag_backend - INFO - ✅ Database initialized successfully!
2025-12-07 12:00:00 - rag_backend - INFO - Tables created: chat_sessions, chat_messages
```

### 4. Index Textbook Content

Index all markdown files from `../docs` into Qdrant vector database:

```bash
cd backend
uv run python scripts/index_textbook.py
```

This script will:
- Discover all `.md` and `.mdx` files in the `../docs` directory
- Extract sections by heading (# and ##)
- Chunk text into ~500 token chunks with 50 token overlap
- Generate embeddings using OpenAI `text-embedding-3-small`
- Upload to Qdrant with metadata (doc_path, heading, chunk_text)

**Progress output:**
```
============================================================
Starting textbook indexing process
============================================================
Initializing OpenAI and Qdrant clients...
Ensuring collection 'textbook_chunks' exists...
Discovering markdown files in /path/to/docs...
Found 15 markdown files

[1/15] Processing: docs/intro.md
  Extracted 3 sections
  Section 'Introduction': 2 chunks
  Uploading batch of 100 points...

...

============================================================
✅ Indexing completed successfully!
Total files processed: 15
Total chunks indexed: 342
Collection: textbook_chunks
============================================================
```

**Note:** Indexing requires valid `OPENAI_API_KEY` and `QDRANT_URL`/`QDRANT_API_KEY`. The process may take 2-5 minutes depending on the number of documents.

### 5. Run Development Server

```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

### 6. Test Health Endpoint

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "database": "connected",
  "qdrant": "connected (collection: textbook_chunks, points: 342)",
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
│   ├── init_db.py                 # Database initialization script
│   └── index_textbook.py          # Textbook indexing script
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
