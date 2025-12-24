# Technical Implementation Plan: RAG Backend & Study Assistant API

**Feature**: `002-rag-backend-study-assistant`
**Created**: 2025-12-07
**Status**: Draft
**Based on**: [spec.md](./spec.md)

## Overview

This plan outlines the technical architecture and implementation approach for the RAG backend and Study Assistant API. The system will use FastAPI (Python 3.11+), Qdrant Cloud for vector storage, Neon Postgres for relational data, and OpenAI for embeddings and chat completion.

**Key Architectural Principles**:
- **Separation of Concerns**: Clear layering between API, services, and data access
- **Async-First**: Leverage async/await for all I/O operations (database, HTTP)
- **Type Safety**: Pydantic models for validation, type hints throughout
- **Configuration as Code**: Environment-driven config with Pydantic BaseSettings
- **Testability**: Dependency injection for easy mocking

---

## 1. Project & Directory Structure

### Root Layout

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entrypoint, lifespan events
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                # Dependency injection (get_db, get_qdrant, etc.)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py          # Main router aggregator
│   │       ├── health.py          # GET /api/v1/health
│   │       └── chat.py            # POST /api/v1/chat
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Pydantic Settings for env vars
│   │   ├── logging.py             # Structured logging setup
│   │   └── security.py            # Input sanitization, CORS config
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py            # SQLAlchemy ORM models (ChatSession, ChatMessage)
│   │   └── schemas.py             # Pydantic request/response schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── rag.py                 # RAG orchestration (query → retrieve → generate)
│   │   ├── embeddings.py          # OpenAI embedding generation
│   │   ├── qdrant_client.py       # Qdrant vector search operations
│   │   ├── openai_chat.py         # OpenAI chat completion (Agents/ChatKit)
│   │   └── session_manager.py     # Session creation and persistence
│   └── db/
│       ├── __init__.py
│       ├── base.py                # SQLAlchemy declarative base
│       ├── session.py             # Async session factory
│       └── migrations/            # Alembic migrations (future)
├── scripts/
│   ├── __init__.py
│   └── index_docs.py              # Indexing script for Markdown/MDX files
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Pytest fixtures (mock DB, Qdrant, OpenAI)
│   ├── test_health.py             # Health endpoint tests
│   └── test_chat.py               # Chat endpoint tests
├── pyproject.toml                 # uv-managed dependencies
├── uv.lock                        # Lockfile
├── .env.example                   # Example environment variables
├── .gitignore
└── README.md                      # Setup and usage instructions
```

### File Responsibilities

**`main.py`**:
- FastAPI app initialization
- CORS middleware configuration
- Router registration (`api.v1.router`)
- Lifespan events (startup: initialize Qdrant client, DB pool; shutdown: cleanup)

**`api/deps.py`**:
- Dependency injection functions:
  - `get_db()`: Async database session
  - `get_qdrant()`: Qdrant client instance
  - `get_settings()`: Configuration object
- Used with FastAPI's `Depends()` for clean injection

**`api/v1/chat.py`**:
- `POST /api/v1/chat` endpoint
- Request validation (Pydantic schema)
- Calls `RAGService.answer_question()`
- Response formatting and error handling

**`services/rag.py`**:
- Orchestrates RAG pipeline:
  - Whole-book mode: Embed question → search Qdrant → generate answer
  - Selection mode: Filter by docPath → search → generate
- Constructs system prompts for OpenAI
- Formats citations from retrieved chunks

**`services/qdrant_client.py`**:
- Wrapper around `qdrant-client` SDK
- Methods: `search_whole_book()`, `search_by_document()`, `upsert_chunks()`
- Handles connection pooling and retries

**`services/session_manager.py`**:
- Creates or retrieves `ChatSession` records
- Persists `ChatMessage` rows (user + assistant)
- Handles anonymous users (no DB writes when `userId` is null)

**`scripts/index_docs.py`**:
- CLI script: `uv run python backend/scripts/index_docs.py [--incremental]`
- Scans `../docs/` directory for `.md` and `.mdx` files
- Strips YAML frontmatter
- Chunks by heading (H2/H3) + max token length (500)
- Generates embeddings via `services/embeddings.py`
- Upserts to Qdrant with metadata

---

## 2. Configuration & Environment

### Environment Variables

All configuration loaded via **Pydantic BaseSettings** in `core/config.py`:

```python
# core/config.py (conceptual structure)
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    APP_NAME: str = "RAG Study Assistant"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_CHAT_MODEL: str = "gpt-4-turbo-preview"  # or gpt-3.5-turbo for cost
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Qdrant
    QDRANT_URL: str  # e.g., https://xyz.qdrant.io
    QDRANT_API_KEY: str
    QDRANT_COLLECTION: str = "textbook_chunks"

    # Neon Postgres
    DATABASE_URL: str  # postgresql+asyncpg://user:pass@host/db

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]  # Dev default

    # RAG Config
    RAG_TOP_K_CHUNKS: int = 7  # Number of chunks to retrieve
    RAG_CHUNK_MAX_TOKENS: int = 500

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

### `.env` File Placement

**Development**: `backend/.env` (gitignored)
```env
OPENAI_API_KEY=sk-...
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-api-key
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/studyassist_dev
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
DEBUG=true
```

**Production**: Environment variables injected by deployment platform (Railway, Render, Fly.io)
- `CORS_ORIGINS` updated to include GitHub Pages URL
- `DEBUG=false`

### `.gitignore` Rules

```gitignore
backend/.env
backend/.env.*
!backend/.env.example
backend/__pycache__/
backend/**/__pycache__/
backend/.pytest_cache/
backend/uv.lock  # Optional: commit for reproducibility
backend/dist/
```

---

## 3. Data Modeling (Neon Postgres)

### SQLAlchemy Models

**File**: `app/models/database.py`

```python
# Conceptual schema (not full code)
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=True, index=True)  # Nullable for anonymous
    mode = Column(Enum("whole-book", "selection", name="chat_mode"), nullable=False)
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_message_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(Enum("user", "assistant", name="message_role"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    selected_text = Column(Text, nullable=True)  # For selection mode
    doc_path = Column(String, nullable=True)    # For selection mode

    session = relationship("ChatSession", back_populates="messages")
```

### Table Justification

- **UUID Primary Keys**: Avoids sequence exhaustion, better for distributed systems
- **`user_id` as String**: Future-proof for Better-Auth integration (external IDs)
- **Nullable `user_id`**: Supports anonymous usage (no DB writes when null per FR-029)
- **`mode` Enum**: Ensures data consistency ("whole-book" | "selection")
- **Timestamps with Timezone**: Accurate across regions
- **`selected_text` and `doc_path`**: Nullable, populated only for selection mode
- **Cascade Delete**: Deleting a session removes all messages (future cleanup jobs)

### Async SQLAlchemy Setup

**File**: `app/db/session.py`

```python
# Conceptual setup
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

### Migrations (Future)

- Use **Alembic** for schema migrations
- Initial migration creates `chat_sessions` and `chat_messages` tables
- Store migrations in `backend/app/db/migrations/`
- Run: `alembic revision --autogenerate -m "Initial schema"`

---

## 4. Qdrant Schema & Indexing Strategy

### Qdrant Collection Schema

**Collection Name**: `textbook_chunks` (configurable via `QDRANT_COLLECTION`)

**Vector Configuration**:
- **Dimension**: 1536 (for `text-embedding-3-small` or `text-embedding-ada-002`)
  - If using `text-embedding-3-large`: 3072 dimensions
- **Distance Metric**: Cosine similarity
- **Index Type**: HNSW (default, optimized for speed/accuracy balance)

**Metadata (Payload) Fields**:
```python
{
    "doc_path": str,           # e.g., "docs/module-1-ros2/chapter-1-basics.mdx"
    "module_id": int,          # Extracted from directory (1-4)
    "heading": str,            # Section title (H2/H3)
    "chunk_index": int,        # Position in document (0, 1, 2, ...)
    "content": str,            # Raw text of the chunk (for citation snippets)
    "token_count": int,        # Approximate token count
    "file_hash": str           # MD5 hash of source file (for incremental indexing)
}
```

### Indexing Script: `scripts/index_docs.py`

**Purpose**: Populate Qdrant with textbook content from `../docs/`

**Algorithm**:

1. **Scan Documents**:
   - Recursively find all `.md` and `.mdx` files in `../docs/`
   - Extract `module_id` from path (e.g., `module-1-ros2` → `1`)

2. **Parse & Clean**:
   - Strip YAML frontmatter (lines between `---` delimiters)
   - Preserve Markdown headings (H1, H2, H3)
   - Remove excessive whitespace, but keep paragraph structure

3. **Chunking Strategy** (Hybrid Approach):
   - **Primary**: Split by H2/H3 headings (semantic sections)
   - **Secondary**: If a section exceeds `RAG_CHUNK_MAX_TOKENS` (500), split further by:
     - Sentence boundaries (prefer complete sentences)
     - Paragraph boundaries
   - **Metadata**: Each chunk stores:
     - `heading`: Most recent H2/H3 title
     - `chunk_index`: Sequential position within document

4. **Embedding Generation**:
   - Call `services/embeddings.py` → `OpenAI.embeddings.create()`
   - Model: `text-embedding-3-small` (cost-effective, 1536 dims)
   - Batch embeddings (10-20 chunks per API call for efficiency)

5. **Upsert to Qdrant**:
   - Use **document path + chunk index** as the point ID (deterministic)
     - Example ID: `md5("docs/module-1-ros2/chapter-1-basics.mdx#0")`
   - Upserting (vs inserting) ensures idempotence:
     - Re-running the script updates existing chunks
     - Prevents duplicates

6. **Incremental Mode** (Optional `--incremental` flag):
   - Compute MD5 hash of each source file
   - Query Qdrant for existing chunks by `doc_path`
   - Compare `file_hash` metadata:
     - If hash matches: Skip file
     - If hash differs: Delete old chunks, re-index file
   - Significantly faster for large corpora

7. **Error Handling**:
   - Log errors for malformed MDX (e.g., invalid frontmatter)
   - Continue processing remaining files (FR-019)
   - Return summary: `{processed: N, errors: M, skipped: K}`

**CLI Usage**:
```bash
# Full re-index
uv run python backend/scripts/index_docs.py

# Incremental (only changed files)
uv run python backend/scripts/index_docs.py --incremental

# Specify docs directory
uv run python backend/scripts/index_docs.py --docs-dir ../docs
```

**Dependencies**:
- `qdrant-client`: Interact with Qdrant Cloud
- `openai`: Generate embeddings
- `python-frontmatter`: Parse YAML frontmatter
- `tiktoken`: Count tokens for chunking decisions

---

## 5. Chat Pipeline (Whole-book & Selection-based)

### Request/Response Schemas

**File**: `app/models/schemas.py`

```python
# Conceptual Pydantic models
from pydantic import BaseModel, Field, validator
from typing import Literal, Optional

class ChatRequest(BaseModel):
    mode: Literal["whole-book", "selection"]
    question: str = Field(..., min_length=1, max_length=2000)
    selected_text: Optional[str] = Field(None, max_length=5000)
    doc_path: Optional[str] = None
    user_id: Optional[str] = None  # Anonymous if null
    session_id: Optional[str] = None  # For continuing sessions

    @validator("selected_text")
    def validate_selection_mode(cls, v, values):
        if values.get("mode") == "selection" and not v:
            # Allow selection mode without selected_text (explain passage scenario)
            pass
        return v

class Citation(BaseModel):
    doc_path: str
    heading: str
    snippet: str = Field(..., max_length=150)  # 50-100 chars per spec

class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    mode: Literal["whole-book", "selection"]
    session_id: str
```

### Whole-book Mode Pipeline

**Entry Point**: `POST /api/v1/chat` with `mode: "whole-book"`

**Flow** (in `services/rag.py`):

1. **Input Validation**:
   - Sanitize `question` (remove excess whitespace, check length)
   - Detect language (if non-English, return polite error per edge case)

2. **Query Embedding**:
   - Call `services/embeddings.generate_embedding(question)`
   - Returns 1536-dim vector

3. **Vector Search**:
   - `qdrant_client.search(collection="textbook_chunks", query_vector=embedding, limit=7)`
   - **No filters** (whole-book mode searches all chunks)
   - Returns top 7 chunks ranked by cosine similarity

4. **Context Assembly**:
   - Sort chunks by `doc_path` and `chunk_index` for readability
   - Format as:
     ```
     [Module 1, Chapter 1 - ROS 2 Basics]
     {chunk.content}

     [Module 2, Chapter 3 - Gazebo Sensors]
     {chunk.content}
     ```

5. **LLM Call** (OpenAI Chat Completion):
   - **System Prompt**:
     ```
     You are a helpful study assistant for a textbook on Physical AI and Humanoid Robotics.
     Answer the user's question based ONLY on the provided textbook excerpts.
     If the excerpts don't contain enough information, say so.
     Always cite the source (module, chapter, section) when referencing information.
     Do not add information outside the provided context.
     ```
   - **User Prompt**:
     ```
     Textbook Excerpts:
     {assembled_context}

     Question: {user_question}

     Answer:
     ```
   - Model: `gpt-4-turbo-preview` or `gpt-3.5-turbo` (configurable)
   - Temperature: 0.3 (low for factual accuracy)

6. **Citation Extraction**:
   - Parse LLM response for references to chunks
   - For each cited chunk:
     - `doc_path`: from metadata
     - `heading`: from metadata
     - `snippet`: First 80-100 chars of `chunk.content`
   - If LLM doesn't cite explicitly, return all top 3 retrieved chunks as citations

7. **Response**:
   - Return `ChatResponse` with answer + citations

### Selection-based Mode Pipeline

**Entry Point**: `POST /api/v1/chat` with `mode: "selection"`

**Flow**:

1. **Input Validation**:
   - Require `doc_path` (validate it exists in Qdrant)
   - `selected_text` is optional (for "explain this passage" scenario)

2. **Filtered Vector Search**:
   - If `selected_text` provided:
     - Generate embedding of `selected_text`
     - Search Qdrant with **filter**: `doc_path == {provided_doc_path}`
     - Limit: 5 chunks (narrower scope than whole-book)
   - If `selected_text` is null (explain passage mode):
     - Use `question` embedding
     - Same doc_path filter

3. **Context Assembly**:
   - Include `selected_text` at the top:
     ```
     Selected Text:
     "{selected_text}"

     Related Context from Same Chapter:
     {chunk1.content}
     {chunk2.content}
     ```

4. **LLM Call**:
   - **System Prompt**:
     ```
     You are a study assistant. The user has selected a specific passage from the textbook.
     Explain or answer their question about this passage using the selected text and nearby context.
     Focus your explanation specifically on the selected text.
     ```
   - **User Prompt**:
     ```
     Selected Text: "{selected_text}"

     Related Context: {chunks}

     Question: {user_question}
     ```

5. **Response**:
   - Same citation format as whole-book mode
   - Response tagged with `mode: "selection"`

### Hallucination Control

**Strategies**:
- **System Prompt**: Explicitly instruct "answer ONLY from provided excerpts"
- **Temperature**: Low (0.2-0.3) for factual accuracy
- **Post-Processing**: (Future) Compare answer against source chunks via semantic similarity

---

## 6. API Design & Routing

### Endpoint Definitions

**File**: `app/api/v1/health.py`

```python
# GET /api/v1/health
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
```

**File**: `app/api/v1/chat.py`

```python
# POST /api/v1/chat
@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    qdrant: QdrantClient = Depends(get_qdrant),
    settings: Settings = Depends(get_settings)
):
    try:
        # Orchestrate RAG pipeline
        rag_service = RAGService(qdrant, db, settings)
        response = await rag_service.answer_question(request)
        return response
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail="The assistant is currently busy. Please try again in a moment.")
    except OpenAIError as e:
        logger.error(f"OpenAI error: {e}")
        raise HTTPException(status_code=500, detail="Unable to generate answer. Please try again.")
    except QdrantException as e:
        logger.error(f"Qdrant error: {e}")
        raise HTTPException(status_code=500, detail="Unable to search knowledge base. Please try again.")
    except Exception as e:
        logger.exception("Unexpected error in chat endpoint")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
```

### CORS Configuration

**File**: `app/main.py`

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # ["http://localhost:3000", "https://user.github.io"]
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)
```

**Development**:
- `CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]`

**Production**:
- `CORS_ORIGINS=["https://username.github.io", "https://custom-domain.com"]`

### Error Response Format

**Standard Error Schema**:
```python
class ErrorResponse(BaseModel):
    detail: str  # User-friendly message
    code: Optional[str] = None  # Machine-readable code (e.g., "RATE_LIMIT_EXCEEDED")
    timestamp: str
```

**HTTP Status Codes**:
- `200`: Success
- `400`: Invalid request (missing fields, validation errors)
- `429`: Rate limit exceeded (OpenAI or internal)
- `500`: Internal server error (DB, Qdrant, OpenAI failures)

### Router Aggregation

**File**: `app/api/v1/router.py`

```python
from fastapi import APIRouter
from app.api.v1 import health, chat

router = APIRouter(prefix="/api/v1")
router.include_router(health.router, tags=["health"])
router.include_router(chat.router, tags=["chat"])
```

**File**: `app/main.py`

```python
from app.api.v1.router import router as api_v1_router

app.include_router(api_v1_router)
```

---

## 7. Session Persistence Logic

### Session Creation

**File**: `app/services/session_manager.py`

**Behavior** (aligned with FR-025 to FR-029):

1. **Anonymous Users** (`user_id` is null):
   - **Skip DB writes** entirely (per spec assumption)
   - Generate a client-side `session_id` (UUID) in the response
   - Frontend stores `session_id` in browser local storage
   - Subsequent requests include `session_id`, but backend doesn't persist messages
   - Rationale: Reduces DB load, supports anonymous usage

2. **Identified Users** (`user_id` is provided):
   - **Check for existing session**:
     - If `session_id` provided in request:
       - Query: `SELECT * FROM chat_sessions WHERE id = {session_id} AND user_id = {user_id}`
       - If exists: Reuse session
       - If not exists: Create new session
     - If `session_id` is null: Create new session
   - **Session attributes**:
     - `id`: UUID
     - `user_id`: From request
     - `mode`: From request
     - `started_at`: Current timestamp
     - `last_message_at`: Updated on each message

3. **Message Persistence**:
   - Create two `ChatMessage` rows per interaction:
     - User message: `role="user"`, `content={question}`, `selected_text={...}`, `doc_path={...}`
     - Assistant message: `role="assistant"`, `content={answer}`
   - Link both to `session_id`

### Pseudocode

```python
async def handle_chat_request(request: ChatRequest, db: AsyncSession):
    if request.user_id is None:
        # Anonymous: no DB persistence
        session_id = str(uuid.uuid4())
        # ... RAG pipeline ...
        return ChatResponse(session_id=session_id, ...)

    else:
        # Identified user: persist session and messages
        if request.session_id:
            session = await db.get(ChatSession, request.session_id)
            if not session or session.user_id != request.user_id:
                session = ChatSession(user_id=request.user_id, mode=request.mode)
                db.add(session)
        else:
            session = ChatSession(user_id=request.user_id, mode=request.mode)
            db.add(session)

        # Create user message
        user_msg = ChatMessage(
            session_id=session.id,
            role="user",
            content=request.question,
            selected_text=request.selected_text,
            doc_path=request.doc_path
        )
        db.add(user_msg)

        # ... RAG pipeline ...

        # Create assistant message
        assistant_msg = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=rag_response.answer
        )
        db.add(assistant_msg)

        session.last_message_at = datetime.now(timezone.utc)
        await db.commit()

        return ChatResponse(session_id=str(session.id), ...)
```

---

## 8. Testing & Local Development

### Local Development Commands

**1. Install Dependencies**:
```bash
cd backend
uv sync  # Creates venv and installs from pyproject.toml
```

**2. Setup Environment**:
```bash
cp .env.example .env
# Edit .env with actual API keys
```

**3. Initialize Database**:
```bash
# Run Alembic migrations (future)
alembic upgrade head
```

**4. Index Textbook Content**:
```bash
uv run python backend/scripts/index_docs.py
```

**5. Start FastAPI Server**:
```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**6. Test Endpoints**:
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Chat (whole-book mode)
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"mode": "whole-book", "question": "What is ROS 2?"}'
```

### Testing Strategy

**File**: `tests/conftest.py`

```python
# Pytest fixtures for mocking
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_qdrant():
    """Mock Qdrant client"""
    client = MagicMock()
    client.search = AsyncMock(return_value=[
        # Mock search results
    ])
    return client

@pytest.fixture
def mock_openai():
    """Mock OpenAI client"""
    client = MagicMock()
    client.embeddings.create = AsyncMock(return_value=...)
    client.chat.completions.create = AsyncMock(return_value=...)
    return client

@pytest.fixture
async def db_session():
    """In-memory SQLite session for testing"""
    # Use SQLite in-memory DB for tests
    pass
```

**File**: `tests/test_health.py`

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

**File**: `tests/test_chat.py`

```python
@pytest.mark.asyncio
async def test_chat_whole_book_mode(mock_qdrant, mock_openai):
    # Arrange
    request = {"mode": "whole-book", "question": "What is ROS 2?"}

    # Act
    response = client.post("/api/v1/chat", json=request)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "whole-book"
    assert len(data["citations"]) > 0
```

### Frontend Integration (Dev)

**Docusaurus Dev Server**: `http://localhost:3000`
**Backend API**: `http://localhost:8000`

**Frontend .env**:
```env
REACT_APP_API_URL=http://localhost:8000/api/v1
```

**CORS**: Backend allows `http://localhost:3000` in dev

**API Calls** (from `ChatPanelPlaceholder`):
```typescript
const response = await fetch(`${API_URL}/chat`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    mode: 'whole-book',
    question: userQuestion,
    user_id: null  // Anonymous
  })
});
```

---

## 9. Deployment Considerations

### Platform Options

**Recommended**: Railway, Render, or Fly.io (all support Python/FastAPI with free tiers)

**Comparison**:

| Platform | Pros | Cons |
|----------|------|------|
| **Railway** | Simple deploy from GitHub, generous free tier, Postgres included | Less configurability |
| **Render** | Free tier, auto-deploy from Git, Web Services + Postgres | Cold starts on free tier |
| **Fly.io** | Global edge deployment, Dockerfile support, great for async apps | Steeper learning curve |

### Deployment Configuration

**Railway**:
- Connect GitHub repo
- Detect `backend/` as Python app (via `pyproject.toml`)
- Set environment variables in dashboard
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Render**:
- Create Web Service from GitHub
- Build command: `cd backend && uv sync`
- Start command: `cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Environment variables: Set in dashboard

**Environment Variables in Production**:
- `OPENAI_API_KEY`: From OpenAI account
- `QDRANT_URL` + `QDRANT_API_KEY`: From Qdrant Cloud dashboard
- `DATABASE_URL`: From Neon dashboard (auto-provided by Railway/Render Postgres addons)
- `CORS_ORIGINS`: `["https://username.github.io"]`
- `DEBUG`: `false`

### Indexing in Production

**Option 1: Manual Indexing** (Recommended for MVP)
- Run `index_docs.py` locally before deployment
- Qdrant Cloud is persistent; indexed data survives backend restarts
- Re-run script manually when textbook content updates

**Option 2: Scheduled Job** (Future Enhancement)
- Use Railway Cron Jobs, Render Cron Jobs, or GitHub Actions
- Schedule: Daily or weekly
- Command: `uv run python backend/scripts/index_docs.py --incremental`

**Option 3: On-Demand via API** (Advanced)
- Add `POST /api/v1/admin/reindex` endpoint (requires auth)
- Trigger indexing via webhook when Docusaurus content changes

### Performance Considerations

**Qdrant Cloud Free Tier Limits**:
- 1GB storage (~100k-200k chunks with 1536-dim vectors)
- API rate limits: ~100 queries/second
- Sufficient for MVP; monitor usage

**Neon Free Tier Limits**:
- 0.5GB storage
- Limited compute hours (reset monthly)
- Sufficient for chat history; consider retention policies

**OpenAI Rate Limits**:
- Free tier: Low rate limits
- Pay-as-you-go: $5-$20/month for moderate usage
- Monitor costs; set billing alerts

### Scaling Strategy (Future)

**If free tiers are exceeded**:
1. **Qdrant**: Upgrade to $25/month plan (10GB storage)
2. **Neon**: Upgrade to $19/month Pro plan (unlimited storage)
3. **Backend**: Scale to multiple instances (Render/Railway support horizontal scaling)

---

## 10. Implementation Checklist

### Phase 1: Foundation (P1 - Indexing & Whole-book Q&A)

- [ ] Set up `backend/` directory structure
- [ ] Create `pyproject.toml` with dependencies (FastAPI, SQLAlchemy, Qdrant, OpenAI, etc.)
- [ ] Implement `core/config.py` (Pydantic Settings)
- [ ] Implement `models/database.py` (ChatSession, ChatMessage)
- [ ] Implement `db/session.py` (async DB connection)
- [ ] Create Qdrant collection via script or dashboard
- [ ] Implement `scripts/index_docs.py`:
  - [ ] Scan `../docs/` for MDX files
  - [ ] Strip frontmatter and chunk by heading
  - [ ] Generate OpenAI embeddings
  - [ ] Upsert to Qdrant
- [ ] Implement `services/embeddings.py`
- [ ] Implement `services/qdrant_client.py` (search methods)
- [ ] Implement `services/rag.py` (whole-book mode)
- [ ] Implement `api/v1/health.py`
- [ ] Implement `api/v1/chat.py` (whole-book mode only)
- [ ] Test indexing: Run script, verify Qdrant has chunks
- [ ] Test API: `POST /api/v1/chat` with whole-book mode
- [ ] Deploy to Railway/Render (dev environment)

### Phase 2: Selection-based Q&A (P2)

- [ ] Extend `services/rag.py` for selection mode
- [ ] Implement doc_path filtering in Qdrant search
- [ ] Update `api/v1/chat.py` to handle selection mode
- [ ] Test with frontend: Select text, ask question

### Phase 3: Session Persistence (P3)

- [ ] Implement `services/session_manager.py`
- [ ] Add session creation logic to `api/v1/chat.py`
- [ ] Test with authenticated `user_id` (mock for now)
- [ ] Verify anonymous users skip DB writes

### Phase 4: Polish & Production

- [ ] Add comprehensive error handling
- [ ] Implement structured logging
- [ ] Add request ID tracing
- [ ] Write unit tests (health, chat endpoints)
- [ ] Add integration tests (mock OpenAI/Qdrant)
- [ ] Deploy to production
- [ ] Update CORS to production frontend URL
- [ ] Monitor logs and errors

---

## Appendix: Key Dependencies

**`pyproject.toml`** (managed by `uv`):

```toml
[project]
name = "rag-backend"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "pydantic>=2.6.0",
    "pydantic-settings>=2.1.0",
    "sqlalchemy>=2.0.25",
    "asyncpg>=0.29.0",      # Postgres async driver
    "alembic>=1.13.0",       # Migrations (future)
    "qdrant-client>=1.7.0",
    "openai>=1.10.0",
    "python-dotenv>=1.0.0",
    "python-frontmatter>=1.0.0",  # Parse MDX frontmatter
    "tiktoken>=0.5.2",       # Token counting
    "httpx>=0.26.0",         # Async HTTP client
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
]
```

---

## Summary

This plan provides a comprehensive blueprint for implementing the RAG backend with:
- Clear directory structure and separation of concerns
- Type-safe configuration management
- Async-first database and API design
- Hybrid chunking strategy for optimal retrieval
- Robust error handling and logging
- Testability through dependency injection
- Scalable deployment architecture

Next steps: Begin Phase 1 implementation, starting with project scaffolding and indexing pipeline.
