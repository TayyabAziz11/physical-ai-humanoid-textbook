---
id: 0008
title: Phase 6 reindexing automation
stage: green
date: 2025-12-19
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-rag-chatbot-system
branch: 001-rag-chatbot-system
user: user
command: /sp.implement
labels: ["implementation", "reindexing", "us3", "indexer", "admin", "cli"]
links:
  spec: specs/001-rag-chatbot-system/spec.md
  plan: specs/001-rag-chatbot-system/plan.md
  tasks: specs/001-rag-chatbot-system/tasks.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/app/services/indexer.py
  - backend/app/api/v1/endpoints/admin.py
  - backend/app/api/v1/router.py
  - backend/scripts/reindex_content.py
tests:
  - none (Phase 6 services - manual testing required)
---

## Prompt

Implement Phase 6: Re-indexing Automation (US3).

Scope:
- Tasks T030–T032 from tasks.md
- Implement backend/app/services/indexer.py with atomic swap strategy
- Implement POST /admin/reindex endpoint (dev-only)
- Implement CLI script scripts/reindex_content.py

Rules:
- Must re-parse Docusaurus Markdown source files
- Must reuse existing parser, chunker, embedder services
- Use Qdrant atomic swap pattern:
  create new collection → upload vectors → swap alias → delete old collection
- Do NOT modify existing query endpoints
- Include clear logging for each step
- Output file path + full file contents
- Stop after Phase 6 tasks are complete

## Response snapshot

Successfully completed Phase 6: Re-indexing Automation (US3) for RAG chatbot system.

**Tasks Completed (T030-T032)**: 3 tasks

### Indexing Service (T030)

**Created**: `backend/app/services/indexer.py`

**IndexingService class** with three main methods:

**1. `index_documents(docs_dir: str) -> dict`**
- Recursively finds all .md files using Path.rglob("*.md")
- Parses each file with MarkdownParser.parse_file()
- Chunks sections with ContentChunker.chunk_sections()
- Generates embeddings with EmbeddingService.embed_chunks()
- Returns summary: {"total_files": int, "total_chunks": int, "chunks": list[ContentChunk]}
- Error handling: Continues processing if individual file fails
- Comprehensive logging at each step

**2. `upsert_chunks_to_qdrant(chunks: list[ContentChunk], collection_name: str)`**
- Batch upload with configurable batch_size (default 100)
- Generates unique chunk IDs: f"{source_file}_{chunk_index}"
- Converts ContentChunk to PointStruct using chunk.to_qdrant_point()
- Logs progress for each batch
- Validates embeddings are present before upload

**3. `reindex_full(docs_dir: str) -> ReindexResponse`** - Atomic Swap Strategy
- **Step 1**: Create temporary collection with unique timestamp suffix
  - Collection name: f"{QDRANT_COLLECTION}_temp_{timestamp}"
  - Vector config: size=1536, distance=COSINE
- **Step 2**: Index all documents into temp collection
  - Calls index_documents() to process all .md files
- **Step 3**: Upload chunks to temp collection
  - Calls upsert_chunks_to_qdrant() with batch processing
- **Step 4**: Atomic swap via alias update
  - Detects existing alias or collection
  - Deletes old alias (if exists)
  - Creates new alias pointing to temp collection
  - Uses update_collection_aliases() for atomic operation
- **Step 5**: Cleanup old collection
  - Deletes previous collection after successful swap
  - Logs warnings if deletion fails (non-blocking)
- Tracks total duration
- Returns ReindexResponse with status, total_files, total_chunks, duration_seconds

**Logging**: Comprehensive logging with progress indicators [1/5], [2/5], etc., and visual separators (=== 80 chars)

### Admin Endpoint (T031)

**Created**: `backend/app/api/v1/endpoints/admin.py`

**POST /admin/reindex** endpoint:
- Accepts ReindexRequest with docs_directory parameter
- Validates directory exists and is valid
- Uses FastAPI BackgroundTasks for async processing
- Returns HTTP 202 (Accepted) immediately with status="started"
- Background task calls indexer.reindex_full()
- Comprehensive error handling:
  - 404: Directory not found
  - 400: Path is not a directory
  - Logs all errors during background processing

**GET /admin/health** endpoint:
- Simple health check for admin service
- Returns {"status": "healthy", "service": "admin"}

**Updated**: `backend/app/api/v1/router.py`
- Added import for admin endpoints
- Included admin.router with prefix="/admin" and tag="Admin"

### CLI Script (T032)

**Created**: `backend/scripts/reindex_content.py` (executable)

**Features**:
- Uses argparse for command-line interface
- Arguments:
  - `--docs-dir`: Path to documentation directory (default: ./docs)
  - `--verbose`, `-v`: Enable verbose logging
- Adds backend directory to sys.path for imports
- Validates docs_directory exists and is a directory
- Prints configuration summary before starting
- Calls IndexingService().reindex_full()
- Pretty-printed output with emojis and visual formatting
- Exit codes:
  - 0: Success
  - 1: Error
  - 130: Keyboard interrupt
- Comprehensive error handling with try/except blocks
- Help text with examples and environment variable documentation

**Usage**:
```bash
# Run from backend directory
python scripts/reindex_content.py --docs-dir ./docs

# Run from project root
python backend/scripts/reindex_content.py --docs-dir ./docs

# Verbose mode
python scripts/reindex_content.py --docs-dir ./docs --verbose
```

### Atomic Swap Strategy Details

**Why atomic swap?**
- Zero-downtime re-indexing
- Old collection remains queryable until swap completes
- Rollback possible if new index fails
- Clean separation between old and new data

**Implementation**:
1. Temp collection created: `textbook_chunks_temp_1734648000`
2. All content indexed into temp collection
3. Alias `textbook_chunks` updated to point to temp collection
4. Old collection deleted
5. Queries always use alias, so they're never disrupted

**Collection naming**:
- Alias (stable): `textbook_chunks` (from settings.QDRANT_COLLECTION)
- Temp collections: `textbook_chunks_temp_{timestamp}`
- Old collections deleted after swap

**Phase 6 Status**: ✅ COMPLETE - Re-indexing automation fully implemented

## Outcome

- ✅ Impact: Authors can now update book content and re-index via CLI or API endpoint. Zero-downtime re-indexing ensures queries are never disrupted.
- 🧪 Tests: Manual testing required (run CLI script with docs directory, verify Qdrant collection populated)
- 📁 Files: 4 files created/updated (1 indexer service, 1 admin endpoint, 1 router update, 1 CLI script)
- 🔁 Next prompts: `/sp.implement` for Phase 7 (Citations & Error Handling - T033-T036: enhanced citations, error messages) or test end-to-end re-indexing
- 🧠 Reflection: Atomic swap strategy provides production-ready zero-downtime re-indexing. Comprehensive logging at each step makes debugging easy. Background task pattern allows API to return immediately. CLI script provides convenient command-line interface for manual re-indexing. All existing services (parser, chunker, embedder) reused successfully.

## Evaluation notes (flywheel)

- Failure modes observed: None - atomic swap pattern ensures safe re-indexing even if process fails
- Graders run and results (PASS/FAIL): N/A (manual testing required)
- Prompt variant (if applicable): Standard /sp.implement with explicit atomic swap strategy requirements
- Next experiment (smallest change to try): Run `python backend/scripts/reindex_content.py --docs-dir ./docs` to test end-to-end indexing with actual documentation files
