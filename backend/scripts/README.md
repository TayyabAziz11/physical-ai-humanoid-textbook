# Backend Scripts

This directory contains utility scripts for the RAG backend.

## Available Scripts

### `index_docs.py` - Document Indexing Script

Discovers markdown files in `../docs`, chunks content by headings, generates embeddings using OpenAI, and uploads to Qdrant vector database.

**Features:**
- Discovers all `.md` and `.mdx` files recursively
- Strips YAML frontmatter
- Extracts metadata (doc_path, module_id, heading)
- Chunks text into 200-500 token pieces with 50 token overlap
- Generates embeddings using OpenAI text-embedding-3-small
- Uploads to Qdrant in batches of 100
- Progress logging throughout

**Usage:**

```bash
# Test the script without making API calls (dry run)
cd backend
uv run python -m scripts.index_docs --dry-run

# Test with limited number of documents
uv run python -m scripts.index_docs --dry-run --limit 5

# Full indexing (requires API keys configured)
uv run python -m scripts.index_docs
```

**Prerequisites:**

Before running (non-dry-run), ensure these environment variables are set in `backend/.env`:

```env
OPENAI_API_KEY=sk-your-openai-api-key
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key
QDRANT_COLLECTION=textbook_chunks
```

**CLI Options:**

- `--dry-run` - Parse and analyze documents without making API calls (no embeddings, no Qdrant)
- `--limit N` - Process only first N documents (useful for testing)

**Expected Output:**

```
======================================================================
Document Indexing Script
======================================================================
🔍 DRY RUN MODE - No API calls will be made
Discovering markdown files in /path/to/docs...
Found 17 markdown files
Limiting to first 2 files

[1/2] Processing: docs/intro.md
  Generated 2 chunks

[2/2] Processing: docs/module-1-ros2/chapter-1-basics.mdx
  Generated 1 chunks

======================================================================
✅ DRY RUN COMPLETE
Files processed: 2
Total chunks generated: 3
======================================================================
```

---

### `init_db.py` - Database Initialization

Creates database tables for chat sessions and messages.

**Usage:**

```bash
cd backend
uv run python scripts/init_db.py
```

**Prerequisites:**

Requires `DATABASE_URL` configured in `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database
```

---

## Development Notes

- All scripts are safe to import (no network calls on import)
- Network calls only happen when scripts are executed
- Scripts use `app.core.logging` for consistent logging
- Scripts use lazy-initialized clients (singleton pattern)
