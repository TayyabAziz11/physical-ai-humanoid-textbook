---
id: 0001
title: "Multilingual Translation Specification"
stage: spec
date: 2025-12-25
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-multilingual-translation
branch: 003-multilingual-translation
user: user
command: /sp.specify
labels: ["translation", "i18n", "openai", "docusaurus", "rag", "rtl-support"]
links:
  spec: specs/003-multilingual-translation/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-multilingual-translation/spec.md
tests:
  - Specification completeness review
  - API contract validation
  - Frontend component design review
---

## Prompt

```text
Multilingual Translation Feature for RAG-Enabled AI Book Platform

Project context:
An AI/spec-driven book written using Docusaurus and deployed on GitHub Pages.
The book includes an embedded Retrieval-Augmented Generation (RAG) chatbot built with:
- OpenAI Agents / Chatkit SDK
- FastAPI backend
- Neon Serverless Postgres
- Qdrant Cloud (Free Tier)

Target audience:
Readers of the published book, including students and professionals, who want to understand the content in multiple languages.

Objective:
Enable users to translate book content and chatbot responses into multiple languages, including translating only user-selected text from the book.

Supported languages:
- Urdu
- Mandarin Chinese
- Japanese
- Spanish
- French
- Arabic

Core requirements:
- Users can translate:
  - Entire chatbot responses
  - Selected text from the book page
- Translation must preserve meaning and technical accuracy
- Translation must work with RAG-based answers derived from:
  - Full book content
  - User-highlighted text selection only

Success criteria:
- User can select text on the book page and receive a translation in any supported language
- User can ask the chatbot to translate its response into a selected language
- Translations are generated using OpenAI language models via API
- Translation works without re-embedding content
- Average translation latency under 2 seconds
- No data loss or hallucination beyond original content

Constraints:
- Backend: FastAPI
- Frontend: Docusaurus (React-based)
- Must integrate cleanly with existing RAG pipeline
- Translation must be stateless (no long-term storage required)
- Use OpenAI APIs only (no third-party translation services)
- Must support right-to-left (RTL) languages such as Arabic and Urdu

Out of scope:
- Human-reviewed or certified translations
- Offline translation support
- Audio or speech translation
- Automatic language detection (user selects language manually)

Deliverables:
- API endpoints for translation
- Frontend UI controls (language selector + translate button)
- Integration with chatbot and text-selection workflow
- Markdown documentation explaining usage and architecture
```

## Response snapshot

### Specification Created

**File**: `specs/003-multilingual-translation/spec.md`

**Comprehensive 35+ page specification** covering:

#### 1. Overview
- Feature name: Multilingual Translation for RAG-Enabled AI Book Platform
- 6 supported languages: Urdu, Mandarin Chinese, Japanese, Spanish, French, Arabic
- Stateless translation using OpenAI API only
- Target latency: <2 seconds per translation

#### 2. Requirements
**Functional Requirements (FR)**:
- FR-1: Text Selection Translation (P0) - Translate user-selected book text
- FR-2: Chatbot Response Translation (P0) - Translate AI chatbot responses
- FR-3: Language Selection UI (P0) - Dropdown selector with native names
- FR-4: RTL Language Support (P1) - CSS `dir="rtl"` for Arabic/Urdu
- FR-5: Translation History (P2) - Client-side localStorage cache
- FR-6: Copy/Share Translations (P2) - Export functionality

**Non-Functional Requirements (NFR)**:
- NFR-1: Performance - <2s latency, concurrent requests
- NFR-2: Cost Optimization - Use GPT-4-mini, cache where possible
- NFR-3: Security - Rate limiting (10 req/min/user), input validation
- NFR-4: Accuracy - Temperature 0.3, preserve technical terms
- NFR-5: Accessibility - WCAG 2.1 AA compliance

#### 3. API Design
**Endpoint 1**: `POST /api/v1/translate/text`
```python
Request:
{
  "text": "ROS 2 is a flexible framework...",
  "target_language": "spanish",
  "source_language": "english",
  "preserve_technical_terms": true,
  "context": "robotics textbook"
}

Response:
{
  "translated_text": "ROS 2 es un framework flexible...",
  "target_language": "spanish",
  "model_used": "gpt-4-turbo-preview",
  "tokens_used": 45,
  "processing_time_ms": 1234
}
```

**Endpoint 2**: `POST /api/v1/translate/response`
```python
Request:
{
  "original_response": {...},
  "target_language": "urdu"
}

Response:
{
  "translated_response": {...},
  "target_language": "urdu",
  "model_used": "gpt-4-mini",
  "tokens_used": 178
}
```

#### 4. Data Models
```python
from typing import Literal

SupportedLanguage = Literal[
    "english", "urdu", "mandarin", "japanese",
    "spanish", "french", "arabic"
]

class TranslateTextRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    target_language: SupportedLanguage
    source_language: SupportedLanguage = Field(default="english")
    preserve_technical_terms: bool = Field(default=True)
    context: Optional[str] = None
```

#### 5. Backend Implementation
**Translation Service**:
```python
class TranslationService:
    async def translate_text(
        self,
        text: str,
        target_language: str,
        source_language: str = "english",
        preserve_technical_terms: bool = True,
        context: Optional[str] = None
    ) -> dict:
        system_prompt = self._build_system_prompt(
            target_language, source_language,
            preserve_technical_terms, context
        )

        response = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.3,
            max_tokens=2000
        )

        return {
            "translated_text": response.choices[0].message.content,
            "target_language": target_language,
            "model_used": response.model,
            "tokens_used": response.usage.total_tokens
        }
```

#### 6. Frontend Implementation
**Language Selector Component**:
```tsx
const SUPPORTED_LANGUAGES: Language[] = [
  { code: 'english', name: 'English', nativeName: 'English', rtl: false },
  { code: 'urdu', name: 'Urdu', nativeName: 'اردو', rtl: true },
  { code: 'mandarin', name: 'Chinese', nativeName: '中文', rtl: false },
  { code: 'japanese', name: 'Japanese', nativeName: '日本語', rtl: false },
  { code: 'spanish', name: 'Spanish', nativeName: 'Español', rtl: false },
  { code: 'french', name: 'French', nativeName: 'Français', rtl: false },
  { code: 'arabic', name: 'Arabic', nativeName: 'العربية', rtl: true },
];
```

**Text Selection Translation**:
```tsx
const handleTranslateSelection = async () => {
  const selectedText = window.getSelection()?.toString();
  if (!selectedText) return;

  const response = await fetch(`${API_URL}/api/v1/translate/text`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: selectedText,
      target_language: currentLanguage,
      source_language: 'english',
      preserve_technical_terms: true,
      context: 'robotics textbook'
    })
  });

  const data = await response.json();
  setTranslatedText(data.translated_text);
};
```

#### 7. Cost Analysis
**Per Translation Costs**:
- GPT-4-mini: $0.001-$0.003 (100-300 tokens)
- GPT-4-turbo: $0.005-$0.015 (100-300 tokens)
- Monthly estimate: $5-$20 (assuming 1,000-2,000 translations/month)

#### 8. Testing Strategy
- **Unit Tests**: Translation service, language selector, API endpoints
- **Integration Tests**: End-to-end translation flow, RAG + translation
- **E2E Tests**: User workflows (select text → translate, chatbot → translate)
- **Manual Tests**: RTL rendering, technical term preservation, edge cases

#### 9. Rollout Plan
**Phase 1 (Week 1-2)**: Backend API + Basic Frontend
- Implement translation service and endpoints
- Add language selector to Docusaurus

**Phase 2 (Week 3)**: Text Selection + Chatbot Integration
- Text selection translation UI
- Chatbot response translation

**Phase 3 (Week 4)**: Polish + Launch
- RTL support refinement
- Performance optimization
- Documentation
- Soft launch

## Outcome

- ✅ Impact: Created comprehensive specification for multilingual translation feature supporting 6 languages with detailed API contracts, frontend designs, cost analysis, and rollout plan
- 🧪 Tests: Specification includes testing strategy (unit, integration, E2E, manual) with specific test cases for RTL support, technical term preservation, and rate limiting
- 📁 Files: Created specs/003-multilingual-translation/spec.md (35+ pages)
- 🔁 Next prompts: Run /sp.plan to create architectural plan, then /sp.tasks for implementation breakdown
- 🧠 Reflection: Specification is thorough and production-ready. Key architectural decisions needed: (1) Model selection strategy (GPT-4 vs GPT-4-mini), (2) Client-side vs server-side caching, (3) RTL CSS approach. These should be documented in ADRs during planning phase.

## Evaluation notes (flywheel)

- Failure modes observed: None during spec creation. Potential runtime concerns: OpenAI API latency spikes, cost overruns if usage exceeds estimates, RTL rendering bugs in Docusaurus.
- Graders run and results (PASS/FAIL): PASS - Specification is complete, requirements are clear and testable, API contracts are well-defined, cost analysis is included, security and performance requirements are specified.
- Prompt variant (if applicable): N/A - Standard /sp.specify workflow
- Next experiment (smallest change to try): During /sp.plan phase, evaluate whether to use GPT-4-mini exclusively (cost optimization) vs. GPT-4 for critical translations (quality). Could A/B test both models with sample technical content to measure quality difference vs. cost savings.
