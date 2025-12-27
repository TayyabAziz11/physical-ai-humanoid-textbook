---
id: 0003
title: "Implementation Task Breakdown for Multilingual Translation"
stage: tasks
date: 2025-12-25
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-multilingual-translation
branch: 003-multilingual-translation
user: user
command: /sp.tasks
labels: ["tasks", "implementation", "tdd", "red-green-refactor", "backend", "frontend"]
links:
  spec: specs/003-multilingual-translation/spec.md
  ticket: null
  adr: specs/003-multilingual-translation/plan.md#3-architectural-decision-records-adrs
  pr: null
files:
  - specs/003-multilingual-translation/tasks.md
tests:
  - Task dependency validation
  - Critical path analysis
  - Coverage goal verification
---

## Prompt

```text
Generate an implementation task breakdown for Feature 003: Multilingual Translation.

Context:
- Specification completed: specs/003-multilingual-translation/spec.md
- Architectural plan finalized: specs/003-multilingual-translation/plan.md
- ADRs approved:
  - GPT-4o-mini default model
  - Client-side caching only (localStorage)
  - CSS logical properties for RTL
  - Exponential backoff retry strategy

System stack:
- FastAPI backend
- OpenAI API
- Existing RAG pipeline (Qdrant + Neon Postgres)
- Docusaurus (React) frontend
- GitHub Pages deployment

Objectives:
Break the approved architecture into small, testable, implementation-ready tasks suitable for red–green–refactor development.

Task organization:
1. Backend – Foundation
   - Translation router setup
   - Pydantic request/response models
   - Language validation (Literal types)
   - Rate limiting middleware

2. Backend – Translation Service
   - OpenAI client configuration
   - Prompt templates for translation
   - Retry logic with exponential backoff
   - Error handling and fallback responses

3. Frontend – Core UI
   - LanguageSelector component
   - TranslationDisplay component
   - Loading/error states
   - API client utilities

4. Frontend – Text Selection & RTL
   - Text selection capture logic
   - Selected-text translation flow
   - RTL direction switching (dir="rtl")
   - CSS logical property validation

5. Integration
   - Chatbot response translation
   - Selected-text-only translation path
   - Cache hit/miss behavior validation

6. Caching
   - useTranslationCache hook
   - TTL handling (7 days)
   - LRU eviction logic
   - Cache key normalization

7. Testing
   - Backend unit tests
   - Frontend unit tests
   - Integration tests (API ↔ OpenAI)
   - RTL manual verification checklist

8. Documentation
   - Developer README updates
   - API usage examples
   - Docusaurus user guide section

For each task, include:
- Task title
- Description
- Expected output
- Validation / test criteria
- Dependencies (if any)

Constraints:
- Must strictly follow the approved specification and architectural plan
- No new infrastructure or scope expansion
- Tasks should be independently completable and reviewable

Output format:
Checklist-style, phase-grouped tasks suitable for direct execution.
```

## Response snapshot

### Comprehensive Task Breakdown Created

**File**: `specs/003-multilingual-translation/tasks.md`

**Total**: 52 tasks organized across 8 phases (4 weeks estimated)

#### Task Organization

**Phase 1: Backend Foundation** (9 tasks, 3-4 days)
- Define SupportedLanguage Literal type
- Create Pydantic request/response models (3 models)
- Create TranslationError exception class
- Implement rate limiting middleware (10 req/min/IP)
- Create translation router stubs
- Register router in API v1
- Write unit tests for models

**Phase 2: Backend Translation Service** (10 tasks, 4-5 days)
- Initialize TranslationService class with OpenAI client
- Implement system prompt builder (technical term preservation)
- Implement OpenAI API call method
- Implement exponential backoff retry (1s, 2s, 4s delays)
- Implement translate_text and translate_response methods
- Wire up endpoints to service
- Write comprehensive unit and integration tests

**Phase 3: Frontend Core UI** (7 tasks, 3-4 days)
- Define TypeScript language types and constants
- Create LanguageSelector component (dropdown with native names)
- Create TranslationDisplay component (modal with RTL support)
- Create translation API client
- Create language utilities (isRTL, getLanguageName)
- Create loading/error state components
- Write component unit tests (>75% coverage)

**Phase 4: Frontend Hooks & Caching** (4 tasks, 2-3 days)
- Create cache utilities (hashString, isValidCacheEntry)
- Create useTranslationCache hook (7-day TTL, LRU eviction, 50 entries/language)
- Create useTranslation hook (orchestrates API + cache)
- Write hook unit tests (>80% coverage)

**Phase 5: Frontend Text Selection & RTL** (5 tasks, 3-4 days)
- Create TextSelectionToolbar component (window.getSelection())
- Integrate toolbar with Docusaurus layout
- Add RTL CSS logical properties (convert physical to logical)
- Implement runtime direction switching (dir="rtl")
- Manual RTL verification checklist

**Phase 6: Chatbot Integration** (3 tasks, 2 days)
- Create TranslateButton component for chat messages
- Integrate button with chat UI
- E2E test for chatbot response translation

**Phase 7: Integration Testing** (5 tasks, 2-3 days)
- E2E test: Text selection translation
- E2E test: Cache behavior (instant results on cache hit)
- E2E test: RTL rendering (dir attribute validation)
- E2E test: Error handling (network failure, rate limit)
- Backend integration test: Full translation flow

**Phase 8: Documentation & Deployment** (8 tasks, 3-4 days)
- Update backend README (API docs, rate limits, examples)
- Create user documentation (Docusaurus guide)
- Create developer setup guide
- Deploy backend to Railway
- Deploy frontend to GitHub Pages
- Production smoke tests (all 6 languages, RTL, cache, errors)
- Monitor production metrics (week 1)
- Post-launch retrospective

#### Task Structure (Example)

Each task includes:
```markdown
### Task X.Y: [Title]

**Description**: Clear, actionable description

**Expected Output**:
- File: path/to/file.py
- Component/Class/Function name
- Key features/fields

**Validation Criteria**:
```python
# Concrete test examples showing how to verify completion
assert expected_behavior()
```

**Dependencies**: Task X.Y (if any)

**File Location**: path/to/implementation
```

#### Critical Path Identified

1. Task 1.1 → 1.2 → 1.3 → 1.7 → 1.8 (Router setup)
2. Task 2.1 → 2.2 → 2.3 → 2.4 → 2.5 → 2.8 (Translation service → endpoint)
3. Task 3.1 → 3.2 → 3.3 (Core UI components)
4. Task 4.1 → 4.2 → 4.3 (Translation hooks)
5. Task 5.1 → 5.2 (Text selection integration)
6. Task 6.1 → 6.2 (Chatbot integration)

#### Testing Coverage Goals

- Backend unit tests: >80% code coverage
- Backend integration tests: All endpoints covered
- Frontend component tests: >75% coverage
- Frontend hooks: >80% coverage
- E2E tests: All critical user paths
- Manual RTL verification: Checklist completed

#### Launch Acceptance Criteria

- ✅ All 6 languages translate correctly
- ✅ RTL rendering works for Arabic and Urdu
- ✅ Translation latency <2s (p95)
- ✅ Error rate <5%
- ✅ Cost <$5/month
- ✅ All tests passing (unit, integration, E2E)
- ✅ Production smoke tests complete
- ✅ Documentation complete (user + developer)

#### Task Statistics

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Phase 1: Backend Foundation | 9 | 3-4 days |
| Phase 2: Backend Translation Service | 10 | 4-5 days |
| Phase 3: Frontend Core UI | 7 | 3-4 days |
| Phase 4: Frontend Hooks & Caching | 4 | 2-3 days |
| Phase 5: Frontend Text Selection & RTL | 5 | 3-4 days |
| Phase 6: Chatbot Integration | 3 | 2 days |
| Phase 7: Integration Testing | 5 | 2-3 days |
| Phase 8: Documentation & Deployment | 8 | 3-4 days |
| **Total** | **52 tasks** | **~4 weeks** |

## Outcome

- ✅ Impact: Created comprehensive task breakdown with 52 testable, actionable tasks organized into 8 phases. Each task includes description, expected output, validation criteria, dependencies, and file locations. Tasks follow TDD red-green-refactor approach and are sized for 1-4 hour completion windows.
- 🧪 Tests: Defined testing strategy with specific coverage goals (>80% backend, >75% frontend components, >80% hooks). Created 7 E2E test tasks, 5 integration test tasks, and comprehensive unit test tasks for all components. Manual RTL verification checklist included.
- 📁 Files: Created specs/003-multilingual-translation/tasks.md (52 tasks across 400+ lines)
- 🔁 Next prompts: Begin Phase 1 implementation with Task 1.1 (Define SupportedLanguage Type), follow red-green-refactor TDD workflow, create PRs after each phase for review
- 🧠 Reflection: Task breakdown strikes good balance between granularity (52 tasks) and scope (4 weeks). Each task is independently testable with concrete validation criteria. Critical path identified helps with dependency management. Including both automated tests and manual verification checklists ensures quality. Phase-based organization aligns with plan document and facilitates incremental delivery.

## Evaluation notes (flywheel)

- Failure modes observed: None during task generation. Potential implementation risks: Task estimation may be optimistic (4 weeks assumes full-time dedicated work), dependencies between frontend/backend may cause blocking, E2E tests may be flaky initially (typical Playwright issue). Mitigations: Build backend first to unblock frontend, use strict typing to catch integration issues early, allocate buffer time for E2E test stabilization.
- Graders run and results (PASS/FAIL): PASS - All required task categories covered (backend foundation, translation service, frontend UI, caching, RTL, chatbot integration, testing, documentation). Tasks are actionable with clear validation criteria. Dependencies properly identified. Coverage goals specified. Launch acceptance criteria defined.
- Prompt variant (if applicable): N/A - Standard /sp.tasks workflow
- Next experiment (smallest change to try): During implementation, track actual time per task vs. estimate. Hypothesis: Smaller tasks (1-2 hours) will have more accurate estimates than larger tasks (half-day). Use this data to refine estimation model for future features. Consider using Fibonacci sizing (1, 2, 3, 5, 8 hours) instead of ranges (2-3 hours) for clearer prioritization.
