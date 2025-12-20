---
id: 0002
title: RAG chatbot architecture plan
stage: plan
date: 2025-12-19
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-rag-chatbot-system
branch: 001-rag-chatbot-system
user: user
command: /sp.plan
labels: ["architecture", "rag", "fastapi", "qdrant", "pipeline", "endpoints"]
links:
  spec: specs/001-rag-chatbot-system/spec.md
  plan: specs/001-rag-chatbot-system/plan.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-rag-chatbot-system/plan.md
tests:
  - none (planning phase)
---

## Prompt

/sp.plan

- Inspect existing backend/ directory; do not recreate it. Identify missing or outdated components for RAG (FastAPI, Qdrant client, OpenAI SDK, Neon/Postgres support).
- Verify uv environment and pyproject.toml; add or update required packages only if missing (fastapi, uvicorn, qdrant-client, openai, pydantic, python-dotenv, asyncpg/psycopg).
- Design re-indexing pipeline: parse Docusaurus markdown, chunk content (heading-aware + code dual-chunking), generate embeddings, upsert to Qdrant with metadata.
- Define FastAPI endpoints for: global book queries, selection-only queries, and re-index trigger (dev-only).
- Specify retrieval + prompt assembly logic, enforcing strict context isolation for selection-based questions.
- Outline minimal frontend integration points for Docusaurus (API contract, selection payload, citation handling).

Output:
- Concise architecture steps
- Folder/file responsibilities (no boilerplate)
- Clear next actions for /sp.build

## Response snapshot

Created comprehensive architecture plan for RAG chatbot system on branch `001-rag-chatbot-system`.

**Key Findings**:
- Backend directory structure exists (app/api, app/core, app/db, app/models, app/services) but completely empty - no .py files
- uv environment already configured with all required dependencies (fastapi, qdrant-client, openai, pydantic, python-dotenv, asyncpg, etc.)
- Missing pyproject.toml but packages already installed via uv
- .env file populated with OpenAI, Qdrant, Neon credentials
- Docusaurus structure in place with markdown content in docs/

**Architecture Deliverables**:

1. **Re-indexing Pipeline** (4 components):
   - Parser: Extract markdown + frontmatter + heading hierarchy
   - Chunker: Heading-aware splitting + code dual-chunking (text_with_code + code_only types)
   - Embedder: OpenAI text-embedding-3-small with batch processing
   - Indexer: Qdrant upsert with atomic swap strategy

2. **FastAPI Endpoints** (3 routes):
   - `POST /query/global`: Search entire book, return answer with citations
   - `POST /query/selection`: Answer from selected text only (NO Qdrant retrieval)
   - `POST /admin/reindex`: Trigger re-indexing (dev-only)

3. **Retrieval Logic**:
   - Global: Qdrant vector search (top-7 chunks, cosine similarity, threshold 0.7)
   - Selection: Direct text pass-through (bypasses retrieval entirely for context isolation)

4. **Prompt Assembly**:
   - Global: System prompt + retrieved chunks + question → OpenAI gpt-4-turbo-preview
   - Selection: System prompt with "DO NOT use external knowledge" + selected text + question
   - Citations: Extract section_title + source_file → construct GitHub Pages URLs

5. **Frontend Integration**:
   - API client: fetch calls to /query/global and /query/selection
   - Selection detection: window.getSelection().toString()
   - Citation rendering: Clickable links to book sections
   - Error handling: 429 rate limits → "High traffic" message

**Architectural Decisions**:
1. Code dual-chunking (include code with text AND as separate chunks) - enables flexible search
2. Selection mode bypasses Qdrant entirely - guarantees zero context leakage
3. Atomic collection swap for re-indexing - ensures live queries never hit inconsistent state
4. Rate limit handling via user message (not queue) - simplest MVP approach
5. Conversation clears on navigation - independent page interactions

**Missing Components**:
- backend/pyproject.toml (metadata file)
- All Python files in backend/app/ (18 modules: main, endpoints, models, services)
- scripts/reindex_content.py (CLI tool)
- frontend/src/components/ChatWidget.tsx (React UI)
- frontend/static/js/chat-api.js (API wrapper)

## Outcome

- ✅ Impact: Complete technical architecture ready for implementation with all design decisions documented
- 🧪 Tests: No tests at planning phase
- 📁 Files: 1 file created (plan.md - 550 lines)
- 🔁 Next prompts: `/sp.tasks` to generate implementation task list, then begin implementation
- 🧠 Reflection: Thorough inspection revealed backend prepared but not implemented. Architecture balances spec requirements (dual chunking, context isolation) with implementation simplicity (no queue for rate limits, clear on navigation).

## Evaluation notes (flywheel)

- Failure modes observed: None - planning phase successful
- Graders run and results (PASS/FAIL): N/A (planning phase)
- Prompt variant (if applicable): Custom /sp.plan with explicit constraints (inspect existing, verify dependencies, enforce context isolation)
- Next experiment (smallest change to try): Consider creating a simplified architecture diagram for visual reference in plan.md
