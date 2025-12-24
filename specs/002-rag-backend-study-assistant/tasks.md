# Tasks: RAG Backend & Study Assistant API

**Feature**: `002-rag-backend-study-assistant`
**Input**: Design documents from `/specs/002-rag-backend-study-assistant/`
**Prerequisites**: plan.md (complete), spec.md (complete)

**Organization**: Tasks are grouped by technical phase to enable systematic backend development.

## Format: `[ID] [P?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- All file paths are relative to `backend/` directory

---

## Phase 1: Backend Project Scaffold

**Purpose**: Initialize FastAPI project with uv and basic health endpoint

- [ ] T001 Create backend/ directory structure per plan.md:
  ```
  backend/
  ├── app/
  │   ├── __init__.py
  │   ├── main.py
  │   ├── api/v1/
  │   ├── core/
  │   ├── models/
  │   ├── services/
  │   └── db/
  ├── scripts/
  ├── tests/
  └── pyproject.toml
  ```
- [ ] T002 Initialize pyproject.toml with uv dependencies:
  - fastapi>=0.109.0
  - uvicorn[standard]>=0.27.0
  - pydantic>=2.6.0, pydantic-settings>=2.1.0
  - sqlalchemy>=2.0.25, asyncpg>=0.29.0
  - qdrant-client>=1.7.0
  - openai>=1.10.0
  - python-dotenv>=1.0.0
  - python-frontmatter>=1.0.0
  - tiktoken>=0.5.2
  - httpx>=0.26.0
- [ ] T003 [P] Create .gitignore for backend/ (.env, .env.*, __pycache__/, .pytest_cache/, dist/)
- [ ] T004 Create minimal backend/app/main.py with FastAPI app initialization
- [ ] T005 Create backend/app/api/v1/router.py as router aggregator (empty for now)
- [ ] T006 [P] Implement backend/app/api/v1/health.py:
  - GET /api/v1/health endpoint
  - Returns: {status: "healthy", version: "0.1.0", timestamp: ISO8601}
- [ ] T007 Wire health router into main.py and test with `uv run uvicorn app.main:app --reload`
- [ ] T008 [P] Create backend/README.md with quickstart instructions (install, run, test health endpoint)

**Checkpoint**: FastAPI app runs and GET /api/v1/health responds

---

## Phase 2: Configuration & Environment Handling

**Purpose**: Centralized configuration management with Pydantic Settings

- [ ] T009 Implement backend/app/core/config.py with Pydantic BaseSettings:
  - APP_NAME, APP_VERSION, DEBUG
  - OPENAI_API_KEY, OPENAI_CHAT_MODEL, OPENAI_EMBEDDING_MODEL
  - QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION
  - DATABASE_URL
  - CORS_ORIGINS (list)
  - RAG_TOP_K_CHUNKS, RAG_CHUNK_MAX_TOKENS
  - env_file = ".env"
- [ ] T010 [P] Create backend/.env.example with all required variables (empty values, comments)
- [ ] T011 [P] Implement backend/app/core/logging.py with structured logging setup
- [ ] T012 [P] Implement backend/app/core/security.py:
  - Input sanitization utilities for user questions and selected text
  - CORS configuration helper
- [ ] T013 Implement backend/app/api/deps.py with dependency injection:
  - get_settings() -> Settings
  - Placeholder for get_db() and get_qdrant() (implement in later phases)
- [ ] T014 Update main.py to add CORS middleware using settings.CORS_ORIGINS
- [ ] T015 Update health.py to use get_settings() and return settings.APP_VERSION

**Checkpoint**: Configuration loaded from .env, CORS configured, health endpoint returns version

---

## Phase 3: Neon Postgres Models & Session Management

**Purpose**: Database schema and async SQLAlchemy setup

- [ ] T016 Implement backend/app/db/base.py with SQLAlchemy declarative base
- [ ] T017 Implement backend/app/db/session.py:
  - create_async_engine() using settings.DATABASE_URL
  - AsyncSessionLocal = async_sessionmaker()
  - async get_db() dependency yielding session
- [ ] T018 Update backend/app/api/deps.py to import and export get_db()
- [ ] T019 Implement backend/app/models/database.py with ORM models:
  - ChatSession: id (UUID), user_id (String, nullable), mode (Enum), started_at, last_message_at
  - ChatMessage: id (UUID), session_id (FK), role (Enum), content (Text), created_at, selected_text (nullable), doc_path (nullable)
  - Relationships: ChatSession.messages = relationship("ChatMessage")
- [ ] T020 [P] Implement backend/app/models/schemas.py with Pydantic models:
  - ChatRequest: mode (Literal), question (str), selected_text (Optional), doc_path (Optional), user_id (Optional), session_id (Optional)
  - Citation: doc_path (str), heading (str), snippet (str)
  - ChatResponse: answer (str), citations (list[Citation]), mode (str), session_id (str)
  - ErrorResponse: detail (str), code (Optional), timestamp (str)
- [ ] T021 Create a manual database initialization script or Alembic migration (optional):
  - Run CREATE TABLE statements for chat_sessions and chat_messages
  - For MVP, can manually create tables using SQLAlchemy metadata.create_all()
- [ ] T022 Test database connection by adding a test route that queries ChatSession.query.count()

**Checkpoint**: Database connection works, ORM models defined, Pydantic schemas ready

---

## Phase 4: Qdrant Client Configuration & Collection Schema

**Purpose**: Vector database setup and search operations

- [ ] T023 Implement backend/app/services/qdrant_client.py:
  - Initialize QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
  - create_collection() method for "textbook_chunks" (1536 dims, cosine, HNSW)
  - search_whole_book(query_vector, limit) -> list of search results
  - search_by_document(query_vector, doc_path, limit) -> filtered search results
  - upsert_chunks(chunks: list) -> upsert to collection
- [ ] T024 Create backend/app/api/deps.py::get_qdrant() dependency:
  - Return singleton QdrantClient instance
  - Initialize on app startup via lifespan events in main.py
- [ ] T025 Update main.py lifespan events:
  - On startup: initialize Qdrant client, ensure collection exists (create if not)
  - On shutdown: close Qdrant client connection (if needed)
- [ ] T026 [P] Add Qdrant connectivity check to health.py:
  - Try to query collection info
  - Return {qdrant_status: "connected"} or error
- [ ] T027 Test Qdrant connection by running health endpoint and verifying qdrant_status

**Checkpoint**: Qdrant client connected, collection created, health check includes Qdrant status

---

## Phase 5: Indexing Script for ../docs → Qdrant

**Purpose**: Populate vector database with textbook content

- [ ] T028 Implement backend/app/services/embeddings.py:
  - generate_embedding(text: str) -> list[float] using OpenAI embeddings API
  - Batch support: generate_embeddings(texts: list[str]) -> list[list[float]]
  - Use settings.OPENAI_EMBEDDING_MODEL (text-embedding-3-small)
- [ ] T029 Implement backend/scripts/index_docs.py:
  - Scan ../docs directory for .md and .mdx files recursively
  - Extract module_id from path (e.g., module-1-ros2 → 1)
  - Parse files with python-frontmatter to strip YAML frontmatter
- [ ] T030 Implement chunking logic in index_docs.py:
  - Primary: split by H2/H3 headings (regex or markdown parser)
  - Secondary: if section > 500 tokens (use tiktoken), split by paragraphs/sentences
  - Assign metadata: doc_path, module_id, heading, chunk_index, content, token_count
- [ ] T031 Implement embedding generation in index_docs.py:
  - For each chunk, call embeddings.generate_embedding(chunk.content)
  - Batch embeddings for efficiency (10-20 chunks per API call)
- [ ] T032 Implement upsert to Qdrant in index_docs.py:
  - Generate deterministic point ID: md5(doc_path + "#" + chunk_index)
  - Use qdrant_client.upsert_chunks() from services/qdrant_client.py
  - Store vector + metadata payload
- [ ] T033 [P] Add --incremental flag to index_docs.py:
  - Compute MD5 hash of each source file
  - Query Qdrant for existing chunks by doc_path
  - Compare file_hash metadata: skip if match, re-index if different
- [ ] T034 [P] Add error handling in index_docs.py:
  - Log errors for malformed MDX files, continue processing
  - Print summary: {processed: N, errors: M, skipped: K}
- [ ] T035 Add CLI usage to index_docs.py:
  - `uv run python backend/scripts/index_docs.py` (full re-index)
  - `uv run python backend/scripts/index_docs.py --incremental`
  - `uv run python backend/scripts/index_docs.py --docs-dir ../docs`
- [ ] T036 Test indexing by running script on ../docs and verifying chunks in Qdrant dashboard or via search

**Checkpoint**: Textbook content indexed in Qdrant with metadata, searchable

---

## Phase 6: /api/chat Endpoint - Whole-book Mode

**Purpose**: Core RAG pipeline for general questions

- [ ] T037 Implement backend/app/services/rag.py with RAGService class:
  - __init__(qdrant_client, db_session, settings)
  - answer_question(request: ChatRequest) -> ChatResponse (router method)
- [ ] T038 Implement whole-book mode pipeline in rag.py::answer_question():
  - Validate input: sanitize question, check length, detect non-English (return error)
  - Generate query embedding using embeddings.generate_embedding(question)
  - Search Qdrant: qdrant_client.search_whole_book(query_vector, limit=7)
  - Sort chunks by doc_path and chunk_index for readability
- [ ] T039 Implement context assembly in rag.py:
  - Format chunks as: "[Module X, Chapter Y - Heading]\n{content}\n\n..."
  - Construct system prompt: "You are a study assistant for Physical AI textbook. Answer based ONLY on excerpts. Cite sources."
  - Construct user prompt: "Textbook Excerpts:\n{context}\n\nQuestion: {question}\n\nAnswer:"
- [ ] T040 Implement backend/app/services/openai_chat.py:
  - generate_answer(system_prompt, user_prompt) -> str
  - Call OpenAI chat.completions.create() with settings.OPENAI_CHAT_MODEL
  - Temperature: 0.3 for factual accuracy
  - Return LLM response text
- [ ] T041 Implement citation extraction in rag.py:
  - Parse LLM response for chunk references (regex or heuristic)
  - For each cited chunk: {doc_path, heading, snippet (first 80-100 chars)}
  - Fallback: return top 3 retrieved chunks as citations if LLM doesn't cite
- [ ] T042 Implement backend/app/api/v1/chat.py:
  - POST /api/v1/chat endpoint
  - Depends on: get_db(), get_qdrant(), get_settings()
  - Validate ChatRequest schema (mode, question required)
  - If mode == "whole-book": call RAGService.answer_question()
  - Return ChatResponse with answer, citations, mode, session_id
- [ ] T043 Add error handling to chat.py:
  - RateLimitError → 429 "The assistant is currently busy..."
  - OpenAIError → 500 "Unable to generate answer..."
  - QdrantException → 500 "Unable to search knowledge base..."
  - ValidationError → 400 with field details
  - Generic Exception → 500 "An unexpected error occurred"
- [ ] T044 Add structured logging to chat.py and rag.py:
  - Log request ID, user_id, mode, question (truncated), response time
  - Log errors with stack traces
- [ ] T045 Test whole-book mode:
  - POST /api/v1/chat with {mode: "whole-book", question: "What is ROS 2?"}
  - Verify response includes answer + citations from Module 1

**Checkpoint**: Whole-book Q&A works end-to-end, returns cited answers

---

## Phase 7: /api/chat Endpoint - Selection-based Mode

**Purpose**: Context-aware Q&A for selected text

- [ ] T046 Extend rag.py::answer_question() for selection mode:
  - If mode == "selection": validate doc_path (required), selected_text (optional)
  - If selected_text provided: generate embedding of selected_text
  - Else: use question embedding (explain passage scenario)
  - Filtered search: qdrant_client.search_by_document(query_vector, doc_path, limit=5)
- [ ] T047 Implement selection-specific context assembly in rag.py:
  - Include selected_text at top: "Selected Text:\n\"{selected_text}\"\n\n"
  - Add "Related Context from Same Chapter:\n{chunks}"
  - System prompt: "User selected a passage. Explain using selected text and nearby context. Focus on selection."
- [ ] T048 Update chat.py to route selection mode:
  - If mode == "selection": ensure selectedText and docPath are validated
  - Call RAGService.answer_question() with selection request
  - Tag response with mode: "selection"
- [ ] T049 Test selection mode:
  - POST /api/v1/chat with {mode: "selection", question: "Explain this", selectedText: "...", docPath: "docs/module-1-ros2/..."}
  - Verify answer focuses on selected text with relevant context

**Checkpoint**: Selection-based Q&A works, answers are contextually focused

---

## Phase 8: Session Persistence in Neon (when userId provided)

**Purpose**: Store chat history for identified users

- [ ] T050 Implement backend/app/services/session_manager.py:
  - create_or_get_session(user_id, session_id, mode, db) -> ChatSession
  - If user_id is null: return generated session_id, skip DB writes
  - If user_id provided: create/retrieve ChatSession in DB
  - persist_message(session_id, role, content, selected_text, doc_path, db) -> ChatMessage
- [ ] T051 Update rag.py::answer_question() to integrate session persistence:
  - Call session_manager.create_or_get_session() at start
  - If user_id not null: persist user message before RAG pipeline
  - After LLM response: persist assistant message
  - Update session.last_message_at timestamp
  - Return session_id in ChatResponse
- [ ] T052 Add conditional persistence logic in session_manager.py:
  - If user_id is null: skip all DB writes, only return generated UUID
  - If user_id provided: execute all DB inserts/updates
- [ ] T053 Test session persistence:
  - POST /api/v1/chat with user_id: "test-user-123"
  - Query DB to verify ChatSession and ChatMessage records created
  - POST again with same session_id, verify messages linked to same session
- [ ] T054 Test anonymous mode:
  - POST /api/v1/chat without user_id
  - Verify response includes session_id but DB has no records

**Checkpoint**: Session persistence works for authenticated users, skipped for anonymous

---

## Phase 9: Basic Tests & Local Dev Instructions

**Purpose**: Quality assurance and developer onboarding

### Testing Setup

- [ ] T055 Create backend/tests/conftest.py with pytest fixtures:
  - mock_qdrant(): Mock QdrantClient with search() returning fake chunks
  - mock_openai(): Mock OpenAI client (embeddings, chat completions)
  - db_session(): In-memory SQLite session or test Postgres instance
  - test_settings(): Override Settings with test values
- [ ] T056 [P] Implement backend/tests/test_health.py:
  - test_health_endpoint(): GET /api/v1/health returns 200 with status="healthy"
  - test_health_includes_version(): Verify version field present
- [ ] T057 [P] Implement backend/tests/test_rag.py (unit tests):
  - test_whole_book_search(): Verify RAG pipeline calls Qdrant correctly
  - test_citation_extraction(): Verify citation formatting
  - test_selection_mode_filtering(): Verify doc_path filter applied
- [ ] T058 [P] Implement backend/tests/test_chat.py (integration tests):
  - test_chat_whole_book_mode(): POST /api/chat with whole-book, verify response structure
  - test_chat_selection_mode(): POST with selection mode, verify focused answer
  - test_chat_validation_errors(): Missing required fields return 400
  - test_chat_rate_limit_error(): Mock rate limit, verify 429 response
- [ ] T059 Run pytest suite: `uv run pytest backend/tests -v`

### Documentation

- [ ] T060 Update backend/README.md with comprehensive local dev guide:
  - Prerequisites: Python 3.11+, uv, Qdrant Cloud account, Neon account, OpenAI API key
  - Installation: `cd backend && uv sync`
  - Environment setup: Copy .env.example to .env, fill in API keys
  - Database setup: Create Neon database, run migrations (if using Alembic)
  - Indexing: `uv run python backend/scripts/index_docs.py`
  - Start server: `uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
  - Test endpoints: curl examples for /health and /chat
  - Run tests: `uv run pytest tests/ -v`
- [ ] T061 [P] Document deployment options in README.md:
  - Railway: Connect GitHub, set env vars, start command
  - Render: Build and start commands, environment variables
  - Fly.io: Dockerfile approach (optional)
- [ ] T062 [P] Create backend/ARCHITECTURE.md:
  - Document key design decisions (async patterns, session persistence strategy, chunking algorithm)
  - Diagram data flow: User query → Embedding → Qdrant → Context → OpenAI → Response
  - Explain anonymous vs authenticated session handling

### Edge Case Testing

- [ ] T063 Test edge case: empty question → 400 "Please enter a question"
- [ ] T064 Test edge case: non-English question → polite error "Only English is supported"
- [ ] T065 Test edge case: zero chunks found → "I couldn't find relevant information in the textbook"
- [ ] T066 Test edge case: OpenAI rate limit → 429 "The assistant is currently busy..."
- [ ] T067 Test edge case: unrelated question → "I'm designed to answer questions about Physical AI..."
- [ ] T068 Test edge case: selected text exactly 10 characters → accepted as valid

**Checkpoint**: Tests pass, documentation complete, edge cases handled

---

## Dependencies & Execution Order

### Phase Dependencies (Sequential)

1. **Phase 1** (Scaffold) → must complete first
2. **Phase 2** (Config) → depends on Phase 1
3. **Phase 3** (Database) → depends on Phase 2 (needs config.py)
4. **Phase 4** (Qdrant) → depends on Phase 2 (needs config.py)
5. **Phase 5** (Indexing) → depends on Phase 2, 4 (needs config + Qdrant client)
6. **Phase 6** (Whole-book) → depends on Phase 2, 3, 4, 5 (needs all services + indexed data)
7. **Phase 7** (Selection) → depends on Phase 6 (extends whole-book pipeline)
8. **Phase 8** (Persistence) → depends on Phase 3, 6 (needs DB models + RAG service)
9. **Phase 9** (Tests) → depends on all prior phases

### Parallel Opportunities

**Within Phase 2**:
- T010, T011, T012 can run in parallel (different files)

**Within Phase 3**:
- T020 (schemas.py) can run in parallel with T016-T019 (database setup)

**Within Phase 4**:
- T026 (health check update) can run in parallel with T023-T025

**Within Phase 5**:
- T033, T034 (incremental mode, error handling) can run in parallel after T032

**Within Phase 9**:
- T056, T057, T058 can run in parallel (different test files)
- T061, T062 can run in parallel (different docs)

### Critical Path

The fastest path to a working MVP:
```
Phase 1 (T001-T008) → Phase 2 (T009-T015) → Phase 3 (T016-T022) →
Phase 4 (T023-T027) → Phase 5 (T028-T036) → Phase 6 (T037-T045)
```

At this point, whole-book Q&A is functional. Phases 7-8 can be added incrementally.

---

## Implementation Strategy

### MVP-First Approach (Recommended)

**Milestone 1: Basic Q&A (Phases 1-6)**
- Complete Phases 1-6 sequentially
- Result: Whole-book Q&A works, no persistence
- Test: `curl -X POST http://localhost:8000/api/v1/chat -d '{"mode":"whole-book","question":"What is ROS 2?"}'`
- Deploy to Railway/Render for demo

**Milestone 2: Enhanced Q&A (Phase 7)**
- Add selection-based mode
- Test: Select text in frontend, verify focused answers
- Deploy update

**Milestone 3: Persistence (Phase 8)**
- Add session storage for authenticated users
- Test: Create sessions, verify DB records
- Deploy update

**Milestone 4: Production Ready (Phase 9)**
- Add tests, documentation, edge case handling
- Final deployment with monitoring

### Parallel Team Strategy

With 2-3 developers:

**After Phase 2 (Config) completes:**
- Developer A: Phase 3 (Database) + Phase 8 (Persistence)
- Developer B: Phase 4 (Qdrant) + Phase 5 (Indexing)
- Developer C: Phase 9 (Tests, Docs)

**After Phase 5 (Indexing) completes:**
- Developer A: Phase 6 (Whole-book Q&A)
- Developer B: Phase 7 (Selection Q&A)

**Merge and integrate Phases 6-7, then deploy**

---

## Notes

- **[P] tasks**: Can run in parallel (different files, no blocking dependencies)
- **File paths**: All relative to `backend/` directory
- **Testing**: Tests included in Phase 9, but can be written alongside implementation (TDD)
- **Commit strategy**: Commit after each task or at end of each phase
- **Free tier limits**: Monitor Qdrant (1GB), Neon (0.5GB), OpenAI usage
- **Error messages**: Always user-friendly in API responses, technical details in logs
- **Security**: Never log API keys or secrets, sanitize all user inputs

**Total Tasks**: 68 tasks across 9 phases

**Estimated Effort**:
- Phase 1: 2 hours (setup)
- Phase 2: 3 hours (config)
- Phase 3: 4 hours (database)
- Phase 4: 3 hours (Qdrant)
- Phase 5: 6 hours (indexing script)
- Phase 6: 8 hours (RAG pipeline + whole-book)
- Phase 7: 3 hours (selection mode)
- Phase 8: 4 hours (persistence)
- Phase 9: 6 hours (tests + docs)

**Total: ~39 hours** (approximately 1 week for solo developer, 3-4 days for team)
