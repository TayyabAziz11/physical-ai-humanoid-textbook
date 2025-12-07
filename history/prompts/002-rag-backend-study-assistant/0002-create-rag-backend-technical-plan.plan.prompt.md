---
id: 0002
title: Create RAG Backend Technical Plan
stage: plan
date: 2025-12-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-rag-backend-study-assistant
branch: 002-rag-backend-study-assistant
user: tayyabaziz
command: /sp.plan
labels: ["plan", "architecture", "rag", "backend", "fastapi", "qdrant", "postgres"]
links:
  spec: specs/002-rag-backend-study-assistant/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-rag-backend-study-assistant/plan.md
tests:
  - Plan structure validation (10 required sections)
  - Technical decision documentation review
---

## Prompt

/sp.plan

Create a detailed technical implementation plan for the feature '002-rag-backend-study-assistant' based on specs/002-rag-backend-study-assistant/spec.md and the project constitution.

Scope: RAG backend + chat API ONLY. Does NOT include frontend, auth, personalization, or Urdu translation (those are out-of-scope or separate features).

Tech stack & high-level decisions:
- Language: Python 3.11+
- Framework: FastAPI (async-first)
- Package/runtime: uv (pyproject.toml, NOT requirements.txt)
- Database: Neon serverless Postgres (asyncpg + SQLAlchemy 2.x async)
- Vector store: Qdrant Cloud Free Tier
- Embeddings & chat: OpenAI API (text-embedding-3-small + gpt-4o-mini or similar)
- Session management: Minimal (sessionId + userId placeholder for future auth)

Please structure the plan with these sections:
1. Project & Directory Structure
2. Configuration & Environment
3. Data Modeling (Postgres: ChatSession, ChatMessage; Pydantic schemas)
4. Qdrant Schema & Indexing Strategy
5. Chat Pipeline (whole-book mode, selection mode, citation extraction)
6. API Design & Routing
7. Session Persistence Logic
8. Testing & Local Development
9. Deployment Considerations
10. Implementation Checklist

For each section, provide:
- Concrete file/module organization
- Key architectural decisions and rationale
- Data schemas and contracts
- Dependencies and configuration patterns
- Error handling and edge cases

## Response snapshot

Created comprehensive technical implementation plan with 10 sections covering:

**1. Project & Directory Structure**
- Backend located at `backend/` with FastAPI app structure
- Organized into: api/v1 (routes), core (config/logging/security), models (ORM + Pydantic), services (RAG/embeddings/Qdrant), db (session management), scripts (indexing)

**2. Configuration & Environment**
- Pydantic Settings for env vars (DATABASE_URL, QDRANT_URL, OPENAI_API_KEY, etc.)
- CORS configuration for Docusaurus frontend
- Separate .env.example template

**3. Data Modeling**
- SQLAlchemy async models: ChatSession (UUID, user_id nullable, mode enum, timestamps) and ChatMessage (UUID, session_id FK, role enum, content, selected_text, doc_path)
- Pydantic schemas for API validation and responses
- Alembic for migrations

**4. Qdrant Schema & Indexing Strategy**
- Collection: textbook_chunks, 1536-dim vectors (text-embedding-3-small)
- Metadata: doc_path, module_id, heading, chunk_index, content, token_count
- Indexing algorithm: scan docs/, parse MDX, chunk by heading (H2/H3) with 500-token fallback, embed, upsert to Qdrant
- Script: scripts/index_docs.py

**5. Chat Pipeline**
- Whole-book mode: embed query → search Qdrant (top 5) → format context → OpenAI chat completion → extract citations
- Selection mode: filter by doc_path → retrieve surrounding chunks → same pipeline
- Citation extraction: regex for [Doc X, Section Y] patterns in response
- Services: services/rag.py (orchestration), services/embeddings.py (OpenAI wrapper), services/qdrant_client.py

**6. API Design & Routing**
- GET /api/v1/health (Qdrant + DB connectivity check)
- POST /api/v1/chat (ChatRequest → ChatResponse with answer + citations)
- Request: { sessionId, mode, question, selectedText?, docPath? }
- Response: { answer, citations: [{ docPath, heading }], sessionId }

**7. Session Persistence Logic**
- Anonymous users (userId=null): skip DB writes, frontend manages sessionId in localStorage
- Authenticated users: persist ChatSession and ChatMessage records
- Conditional writes based on userId presence

**8. Testing & Local Development**
- pytest with async support
- Mocked dependencies: Qdrant (in-memory vectors), OpenAI (fixture responses), DB (SQLite or test Postgres)
- Unit tests for services, integration tests for API endpoints
- uvicorn for local dev server

**9. Deployment Considerations**
- PaaS options: Railway, Render, Fly.io
- Environment variables via platform secrets
- Database migrations on deployment (Alembic upgrade head)
- Health check endpoint for monitoring

**10. Implementation Checklist**
- Phase 1: Foundation (project setup, config, models, migrations)
- Phase 2: Indexing (script + Qdrant schema)
- Phase 3: RAG Pipeline (services for embeddings, search, chat)
- Phase 4: API Layer (routes, error handling, CORS)
- Phase 5: Testing & Deployment (pytest suite, PaaS deployment)

## Outcome

- ✅ Impact: Complete technical blueprint ready for implementation. Provides clear structure for backend development with async-first patterns, separation of concerns (API/services/data), and deployment readiness. Enables frontend integration via well-defined API contract.
- 🧪 Tests: Plan structure validation (all 10 required sections present), technical decision documentation review (passed)
- 📁 Files: Created plan.md (comprehensive 10-section architecture document)
- 🔁 Next prompts: `/sp.tasks` to generate actionable task breakdown, or begin implementation with Phase 1 (Foundation setup)
- 🧠 Reflection: Plan balances architectural rigor with implementation pragmatism. Anonymous session handling is elegant (skip DB writes). Qdrant metadata design supports both query modes. Async patterns throughout ensure performance. Missing: specific error status codes for API (can be added during implementation), ADR candidates (Qdrant schema, session persistence strategy, chunking algorithm).

## Evaluation notes (flywheel)

- Failure modes observed: None. Plan generated successfully without blockers.
- Graders run and results (PASS/FAIL): Structure validation PASSED (all 10 sections present), Technical completeness PASSED (schemas, dependencies, error handling documented)
- Prompt variant (if applicable): N/A - standard /sp.plan workflow
- Next experiment (smallest change to try): N/A - successful on first attempt
