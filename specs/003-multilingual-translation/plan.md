# Architectural Plan: Multilingual Translation Feature

**Feature ID**: 003
**Feature Name**: Multilingual Translation
**Status**: Ready for Implementation
**Created**: 2025-12-25
**Planning Phase**: Architecture Design
**Related Spec**: `specs/003-multilingual-translation/spec.md`

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [High-Level System Architecture](#2-high-level-system-architecture)
3. [Architectural Decision Records (ADRs)](#3-architectural-decision-records-adrs)
4. [Backend Architecture](#4-backend-architecture)
5. [Frontend Architecture](#5-frontend-architecture)
6. [Data Flow Diagrams](#6-data-flow-diagrams)
7. [Non-Functional Considerations](#7-non-functional-considerations)
8. [Implementation Sequence](#8-implementation-sequence)
9. [Testing Strategy](#9-testing-strategy)
10. [Deployment & Rollout](#10-deployment--rollout)
11. [Risk Assessment & Mitigation](#11-risk-assessment--mitigation)

---

## 1. Executive Summary

### 1.1 Architectural Vision

Build a **stateless, API-driven multilingual translation layer** that integrates seamlessly with the existing RAG pipeline. The architecture prioritizes:

- **Simplicity**: No new databases, caching infrastructure, or external services
- **Performance**: <2 second translation latency using OpenAI API
- **Cost Efficiency**: Smart model selection (GPT-4o-mini for most, GPT-4o for critical)
- **Maintainability**: Clean separation of concerns, testable components

### 1.2 Key Architectural Principles

1. **Stateless Translation**: No server-side translation storage/caching (client-side only)
2. **Single Responsibility**: Translation service does ONLY translation, no RAG coupling
3. **Fail-Safe Degradation**: Translation failures don't break core RAG functionality
4. **Openness to Extension**: Easy to add new languages without architecture changes

### 1.3 Technology Stack

**Backend**:
- FastAPI (existing framework)
- AsyncOpenAI client (for translation API calls)
- Pydantic v2 (request/response validation)
- No new dependencies beyond OpenAI SDK (already installed)

**Frontend**:
- React 18 (Docusaurus default)
- TypeScript (type-safe language handling)
- CSS Logical Properties (RTL support)
- localStorage (client-side translation cache)

**Infrastructure**:
- Railway (backend hosting - existing)
- GitHub Pages (frontend - existing)
- OpenAI API (GPT-4o-mini + GPT-4o)

---

## 2. High-Level System Architecture

### 2.1 Component Diagram (Textual)

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Docusaurus/React)                  │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │ Language Selector │  │ Text Selection   │  │ Translation  │ │
│  │ Component         │  │ Toolbar          │  │ Display      │ │
│  └────────┬─────────┘  └────────┬─────────┘  └──────▲───────┘ │
│           │                     │                    │         │
│           └──────────┬──────────┘                    │         │
│                      │                               │         │
│              ┌───────▼────────┐                      │         │
│              │ Translation    │                      │         │
│              │ State Manager  │                      │         │
│              └───────┬────────┘                      │         │
│                      │                               │         │
│              ┌───────▼────────┐                      │         │
│              │ localStorage   │──────────────────────┘         │
│              │ Cache          │                                │
│              └────────────────┘                                │
└──────────────────────┬──────────────────────────────────────────┘
                       │ HTTP/JSON
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│                  BACKEND (FastAPI on Railway)                   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              API v1 Router (/api/v1)                     │  │
│  │                                                          │  │
│  │  ┌─────────────────┐    ┌──────────────────┐           │  │
│  │  │ /translate/text │    │ /translate/      │           │  │
│  │  │                 │    │ response         │           │  │
│  │  └────────┬────────┘    └────────┬─────────┘           │  │
│  └───────────┼──────────────────────┼──────────────────────┘  │
│              │                      │                          │
│      ┌───────▼──────────────────────▼────────┐                │
│      │    Translation Service                │                │
│      │  - Model selection logic               │                │
│      │  - System prompt builder               │                │
│      │  - Token counting                      │                │
│      │  - Technical term preservation         │                │
│      └───────┬──────────────────┬─────────────┘                │
│              │                  │                              │
│      ┌───────▼────────┐  ┌──────▼──────────┐                  │
│      │ Rate Limiter   │  │ Error Handler   │                  │
│      │ Middleware     │  │ (Retry logic)   │                  │
│      └───────┬────────┘  └──────┬──────────┘                  │
│              └──────────┬────────┘                             │
└─────────────────────────┼──────────────────────────────────────┘
                          │ OpenAI API
                          │
                ┌─────────▼────────────┐
                │   OpenAI Platform    │
                │  - GPT-4o-mini       │
                │  - GPT-4o            │
                └──────────────────────┘
```

### 2.2 Integration with Existing RAG Pipeline

**CRITICAL**: Translation service is **decoupled** from RAG pipeline.

```
User Query Flow (Existing RAG):
1. User asks question → /api/v1/query/global
2. Retriever fetches chunks from Qdrant
3. Responder generates answer using OpenAI
4. Response returned to frontend

Translation Flow (New):
5. User clicks "Translate" button
6. Frontend calls /api/v1/translate/response
7. Translation service translates response using OpenAI
8. Translated response returned to frontend
9. Frontend displays both original + translation
```

**Key Principle**: RAG pipeline continues to work in English. Translation is a **post-processing step** applied to RAG outputs.

### 2.3 Request/Response Flow

#### Flow A: Text Selection Translation

```
┌──────────┐                  ┌──────────┐                 ┌──────────┐
│ Frontend │                  │ Backend  │                 │ OpenAI   │
└─────┬────┘                  └────┬─────┘                 └────┬─────┘
      │                            │                            │
      │ 1. User selects text       │                            │
      │    on Docusaurus page      │                            │
      │                            │                            │
      │ 2. POST /api/v1/translate/text                          │
      │    { text, target_language,│                            │
      │      preserve_technical_terms }                         │
      ├───────────────────────────>│                            │
      │                            │                            │
      │                            │ 3. Validate request        │
      │                            │    (Pydantic models)       │
      │                            │                            │
      │                            │ 4. Check rate limits       │
      │                            │    (10 req/min/user)       │
      │                            │                            │
      │                            │ 5. Build system prompt     │
      │                            │    (preserve tech terms)   │
      │                            │                            │
      │                            │ 6. POST /v1/chat/completions
      │                            │    { model: gpt-4o-mini,   │
      │                            │      messages: [...],      │
      │                            │      temperature: 0.3 }    │
      │                            ├───────────────────────────>│
      │                            │                            │
      │                            │ 7. Translated text         │
      │                            │<───────────────────────────┤
      │                            │                            │
      │ 8. { translated_text,      │                            │
      │      model_used,           │                            │
      │      tokens_used,          │                            │
      │      processing_time_ms }  │                            │
      │<───────────────────────────┤                            │
      │                            │                            │
      │ 9. Display translation     │                            │
      │    in modal/panel          │                            │
      │                            │                            │
```

#### Flow B: Chatbot Response Translation

```
┌──────────┐                  ┌──────────┐                 ┌──────────┐
│ Frontend │                  │ Backend  │                 │ OpenAI   │
└─────┬────┘                  └────┬─────┘                 └────┬─────┘
      │                            │                            │
      │ 1. RAG query completes     │                            │
      │    (answer + citations     │                            │
      │     already generated)     │                            │
      │                            │                            │
      │ 2. POST /api/v1/translate/response                      │
      │    { original_response: {  │                            │
      │        answer, citations   │                            │
      │      },                    │                            │
      │      target_language }     │                            │
      ├───────────────────────────>│                            │
      │                            │                            │
      │                            │ 3. Extract answer text     │
      │                            │    from response object    │
      │                            │                            │
      │                            │ 4. Translate answer only   │
      │                            │    (keep citations in EN)  │
      │                            │                            │
      │                            │ 5. POST /v1/chat/completions
      │                            ├───────────────────────────>│
      │                            │                            │
      │                            │ 6. Translated answer       │
      │                            │<───────────────────────────┤
      │                            │                            │
      │                            │ 7. Reconstruct response    │
      │                            │    { answer: translated,   │
      │                            │      citations: original } │
      │                            │                            │
      │ 8. { translated_response,  │                            │
      │      target_language,      │                            │
      │      model_used,           │                            │
      │      tokens_used }         │                            │
      │<───────────────────────────┤                            │
      │                            │                            │
      │ 9. Display both original   │                            │
      │    and translated versions │                            │
      │                            │                            │
```

---

## 3. Architectural Decision Records (ADRs)

### ADR-001: Model Selection Strategy

**Status**: Accepted
**Date**: 2025-12-25
**Deciders**: Development Team
**Related**: NFR-2 (Cost Optimization), NFR-4 (Accuracy)

#### Context

We need to select OpenAI model(s) for translation. Options considered:

1. **GPT-4o** (expensive, highest quality)
2. **GPT-4o-mini** (cheap, good quality)
3. **GPT-3.5-turbo** (cheapest, lower quality)
4. **Hybrid approach** (different models for different use cases)

**Cost Comparison** (as of Dec 2024):
- GPT-4o: $2.50/M input tokens, $10.00/M output tokens
- GPT-4o-mini: $0.150/M input tokens, $0.600/M output tokens
- GPT-3.5-turbo: $0.50/M input tokens, $1.50/M output tokens

**Quality Considerations**:
- Technical content requires accurate translation of domain-specific terms
- Robotics/AI terminology must be preserved correctly
- Some languages (Arabic, Mandarin) are harder than others

#### Decision

**Use GPT-4o-mini as default model** with the following rationale:

1. **Cost-Effective**: 16x cheaper than GPT-4o for output tokens
2. **Sufficient Quality**: GPT-4o-mini handles technical translation well for most use cases
3. **Fast**: Lower latency than GPT-4o (important for <2s target)
4. **Scalable**: Can handle high volume without budget concerns

**Optional GPT-4o upgrade path** (future enhancement):
- Add `model` parameter to translation request
- Allow frontend to request GPT-4o for critical/complex translations
- Frontend shows model selector (mini vs. full) for power users

#### Consequences

**Positive**:
- Low operating cost ($5-20/month estimated for 1000-2000 translations)
- Fast translation responses (<1.5s typical)
- Sustainable at scale

**Negative**:
- Slightly lower quality than GPT-4o (acceptable trade-off)
- May need GPT-4o fallback for complex technical passages (future work)

**Risks**:
- If translation quality is insufficient, need to upgrade to GPT-4o (cost increase)
- Mitigation: Monitor user feedback, add model selection if needed

---

### ADR-002: Caching Strategy

**Status**: Accepted
**Date**: 2025-12-25
**Deciders**: Development Team
**Related**: NFR-1 (Performance), NFR-2 (Cost Optimization)

#### Context

Translation API calls are expensive and slow. Caching can improve performance and reduce costs. Options:

1. **No caching** - Every translation is a fresh API call
2. **Client-side caching** (localStorage/sessionStorage)
3. **Server-side caching** (Redis/in-memory)
4. **Hybrid** (client + server caching)

**Evaluation Criteria**:
- Implementation complexity
- Cost savings
- Performance improvement
- Data privacy (translations contain book content)

#### Decision

**Client-side caching only using localStorage**

**Cache Key Format**:
```typescript
const cacheKey = `translation:${hashString(text)}:${targetLanguage}`;
```

**Cache Structure**:
```typescript
interface TranslationCacheEntry {
  originalText: string;
  translatedText: string;
  targetLanguage: string;
  timestamp: number;
  modelUsed: string;
}
```

**Cache Policy**:
- TTL: 7 days (604800000 ms)
- Max size: 50 entries per language (LRU eviction)
- Clear on user logout/session end (not applicable for static site, but good practice)

**Why Client-Side Only**:
1. **Simplicity**: No Redis/caching infrastructure needed
2. **Privacy**: User's translations stay on their device
3. **Zero cost**: No server resources consumed
4. **Sufficient**: Most users re-translate same passages within a session
5. **Stateless backend**: Aligns with architectural principle

#### Consequences

**Positive**:
- Zero infrastructure cost for caching
- No privacy concerns (data never leaves user's browser)
- Fast cache hits (<10ms from localStorage)
- Simple implementation (50 LOC)

**Negative**:
- Cache not shared across devices/sessions
- Cache lost on browser clear/different device
- No benefit for first-time translations

**Risks**:
- localStorage size limits (5-10MB typical) - Mitigation: LRU eviction, 50 entry limit
- Cache poisoning (user modifies localStorage) - Mitigation: Hash validation, low risk

**Why Not Server-Side**:
- Complexity: Requires Redis setup, cache invalidation logic
- Cost: Redis hosting ($5-10/month minimum)
- Privacy: Book content cached on server (less desirable)
- Diminishing returns: Client cache sufficient for most use cases

---

### ADR-003: RTL (Right-to-Left) Language Support

**Status**: Accepted
**Date**: 2025-12-25
**Deciders**: Development Team
**Related**: FR-4 (RTL Support), NFR-5 (Accessibility)

#### Context

Arabic and Urdu are RTL languages requiring special CSS handling. Options:

1. **CSS Logical Properties** (modern approach)
2. **Separate RTL stylesheets** (traditional approach)
3. **JavaScript-based direction switching**
4. **Tailwind RTL plugin** (if using Tailwind)

**RTL Languages in Scope**:
- Arabic (`ar`)
- Urdu (`ur`)

**Requirements**:
- Text direction flips for RTL languages
- UI elements (buttons, dropdowns) mirror correctly
- Mixed LTR/RTL content handled gracefully (technical terms in English)

#### Decision

**Use CSS Logical Properties with runtime `dir` attribute**

**Implementation**:

1. **Component-level `dir` attribute**:
```tsx
<div
  dir={isRTL(currentLanguage) ? 'rtl' : 'ltr'}
  className="translation-display"
>
  {translatedText}
</div>
```

2. **CSS Logical Properties** (replace physical properties):
```css
/* ❌ Old (physical) */
.translation-panel {
  margin-left: 16px;
  padding-right: 8px;
  text-align: left;
}

/* ✅ New (logical) */
.translation-panel {
  margin-inline-start: 16px;
  padding-inline-end: 8px;
  text-align: start;
}
```

3. **Helper function**:
```typescript
const RTL_LANGUAGES = ['arabic', 'urdu'];

function isRTL(language: string): boolean {
  return RTL_LANGUAGES.includes(language);
}
```

**Why CSS Logical Properties**:
- **Modern standard**: Recommended by W3C, MDN
- **Browser support**: 95%+ (all modern browsers)
- **Automatic mirroring**: Margins, padding, borders flip automatically
- **Future-proof**: New RTL languages work without code changes
- **Accessibility**: Better screen reader support

#### Consequences

**Positive**:
- Clean, maintainable CSS (no duplicate stylesheets)
- Automatic layout mirroring for RTL
- Easy to add new RTL languages
- Works with Docusaurus out-of-the-box

**Negative**:
- Requires CSS refactoring (change `left`/`right` to `inline-start`/`inline-end`)
- Team needs to learn logical properties syntax

**Risks**:
- Browser compatibility (IE11 not supported) - Mitigation: Acceptable, IE11 EOL
- Mixed LTR/RTL content edge cases - Mitigation: Test with Arabic + English terms

**Why Not Separate Stylesheets**:
- Maintenance burden: Duplicate CSS for RTL variants
- Fragile: Easy to update LTR and forget RTL
- Outdated approach: Logical properties are the modern standard

---

### ADR-004: Error Handling and Retry Strategy

**Status**: Accepted
**Date**: 2025-12-25
**Deciders**: Development Team
**Related**: NFR-1 (Performance), NFR-3 (Security)

#### Context

OpenAI API calls can fail due to:
- Rate limiting (429 errors)
- Timeouts (network issues)
- Server errors (500-series)
- Invalid API keys (401)
- Content policy violations (400)

**Requirements**:
- Translation failures should not break core RAG functionality
- Users should see helpful error messages
- Transient errors should be retried
- Permanent errors should fail fast

#### Decision

**Implement tiered error handling with exponential backoff**

**Error Categories**:

1. **Retryable Errors** (with exponential backoff):
   - 429 (Rate Limit Exceeded)
   - 500, 502, 503, 504 (Server Errors)
   - Network timeouts

2. **Non-Retryable Errors** (fail immediately):
   - 401 (Invalid API Key)
   - 400 (Invalid Request/Content Policy)
   - 413 (Payload Too Large)

**Retry Logic**:
```python
class TranslationService:
    MAX_RETRIES = 3
    BASE_DELAY = 1.0  # seconds

    async def translate_with_retry(self, text: str, target_language: str) -> dict:
        """Translate with exponential backoff retry."""
        for attempt in range(self.MAX_RETRIES):
            try:
                return await self._translate(text, target_language)
            except RateLimitError as e:
                if attempt == self.MAX_RETRIES - 1:
                    raise TranslationError("Rate limit exceeded, try again later")
                delay = self.BASE_DELAY * (2 ** attempt)  # 1s, 2s, 4s
                await asyncio.sleep(delay)
            except OpenAIError as e:
                if e.status_code in [401, 400, 413]:
                    raise TranslationError(f"Translation failed: {e.message}")
                if attempt == self.MAX_RETRIES - 1:
                    raise TranslationError("Translation service unavailable")
                await asyncio.sleep(self.BASE_DELAY * (2 ** attempt))
```

**User-Facing Error Messages**:
```python
ERROR_MESSAGES = {
    "rate_limit": "Too many translation requests. Please wait a moment and try again.",
    "invalid_request": "Unable to translate this text. Please try a shorter selection.",
    "service_unavailable": "Translation service is temporarily unavailable. Please try again later.",
    "network_error": "Network error. Please check your connection and try again.",
    "unknown": "An unexpected error occurred. Please try again.",
}
```

**Frontend Error Handling**:
```typescript
async function translateText(text: string, targetLanguage: string): Promise<TranslationResponse> {
  try {
    const response = await fetch('/api/v1/translate/text', { ... });

    if (!response.ok) {
      const error = await response.json();
      throw new TranslationError(error.detail || 'Translation failed');
    }

    return await response.json();
  } catch (error) {
    // Show user-friendly error in UI
    showErrorToast(error.message);
    // Log for debugging
    console.error('Translation failed:', error);
    throw error;
  }
}
```

**Fallback Behavior**:
- If translation fails, show original English text
- Display error message in UI (toast/banner)
- Log error details to backend (for monitoring)
- Don't block user from continuing to use RAG chatbot

#### Consequences

**Positive**:
- Resilient to transient API failures
- Users get helpful error messages
- Core RAG functionality never breaks due to translation errors
- Monitoring data available for debugging

**Negative**:
- Increased complexity in error handling code
- Retry delays can increase latency (up to 7s worst case: 1+2+4)

**Risks**:
- Retry storms during OpenAI outages - Mitigation: Circuit breaker pattern (future)
- Rate limit exhaustion - Mitigation: Client-side rate limiting (10 req/min)

---

## 4. Backend Architecture

### 4.1 FastAPI Router Structure

**New Translation Router** (`app/api/v1/endpoints/translate.py`):

```python
"""Translation endpoints for multilingual support."""

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.core.logging import get_logger
from app.models.request import TranslateTextRequest, TranslateResponseRequest
from app.models.response import TranslationResponse, TranslationErrorResponse
from app.services.translation import TranslationService
from app.middleware.rate_limit import check_rate_limit

logger = get_logger(__name__)
router = APIRouter()

# Initialize translation service (singleton)
translation_service = TranslationService()


@router.post("/text", response_model=TranslationResponse, status_code=status.HTTP_200_OK)
async def translate_text(request: TranslateTextRequest, req: Request) -> TranslationResponse:
    """
    Translate selected text to target language.

    Rate limit: 10 requests per minute per IP.
    Max text length: 10,000 characters.
    """
    # Rate limiting check
    await check_rate_limit(req, limit=10, window_seconds=60)

    try:
        result = await translation_service.translate_text(
            text=request.text,
            target_language=request.target_language,
            source_language=request.source_language,
            preserve_technical_terms=request.preserve_technical_terms,
            context=request.context,
        )
        return TranslationResponse(**result)

    except TranslationError as e:
        logger.error(f"Translation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/response", response_model=TranslationResponse, status_code=status.HTTP_200_OK)
async def translate_response(request: TranslateResponseRequest, req: Request) -> TranslationResponse:
    """
    Translate a chatbot response to target language.

    Only the answer text is translated. Citations remain in English.
    """
    await check_rate_limit(req, limit=10, window_seconds=60)

    try:
        result = await translation_service.translate_response(
            response=request.original_response,
            target_language=request.target_language,
        )
        return TranslationResponse(**result)

    except TranslationError as e:
        logger.error(f"Response translation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
```

**Register in Router** (`app/api/v1/router.py`):

```python
from app.api.v1.endpoints import admin, query, translate  # ADD translate

api_router = APIRouter()

# Existing routers
api_router.include_router(query.router, prefix="/query", tags=["Query"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])

# NEW: Translation router
api_router.include_router(translate.router, prefix="/translate", tags=["Translation"])
```

### 4.2 Translation Service Architecture

**File**: `app/services/translation.py`

```python
"""Translation service using OpenAI Chat Completion API."""

import time
from typing import Any, Literal

from openai import AsyncOpenAI, OpenAIError, RateLimitError

from app.core.config import settings
from app.core.logging import get_logger
from app.models.response import QueryResponse

logger = get_logger(__name__)

SupportedLanguage = Literal["english", "urdu", "mandarin", "japanese", "spanish", "french", "arabic"]

LANGUAGE_NAMES = {
    "english": "English",
    "urdu": "Urdu (اردو)",
    "mandarin": "Mandarin Chinese (中文)",
    "japanese": "Japanese (日本語)",
    "spanish": "Spanish (Español)",
    "french": "French (Français)",
    "arabic": "Arabic (العربية)",
}


class TranslationError(Exception):
    """Exception raised when translation fails."""
    pass


class TranslationService:
    """Service for translating text using OpenAI API."""

    MAX_RETRIES = 3
    BASE_DELAY = 1.0
    DEFAULT_MODEL = "gpt-4o-mini"  # Cost-effective choice (ADR-001)
    TEMPERATURE = 0.3  # Low temperature for consistent translations

    def __init__(self):
        """Initialize translation service with OpenAI client."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.logger = get_logger(__name__)

    async def translate_text(
        self,
        text: str,
        target_language: SupportedLanguage,
        source_language: SupportedLanguage = "english",
        preserve_technical_terms: bool = True,
        context: str | None = None,
    ) -> dict[str, Any]:
        """
        Translate text to target language.

        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code (default: english)
            preserve_technical_terms: Keep technical terms in English (default: True)
            context: Optional context hint (e.g., "robotics textbook")

        Returns:
            Dictionary with translation result and metadata
        """
        start_time = time.time()

        # Build system prompt
        system_prompt = self._build_system_prompt(
            target_language, source_language, preserve_technical_terms, context
        )

        # Translate with retry
        try:
            translated_text = await self._translate_with_retry(text, system_prompt)

            processing_time_ms = int((time.time() - start_time) * 1000)

            return {
                "translated_text": translated_text,
                "target_language": target_language,
                "model_used": self.DEFAULT_MODEL,
                "processing_time_ms": processing_time_ms,
            }

        except Exception as e:
            self.logger.error(f"Translation failed: {str(e)}")
            raise TranslationError(f"Translation failed: {str(e)}")

    async def translate_response(
        self,
        response: QueryResponse,
        target_language: SupportedLanguage,
    ) -> dict[str, Any]:
        """
        Translate a RAG chatbot response.

        Only the answer text is translated. Citations remain in English.

        Args:
            response: Original QueryResponse object
            target_language: Target language code

        Returns:
            Dictionary with translated response and metadata
        """
        # Extract answer text from response
        answer_text = response.answer

        # Translate answer only
        translation_result = await self.translate_text(
            text=answer_text,
            target_language=target_language,
            source_language="english",
            preserve_technical_terms=True,
            context="AI/Robotics chatbot response",
        )

        # Reconstruct response with translated answer
        translated_response = {
            "answer": translation_result["translated_text"],
            "citations": response.citations,  # Keep citations in English
            "query_metadata": response.query_metadata,
        }

        return {
            "translated_response": translated_response,
            "target_language": target_language,
            "model_used": translation_result["model_used"],
            "processing_time_ms": translation_result["processing_time_ms"],
        }

    def _build_system_prompt(
        self,
        target_language: SupportedLanguage,
        source_language: SupportedLanguage,
        preserve_technical_terms: bool,
        context: str | None,
    ) -> str:
        """Build system prompt for translation."""
        language_name = LANGUAGE_NAMES[target_language]

        prompt = f"""You are a professional translator specializing in technical content.

Translate the following text from {LANGUAGE_NAMES[source_language]} to {language_name}.

Instructions:
- Maintain the exact meaning and technical accuracy
- Use natural, fluent {language_name}
- Preserve formatting (paragraphs, line breaks)
"""

        if preserve_technical_terms:
            prompt += """- Keep technical terms in English when no direct translation exists
- For technical acronyms (e.g., ROS, SLAM, PID), keep them in English
- You may add transliteration or brief explanation in parentheses if helpful
"""

        if context:
            prompt += f"\nContext: This text is from {context}.\n"

        prompt += "\nProvide ONLY the translation, no explanations or notes."

        return prompt

    async def _translate_with_retry(self, text: str, system_prompt: str) -> str:
        """Translate with exponential backoff retry."""
        for attempt in range(self.MAX_RETRIES):
            try:
                response = await self.client.chat.completions.create(
                    model=self.DEFAULT_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text},
                    ],
                    temperature=self.TEMPERATURE,
                    max_tokens=4000,  # Allow for text expansion in some languages
                )

                return response.choices[0].message.content.strip()

            except RateLimitError as e:
                if attempt == self.MAX_RETRIES - 1:
                    raise TranslationError("Rate limit exceeded. Please try again later.")
                delay = self.BASE_DELAY * (2 ** attempt)
                self.logger.warning(f"Rate limited, retrying in {delay}s...")
                await asyncio.sleep(delay)

            except OpenAIError as e:
                if e.status_code in [401, 400, 413]:
                    # Non-retryable errors
                    raise TranslationError(f"Translation failed: {e.message}")

                if attempt == self.MAX_RETRIES - 1:
                    raise TranslationError("Translation service unavailable.")

                delay = self.BASE_DELAY * (2 ** attempt)
                self.logger.warning(f"OpenAI error, retrying in {delay}s...")
                await asyncio.sleep(delay)
```

### 4.3 Data Models

**Request Models** (`app/models/request.py`):

```python
from typing import Literal, Optional
from pydantic import BaseModel, Field

SupportedLanguage = Literal["english", "urdu", "mandarin", "japanese", "spanish", "french", "arabic"]


class TranslateTextRequest(BaseModel):
    """Request model for text translation."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Text to translate (max 10,000 characters)"
    )
    target_language: SupportedLanguage = Field(
        ...,
        description="Target language code"
    )
    source_language: SupportedLanguage = Field(
        default="english",
        description="Source language code (default: english)"
    )
    preserve_technical_terms: bool = Field(
        default=True,
        description="Preserve technical terms in English (default: true)"
    )
    context: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Optional context hint (e.g., 'robotics textbook')"
    )


class TranslateResponseRequest(BaseModel):
    """Request model for translating a chatbot response."""

    original_response: dict = Field(
        ...,
        description="Original QueryResponse object to translate"
    )
    target_language: SupportedLanguage = Field(
        ...,
        description="Target language code"
    )
```

**Response Models** (`app/models/response.py`):

```python
class TranslationResponse(BaseModel):
    """Response model for translation requests."""

    translated_text: str = Field(..., description="Translated text")
    target_language: str = Field(..., description="Target language code")
    model_used: str = Field(..., description="OpenAI model used for translation")
    processing_time_ms: int = Field(..., description="Translation processing time in milliseconds")
```

### 4.4 Rate Limiting Middleware

**File**: `app/middleware/rate_limit.py`

```python
"""Simple in-memory rate limiting middleware."""

import time
from collections import defaultdict
from fastapi import HTTPException, Request, status

# In-memory rate limit storage
# Format: {ip_address: {endpoint: [(timestamp, count), ...]}}
rate_limit_store: dict[str, dict[str, list[tuple[float, int]]]] = defaultdict(lambda: defaultdict(list))


async def check_rate_limit(request: Request, limit: int, window_seconds: int) -> None:
    """
    Check if request exceeds rate limit.

    Args:
        request: FastAPI request object
        limit: Max requests per window
        window_seconds: Time window in seconds

    Raises:
        HTTPException: If rate limit exceeded
    """
    # Get client IP (handle Railway proxy headers)
    client_ip = request.client.host
    if forwarded_for := request.headers.get("X-Forwarded-For"):
        client_ip = forwarded_for.split(",")[0].strip()

    endpoint = request.url.path
    current_time = time.time()

    # Clean old entries
    if endpoint in rate_limit_store[client_ip]:
        rate_limit_store[client_ip][endpoint] = [
            (ts, count) for ts, count in rate_limit_store[client_ip][endpoint]
            if current_time - ts < window_seconds
        ]

    # Count requests in current window
    request_count = sum(count for _, count in rate_limit_store[client_ip][endpoint])

    if request_count >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Max {limit} requests per {window_seconds} seconds."
        )

    # Record this request
    rate_limit_store[client_ip][endpoint].append((current_time, 1))
```

**Note**: This is a simple in-memory rate limiter suitable for single-instance deployments (Railway default). For multi-instance deployments, use Redis-based rate limiting.

---

## 5. Frontend Architecture

### 5.1 Component Structure

```
src/
├── components/
│   ├── translation/
│   │   ├── LanguageSelector.tsx       # Language dropdown component
│   │   ├── TranslationDisplay.tsx     # Translation result modal/panel
│   │   ├── TextSelectionToolbar.tsx   # Translate button for selected text
│   │   └── types.ts                   # TypeScript interfaces
│   └── chat/
│       └── TranslateButton.tsx        # Translate button for chatbot messages
├── hooks/
│   ├── useTranslation.ts              # Translation logic hook
│   └── useTranslationCache.ts         # localStorage cache management
├── services/
│   └── translationApi.ts              # API client for translation endpoints
└── utils/
    ├── languageUtils.ts               # RTL detection, language helpers
    └── cacheUtils.ts                  # Cache key generation, validation
```

### 5.2 Core Components

#### Language Selector Component

**File**: `src/components/translation/LanguageSelector.tsx`

```tsx
import React from 'react';

export type SupportedLanguage =
  | 'english'
  | 'urdu'
  | 'mandarin'
  | 'japanese'
  | 'spanish'
  | 'french'
  | 'arabic';

export interface Language {
  code: SupportedLanguage;
  name: string;
  nativeName: string;
  rtl: boolean;
}

export const SUPPORTED_LANGUAGES: Language[] = [
  { code: 'english', name: 'English', nativeName: 'English', rtl: false },
  { code: 'urdu', name: 'Urdu', nativeName: 'اردو', rtl: true },
  { code: 'mandarin', name: 'Chinese', nativeName: '中文', rtl: false },
  { code: 'japanese', name: 'Japanese', nativeName: '日本語', rtl: false },
  { code: 'spanish', name: 'Spanish', nativeName: 'Español', rtl: false },
  { code: 'french', name: 'French', nativeName: 'Français', rtl: false },
  { code: 'arabic', name: 'Arabic', nativeName: 'العربية', rtl: true },
];

interface LanguageSelectorProps {
  currentLanguage: SupportedLanguage;
  onLanguageChange: (language: SupportedLanguage) => void;
  className?: string;
}

export const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  currentLanguage,
  onLanguageChange,
  className = '',
}) => {
  return (
    <div className={`language-selector ${className}`}>
      <label htmlFor="language-select" className="language-selector-label">
        Translate to:
      </label>
      <select
        id="language-select"
        value={currentLanguage}
        onChange={(e) => onLanguageChange(e.target.value as SupportedLanguage)}
        className="language-selector-dropdown"
      >
        {SUPPORTED_LANGUAGES.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.name} ({lang.nativeName})
          </option>
        ))}
      </select>
    </div>
  );
};
```

#### Translation Display Component

**File**: `src/components/translation/TranslationDisplay.tsx`

```tsx
import React from 'react';
import { isRTL } from '@/utils/languageUtils';
import type { SupportedLanguage } from './LanguageSelector';

interface TranslationDisplayProps {
  originalText: string;
  translatedText: string;
  targetLanguage: SupportedLanguage;
  onClose: () => void;
  showOriginal?: boolean;
}

export const TranslationDisplay: React.FC<TranslationDisplayProps> = ({
  originalText,
  translatedText,
  targetLanguage,
  onClose,
  showOriginal = true,
}) => {
  const [showComparison, setShowComparison] = React.useState(showOriginal);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(translatedText);
    // Show toast notification (implement separately)
  };

  return (
    <div className="translation-modal-overlay" onClick={onClose}>
      <div className="translation-modal" onClick={(e) => e.stopPropagation()}>
        <div className="translation-modal-header">
          <h3>Translation</h3>
          <button onClick={onClose} className="close-button">×</button>
        </div>

        <div className="translation-modal-content">
          {showComparison && (
            <div className="translation-section">
              <h4>Original (English)</h4>
              <div className="translation-text" dir="ltr">
                {originalText}
              </div>
            </div>
          )}

          <div className="translation-section">
            <h4>Translation ({targetLanguage})</h4>
            <div
              className="translation-text"
              dir={isRTL(targetLanguage) ? 'rtl' : 'ltr'}
            >
              {translatedText}
            </div>
          </div>
        </div>

        <div className="translation-modal-actions">
          <button onClick={() => setShowComparison(!showComparison)}>
            {showComparison ? 'Hide Original' : 'Show Original'}
          </button>
          <button onClick={copyToClipboard}>Copy Translation</button>
        </div>
      </div>
    </div>
  );
};
```

### 5.3 Translation Hook

**File**: `src/hooks/useTranslation.ts`

```tsx
import { useState } from 'react';
import { translateText, translateResponse } from '@/services/translationApi';
import { useTranslationCache } from './useTranslationCache';
import type { SupportedLanguage } from '@/components/translation/LanguageSelector';

export interface TranslationResult {
  translatedText: string;
  targetLanguage: string;
  modelUsed: string;
  processingTimeMs: number;
  fromCache: boolean;
}

export function useTranslation() {
  const [isTranslating, setIsTranslating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const cache = useTranslationCache();

  const translate = async (
    text: string,
    targetLanguage: SupportedLanguage,
    options?: {
      preserveTechnicalTerms?: boolean;
      context?: string;
    }
  ): Promise<TranslationResult | null> => {
    setIsTranslating(true);
    setError(null);

    try {
      // Check cache first (ADR-002)
      const cached = cache.get(text, targetLanguage);
      if (cached) {
        setIsTranslating(false);
        return {
          ...cached,
          fromCache: true,
        };
      }

      // Call API
      const result = await translateText({
        text,
        target_language: targetLanguage,
        source_language: 'english',
        preserve_technical_terms: options?.preserveTechnicalTerms ?? true,
        context: options?.context,
      });

      // Cache result
      cache.set(text, targetLanguage, result.translated_text, result.model_used);

      setIsTranslating(false);
      return {
        translatedText: result.translated_text,
        targetLanguage: result.target_language,
        modelUsed: result.model_used,
        processingTimeMs: result.processing_time_ms,
        fromCache: false,
      };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Translation failed';
      setError(errorMessage);
      setIsTranslating(false);
      return null;
    }
  };

  return {
    translate,
    isTranslating,
    error,
  };
}
```

### 5.4 Cache Management Hook

**File**: `src/hooks/useTranslationCache.ts`

```tsx
import { useCallback } from 'react';
import { hashString, isValidCacheEntry } from '@/utils/cacheUtils';

const CACHE_PREFIX = 'translation:';
const CACHE_TTL = 7 * 24 * 60 * 60 * 1000; // 7 days
const MAX_ENTRIES_PER_LANGUAGE = 50;

interface CacheEntry {
  originalText: string;
  translatedText: string;
  targetLanguage: string;
  timestamp: number;
  modelUsed: string;
}

export function useTranslationCache() {
  const getCacheKey = useCallback((text: string, targetLanguage: string): string => {
    const textHash = hashString(text);
    return `${CACHE_PREFIX}${textHash}:${targetLanguage}`;
  }, []);

  const get = useCallback((text: string, targetLanguage: string): CacheEntry | null => {
    const key = getCacheKey(text, targetLanguage);
    const cached = localStorage.getItem(key);

    if (!cached) return null;

    try {
      const entry: CacheEntry = JSON.parse(cached);

      // Validate entry
      if (!isValidCacheEntry(entry)) {
        localStorage.removeItem(key);
        return null;
      }

      // Check TTL
      if (Date.now() - entry.timestamp > CACHE_TTL) {
        localStorage.removeItem(key);
        return null;
      }

      return entry;
    } catch {
      localStorage.removeItem(key);
      return null;
    }
  }, [getCacheKey]);

  const set = useCallback((
    text: string,
    targetLanguage: string,
    translatedText: string,
    modelUsed: string
  ): void => {
    const key = getCacheKey(text, targetLanguage);
    const entry: CacheEntry = {
      originalText: text,
      translatedText,
      targetLanguage,
      timestamp: Date.now(),
      modelUsed,
    };

    try {
      localStorage.setItem(key, JSON.stringify(entry));

      // Enforce max entries (LRU eviction)
      evictOldEntries(targetLanguage);
    } catch (error) {
      // localStorage full - evict and retry
      evictOldEntries(targetLanguage, MAX_ENTRIES_PER_LANGUAGE / 2);
      try {
        localStorage.setItem(key, JSON.stringify(entry));
      } catch {
        // Still failed, give up (cache is nice-to-have)
        console.warn('Failed to cache translation:', error);
      }
    }
  }, [getCacheKey]);

  const evictOldEntries = useCallback((targetLanguage: string, maxEntries: number = MAX_ENTRIES_PER_LANGUAGE): void => {
    const entries: Array<{ key: string; timestamp: number }> = [];

    // Collect all cache entries for this language
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key?.startsWith(CACHE_PREFIX) && key.endsWith(`:${targetLanguage}`)) {
        const cached = localStorage.getItem(key);
        if (cached) {
          try {
            const entry: CacheEntry = JSON.parse(cached);
            entries.push({ key, timestamp: entry.timestamp });
          } catch {
            localStorage.removeItem(key);
          }
        }
      }
    }

    // Sort by timestamp (oldest first)
    entries.sort((a, b) => a.timestamp - b.timestamp);

    // Remove oldest entries if exceeding max
    if (entries.length > maxEntries) {
      const toRemove = entries.slice(0, entries.length - maxEntries);
      toRemove.forEach(({ key }) => localStorage.removeItem(key));
    }
  }, []);

  return { get, set };
}
```

### 5.5 Translation API Client

**File**: `src/services/translationApi.ts`

```tsx
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface TranslateTextRequest {
  text: string;
  target_language: string;
  source_language?: string;
  preserve_technical_terms?: boolean;
  context?: string;
}

export interface TranslationResponse {
  translated_text: string;
  target_language: string;
  model_used: string;
  processing_time_ms: number;
}

export async function translateText(request: TranslateTextRequest): Promise<TranslationResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/translate/text`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Translation failed');
  }

  return response.json();
}

export async function translateResponse(
  originalResponse: any,
  targetLanguage: string
): Promise<TranslationResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/translate/response`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      original_response: originalResponse,
      target_language: targetLanguage,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Translation failed');
  }

  return response.json();
}
```

---

## 6. Data Flow Diagrams

### 6.1 Text Selection Translation Flow

```
User Action: Selects text on Docusaurus page
    │
    ▼
┌─────────────────────────────────────┐
│ TextSelectionToolbar component      │
│ - Detects text selection            │
│ - Shows "Translate" button          │
└──────────────┬──────────────────────┘
               │ User clicks "Translate"
               ▼
┌─────────────────────────────────────┐
│ useTranslation hook                 │
│ 1. Check localStorage cache         │
│ 2. If cached: return immediately    │
│ 3. If not: call translateText API   │
└──────────────┬──────────────────────┘
               │ API call
               ▼
┌─────────────────────────────────────┐
│ Backend: POST /api/v1/translate/text│
│ 1. Validate request (Pydantic)      │
│ 2. Check rate limit (10 req/min)    │
│ 3. Call TranslationService          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ TranslationService                  │
│ 1. Build system prompt              │
│ 2. Call OpenAI API (gpt-4o-mini)    │
│ 3. Retry on transient errors        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ OpenAI API                          │
│ - Processes translation request     │
│ - Returns translated text           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Backend: TranslationResponse        │
│ { translated_text, target_language, │
│   model_used, processing_time_ms }  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Frontend: useTranslation hook       │
│ 1. Receive response                 │
│ 2. Cache in localStorage            │
│ 3. Return to component              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ TranslationDisplay component        │
│ - Shows original + translated text  │
│ - Applies RTL direction if needed   │
│ - Provides copy/share buttons       │
└─────────────────────────────────────┘
```

### 6.2 Chatbot Response Translation Flow

```
User Action: Asks chatbot a question
    │
    ▼
┌─────────────────────────────────────┐
│ Existing RAG Pipeline               │
│ 1. Query → Retriever                │
│ 2. Retriever → Qdrant (vector DB)   │
│ 3. Responder → OpenAI (answer gen)  │
│ 4. Return QueryResponse             │
└──────────────┬──────────────────────┘
               │ Response displayed
               ▼
┌─────────────────────────────────────┐
│ Chat UI: TranslateButton            │
│ - Shows "Translate to [lang]"       │
│ - User clicks button                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ useTranslation hook                 │
│ - Calls translateResponse API       │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Backend: /api/v1/translate/response │
│ 1. Extract answer text from response│
│ 2. Translate answer only (not cites)│
│ 3. Reconstruct response object      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ TranslationService                  │
│ - Same flow as text translation     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Frontend: Display translated answer │
│ - Original answer (collapsible)     │
│ - Translated answer (RTL if needed) │
│ - Citations (English, unchanged)    │
└─────────────────────────────────────┘
```

---

## 7. Non-Functional Considerations

### 7.1 Performance

**Target**: <2 second translation latency (95th percentile)

**Optimization Strategies**:

1. **Model Selection** (ADR-001):
   - Use GPT-4o-mini (faster than GPT-4o)
   - Typical latency: 500-1500ms for 200-token translations

2. **Client-Side Caching** (ADR-002):
   - Cache hits: <10ms (localStorage read)
   - Expected cache hit rate: 30-40% (users re-translate similar passages)

3. **Concurrent Requests**:
   - AsyncOpenAI client supports concurrent calls
   - No blocking on translation requests

4. **Rate Limiting**:
   - 10 requests/minute/user prevents API abuse
   - Prevents cost overruns from malicious users

**Performance Budget**:
```
Total latency breakdown (p95):
- Network roundtrip (client → Railway):  100ms
- FastAPI request validation:             10ms
- Rate limit check:                       5ms
- OpenAI API call:                        1500ms
- Response serialization:                 10ms
- Network roundtrip (Railway → client):  100ms
────────────────────────────────────────────────
Total:                                    1725ms ✅ (<2000ms target)
```

### 7.2 Security

**Threat Model**:

1. **Prompt Injection**:
   - **Risk**: User-provided text could manipulate translation output
   - **Mitigation**: System prompt explicitly states "translate ONLY", no code execution
   - **Impact**: Low (translation output is read-only, no data modification)

2. **Rate Limit Abuse**:
   - **Risk**: Users send excessive translation requests, increasing costs
   - **Mitigation**: 10 req/min rate limit, IP-based tracking
   - **Impact**: Medium (cost overrun risk)

3. **API Key Exposure**:
   - **Risk**: OpenAI API key leaked in frontend code
   - **Mitigation**: API key stored in Railway environment variables, never sent to frontend
   - **Impact**: Critical (prevented by architecture)

4. **Cross-Site Scripting (XSS)**:
   - **Risk**: Translated text contains malicious scripts
   - **Mitigation**: React auto-escapes content, CSP headers
   - **Impact**: Low (standard React protection)

**Security Checklist**:
- ✅ API key stored in Railway environment variables
- ✅ Rate limiting implemented (10 req/min/IP)
- ✅ Input validation (Pydantic max_length=10,000)
- ✅ No sensitive data in translation requests (book content is public)
- ✅ HTTPS enforced (Railway + GitHub Pages default)
- ✅ CORS configured for allowed origins only

### 7.3 Observability

**Logging Strategy**:

1. **Backend Logs**:
   ```python
   # Log translation requests
   logger.info(f"Translation request: {text[:50]}... → {target_language}")

   # Log OpenAI API calls
   logger.info(f"OpenAI API call: model={model}, tokens={tokens}")

   # Log errors with context
   logger.error(f"Translation failed: {error}, text={text[:100]}")
   ```

2. **Metrics to Track**:
   - Translation request count (by language)
   - Average latency (by language)
   - OpenAI API cost (by model)
   - Cache hit rate (client-side, via analytics)
   - Error rate (by error type)
   - Rate limit rejections (by IP)

3. **Railway Dashboard Monitoring**:
   - CPU usage (should be low, API-bound workload)
   - Memory usage (monitor for rate limiter growth)
   - Request logs (filter for `/api/v1/translate/*`)

4. **Future Enhancements** (out of scope for v1):
   - OpenTelemetry instrumentation
   - Sentry error tracking
   - Grafana dashboards for translation metrics

**Alerting** (future):
- Alert if error rate >5% for 5 minutes
- Alert if average latency >3 seconds for 10 minutes
- Alert if OpenAI API cost exceeds $50/day

### 7.4 Cost Management

**Cost Breakdown**:

**OpenAI API Costs** (GPT-4o-mini):
- Input: $0.150 / 1M tokens
- Output: $0.600 / 1M tokens

**Example Translation**:
- Input: 200 tokens (text + system prompt)
- Output: 250 tokens (translated text, slight expansion)
- Cost: (200 × $0.150 + 250 × $0.600) / 1,000,000 = $0.00018 per translation

**Monthly Projections**:
```
Scenario A: Low usage (500 translations/month)
  500 × $0.00018 = $0.09/month

Scenario B: Medium usage (2,000 translations/month)
  2,000 × $0.00018 = $0.36/month

Scenario C: High usage (10,000 translations/month)
  10,000 × $0.00018 = $1.80/month
```

**Cost Controls**:
1. Rate limiting: 10 req/min/user = max 14,400 req/day/user
2. Max text length: 10,000 chars (prevents abuse)
3. Client-side caching: Reduces API calls by ~30-40%
4. Model selection: GPT-4o-mini 16x cheaper than GPT-4o

**Total Infrastructure Cost**:
- Backend (Railway): $0/month (existing service)
- Frontend (GitHub Pages): $0/month (existing service)
- OpenAI API: $0.10-$5/month (depends on usage)

**Total: $0.10-$5/month** ✅ Well within budget

---

## 8. Implementation Sequence

### Phase 1: Backend Foundation (Week 1)

**Sprint Goal**: Functional translation API with retry logic

**Tasks**:
1. Create `app/services/translation.py` with `TranslationService` class
2. Implement request/response models in `app/models/request.py` and `app/models/response.py`
3. Create translation router `app/api/v1/endpoints/translate.py`
4. Register router in `app/api/v1/router.py`
5. Implement rate limiting middleware `app/middleware/rate_limit.py`
6. Write unit tests for translation service
7. Write integration tests for API endpoints
8. Deploy to Railway, verify endpoints work

**Acceptance Criteria**:
- ✅ `POST /api/v1/translate/text` returns translated text
- ✅ `POST /api/v1/translate/response` translates chatbot responses
- ✅ Rate limiting blocks requests exceeding 10/min
- ✅ Retry logic handles transient OpenAI errors
- ✅ All tests pass

---

### Phase 2: Frontend Components (Week 2)

**Sprint Goal**: Functional UI for text selection translation

**Tasks**:
1. Create `LanguageSelector` component
2. Create `TranslationDisplay` component
3. Create `TextSelectionToolbar` component
4. Implement `useTranslation` hook
5. Implement `useTranslationCache` hook (localStorage)
6. Create translation API client (`translationApi.ts`)
7. Integrate with Docusaurus (detect text selection, show toolbar)
8. Add RTL CSS support (logical properties)
9. Write component tests (Jest + React Testing Library)
10. Deploy to GitHub Pages

**Acceptance Criteria**:
- ✅ User can select text and see "Translate" button
- ✅ Clicking "Translate" shows language selector
- ✅ Translated text appears in modal with RTL support for Arabic/Urdu
- ✅ Translations are cached in localStorage
- ✅ All component tests pass

---

### Phase 3: Chatbot Integration & Polish (Week 3)

**Sprint Goal**: Complete feature with chatbot translation

**Tasks**:
1. Add `TranslateButton` to chatbot UI
2. Integrate chatbot response translation flow
3. Add error handling UI (toast notifications)
4. Add loading states (spinners, skeleton screens)
5. Add copy-to-clipboard functionality
6. Add translation history UI (show recent translations)
7. Performance optimization (debounce, lazy loading)
8. Accessibility audit (WCAG 2.1 AA compliance)
9. End-to-end testing (Playwright)
10. User acceptance testing (UAT)

**Acceptance Criteria**:
- ✅ User can translate chatbot responses
- ✅ Error messages are user-friendly
- ✅ Loading states provide feedback
- ✅ Copy/share features work
- ✅ Accessibility audit passes
- ✅ E2E tests pass

---

### Phase 4: Deployment & Monitoring (Week 4)

**Sprint Goal**: Production-ready launch

**Tasks**:
1. Create deployment documentation
2. Set up monitoring (Railway logs, error tracking)
3. Create user documentation (how to use translation)
4. Conduct load testing (simulate 100 concurrent users)
5. Security review (penetration testing, OWASP check)
6. Soft launch (beta users only)
7. Collect feedback, iterate
8. Full launch (all users)
9. Post-launch monitoring (1 week)
10. Retrospective, create PHR

**Acceptance Criteria**:
- ✅ Feature is live on production
- ✅ No critical bugs in first week
- ✅ User feedback is positive (>4/5 rating)
- ✅ Performance meets targets (<2s latency)
- ✅ Cost is within budget (<$5/month)

---

## 9. Testing Strategy

### 9.1 Backend Testing

**Unit Tests** (`tests/services/test_translation.py`):

```python
import pytest
from unittest.mock import AsyncMock, patch
from app.services.translation import TranslationService, TranslationError

@pytest.mark.asyncio
async def test_translate_text_success():
    """Test successful text translation."""
    service = TranslationService()

    with patch.object(service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = MockOpenAIResponse(
            content="Hola, esto es una prueba."
        )

        result = await service.translate_text(
            text="Hello, this is a test.",
            target_language="spanish",
        )

        assert result["translated_text"] == "Hola, esto es una prueba."
        assert result["target_language"] == "spanish"
        assert result["model_used"] == "gpt-4o-mini"
        assert result["processing_time_ms"] > 0

@pytest.mark.asyncio
async def test_translate_text_rate_limit_retry():
    """Test retry logic on rate limit error."""
    service = TranslationService()

    with patch.object(service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        # First 2 calls fail with rate limit, 3rd succeeds
        mock_create.side_effect = [
            RateLimitError("Rate limit exceeded"),
            RateLimitError("Rate limit exceeded"),
            MockOpenAIResponse(content="Translated text"),
        ]

        result = await service.translate_text(
            text="Test",
            target_language="spanish",
        )

        assert result["translated_text"] == "Translated text"
        assert mock_create.call_count == 3

@pytest.mark.asyncio
async def test_translate_text_non_retryable_error():
    """Test immediate failure on non-retryable error."""
    service = TranslationService()

    with patch.object(service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = OpenAIError("Invalid API key", status_code=401)

        with pytest.raises(TranslationError, match="Translation failed"):
            await service.translate_text(
                text="Test",
                target_language="spanish",
            )

        assert mock_create.call_count == 1  # No retries
```

**Integration Tests** (`tests/api/test_translate_endpoints.py`):

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_translate_text_endpoint():
    """Test /api/v1/translate/text endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/translate/text",
            json={
                "text": "Hello world",
                "target_language": "spanish",
                "preserve_technical_terms": True,
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "translated_text" in data
        assert data["target_language"] == "spanish"
        assert "model_used" in data

@pytest.mark.asyncio
async def test_translate_text_rate_limit():
    """Test rate limiting blocks excessive requests."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Send 11 requests (limit is 10/min)
        for i in range(11):
            response = await client.post(
                "/api/v1/translate/text",
                json={"text": f"Test {i}", "target_language": "spanish"}
            )

            if i < 10:
                assert response.status_code == 200
            else:
                assert response.status_code == 429  # Rate limit exceeded
```

### 9.2 Frontend Testing

**Component Tests** (`src/components/translation/__tests__/LanguageSelector.test.tsx`):

```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { LanguageSelector } from '../LanguageSelector';

describe('LanguageSelector', () => {
  it('renders all supported languages', () => {
    const onLanguageChange = jest.fn();
    render(
      <LanguageSelector
        currentLanguage="english"
        onLanguageChange={onLanguageChange}
      />
    );

    const select = screen.getByLabelText('Translate to:');
    expect(select).toBeInTheDocument();

    // Check all languages are options
    expect(screen.getByText(/English/)).toBeInTheDocument();
    expect(screen.getByText(/اردو/)).toBeInTheDocument();  // Urdu
    expect(screen.getByText(/中文/)).toBeInTheDocument();  // Chinese
  });

  it('calls onLanguageChange when selection changes', () => {
    const onLanguageChange = jest.fn();
    render(
      <LanguageSelector
        currentLanguage="english"
        onLanguageChange={onLanguageChange}
      />
    );

    const select = screen.getByLabelText('Translate to:');
    fireEvent.change(select, { target: { value: 'spanish' } });

    expect(onLanguageChange).toHaveBeenCalledWith('spanish');
  });
});
```

**Hook Tests** (`src/hooks/__tests__/useTranslation.test.ts`):

```tsx
import { renderHook, waitFor } from '@testing-library/react';
import { useTranslation } from '../useTranslation';
import * as translationApi from '@/services/translationApi';

jest.mock('@/services/translationApi');

describe('useTranslation', () => {
  it('translates text successfully', async () => {
    const mockTranslate = jest.spyOn(translationApi, 'translateText');
    mockTranslate.mockResolvedValue({
      translated_text: 'Hola mundo',
      target_language: 'spanish',
      model_used: 'gpt-4o-mini',
      processing_time_ms: 1234,
    });

    const { result } = renderHook(() => useTranslation());

    expect(result.current.isTranslating).toBe(false);

    const translation = await result.current.translate('Hello world', 'spanish');

    await waitFor(() => {
      expect(result.current.isTranslating).toBe(false);
    });

    expect(translation).toEqual({
      translatedText: 'Hola mundo',
      targetLanguage: 'spanish',
      modelUsed: 'gpt-4o-mini',
      processingTimeMs: 1234,
      fromCache: false,
    });
  });

  it('returns cached translation on second call', async () => {
    const mockTranslate = jest.spyOn(translationApi, 'translateText');
    mockTranslate.mockResolvedValue({
      translated_text: 'Hola mundo',
      target_language: 'spanish',
      model_used: 'gpt-4o-mini',
      processing_time_ms: 1234,
    });

    const { result } = renderHook(() => useTranslation());

    // First call - hits API
    await result.current.translate('Hello world', 'spanish');

    // Second call - should use cache
    const cached = await result.current.translate('Hello world', 'spanish');

    expect(cached?.fromCache).toBe(true);
    expect(mockTranslate).toHaveBeenCalledTimes(1);  // Only called once
  });
});
```

### 9.3 End-to-End Testing

**E2E Tests** (`e2e/translation.spec.ts`):

```typescript
import { test, expect } from '@playwright/test';

test.describe('Translation Feature', () => {
  test('translates selected text', async ({ page }) => {
    // Navigate to a book page
    await page.goto('/docs/chapter-1/introduction');

    // Select text
    await page.selectText('ROS 2 is a flexible framework');

    // Click translate button
    await page.click('[data-testid="translate-selection"]');

    // Select language
    await page.selectOption('[data-testid="language-selector"]', 'spanish');

    // Wait for translation to appear
    await expect(page.locator('[data-testid="translated-text"]')).toBeVisible();

    // Verify translation is shown
    const translatedText = await page.textContent('[data-testid="translated-text"]');
    expect(translatedText).toContain('ROS 2 es un marco flexible');
  });

  test('applies RTL direction for Arabic', async ({ page }) => {
    await page.goto('/docs/chapter-1/introduction');
    await page.selectText('ROS 2 is a flexible framework');
    await page.click('[data-testid="translate-selection"]');
    await page.selectOption('[data-testid="language-selector"]', 'arabic');

    await expect(page.locator('[data-testid="translated-text"]')).toBeVisible();

    // Check dir attribute
    const dir = await page.getAttribute('[data-testid="translated-text"]', 'dir');
    expect(dir).toBe('rtl');
  });

  test('caches translation and retrieves from cache', async ({ page }) => {
    await page.goto('/docs/chapter-1/introduction');
    await page.selectText('Hello world');
    await page.click('[data-testid="translate-selection"]');
    await page.selectOption('[data-testid="language-selector"]', 'spanish');

    // Wait for first translation
    await expect(page.locator('[data-testid="translated-text"]')).toBeVisible();

    // Close modal
    await page.click('[data-testid="close-translation"]');

    // Select same text again
    await page.selectText('Hello world');
    await page.click('[data-testid="translate-selection"]');
    await page.selectOption('[data-testid="language-selector"]', 'spanish');

    // Translation should appear instantly (from cache)
    await expect(page.locator('[data-testid="translated-text"]')).toBeVisible({ timeout: 100 });
  });
});
```

---

## 10. Deployment & Rollout

### 10.1 Deployment Process

**Backend Deployment (Railway)**:

1. **Environment Variables**:
   - OpenAI API key already configured (existing RAG setup)
   - No new environment variables needed

2. **Deployment Steps**:
   ```bash
   # Push to main branch (Railway auto-deploys)
   git push origin 003-multilingual-translation

   # Railway automatically:
   # 1. Detects changes
   # 2. Installs dependencies (requirements.txt)
   # 3. Runs migrations (if any)
   # 4. Restarts service
   # 5. Health check: /health endpoint
   ```

3. **Post-Deployment Verification**:
   ```bash
   # Test translation endpoint
   curl -X POST https://your-railway-app.railway.app/api/v1/translate/text \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Hello world",
       "target_language": "spanish"
     }'

   # Expected: {"translated_text": "Hola mundo", ...}
   ```

**Frontend Deployment (GitHub Pages)**:

1. **Build Process**:
   ```bash
   # Docusaurus build
   npm run build

   # Deploy to gh-pages branch
   npm run deploy
   ```

2. **Verification**:
   - Navigate to production site
   - Select text, verify "Translate" button appears
   - Test translation for all 6 languages
   - Verify RTL rendering for Arabic/Urdu

### 10.2 Rollout Plan

**Phase 1: Internal Testing (Day 1-2)**:
- Deploy to staging environment
- Team testing (developers, QA)
- Fix critical bugs

**Phase 2: Beta Launch (Day 3-5)**:
- Add feature flag to show translation only to beta users
- Invite 10-20 beta testers
- Collect feedback via survey
- Monitor error rates, latency

**Phase 3: Gradual Rollout (Day 6-7)**:
- Enable for 10% of users
- Monitor metrics (latency, error rate, cost)
- Increase to 50% if no issues
- Increase to 100%

**Phase 4: Full Launch (Day 8+)**:
- Remove feature flag
- Announce feature (blog post, social media)
- Monitor for 1 week
- Iterate based on user feedback

### 10.3 Rollback Plan

**Trigger Conditions**:
- Error rate >10% for 10 minutes
- Average latency >5 seconds
- OpenAI API cost exceeds $10/day
- Critical security vulnerability discovered

**Rollback Procedure**:

1. **Frontend Rollback**:
   ```bash
   # Revert to previous commit
   git revert HEAD

   # Rebuild and deploy
   npm run build && npm run deploy
   ```

2. **Backend Rollback**:
   ```bash
   # Revert to previous Railway deployment
   railway rollback

   # Or revert Git commit and push
   git revert HEAD && git push origin main
   ```

3. **Partial Rollback** (keep backend, disable frontend):
   - Add feature flag to hide translation UI
   - Users can still access RAG chatbot (no impact)

---

## 11. Risk Assessment & Mitigation

### 11.1 Technical Risks

**Risk 1: OpenAI API Latency Spikes**

- **Likelihood**: Medium (happens occasionally during high traffic)
- **Impact**: High (users experience >5s latency, frustration)
- **Mitigation**:
  - Set 10-second timeout on OpenAI API calls
  - Show loading indicator to manage user expectations
  - Implement circuit breaker (if errors persist, fail fast)
  - Cache translations client-side to reduce API calls

**Risk 2: Translation Quality Issues**

- **Likelihood**: Medium (GPT-4o-mini may struggle with complex technical terms)
- **Impact**: Medium (users get inaccurate translations, trust degraded)
- **Mitigation**:
  - Use `preserve_technical_terms: true` by default
  - Add feedback button ("Report bad translation")
  - Monitor user feedback, upgrade to GPT-4o for critical passages
  - Add model selector (future): let power users choose GPT-4o

**Risk 3: Cost Overrun**

- **Likelihood**: Low (rate limiting + client cache prevent abuse)
- **Impact**: Medium (unexpected $50-100 bill)
- **Mitigation**:
  - Rate limit: 10 req/min/user
  - Max text length: 10,000 chars
  - Monitor OpenAI API usage dashboard daily
  - Set budget alert: email if cost >$20/day

**Risk 4: RTL Rendering Bugs**

- **Likelihood**: Medium (RTL CSS is complex, edge cases exist)
- **Impact**: Low (visual bugs, not functional breakage)
- **Mitigation**:
  - Test RTL layouts manually (Arabic, Urdu)
  - Test mixed LTR/RTL content (English terms in Arabic text)
  - Add E2E tests for RTL rendering
  - Monitor user feedback for RTL issues

### 11.2 Product Risks

**Risk 5: Low Adoption**

- **Likelihood**: Medium (users may not discover feature)
- **Impact**: Medium (wasted development effort)
- **Mitigation**:
  - Add onboarding tooltip on first visit
  - Announce feature prominently (blog post, banner)
  - Add to documentation ("How to translate book content")
  - Track usage metrics, iterate on UX if adoption is low

**Risk 6: Security Vulnerability (Prompt Injection)**

- **Likelihood**: Low (translation is read-only operation)
- **Impact**: Low (worst case: malicious translation output, no data breach)
- **Mitigation**:
  - System prompt is explicit: "Translate ONLY, no code execution"
  - React auto-escapes content (XSS prevention)
  - Conduct security review before launch
  - Add rate limiting to prevent abuse

### 11.3 Operational Risks

**Risk 7: Railway Deployment Failure**

- **Likelihood**: Low (Railway is reliable, we have rollback)
- **Impact**: High (backend unavailable, RAG + translation down)
- **Mitigation**:
  - Test deployment in staging first
  - Deploy during low-traffic hours
  - Have rollback procedure ready
  - Monitor Railway logs during deployment

**Risk 8: OpenAI API Outage**

- **Likelihood**: Low (OpenAI has 99.9% uptime SLA)
- **Impact**: High (translation fails, users frustrated)
- **Mitigation**:
  - Degrade gracefully: show original English text
  - Display helpful error message: "Translation service unavailable"
  - Retry logic with exponential backoff
  - Don't block core RAG functionality

---

## 12. Summary & Next Steps

### 12.1 Architectural Summary

This plan delivers a **stateless, cost-effective multilingual translation feature** with the following characteristics:

✅ **Simple**: No new infrastructure (Redis, databases), uses existing OpenAI API
✅ **Fast**: <2s latency target using GPT-4o-mini + client-side caching
✅ **Cheap**: $0.10-$5/month operating cost with rate limiting
✅ **Reliable**: Retry logic, error handling, graceful degradation
✅ **Maintainable**: Clean separation of concerns, well-tested components
✅ **Accessible**: RTL support, WCAG 2.1 AA compliance

**Key Architectural Decisions**:
1. **GPT-4o-mini** as default model (cost vs. quality trade-off)
2. **Client-side caching** only (simplicity, privacy)
3. **CSS Logical Properties** for RTL (modern, maintainable)
4. **Exponential backoff retry** for resilience

### 12.2 Implementation Readiness

**Immediate Next Steps**:

1. **Run `/sp.tasks`** to generate implementation tasks from this plan
2. **Create ADR documents** in `history/adr/` for the 4 key decisions:
   - ADR-001: Model Selection (GPT-4o-mini vs GPT-4o)
   - ADR-002: Caching Strategy (client-side only)
   - ADR-003: RTL Support (CSS Logical Properties)
   - ADR-004: Error Handling (exponential backoff retry)
3. **Begin Phase 1 implementation** (backend foundation)

**Success Criteria for Launch**:
- ✅ All functional requirements met (FR-1, FR-2, FR-3, FR-4)
- ✅ Performance target achieved (<2s latency, 95th percentile)
- ✅ Cost within budget (<$5/month)
- ✅ Security audit passed (no critical vulnerabilities)
- ✅ User feedback positive (>4/5 rating)
- ✅ All tests passing (unit, integration, E2E)

This architecture is **ready for immediate implementation**. The plan provides sufficient detail for task breakdown while remaining flexible for iteration based on testing and user feedback.

---

**End of Architectural Plan**

---

## Appendix A: Decision Matrix

| Decision Point | Options Considered | Chosen | Rationale |
|---------------|-------------------|--------|-----------|
| Translation Model | GPT-4o, GPT-4o-mini, GPT-3.5 | GPT-4o-mini | 16x cheaper than GPT-4o, sufficient quality |
| Caching Strategy | Client-side, Server-side, Both | Client-side | Simplicity, zero cost, privacy |
| RTL Support | Logical properties, Separate stylesheets | Logical properties | Modern standard, maintainable |
| Error Handling | Fail fast, Retry once, Exponential backoff | Exponential backoff | Resilience to transient errors |
| Rate Limiting | None, IP-based, User-based | IP-based | Prevents abuse, simple to implement |

---

## Appendix B: API Contract Summary

**Endpoint 1**: `POST /api/v1/translate/text`

```typescript
Request: {
  text: string;              // 1-10,000 chars
  target_language: "spanish" | "urdu" | "mandarin" | "japanese" | "french" | "arabic";
  source_language?: "english";  // default: english
  preserve_technical_terms?: boolean;  // default: true
  context?: string;  // optional, max 200 chars
}

Response: {
  translated_text: string;
  target_language: string;
  model_used: string;  // e.g., "gpt-4o-mini"
  processing_time_ms: number;
}

Errors:
- 400: Invalid request (bad language code, text too long)
- 429: Rate limit exceeded (>10 req/min)
- 500: Translation failed (OpenAI API error)
```

**Endpoint 2**: `POST /api/v1/translate/response`

```typescript
Request: {
  original_response: QueryResponse;  // From RAG pipeline
  target_language: "spanish" | "urdu" | "mandarin" | "japanese" | "french" | "arabic";
}

Response: {
  translated_response: {
    answer: string;  // Translated answer text
    citations: Citation[];  // Original citations (English)
    query_metadata: object;  // Original metadata
  };
  target_language: string;
  model_used: string;
  processing_time_ms: number;
}

Errors: (same as /translate/text)
```

---

**Plan Status**: ✅ Ready for `/sp.tasks`
