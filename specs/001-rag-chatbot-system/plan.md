# Implementation Plan: RAG-Powered Interactive Chatbot

**Branch**: `001-rag-chatbot-system` | **Date**: 2025-12-19 | **Spec**: [spec.md](./spec.md)

## Summary

Build an embedded RAG chatbot for the Docusaurus technical book that enables readers to ask questions about book content (global mode) or selected text passages (selection mode). The system will parse markdown content, generate embeddings, store in Qdrant Cloud, and expose FastAPI endpoints for querying. OpenAI models handle embeddings and response generation.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, Qdrant Client, OpenAI SDK, Uvicorn, Pydantic, python-dotenv, asyncpg, python-frontmatter, tiktoken
**Storage**: Qdrant Cloud (vector database), Neon Postgres (optional metadata), Markdown files (source content)
**Testing**: pytest, pytest-asyncio
**Target Platform**: Linux/WSL server (development), cloud deployment (production)
**Project Type**: Web application (backend API + frontend integration)
**Performance Goals**: < 3s query response time, support 50 concurrent users, < 15min full re-indexing for 200-page book
**Constraints**: Qdrant Cloud Free Tier limits, OpenAI API rate limits, GitHub Pages CORS restrictions
**Scale/Scope**: ~200 book pages, ~1000-2000 content chunks, dozens of concurrent readers

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Based on project constitution (.specify/memory/constitution.md):
- **Code Quality**: Modular, typed (Pydantic models), error handling at service boundaries
- **Testing**: Contract tests for API endpoints, unit tests for chunking logic
- **Security**: Input sanitization, API key management via .env, CORS configuration
- **Architecture**: Separate concerns (parsing, embedding, retrieval, API), no premature abstractions
- **Performance**: Async I/O for external services (Qdrant, OpenAI), connection pooling

## Project Structure

### Documentation (this feature)

```text
specs/001-rag-chatbot-system/
├── spec.md              # Business requirements (completed)
├── plan.md              # This file
├── checklists/
│   └── requirements.md  # Validation checklist (completed)
└── tasks.md             # Implementation tasks (pending /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── main.py                    # FastAPI application entry point
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── query.py       # /query/global and /query/selection endpoints
│   │       │   └── admin.py       # /admin/reindex endpoint (dev-only)
│   │       └── router.py          # API router aggregator
│   ├── core/
│   │   ├── config.py              # Settings (Pydantic BaseSettings from .env)
│   │   └── logging.py             # Logging configuration
│   ├── db/
│   │   ├── qdrant.py              # Qdrant client initialization & connection
│   │   └── postgres.py            # Optional Neon Postgres client (future use)
│   ├── models/
│   │   ├── request.py             # Pydantic request models (QueryRequest, SelectionQueryRequest)
│   │   ├── response.py            # Pydantic response models (QueryResponse, Citation)
│   │   └── chunk.py               # ContentChunk model (text, metadata, embedding)
│   └── services/
│       ├── parser.py              # Markdown parsing, heading extraction
│       ├── chunker.py             # Content chunking (heading-aware + code dual-chunking)
│       ├── embedder.py            # OpenAI embedding generation
│       ├── indexer.py             # Qdrant upsert operations, re-indexing orchestration
│       ├── retriever.py           # Vector search, top-k retrieval
│       └── responder.py           # OpenAI chat completion, prompt assembly, citation formatting
├── scripts/
│   └── reindex_content.py         # CLI script to trigger re-indexing locally
├── .env                            # Environment variables (already exists, populated)
├── .venv/                          # uv-managed virtual environment (already exists)
├── uv.lock                         # uv lock file (already exists)
└── pyproject.toml                  # Project metadata (needs creation)

frontend/ (Docusaurus)
├── src/
│   └── components/
│       └── ChatWidget.tsx          # React component for embedded chat interface
├── static/
│   └── js/
│       └── chat-api.js             # API client for backend communication
└── docusaurus.config.ts            # Docusaurus configuration (CORS, plugins)

docs/ (Markdown content - already exists)
├── intro.md
├── module-1-ros2/
├── module-2-digital-twin-gazebo-unity/
├── module-3-nvidia-isaac/
└── module-4-vision-language-action/
```

**Structure Decision**: Web application structure with existing backend/ and frontend (Docusaurus). Backend has folder structure (app/api, app/core, app/db, app/models, app/services) but no Python files yet. All implementation files need creation.

## Architecture

### 1. Re-indexing Pipeline

**Responsibility**: Convert markdown files → searchable chunks → Qdrant vectors

**Components**:

- **Parser** (`services/parser.py`):
  - Read markdown files from `docs/` directory recursively
  - Extract frontmatter metadata (title, module, section)
  - Parse heading hierarchy (h1, h2, h3) to build document structure
  - Identify code blocks, tables, and text content
  - **Output**: Structured document tree with metadata

- **Chunker** (`services/chunker.py`):
  - **Heading-aware chunking**: Split content at heading boundaries (h2/h3 level)
  - **Token-based splitting**: Ensure chunks don't exceed `RAG_CHUNK_MAX_TOKENS` (500 tokens from .env)
  - **Code dual-chunking** (per spec decision):
    - Include code blocks within surrounding text chunks (preserves context)
    - Extract code blocks as separate chunks (enables code-specific search)
    - Tag chunks with `chunk_type: "text_with_code"` or `chunk_type: "code_only"`
  - **Metadata preservation**: Attach source file path, section title, heading hierarchy, chunk index
  - **Output**: List of ContentChunk objects

- **Embedder** (`services/embedder.py`):
  - Call OpenAI Embeddings API (`text-embedding-3-small` from .env)
  - Batch embedding requests (max 100 chunks per API call)
  - Handle rate limiting with exponential backoff
  - **Output**: Add embedding vector to each ContentChunk

- **Indexer** (`services/indexer.py`):
  - Initialize Qdrant collection (`textbook_chunks` from .env) with:
    - Vector size: 1536 (text-embedding-3-small dimension)
    - Distance metric: Cosine similarity
    - Payload schema: `{text, source_file, section_title, heading_hierarchy, chunk_index, chunk_type}`
  - Upsert chunks to Qdrant (use `chunk_id` as point ID: `{source_file}_{chunk_index}`)
  - Atomic swap strategy: Create new collection, index all content, swap collection alias
  - **Output**: Updated Qdrant collection

**Re-indexing Trigger**:
- Development: CLI script `scripts/reindex_content.py --docs-dir ./docs`
- Production: API endpoint `POST /admin/reindex` (requires auth token in future, dev-only for now)

**Error Handling**:
- If parsing fails → log error, skip file, continue
- If embedding fails → retry 3x with backoff, then skip chunk
- If Qdrant upsert fails → rollback to previous collection

---

### 2. FastAPI Endpoints

**Base URL**: `http://localhost:8000/api/v1`

#### Endpoint 1: Global Query

**Route**: `POST /query/global`

**Request** (`models/request.py`):
```python
class GlobalQueryRequest(BaseModel):
    question: str  # Max MAX_QUESTION_TOKENS (2000 from .env)
    conversation_history: list[dict] | None = None  # Optional for P3 feature
```

**Response** (`models/response.py`):
```python
class Citation(BaseModel):
    section_title: str
    source_file: str
    link_url: str  # Constructed from source_file + heading anchor

class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
    retrieved_chunks: int
    processing_time_ms: float
```

**Logic**:
1. Validate question length (max 2000 tokens)
2. Generate question embedding (OpenAI)
3. Query Qdrant for top-k similar chunks (`RAG_TOP_K_CHUNKS=7` from .env)
4. Pass retrieved chunks + question to responder service
5. Return formatted answer with citations

---

#### Endpoint 2: Selection Query

**Route**: `POST /query/selection`

**Request**:
```python
class SelectionQueryRequest(BaseModel):
    question: str
    selected_text: str  # Max MAX_SELECTION_TOKENS (5000 from .env)
```

**Response**: Same as `QueryResponse`

**Logic**:
1. Validate question and selected_text lengths
2. **Critical**: Do NOT query Qdrant for this mode
3. Pass selected_text directly as context to responder service
4. Ensure responder prompt explicitly forbids using external knowledge
5. Return answer constrained to selected_text only

---

#### Endpoint 3: Re-index (Dev Only)

**Route**: `POST /admin/reindex`

**Request**:
```python
class ReindexRequest(BaseModel):
    docs_directory: str = "./docs"
```

**Response**:
```python
class ReindexResponse(BaseModel):
    status: str  # "started" | "completed" | "failed"
    total_files: int
    total_chunks: int
    duration_seconds: float
```

**Logic**:
1. Trigger indexer service asynchronously
2. Return immediate "started" response
3. Log progress and completion to application logs

---

### 3. Retrieval & Prompt Assembly Logic

**Retriever** (`services/retriever.py`):

**Global Mode**:
```python
async def retrieve_global(question: str, top_k: int = 7) -> list[ContentChunk]:
    # Generate question embedding
    question_embedding = await embedder.embed([question])

    # Query Qdrant
    results = qdrant_client.search(
        collection_name="textbook_chunks",
        query_vector=question_embedding[0],
        limit=top_k,
        score_threshold=0.7  # Minimum similarity score
    )

    # Convert to ContentChunk objects
    return [ContentChunk.from_qdrant_point(r) for r in results]
```

**Selection Mode**:
```python
async def retrieve_selection(selected_text: str) -> list[ContentChunk]:
    # No retrieval - directly wrap selected text
    return [ContentChunk(
        text=selected_text,
        metadata={"source": "user_selection"},
        chunk_type="selection"
    )]
```

---

**Responder** (`services/responder.py`):

**Prompt Assembly**:

Global Mode:
```python
system_prompt = """You are a helpful assistant answering questions about a technical book on Physical AI and Humanoid Robotics.

Rules:
- Answer based ONLY on the provided context chunks
- If information is not in the context, say "This topic is not covered in the book"
- Include citations in format [Section: {section_title}]
- Be concise and accurate
"""

user_prompt = f"""
Context chunks:
{format_chunks(retrieved_chunks)}

Question: {user_question}

Answer the question based on the context above.
"""
```

Selection Mode:
```python
system_prompt = """You are a helpful assistant explaining a selected text passage.

CRITICAL RULES:
- Answer using ONLY the selected text provided below
- Do NOT use any external knowledge
- If the answer is not in the selected text, say "The selected text doesn't contain this information"
"""

user_prompt = f"""
Selected text:
{selected_text}

Question: {user_question}

Answer based strictly on the selected text above.
"""
```

**OpenAI Call**:
```python
response = await openai_client.chat.completions.create(
    model=settings.OPENAI_CHAT_MODEL,  # gpt-4-turbo-preview from .env
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    temperature=0.3,  # Low temperature for factual accuracy
    max_tokens=500
)
```

**Citation Extraction**:
- Parse retrieved chunks to extract unique section titles and source files
- Construct citation links: `https://tayyabaziz11.github.io/physical-ai-humanoid-textbook/{module}/{page}#{heading-anchor}`
- Return structured Citation objects

---

### 4. Frontend Integration Points

**API Contract** (frontend → backend):

```typescript
// chat-api.js
const API_BASE = "http://localhost:8000/api/v1";

async function queryGlobal(question: string): Promise<QueryResponse> {
  return fetch(`${API_BASE}/query/global`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question })
  }).then(r => r.json());
}

async function querySelection(question: string, selectedText: string): Promise<QueryResponse> {
  return fetch(`${API_BASE}/query/selection`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, selected_text: selectedText })
  }).then(r => r.json());
}
```

**Selection Payload**:
- Frontend captures `window.getSelection().toString()` when user highlights text
- Passes as `selected_text` parameter to `/query/selection`
- UI shows toggle button: "Ask about this book" (global) vs "Ask about selection" (selection mode)

**Citation Handling**:
- Backend returns `citations: [{ section_title, source_file, link_url }]`
- Frontend renders citations as clickable links below the answer
- Clicking citation navigates to that book page with anchor scroll

**CORS Configuration**:
- Backend already configured in .env: `CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]`
- Add GitHub Pages origin in production: `https://TayyabAziz11.github.io`

**Error Handling**:
- Network failures → Show "Unable to reach chatbot service. Please try again."
- Rate limit errors (429) → Show "High traffic detected. Please wait a moment and try again."
- Empty response → Show "No relevant information found in the book."

---

## Missing Components

### Backend
1. **pyproject.toml** - Needs creation with:
   - `[project]` metadata: name="rag-backend", version="0.1.0", requires-python=">=3.11"
   - `[project.dependencies]`: fastapi, uvicorn, qdrant-client, openai, pydantic, python-dotenv, asyncpg, python-frontmatter, tiktoken
   - `[tool.uv]` section for uv package manager

2. **All Python files in app/** - Directory structure exists but empty:
   - `app/main.py`
   - `app/api/v1/endpoints/query.py`, `app/api/v1/endpoints/admin.py`
   - `app/core/config.py`, `app/core/logging.py`
   - `app/db/qdrant.py`, `app/db/postgres.py`
   - `app/models/request.py`, `app/models/response.py`, `app/models/chunk.py`
   - `app/services/parser.py`, `app/services/chunker.py`, `app/services/embedder.py`
   - `app/services/indexer.py`, `app/services/retriever.py`, `app/services/responder.py`

3. **scripts/reindex_content.py** - CLI tool for manual re-indexing

### Frontend (Docusaurus)
1. **src/components/ChatWidget.tsx** - React component for chat UI
2. **static/js/chat-api.js** - API client wrapper
3. **Docusaurus plugin configuration** - Inject ChatWidget into all pages

### Dependencies
All required packages are already listed in `.venv` metadata (rag_backend-0.1.0.dist-info/METADATA):
- ✅ fastapi>=0.109.0
- ✅ uvicorn[standard]>=0.27.0
- ✅ qdrant-client>=1.7.0
- ✅ openai>=1.10.0
- ✅ pydantic>=2.6.0
- ✅ python-dotenv>=1.0.0
- ✅ asyncpg>=0.29.0
- ✅ python-frontmatter>=1.0.0
- ✅ tiktoken>=0.5.2
- ✅ sqlalchemy>=2.0.25 (for future Postgres use)
- ✅ psycopg2-binary>=2.9.11

**Action**: Create `backend/pyproject.toml` with these dependencies already installed via uv.

---

## Next Steps for /sp.tasks

1. **Phase 1: Core Backend (P1 Features)**
   - Task 1.1: Create pyproject.toml and verify uv dependencies
   - Task 1.2: Implement config.py (load .env settings)
   - Task 1.3: Implement qdrant.py (client initialization)
   - Task 1.4: Implement parser.py (markdown parsing)
   - Task 1.5: Implement chunker.py (heading-aware + code dual-chunking)
   - Task 1.6: Implement embedder.py (OpenAI embeddings)
   - Task 1.7: Implement indexer.py (Qdrant upsert, re-indexing)
   - Task 1.8: Implement retriever.py (vector search)
   - Task 1.9: Implement responder.py (prompt assembly, OpenAI chat)
   - Task 1.10: Implement query.py endpoints (global, selection)
   - Task 1.11: Implement main.py (FastAPI app, CORS, logging)
   - Task 1.12: Test global query flow end-to-end

2. **Phase 2: Frontend Integration (P1 Features)**
   - Task 2.1: Create ChatWidget.tsx (React component)
   - Task 2.2: Create chat-api.js (API client)
   - Task 2.3: Integrate ChatWidget into Docusaurus pages
   - Task 2.4: Implement selection detection and mode switching
   - Task 2.5: Test selection query flow end-to-end

3. **Phase 3: Re-indexing (P2 Feature)**
   - Task 3.1: Implement admin.py endpoint (re-index trigger)
   - Task 3.2: Create scripts/reindex_content.py (CLI tool)
   - Task 3.3: Test re-indexing with updated book content

4. **Phase 4: Citations & Error Handling (P2 Feature)**
   - Task 4.1: Implement citation extraction and URL construction
   - Task 4.2: Add frontend citation rendering with clickable links
   - Task 4.3: Implement rate limit handling (429 responses)
   - Task 4.4: Add comprehensive error messages for all failure modes

5. **Phase 5: Conversational Follow-ups (P3 Feature - Optional)**
   - Task 5.1: Add conversation_history parameter to global query
   - Task 5.2: Update responder to use conversation history in prompts
   - Task 5.3: Implement frontend conversation state management

---

## Architectural Decisions

### Decision 1: Code Block Dual-Chunking
**Problem**: Code blocks could be included with surrounding text or extracted separately.

**Options**:
- A: Include code with surrounding text only
- B: Extract code as separate chunks only
- C: Both (selected)

**Rationale**: Option C provides maximum flexibility - readers can search for code examples independently while also retrieving code with explanatory context. Storage cost is acceptable given Qdrant Free Tier limits (1GB, sufficient for ~500K chunks).

**Implementation**: Chunker tags chunks with `chunk_type: "text_with_code"` or `chunk_type: "code_only"`. Retriever can filter by type if needed.

---

### Decision 2: Selection Mode Context Isolation
**Problem**: Selection-mode queries must never use information outside selected text.

**Options**:
- A: Query Qdrant but restrict to selected text chunk
- B: Skip Qdrant entirely, pass selected text directly (selected)

**Rationale**: Option B guarantees zero information leakage. Option A risks retrieval bugs that leak context. System prompt reinforcement alone is insufficient - architectural enforcement is required.

**Implementation**: `/query/selection` endpoint bypasses retriever entirely. Responder receives raw selected_text with explicit "DO NOT use external knowledge" prompt.

---

### Decision 3: Re-indexing Strategy (Atomic Swap)
**Problem**: Re-indexing must not disrupt live chatbot queries.

**Options**:
- A: Update collection in-place (risks inconsistency)
- B: Create new collection, atomic swap (selected)

**Rationale**: Option B ensures readers always query a consistent index. Qdrant supports collection aliases - create `textbook_chunks_v2`, index all content, then swap alias `textbook_chunks` to point to v2. Old collection deleted after swap.

**Implementation**: Indexer checks if `textbook_chunks` exists → rename to `_old`, create new, swap, delete old.

---

### Decision 4: Rate Limit Handling (Display Message)
**Problem**: OpenAI API rate limits can be hit during high traffic.

**Options**:
- A: Queue queries (complex infrastructure)
- B: Display "high traffic" message (selected)
- C: Use cached responses (requires cache layer)

**Rationale**: Per spec clarification, Option B is simplest for MVP. Backend returns 429 status, frontend shows user-friendly message. Future enhancement: add caching for frequent questions.

**Implementation**: Responder catches `RateLimitError` from OpenAI SDK → return 429 with `{"detail": "High traffic. Please wait and try again."}`. Frontend detects 429 → display message.

---

### Decision 5: Conversation History (Clear on Navigation)
**Problem**: Should conversation persist across page navigations?

**Options**:
- A: Clear on navigation (selected)
- B: Persist across pages
- C: Persist within chapter only

**Rationale**: Per spec clarification, Option A keeps implementation simple. Each page interaction is independent. Frontend stores conversation in component state (not sessionStorage).

**Implementation**: ChatWidget initializes empty `messages: []` on mount. Navigating to new page remounts component → fresh conversation.

---

## Risk Analysis

### Risk 1: Qdrant Free Tier Limits
**Impact**: 1GB storage, 1 cluster
**Mitigation**: Monitor chunk count (target ~1000-2000 for 200-page book). Each chunk ~512 bytes text + 1536×4 bytes vector = ~6.6KB → ~150K chunks fit in 1GB. Well within limits.

### Risk 2: OpenAI API Costs
**Impact**: Embeddings cost $0.00002/1K tokens, Chat cost $0.01/1K tokens
**Mitigation**: 200 pages ~400K tokens → ~$8 for initial indexing. Per-query cost ~$0.0001. Monitor via OpenAI dashboard.

### Risk 3: CORS Configuration
**Impact**: GitHub Pages requires specific origin allowlist
**Mitigation**: Backend .env already has localhost origins. Add `https://TayyabAziz11.github.io` before production deployment.

### Risk 4: Selection Text Size
**Impact**: Users could select entire chapters (>5000 tokens)
**Mitigation**: Backend validates `len(tiktoken.encode(selected_text)) <= MAX_SELECTION_TOKENS`. Return 400 error if exceeded.

### Risk 5: Citation Link Construction
**Impact**: Markdown file paths must map correctly to Docusaurus URLs
**Mitigation**: Parser extracts file paths like `docs/module-1-ros2/intro.md` → URL `https://.../module-1-ros2/intro#heading`. Test with real file structure.

---

## Complexity Tracking

No Constitution violations require justification. Architecture follows:
- **Single responsibility**: Each service has one job (parse, chunk, embed, retrieve, respond)
- **No premature abstractions**: No repository pattern (direct Qdrant calls), no ORM for Postgres (asyncpg when needed)
- **Minimal dependencies**: All dependencies serve specific purposes (no "just in case" packages)
- **Testable**: Services accept injected clients (Qdrant, OpenAI) for unit testing
