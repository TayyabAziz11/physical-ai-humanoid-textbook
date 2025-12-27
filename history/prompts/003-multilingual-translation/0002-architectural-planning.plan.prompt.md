---
id: 0002
title: "Architectural Planning for Multilingual Translation"
stage: plan
date: 2025-12-25
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-multilingual-translation
branch: 003-multilingual-translation
user: user
command: /sp.plan
labels: ["architecture", "adr", "planning", "translation", "openai", "fastapi", "react"]
links:
  spec: specs/003-multilingual-translation/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-multilingual-translation/plan.md
tests:
  - Architectural decision validation
  - Cost model verification
  - Performance budget analysis
---

## Prompt

```text
Architectural planning for Feature 003: Multilingual Translation

Context:
The multilingual translation specification is finalized at:
- specs/003-multilingual-translation/spec.md
- PHR documented in history/prompts/003-multilingual-translation/

System context:
- FastAPI backend
- OpenAI Agents / Chatkit SDK
- Existing RAG pipeline (Qdrant + Neon Postgres)
- Docusaurus (React) frontend
- GitHub Pages deployment

Objectives:
Produce an implementation-ready architectural plan that resolves all open technical decisions.

Required outputs:
1. High-level system architecture (textual diagram)
   - Translation flow for:
     a) User-selected text
     b) Full chatbot response
   - Interaction with existing RAG pipeline

2. Architectural Decision Records (ADRs) for:
   - Model selection:
     - GPT-4 vs GPT-4o-mini (or equivalent)
     - Trade-offs: cost, latency, translation fidelity
   - Caching strategy:
     - Client-side vs server-side
     - Cache keys, TTL, invalidation
   - RTL support strategy:
     - CSS approach (logical properties vs separate RTL stylesheets)
     - Runtime direction switching
   - Error-handling strategy for partial translations and API failures

3. Backend architecture:
   - FastAPI router structure
   - TranslationService lifecycle
   - OpenAI client configuration
   - Rate limiting and cost guards

4. Frontend architecture:
   - React component boundaries
   - Language selector state management
   - Text-selection capture mechanism
   - RTL layout switching strategy

5. Non-functional considerations:
   - Performance targets (<2s translation latency)
   - Security and prompt-injection mitigation
   - Observability (logging, metrics)

Constraints:
- Must align strictly with the approved specification
- No scope expansion beyond Feature 003
- Keep architecture simple, testable, and production-oriented

Deliverable:
A clear architectural plan suitable for immediate task breakdown and implementation.
```

## Response snapshot

### Comprehensive Architectural Plan Created

**File**: `specs/003-multilingual-translation/plan.md`

**Plan Contents** (12 main sections, 400+ lines):

#### 1. Executive Summary
- Architectural vision: Stateless, API-driven translation layer
- Key principles: Simplicity, performance, cost efficiency, maintainability
- Technology stack: FastAPI + AsyncOpenAI + React + TypeScript

#### 2. High-Level System Architecture
- **Component diagram** showing translation flow (textual ASCII)
- **Integration with RAG pipeline**: Translation is decoupled post-processing step
- **Request/response flows**:
  - Flow A: Text selection translation (9-step sequence)
  - Flow B: Chatbot response translation (9-step sequence)

#### 3. Architectural Decision Records (ADRs)

**ADR-001: Model Selection Strategy**
- **Decision**: Use GPT-4o-mini as default model
- **Rationale**: 16x cheaper than GPT-4o, sufficient quality for technical content
- **Cost**: $0.00018 per translation (200 input + 250 output tokens)
- **Performance**: 500-1500ms typical latency
- **Future**: Optional GPT-4o upgrade path via request parameter

**ADR-002: Caching Strategy**
- **Decision**: Client-side caching only using localStorage
- **Rationale**: Zero infrastructure cost, privacy, simplicity
- **Cache structure**: Hash-based keys, 7-day TTL, max 50 entries/language (LRU eviction)
- **Why not server-side**: Complexity, cost, diminishing returns

**ADR-003: RTL Language Support**
- **Decision**: CSS Logical Properties with runtime `dir` attribute
- **Rationale**: Modern standard, automatic layout mirroring, future-proof
- **Implementation**: Replace physical properties (`left`/`right`) with logical (`inline-start`/`inline-end`)
- **RTL languages**: Arabic, Urdu

**ADR-004: Error Handling Strategy**
- **Decision**: Tiered error handling with exponential backoff retry
- **Retryable errors**: 429 (rate limit), 500-series (server errors), timeouts
- **Non-retryable errors**: 401 (auth), 400 (invalid request), 413 (payload too large)
- **Retry logic**: 3 attempts, exponential backoff (1s, 2s, 4s delays)
- **User-facing**: Friendly error messages, fallback to original English text

#### 4. Backend Architecture
- **Router structure**: New `app/api/v1/endpoints/translate.py` with 2 endpoints
- **Translation service**: `app/services/translation.py` with retry logic
- **Data models**: Pydantic request/response models with strict validation
- **Rate limiting**: In-memory middleware (10 req/min/IP)

**Key code patterns**:
```python
# Translation service with retry
async def translate_with_retry(self, text, system_prompt):
    for attempt in range(MAX_RETRIES):
        try:
            return await self.client.chat.completions.create(...)
        except RateLimitError:
            delay = BASE_DELAY * (2 ** attempt)
            await asyncio.sleep(delay)
```

#### 5. Frontend Architecture
- **Component structure**: 7 new components (LanguageSelector, TranslationDisplay, etc.)
- **Hooks**: `useTranslation` (API calls), `useTranslationCache` (localStorage)
- **API client**: `translationApi.ts` for backend communication
- **RTL utilities**: `isRTL()` helper, CSS logical properties

**Key component patterns**:
```tsx
// Language selector with native names
const SUPPORTED_LANGUAGES = [
  { code: 'urdu', name: 'Urdu', nativeName: 'اردو', rtl: true },
  { code: 'arabic', name: 'Arabic', nativeName: 'العربية', rtl: true },
  // ...
];
```

#### 6. Data Flow Diagrams
- Detailed 9-step sequences for both translation flows
- Shows interaction between frontend, backend, and OpenAI API
- Includes caching, rate limiting, and error handling steps

#### 7. Non-Functional Considerations

**Performance**:
- Target: <2s translation latency (p95)
- Budget breakdown: 1725ms total (within target)
- Optimizations: GPT-4o-mini, client cache, concurrent requests

**Security**:
- Prompt injection mitigation (explicit system prompts)
- Rate limiting (10 req/min/IP)
- API key protection (server-side only)
- XSS protection (React auto-escaping)

**Observability**:
- Logging strategy (request, API calls, errors)
- Metrics to track (latency, cost, error rate, cache hits)
- Railway monitoring (CPU, memory, logs)

**Cost Management**:
- Per-translation cost: $0.00018
- Monthly projections: $0.09-$1.80 (500-10K translations)
- Cost controls: Rate limiting, max text length, caching

#### 8. Implementation Sequence
- **Phase 1**: Backend foundation (Week 1)
- **Phase 2**: Frontend components (Week 2)
- **Phase 3**: Chatbot integration & polish (Week 3)
- **Phase 4**: Deployment & monitoring (Week 4)

Each phase includes detailed tasks and acceptance criteria.

#### 9. Testing Strategy
- **Unit tests**: Translation service, retry logic, cache management
- **Integration tests**: API endpoints, rate limiting
- **Component tests**: React components with RTL rendering
- **E2E tests**: Full user workflows (Playwright)

**Test coverage goals**:
- Backend: >80% code coverage
- Frontend: >75% component coverage
- E2E: All critical user paths

#### 10. Deployment & Rollout
- **Railway deployment**: Auto-deploy on push, no new env vars needed
- **GitHub Pages**: Standard Docusaurus build/deploy
- **Rollout plan**: Internal → Beta (10-20 users) → Gradual (10%→50%→100%) → Full launch
- **Rollback plan**: Trigger conditions, revert procedures

#### 11. Risk Assessment & Mitigation
**8 identified risks**:
1. OpenAI API latency spikes (Medium likelihood, High impact)
2. Translation quality issues (Medium/Medium)
3. Cost overrun (Low/Medium)
4. RTL rendering bugs (Medium/Low)
5. Low adoption (Medium/Medium)
6. Security vulnerability (Low/Low)
7. Railway deployment failure (Low/High)
8. OpenAI API outage (Low/High)

Each risk includes likelihood, impact, and detailed mitigation strategies.

#### 12. Summary & Next Steps
- Architecture is production-ready
- All 4 ADRs documented inline
- Next step: Run `/sp.tasks` to generate implementation tasks
- Success criteria defined for launch

**Appendices**:
- Appendix A: Decision matrix (comparison table)
- Appendix B: API contract summary (full request/response schemas)

## Outcome

- ✅ Impact: Created production-ready architectural plan with 4 comprehensive ADRs, detailed backend/frontend architecture, performance budgets, cost models, and risk mitigation strategies. Plan resolves all open technical decisions and is ready for task breakdown.
- 🧪 Tests: Plan includes complete testing strategy (unit, integration, component, E2E) with specific test cases for retry logic, rate limiting, RTL rendering, and cache management. Test coverage goals defined (>80% backend, >75% frontend).
- 📁 Files: Created specs/003-multilingual-translation/plan.md (400+ lines, 12 sections)
- 🔁 Next prompts: Run /sp.tasks to break down plan into implementation tasks, then create ADR documents in history/adr/ for the 4 key architectural decisions
- 🧠 Reflection: This plan took a comprehensive approach to architecture, embedding ADRs directly in the plan document rather than creating separate ADR files. This works well for tightly coupled decisions (all 4 ADRs relate to the same feature). For cross-cutting decisions that affect multiple features, separate ADR files would be better. The plan is detailed enough for immediate implementation but maintains flexibility for iteration.

## Evaluation notes (flywheel)

- Failure modes observed: None during planning. Potential implementation risks identified: OpenAI API latency variability (mitigated with retry logic + cache), RTL CSS edge cases (mitigated with E2E tests), cost overruns (mitigated with rate limiting). All risks have documented mitigation strategies.
- Graders run and results (PASS/FAIL): PASS - All required outputs delivered (system architecture, 4 ADRs, backend/frontend architecture, NFRs, implementation sequence). Plan aligns with spec, makes clear technical decisions, and provides sufficient detail for task breakdown.
- Prompt variant (if applicable): N/A - Standard /sp.plan workflow
- Next experiment (smallest change to try): During /sp.tasks phase, experiment with task granularity - break backend Phase 1 into smaller tasks (1-2 hours each) vs. larger tasks (half-day each) and compare developer velocity. Hypothesis: Smaller tasks provide better progress tracking but may increase context-switching overhead.
