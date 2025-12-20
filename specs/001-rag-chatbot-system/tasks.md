# Tasks: RAG-Powered Interactive Chatbot

**Input**: Design documents from `/specs/001-rag-chatbot-system/`
**Prerequisites**: plan.md ✅, spec.md ✅

**Organization**: Tasks grouped by phase and user story for incremental delivery

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1=Global Query, US2=Selection Query, US3=Re-indexing, US4=Citations)
- Exact file paths included in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency management

- [x] **T001** Create `backend/pyproject.toml` with project metadata: name="rag-backend", version="0.1.0", requires-python=">=3.11", dependencies list (fastapi, uvicorn, qdrant-client, openai, pydantic, pydantic-settings, python-dotenv, asyncpg, python-frontmatter, tiktoken, httpx)
- [x] **T002** [P] Create `backend/app/__init__.py` (empty file for package initialization)
- [x] **T003** [P] Create `backend/app/api/__init__.py` (empty file)
- [x] **T004** [P] Create `backend/app/api/v1/__init__.py` (empty file)
- [x] **T005** [P] Create `backend/app/api/v1/endpoints/__init__.py` (empty file)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Configuration & Logging

- [x] **T006** Create `backend/app/core/__init__.py` (empty file)
- [x] **T007** Implement `backend/app/core/config.py`:
  - Pydantic `BaseSettings` class loading from `.env`
  - Fields: `OPENAI_API_KEY`, `OPENAI_CHAT_MODEL`, `OPENAI_EMBEDDING_MODEL`, `QDRANT_URL`, `QDRANT_API_KEY`, `QDRANT_COLLECTION`, `DATABASE_URL`, `CORS_ORIGINS` (JSON list), `RAG_TOP_K_CHUNKS`, `RAG_CHUNK_MAX_TOKENS`, `MAX_QUESTION_TOKENS`, `MAX_SELECTION_TOKENS`, `LOG_LEVEL`
  - Export singleton `settings` instance
- [x] **T008** [P] Implement `backend/app/core/logging.py`:
  - Configure Python logging with format: `[%(asctime)s] %(levelname)s - %(name)s - %(message)s`
  - Set level from `settings.LOG_LEVEL`
  - Export `get_logger(name: str)` function

### Database Clients

- [x] **T009** Create `backend/app/db/__init__.py` (empty file)
- [x] **T010** Implement `backend/app/db/qdrant.py`:
  - Initialize Qdrant client with `settings.QDRANT_URL` and `settings.QDRANT_API_KEY`
  - Function `get_qdrant_client() -> QdrantClient` (singleton pattern)
  - Function `init_collection()`: Create collection if not exists with vector_size=1536, distance=Cosine
  - Export client getter

### Data Models

- [x] **T011** Create `backend/app/models/__init__.py` (empty file)
- [x] **T012** Implement `backend/app/models/chunk.py`:
  - Pydantic model `ContentChunk`: fields = `text: str`, `metadata: dict`, `chunk_type: str` (text_with_code | code_only | selection), `embedding: list[float] | None`
  - Method `from_qdrant_point(point)` to convert Qdrant search results
  - Method `to_qdrant_point(chunk_id: str)` to prepare for upsert
- [x] **T013** Implement `backend/app/models/request.py`:
  - Pydantic model `GlobalQueryRequest`: fields = `question: str` (max length validation using MAX_QUESTION_TOKENS), `conversation_history: list[dict] | None = None`
  - Pydantic model `SelectionQueryRequest`: fields = `question: str`, `selected_text: str` (max length validation using MAX_SELECTION_TOKENS)
  - Pydantic model `ReindexRequest`: fields = `docs_directory: str = "./docs"`
- [x] **T014** Implement `backend/app/models/response.py`:
  - Pydantic model `Citation`: fields = `section_title: str`, `source_file: str`, `link_url: str`
  - Pydantic model `QueryResponse`: fields = `answer: str`, `citations: list[Citation]`, `retrieved_chunks: int`, `processing_time_ms: float`
  - Pydantic model `ReindexResponse`: fields = `status: str`, `total_files: int`, `total_chunks: int`, `duration_seconds: float`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Global Book Query (Priority: P1) 🎯 MVP

**Goal**: Enable readers to ask questions about any topic in the book and receive answers with citations

**Independent Test**: Start FastAPI server, POST to `/query/global` with question="What is ROS2?", verify response contains answer and citations

### Core Services (Backend)

- [x] **T015** [US1] Create `backend/app/services/__init__.py` (empty file)
- [x] **T016** [US1] Implement `backend/app/services/parser.py`:
  - Function `parse_markdown_file(file_path: str) -> dict`: Read file, extract frontmatter (title, module), parse markdown content
  - Function `extract_heading_hierarchy(content: str) -> list[dict]`: Identify h1/h2/h3 headings with text ranges
  - Function `identify_code_blocks(content: str) -> list[dict]`: Find code fence blocks with language and text
  - Export parsing functions
- [x] **T017** [US1] Implement `backend/app/services/chunker.py`:
  - Function `chunk_by_headings(parsed_doc: dict, max_tokens: int) -> list[dict]`: Split at h2/h3 boundaries, respect token limit
  - Function `extract_code_chunks(parsed_doc: dict) -> list[dict]`: Extract code blocks as separate chunks
  - Function `create_content_chunks(parsed_doc: dict, source_file: str) -> list[ContentChunk]`: Orchestrate heading + code dual-chunking, tag with chunk_type, attach metadata (source_file, section_title, heading_hierarchy, chunk_index)
  - Use tiktoken for token counting
- [x] **T018** [US1] Implement `backend/app/services/embedder.py`:
  - Function `generate_embeddings(texts: list[str]) -> list[list[float]]`: Call OpenAI Embeddings API with model from settings
  - Batch processing (max 100 texts per request)
  - Exponential backoff for rate limit errors (3 retries)
  - Export embedding function
- [x] **T019** [US1] Implement `backend/app/services/retriever.py`:
  - Async function `retrieve_global(question: str, top_k: int, score_threshold: float = 0.7) -> list[ContentChunk]`: Generate question embedding, query Qdrant, convert results to ContentChunk objects
  - Filter by score_threshold
  - Export retrieval functions
- [x] **T020** [US1] Implement `backend/app/services/responder.py`:
  - Async function `generate_response_global(question: str, chunks: list[ContentChunk]) -> tuple[str, list[dict]]`: Build system prompt ("Answer based ONLY on context"), format chunks, call OpenAI Chat API, return (answer, raw_citations)
  - Temperature=0.3 for factual accuracy
  - Max tokens=500
  - Export responder functions

### API Endpoints (Backend)

- [x] **T021** [US1] Implement `backend/app/api/v1/endpoints/query.py`:
  - Endpoint `POST /global`: Accept `GlobalQueryRequest`, validate question length, call retriever.retrieve_global(), call responder.generate_response_global(), format citations with link_url construction, return `QueryResponse`
  - Error handling: 400 for validation errors, 429 for rate limits, 500 for server errors
  - Track processing time
- [x] **T022** [US1] Implement `backend/app/api/v1/router.py`:
  - Create APIRouter for v1
  - Include query endpoints
  - Export router
- [x] **T023** [US1] Implement `backend/app/main.py`:
  - Create FastAPI app with title="RAG Study Assistant", version="0.1.0"
  - Configure CORS with origins from settings.CORS_ORIGINS
  - Include v1 router at prefix="/api/v1"
  - Add startup event: `init_collection()`
  - Add health check endpoint `GET /health`
  - Configure logging

**Test**: Run `cd backend && uv run uvicorn app.main:app --reload`, POST to `http://localhost:8000/api/v1/query/global` with `{"question": "What is ROS2?"}`, verify JSON response with answer and citations

---

## Phase 4: User Story 2 - Selection-Based Query (Priority: P1) 🎯 MVP

**Goal**: Enable readers to ask questions about highlighted text without retrieving external context

**Independent Test**: POST to `/query/selection` with selected_text="[paragraph]" and question="Explain this", verify answer uses only selected text

### Services (Backend)

- [x] **T024** [US2] Update `backend/app/services/retriever.py`:
  - Async function `retrieve_selection(selected_text: str) -> list[ContentChunk]`: Wrap selected_text in ContentChunk with chunk_type="selection", metadata={"source": "user_selection"}
  - NO Qdrant query - direct pass-through
- [x] **T025** [US2] Update `backend/app/services/responder.py`:
  - Async function `generate_response_selection(question: str, selected_text: str) -> tuple[str, list[dict]]`: Build system prompt with "CRITICAL: Answer using ONLY the selected text. DO NOT use external knowledge", format selected_text, call OpenAI Chat, return (answer, empty_citations)
  - Ensure prompt explicitly forbids external information

### API Endpoints (Backend)

- [x] **T026** [US2] Update `backend/app/api/v1/endpoints/query.py`:
  - Endpoint `POST /selection`: Accept `SelectionQueryRequest`, validate lengths, call retriever.retrieve_selection(), call responder.generate_response_selection(), return `QueryResponse` with citations=[]
  - Error handling same as global endpoint

**Test**: POST to `/selection` with `{"question": "What does this mean?", "selected_text": "ROS2 is a robot operating system"}`, verify response doesn't include information from other book sections

---

## Phase 5: Frontend Integration (Priority: P1) 🎯 MVP

**Goal**: Embed chat widget in Docusaurus pages with global and selection modes

**Independent Test**: Open book page, type question in chat, see answer. Highlight text, click "Ask about selection", see constrained answer.

### API Client (Frontend)

- [x] **T027** [US1, US2] Create `static/js/chat-api.js`:
  - Function `queryGlobal(question: string): Promise<QueryResponse>`: Fetch POST to `/api/v1/query/global`
  - Function `querySelection(question: string, selectedText: string): Promise<QueryResponse>`: Fetch POST to `/api/v1/query/selection`
  - Error handling for network failures and HTTP errors
  - Export API functions

### Chat Widget Component (Frontend)

- [x] **T028** [US1, US2] Create `src/components/ChatWidget.tsx`:
  - React component with state: `messages: array`, `inputText: string`, `mode: "global" | "selection"`, `selectedText: string`, `isLoading: boolean`
  - UI: Chat bubble button (bottom-right), expandable panel, message list, input field, mode toggle button
  - On submit: Call appropriate API function based on mode, display answer with citations
  - Selection detection: Listen for text selection events, capture `window.getSelection().toString()`, enable selection mode if text selected
  - Citation rendering: Clickable links to book sections
  - Error messages: Show user-friendly errors for 429 (rate limit), network failures, empty responses

### Docusaurus Integration (Frontend)

- [x] **T029** [US1, US2] Update `docusaurus.config.ts`:
  - Add ChatWidget to theme config or create custom plugin
  - Ensure widget loads on all pages
  - Configure CORS for production (add GitHub Pages origin)

**Test**: Run `npm start` in frontend, open `http://localhost:3000`, verify chat widget appears, test global and selection queries end-to-end

---

## Phase 6: User Story 3 - Content Re-indexing (Priority: P2)

**Goal**: Allow authors to update searchable book content when chapters change

**Independent Test**: Update a markdown file in `docs/`, run re-index command, query chatbot about new content, verify correct answer

### Indexing Service (Backend)

- [x] **T030** [US3] Implement `backend/app/services/indexer.py`:
  - Async function `index_documents(docs_dir: str) -> dict`: Recursively find all .md files, parse each with parser, chunk with chunker, generate embeddings with embedder, return summary (total_files, total_chunks)
  - Async function `upsert_chunks_to_qdrant(chunks: list[ContentChunk], collection_name: str)`: Batch upsert to Qdrant (use chunk_id = f"{source_file}_{chunk_index}")
  - Async function `reindex_full(docs_dir: str) -> ReindexResponse`: Atomic swap strategy - create temp collection, index all content, swap alias, delete old collection
  - Track duration

### Admin Endpoint (Backend)

- [x] **T031** [US3] Create `backend/app/api/v1/endpoints/admin.py`:
  - Endpoint `POST /reindex`: Accept `ReindexRequest`, trigger indexer.reindex_full() asynchronously (use BackgroundTasks), return immediate `ReindexResponse` with status="started"
  - Log progress and completion
  - Include in router.py

### CLI Script (Backend)

- [x] **T032** [US3] Create `backend/scripts/reindex_content.py`:
  - CLI script using argparse: `python scripts/reindex_content.py --docs-dir ./docs`
  - Load settings, call indexer.reindex_full(), print summary
  - Executable script

**Test**: Run `python backend/scripts/reindex_content.py --docs-dir ./docs`, verify Qdrant collection populated. Add new content to docs/, re-run, query chatbot for new content.

---

## Phase 7: User Story 4 - Citations & Error Handling (Priority: P2)

**Goal**: Provide clickable source citations and handle all error scenarios gracefully

**Independent Test**: Query chatbot, click citation link, verify navigation to correct book section. Simulate rate limit, verify user-friendly message.

### Citation Generation (Backend)

- [ ] **T033** [US4] Update `backend/app/services/responder.py`:
  - Function `extract_citations(chunks: list[ContentChunk]) -> list[Citation]`: Parse chunks metadata, extract unique (section_title, source_file) pairs
  - Function `construct_citation_url(source_file: str, section_title: str) -> str`: Map file paths to GitHub Pages URLs with heading anchors (e.g., `docs/module-1-ros2/intro.md` → `https://TayyabAziz11.github.io/physical-ai-humanoid-textbook/module-1-ros2/intro#heading-anchor`)
  - Group citations by chapter when multiple chunks from same chapter
  - Return structured Citation objects

### Enhanced Error Handling (Backend)

- [ ] **T034** [US4] Update `backend/app/api/v1/endpoints/query.py`:
  - Catch OpenAI `RateLimitError`: Return HTTP 429 with JSON `{"detail": "High traffic. Please wait and try again."}`
  - Catch Qdrant connection errors: Return HTTP 503 with message "Chatbot service temporarily unavailable"
  - Catch validation errors: Return HTTP 400 with specific field errors
  - Add request timeout handling (max 10 seconds)

### Frontend Error Handling

- [ ] **T035** [US4] Update `src/components/ChatWidget.tsx`:
  - Handle HTTP 429: Display message "High traffic detected. Please wait a moment and try again."
  - Handle network errors: Display "Unable to reach chatbot service. Please check your connection."
  - Handle empty results (citations=[], answer contains "not found"): Display "No relevant information found in the book for this question."
  - Add loading spinner during API calls

### Citation UI (Frontend)

- [ ] **T036** [US4] Update `src/components/ChatWidget.tsx`:
  - Render citations as clickable links below answer text
  - Format: "Sources: [Chapter 1: Introduction], [Chapter 3: Advanced Topics]"
  - On click: Navigate to citation.link_url with smooth scroll to anchor
  - Style citations distinctly (smaller font, gray color, underline on hover)

**Test**: Query "What is ROS2?", verify citations render with correct links. Click citation, verify navigation. Simulate rate limit (send 10 rapid requests), verify 429 error message displays.

---

## Phase 8: Optional - Conversational Follow-ups (Priority: P3)

**Goal**: Support multi-turn conversations where users can ask follow-up questions

**Independent Test**: Ask "What is ROS2?", then ask "Can you give an example?", verify context from first question is used

### Conversation State (Backend)

- [ ] **T037** [US5] Update `backend/app/services/responder.py`:
  - Modify `generate_response_global()` to accept `conversation_history: list[dict]` parameter
  - Build OpenAI messages array including history: `[{"role": "user", "content": prev_q}, {"role": "assistant", "content": prev_a}, ...]`
  - Limit history to last 5 turns to avoid token overflow

### API Update (Backend)

- [ ] **T038** [US5] Update `backend/app/api/v1/endpoints/query.py`:
  - Modify `/global` endpoint to accept `conversation_history` from `GlobalQueryRequest`
  - Pass history to responder

### Frontend State Management

- [ ] **T039** [US5] Update `src/components/ChatWidget.tsx`:
  - Maintain conversation state: `conversationHistory: array` in component state
  - On each query, append `{role: "user", content: question}` and `{role: "assistant", content: answer}` to history
  - Pass history array in API request
  - Clear history on page navigation (component unmount/remount)

**Test**: Ask initial question, receive answer, ask follow-up using pronoun ("Can you explain more?"), verify answer uses context from first question.

---

## Summary

**Total Tasks**: 39
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundation): 9 tasks
- Phase 3 (US1 - Global Query): 9 tasks
- Phase 4 (US2 - Selection Query): 3 tasks
- Phase 5 (Frontend Integration): 3 tasks
- Phase 6 (US3 - Re-indexing): 3 tasks
- Phase 7 (US4 - Citations/Errors): 4 tasks
- Phase 8 (US5 - Conversations): 3 tasks (optional)

**Critical Path**:
1. Complete Phase 1-2 (Setup + Foundation) first - **14 tasks**
2. Implement Phase 3 (Global Query) - **9 tasks** → Testable MVP
3. Add Phase 4 (Selection Query) - **3 tasks** → Complete P1 features
4. Integrate Phase 5 (Frontend) - **3 tasks** → User-facing MVP
5. Add Phase 6-7 (Re-indexing, Citations) - **7 tasks** → Complete P2 features
6. Optional Phase 8 (Conversations) - **3 tasks** → P3 feature

**Parallel Opportunities**:
- T002-T005 (package `__init__.py` files) - can run in parallel
- T008 (logging) - parallel with T007 (config)
- After Phase 2: US1 backend (T015-T020) can develop in parallel with partial frontend prep

**Dependencies**:
- Phase 3-8 all depend on Phase 2 completion
- Frontend (Phase 5) depends on at least T021-T023 (API endpoints exist)
- T024-T026 (Selection) depend on T015-T020 (Services exist)
- T030-T032 (Indexing) depend on T016-T018 (Parser, Chunker, Embedder)
- T033-T036 (Citations/Errors) depend on Phase 3-5 (core features exist)
