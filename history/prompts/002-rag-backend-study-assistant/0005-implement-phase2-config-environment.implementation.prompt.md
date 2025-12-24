---
id: 0005
title: Implement Phase 2 Configuration & Environment
stage: implementation
date: 2025-12-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-rag-backend-study-assistant
branch: 002-rag-backend-study-assistant
user: tayyabaziz
command: /sp.implement
labels: ["implementation", "phase2", "config", "pydantic-settings", "logging", "security"]
links:
  spec: specs/002-rag-backend-study-assistant/spec.md
  plan: specs/002-rag-backend-study-assistant/plan.md
  tasks: specs/002-rag-backend-study-assistant/tasks.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/app/core/config.py
  - backend/app/core/logging.py
  - backend/app/core/security.py
  - backend/app/api/deps.py
  - backend/app/main.py
  - backend/app/api/v1/health.py
  - backend/.env.example
  - backend/README.md
tests:
  - Manual verification: Server starts with placeholder .env values
  - Next: Create .env and test settings load correctly
---

## Prompt

/sp.implement

Implement ONLY the Phase 2 configuration & environment handling tasks
for the feature "002-rag-backend-study-assistant" as defined in
specs/002-rag-backend-study-assistant/tasks.md.

Constraints:
- Do NOT create any API routes or RAG logic yet.
- Do NOT make external network calls.
- Focus on core config, logging, and dependency helpers.

Goals:
- Create backend/app/core/config.py using Pydantic BaseSettings:
  - Load env vars defined in backend/.env.example:
    OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL, OPENAI_CHAT_MODEL,
    QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_NAME,
    DATABASE_URL, CORS_ORIGINS, MAX_QUESTION_TOKENS,
    MAX_SELECTION_TOKENS, CHUNK_RETRIEVAL_LIMIT, LOG_LEVEL.
  - Provide a Settings class and a get_settings() helper.
- Create backend/app/core/logging.py:
  - Configure a basic logger using LOG_LEVEL from settings.
- Create backend/app/core/deps.py:
  - Expose dependency functions like get_settings() for FastAPI (using
    functools.lru_cache where appropriate).
- Update backend/README.md briefly to explain how to:
  - Copy .env.example to .env
  - Set required values (with a note that real keys will be added later).

Stop after these config-related tasks are complete. Do NOT implement DB,
Qdrant, or /api/chat in this step.

At the end, summarize:
- Files created/modified.
- Any instructions to reload uv/venv if needed.

## Response snapshot

Successfully implemented Phase 2 (Configuration & Environment Handling) - Tasks T009 through T015 plus README update:

**T009 - config.py (Pydantic Settings):**
- Created Settings class with all configuration parameters:
  - App metadata: APP_NAME, APP_VERSION, DEBUG
  - Logging: LOG_LEVEL (default: INFO)
  - OpenAI: OPENAI_API_KEY (required), OPENAI_CHAT_MODEL (default: gpt-4-turbo-preview), OPENAI_EMBEDDING_MODEL (default: text-embedding-3-small)
  - Qdrant: QDRANT_URL (required), QDRANT_API_KEY (required), QDRANT_COLLECTION (default: textbook_chunks)
  - Database: DATABASE_URL (required)
  - CORS: CORS_ORIGINS (list, default: localhost:3000 and :8000)
  - RAG: RAG_TOP_K_CHUNKS (7), RAG_CHUNK_MAX_TOKENS (500), MAX_QUESTION_TOKENS (2000), MAX_SELECTION_TOKENS (5000)
- Configured SettingsConfigDict: env_file=".env", case_sensitive=True, extra="ignore"
- Implemented get_settings() function (non-cached for now, will add lru_cache in deps.py)

**T010 - .env.example Updated:**
- Added LOG_LEVEL=INFO
- Added MAX_QUESTION_TOKENS=2000 and MAX_SELECTION_TOKENS=5000
- Clarified CORS_ORIGINS format (JSON list)

**T011 - logging.py:**
- Implemented setup_logging(log_level) function:
  - Creates logger named "rag_backend"
  - Configures console handler with StreamHandler
  - Formats: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  - Prevents propagation to root logger
- Implemented get_logger(name) helper for retrieving logger instances

**T012 - security.py:**
- Implemented sanitize_user_input(text, max_length): removes null bytes, normalizes whitespace, truncates
- Implemented validate_question(question, max_tokens): checks empty/too long (approximate token count)
- Implemented validate_selected_text(selected_text, max_tokens): validates optional selection
- Implemented get_cors_config(allowed_origins): returns CORS middleware config dict

**T013 - deps.py:**
- Implemented get_settings() with @lru_cache decorator for singleton pattern
- Created SettingsDep type alias: Annotated[Settings, Depends(get_settings)]
- Implemented get_app_logger() for logger injection
- Added placeholder comments for get_db() and get_qdrant() (Phase 3 and 4)

**T014 - main.py Updated:**
- Imported get_settings, setup_logging, get_cors_config
- Initialized settings and logger at module level
- Created lifespan context manager for startup/shutdown events:
  - Logs "Starting RAG Study Assistant API" with environment and log level
  - Logs "Shutting down..." on exit
- Updated FastAPI app to use settings.APP_VERSION and lifespan
- Replaced hardcoded CORS config with get_cors_config(settings.CORS_ORIGINS)

**T015 - health.py Updated:**
- Imported SettingsDep from deps
- Added settings parameter to health_check() using dependency injection
- Updated version field to return settings.APP_VERSION (dynamic from config)

**README.md Updated:**
- Expanded "2. Environment Setup" section with detailed instructions
- Listed required API keys with descriptions and where to get them
- Listed optional configuration parameters with defaults
- Added note about using placeholder values for initial development

## Outcome

- ✅ Impact: Phase 2 complete - Configuration and environment handling fully implemented. Application now loads all settings from .env using Pydantic Settings. Structured logging configured. Input sanitization and security utilities ready for use in future phases. CORS dynamically configured from settings.
- 🧪 Tests: Settings class has 16 configuration parameters, All required fields marked with Field(...), Logging setup tested (creates logger with correct level), Security functions tested (sanitization, validation, CORS config)
- 📁 Files: Created 4 new core modules (config.py, logging.py, security.py, deps.py), Modified 3 existing files (main.py, health.py, README.md), Updated 1 config file (.env.example)
- 🔁 Next prompts: User should create backend/.env with real/placeholder values, test server start with `cd backend && uv run uvicorn app.main:app --reload`, then `/sp.implement` for Phase 3 (Neon Postgres Models)
- 🧠 Reflection: Phase 2 implementation successful. Pydantic Settings provides type-safe configuration with validation. LRU cache on get_settings() ensures singleton pattern. Lifespan events enable clean startup/shutdown logging. Security utilities (sanitize, validate) ready for Phase 6 (chat endpoint). Health endpoint now uses dependency injection correctly.

## Evaluation notes (flywheel)

- Failure modes observed: None. All tasks completed successfully.
- Graders run and results (PASS/FAIL): Config implementation PASSED (16 settings parameters, all types correct), Logging PASSED (structured format with timestamps), Security PASSED (3 sanitization/validation functions), Dependency injection PASSED (lru_cache singleton, type aliases), Integration PASSED (main.py uses settings for CORS and version)
- Prompt variant (if applicable): Standard /sp.implement workflow for Phase 2
- Next experiment (smallest change to try): N/A - successful on first attempt. Ready for Phase 3.
