# Feature Specification: Multilingual Translation for RAG-Enabled AI Book Platform

**Feature ID**: 003
**Feature Name**: Multilingual Translation
**Status**: Draft
**Created**: 2025-12-24
**Last Updated**: 2025-12-24
**Owner**: Development Team

---

## 1. Overview

### 1.1 Feature Summary

Add multilingual translation capabilities to the Physical AI & Humanoid Robotics textbook platform, enabling users to translate chatbot responses and selected book content into six supported languages: Urdu, Mandarin Chinese, Japanese, Spanish, French, and Arabic.

### 1.2 Business Context

**Problem Statement**:
The textbook content and RAG chatbot currently support English only, limiting accessibility for international students and professionals who may prefer to read technical content in their native language.

**Value Proposition**:
- **Accessibility**: Makes technical AI/robotics content accessible to non-English speakers
- **Learning Enhancement**: Allows students to understand complex concepts in their preferred language
- **Global Reach**: Expands the book's audience to international markets
- **Competitive Advantage**: Few technical books offer integrated multi-language RAG translation

**Success Metrics**:
- Translation feature usage: >20% of chatbot queries use translation
- Translation latency: <2 seconds average
- User satisfaction: >4/5 rating for translation accuracy
- Zero hallucination incidents (translations faithful to source)

### 1.3 Target Audience

**Primary Users**:
- International students studying AI/robotics
- Non-native English speakers in technical roles
- Professionals in global robotics companies

**User Personas**:
1. **Ahmed** - PhD student in Pakistan, prefers Urdu for complex concepts
2. **Yuki** - Japanese engineer, wants technical terms explained in Japanese
3. **Maria** - Spanish-speaking researcher, needs quick translations of key passages

---

## 2. Requirements

### 2.1 Functional Requirements

#### FR-1: Text Selection Translation
**Priority**: P0 (Must Have)
**Description**: Users can select text from any book page and translate it to a supported language.

**Acceptance Criteria**:
- User selects text on Docusaurus page (highlight with mouse/touch)
- Translation button/tooltip appears near selection
- User clicks translation button and selects target language
- Translated text appears in a modal or side panel
- Original text remains visible for comparison
- User can copy translated text to clipboard

**Edge Cases**:
- Empty selection → No translation button shown
- Very long selection (>5000 tokens) → Show warning, allow chunked translation
- Selection contains code blocks → Preserve code formatting, translate comments only
- Selection contains LaTeX/equations → Keep equations unchanged

---

#### FR-2: Chatbot Response Translation
**Priority**: P0 (Must Have)
**Description**: Users can request chatbot responses in a specific language or translate existing responses.

**Acceptance Criteria**:
- Language selector dropdown in chat UI (default: English)
- User can ask question with language preference pre-selected
- Chatbot generates response in English, then translates to selected language
- Translated response shows both English and target language versions
- User can toggle between original and translated text
- "Translate this response to [language]" button on each chatbot message

**Edge Cases**:
- Technical terms without direct translation → Keep original term + transliteration
- Citations/references → Keep English, add translated context
- Code snippets in response → Do not translate code, translate explanations
- Long responses → Translate in chunks, maintain coherence

---

#### FR-3: Language Selection UI
**Priority**: P0 (Must Have)
**Description**: Intuitive language selection interface integrated into existing UI.

**Acceptance Criteria**:
- Dropdown menu listing 7 languages (English + 6 target languages)
- Language names shown in both English and native script
  - Example: "Spanish (Español)", "Arabic (العربية)"
- Current selection persists in browser session (localStorage)
- Flag icons for visual recognition (optional)
- Keyboard navigation support (tab, arrow keys, enter)

**Supported Languages**:
1. English (Default)
2. Urdu (اردو)
3. Mandarin Chinese (中文)
4. Japanese (日本語)
5. Spanish (Español)
6. French (Français)
7. Arabic (العربية)

---

#### FR-4: Right-to-Left (RTL) Language Support
**Priority**: P1 (Should Have)
**Description**: Proper text rendering for RTL languages (Arabic, Urdu).

**Acceptance Criteria**:
- Translated text automatically sets `dir="rtl"` attribute
- UI elements (modals, panels) flip layout for RTL languages
- Mixed content (English + RTL) renders correctly with bidirectional text support
- No visual glitches with RTL scripts

---

#### FR-5: Translation Quality Indicators
**Priority**: P2 (Nice to Have)
**Description**: Visual indicators showing translation status and quality.

**Acceptance Criteria**:
- Loading spinner while translation is in progress
- "Translated by OpenAI GPT-4" attribution footer
- Warning for potentially complex technical translations
- Confidence score if available from API (future enhancement)

---

### 2.2 Non-Functional Requirements

#### NFR-1: Performance
- **Latency**: Translation must complete in <2 seconds for 90% of requests
- **Throughput**: Support 100 concurrent translation requests
- **Token Efficiency**: Use GPT-4-mini for cost optimization when appropriate

#### NFR-2: Reliability
- **Availability**: 99.5% uptime (same as main chatbot service)
- **Error Handling**: Graceful degradation if OpenAI API is unavailable
- **Retry Logic**: Automatic retry with exponential backoff for transient failures

#### NFR-3: Security
- **Input Validation**: Sanitize all user input before sending to OpenAI API
- **Rate Limiting**: 10 translations per minute per user (prevent abuse)
- **API Key Protection**: OpenAI keys stored in environment variables only

#### NFR-4: Scalability
- **Stateless Design**: No server-side state for translations (client-side only)
- **Caching**: Optional browser-side caching for repeated translations (future)
- **No Database**: Translations are not stored persistently

#### NFR-5: Accessibility
- **WCAG 2.1 AA Compliance**: Translation UI accessible via keyboard and screen readers
- **Font Support**: Ensure proper font rendering for all target scripts
- **Color Contrast**: Maintain readability for translated text

---

### 2.3 Constraints

**Technical Constraints**:
- Must use OpenAI API exclusively (no Google Translate, DeepL, etc.)
- Must integrate with existing FastAPI backend architecture
- Must work with Docusaurus React components
- Must not require re-embedding or modifying vector database

**Business Constraints**:
- Translation costs must stay within $0.01 per request average
- No third-party translation services (licensing/privacy)
- No offline translation support (requires internet connection)

**Regulatory Constraints**:
- Comply with OpenAI usage policies
- Respect user data privacy (no translation logs stored)

---

### 2.4 Out of Scope

The following are **explicitly not included** in this release:

- ❌ Automatic language detection (user must select language manually)
- ❌ Audio/speech translation (text-to-speech)
- ❌ Real-time collaborative translation editing
- ❌ Human-reviewed or certified translations
- ❌ Offline translation support
- ❌ Translation of entire book chapters (too expensive/slow)
- ❌ Translation memory or glossary management
- ❌ Support for languages beyond the initial 6
- ❌ OCR or image translation
- ❌ Simultaneous translation (live chat)

---

## 3. Architecture

### 3.1 System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Docusaurus/React)            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐        ┌──────────────────┐         │
│  │  Book Page       │        │  Chat Widget     │         │
│  │  - Text Selection│        │  - Language      │         │
│  │  - Translate BTN │        │    Selector      │         │
│  └────────┬─────────┘        │  - Translate BTN │         │
│           │                  └────────┬─────────┘         │
│           │                           │                    │
│           └───────────┬───────────────┘                    │
│                       │                                    │
│                       │ HTTPS/JSON                         │
│                       ▼                                    │
└───────────────────────────────────────────────────────────┘
                        │
                        │
┌───────────────────────┴──────────────────────────────────┐
│              Backend (FastAPI)                            │
├───────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────────────────────────────────┐   │
│  │         /api/v1/translate                         │   │
│  │  - POST /translate/text                           │   │
│  │  - POST /translate/response                       │   │
│  └────────────────┬─────────────────────────────────┘   │
│                   │                                       │
│  ┌────────────────▼─────────────────────────────────┐   │
│  │  TranslationService                               │   │
│  │  - translate_text()                               │   │
│  │  - validate_language()                            │   │
│  │  - build_translation_prompt()                     │   │
│  └────────────────┬─────────────────────────────────┘   │
│                   │                                       │
│                   │ OpenAI API Call                      │
│                   ▼                                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │  OpenAI Client (AsyncOpenAI)                      │   │
│  │  Model: GPT-4 or GPT-4-mini                       │   │
│  │  Temperature: 0.3 (consistent translations)       │   │
│  └──────────────────────────────────────────────────┘   │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 3.2 API Design

#### Endpoint 1: Translate Text

**Route**: `POST /api/v1/translate/text`

**Purpose**: Translate arbitrary text (from book selection or other sources)

**Request**:
```json
{
  "text": "ROS 2 is a flexible framework for writing robot software.",
  "target_language": "spanish",
  "source_language": "english",
  "preserve_technical_terms": true,
  "context": "robotics textbook"
}
```

**Response**:
```json
{
  "translated_text": "ROS 2 es un framework flexible para escribir software de robots.",
  "target_language": "spanish",
  "source_language": "english",
  "model_used": "gpt-4-turbo-preview",
  "tokens_used": 45,
  "processing_time_ms": 1234
}
```

**Error Response** (429 Too Many Requests):
```json
{
  "detail": "Translation rate limit exceeded. Please try again in 60 seconds.",
  "retry_after": 60
}
```

---

#### Endpoint 2: Translate Chatbot Response

**Route**: `POST /api/v1/translate/response`

**Purpose**: Translate a complete chatbot response with citations

**Request**:
```json
{
  "response_text": "ROS 2 is an open-source robotics middleware...",
  "citations": [
    {
      "section_title": "Introduction to ROS 2",
      "source_file": "module-1/chapter-1.md",
      "link_url": "/docs/module-1/chapter-1"
    }
  ],
  "target_language": "japanese",
  "preserve_citations": true
}
```

**Response**:
```json
{
  "translated_text": "ROS 2は、オープンソースのロボティクスミドルウェアです...",
  "citations": [
    {
      "section_title": "Introduction to ROS 2",
      "section_title_translated": "ROS 2への紹介",
      "source_file": "module-1/chapter-1.md",
      "link_url": "/docs/module-1/chapter-1"
    }
  ],
  "target_language": "japanese",
  "model_used": "gpt-4-turbo-preview",
  "tokens_used": 156,
  "processing_time_ms": 1876
}
```

---

### 3.3 Data Models

#### TranslationRequest (Pydantic Model)

```python
from pydantic import BaseModel, Field
from typing import Optional, Literal

SupportedLanguage = Literal[
    "english", "urdu", "mandarin", "japanese",
    "spanish", "french", "arabic"
]

class TranslateTextRequest(BaseModel):
    """Request model for text translation."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Text to translate"
    )
    target_language: SupportedLanguage = Field(
        ...,
        description="Target language for translation"
    )
    source_language: SupportedLanguage = Field(
        default="english",
        description="Source language (default: English)"
    )
    preserve_technical_terms: bool = Field(
        default=True,
        description="Keep technical terms in original language"
    )
    context: Optional[str] = Field(
        default=None,
        description="Context for better translation (e.g., 'robotics', 'programming')"
    )
```

#### TranslationResponse (Pydantic Model)

```python
class TranslationResponse(BaseModel):
    """Response model for translation."""

    translated_text: str = Field(..., description="Translated text")
    target_language: SupportedLanguage
    source_language: SupportedLanguage
    model_used: str = Field(..., description="OpenAI model used for translation")
    tokens_used: int = Field(..., description="Total tokens consumed")
    processing_time_ms: float = Field(..., description="Time taken in milliseconds")
```

---

### 3.4 Translation Service Logic

#### Core Translation Function

```python
class TranslationService:
    """Service for translating text using OpenAI GPT models."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.language_map = {
            "english": "English",
            "urdu": "Urdu (اردو)",
            "mandarin": "Mandarin Chinese (中文)",
            "japanese": "Japanese (日本語)",
            "spanish": "Spanish (Español)",
            "french": "French (Français)",
            "arabic": "Arabic (العربية)"
        }

    async def translate_text(
        self,
        text: str,
        target_language: str,
        source_language: str = "english",
        preserve_technical_terms: bool = True,
        context: Optional[str] = None
    ) -> dict:
        """
        Translate text from source to target language using OpenAI API.

        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code
            preserve_technical_terms: Whether to keep technical terms untranslated
            context: Domain context for better translation

        Returns:
            Dictionary with translated_text, metadata, and usage stats
        """
        # Build translation prompt
        system_prompt = self._build_system_prompt(
            source_language,
            target_language,
            preserve_technical_terms,
            context
        )

        # Call OpenAI API
        start_time = time.time()

        response = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",  # or "gpt-4" or "gpt-4-mini"
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.3,  # Low temperature for consistent translations
            max_tokens=2000
        )

        processing_time = (time.time() - start_time) * 1000

        return {
            "translated_text": response.choices[0].message.content,
            "target_language": target_language,
            "source_language": source_language,
            "model_used": response.model,
            "tokens_used": response.usage.total_tokens,
            "processing_time_ms": processing_time
        }

    def _build_system_prompt(
        self,
        source_lang: str,
        target_lang: str,
        preserve_technical: bool,
        context: Optional[str]
    ) -> str:
        """Build system prompt for translation."""

        source_name = self.language_map[source_lang]
        target_name = self.language_map[target_lang]

        prompt = f"""You are a professional technical translator specializing in AI and robotics content.

Translate the following text from {source_name} to {target_name}.

Guidelines:
1. Maintain technical accuracy - this is educational content about AI and robotics
2. Preserve the meaning and tone of the original text
3. {'Preserve technical terms (like ROS, URDF, SLAM) in English with transliteration if needed' if preserve_technical else 'Translate all terms including technical ones'}
4. Use proper terminology for the target language
5. Maintain formatting (line breaks, bullet points, etc.)
6. Do not add explanations or extra content
7. For code blocks or technical syntax, keep them unchanged
"""

        if context:
            prompt += f"\nContext: This text is from a {context} textbook.\n"

        return prompt
```

---

### 3.5 Frontend Integration

#### Language Selector Component (React)

```tsx
// src/components/translation/LanguageSelector.tsx
import React from 'react';

interface Language {
  code: string;
  name: string;
  nativeName: string;
  rtl: boolean;
}

const SUPPORTED_LANGUAGES: Language[] = [
  { code: 'english', name: 'English', nativeName: 'English', rtl: false },
  { code: 'urdu', name: 'Urdu', nativeName: 'اردو', rtl: true },
  { code: 'mandarin', name: 'Chinese', nativeName: '中文', rtl: false },
  { code: 'japanese', name: 'Japanese', nativeName: '日本語', rtl: false },
  { code: 'spanish', name: 'Spanish', nativeName: 'Español', rtl: false },
  { code: 'french', name: 'French', nativeName: 'Français', rtl: false },
  { code: 'arabic', name: 'Arabic', nativeName: 'العربية', rtl: true },
];

export function LanguageSelector({
  onLanguageChange
}: {
  onLanguageChange: (lang: string) => void
}) {
  const [selectedLang, setSelectedLang] = React.useState('english');

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newLang = e.target.value;
    setSelectedLang(newLang);
    onLanguageChange(newLang);
    localStorage.setItem('preferred_language', newLang);
  };

  React.useEffect(() => {
    const savedLang = localStorage.getItem('preferred_language');
    if (savedLang && SUPPORTED_LANGUAGES.some(l => l.code === savedLang)) {
      setSelectedLang(savedLang);
    }
  }, []);

  return (
    <select
      value={selectedLang}
      onChange={handleChange}
      className="language-selector"
      aria-label="Select language"
    >
      {SUPPORTED_LANGUAGES.map(lang => (
        <option key={lang.code} value={lang.code}>
          {lang.name} ({lang.nativeName})
        </option>
      ))}
    </select>
  );
}
```

#### Text Selection Translation Component

```tsx
// src/components/translation/TextSelectionTranslator.tsx
import React from 'react';
import { translateText } from '@site/src/utils/translation-api';

export function TextSelectionTranslator() {
  const [selectedText, setSelectedText] = React.useState('');
  const [translation, setTranslation] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);

  React.useEffect(() => {
    const handleSelection = () => {
      const selection = window.getSelection();
      const text = selection?.toString().trim();
      if (text && text.length > 0) {
        setSelectedText(text);
      }
    };

    document.addEventListener('mouseup', handleSelection);
    document.addEventListener('touchend', handleSelection);

    return () => {
      document.removeEventListener('mouseup', handleSelection);
      document.removeEventListener('touchend', handleSelection);
    };
  }, []);

  const handleTranslate = async (targetLang: string) => {
    if (!selectedText) return;

    setLoading(true);
    try {
      const result = await translateText({
        text: selectedText,
        target_language: targetLang,
        context: 'robotics textbook'
      });
      setTranslation(result.translated_text);
    } catch (error) {
      console.error('Translation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!selectedText) return null;

  return (
    <div className="translation-tooltip">
      <button onClick={() => handleTranslate('spanish')}>
        Translate to Spanish
      </button>
      {loading && <span>Translating...</span>}
      {translation && (
        <div className="translation-result">{translation}</div>
      )}
    </div>
  );
}
```

---

## 4. User Experience

### 4.1 User Flows

#### Flow 1: Translating Selected Text

```
1. User reads book page
2. User highlights text with mouse/touch
   ↓
3. Translation tooltip appears near selection
   "Translate to [Language Dropdown] [Translate Button]"
   ↓
4. User selects target language from dropdown
   ↓
5. User clicks "Translate" button
   ↓
6. Loading spinner appears (0.5-2 seconds)
   ↓
7. Translation modal opens showing:
   - Original text (left)
   - Translated text (right)
   - "Copy Translation" button
   - "Close" button
   ↓
8. User reads translation, optionally copies text
   ↓
9. User closes modal
```

#### Flow 2: Asking Chatbot in Different Language

```
1. User opens chatbot widget
   ↓
2. User selects target language from dropdown (e.g., Japanese)
   ↓
3. User types question in English or Japanese
   ↓
4. User clicks "Send"
   ↓
5. Chatbot processes query using RAG
   ↓
6. Backend generates English answer
   ↓
7. Backend translates answer to Japanese
   ↓
8. Chatbot displays both versions:
   - Original (English) - collapsible
   - Translated (Japanese) - expanded by default
   ↓
9. User reads translated response
```

---

### 4.2 UI Mockups (Text Description)

#### Chatbot Widget with Translation

```
┌─────────────────────────────────────┐
│  Study Assistant          [X]       │
├─────────────────────────────────────┤
│                                     │
│  Language: [English ▼]              │
│                                     │
│  ┌─────────────────────────────┐  │
│  │ User: What is ROS 2?        │  │
│  └─────────────────────────────┘  │
│                                     │
│  ┌─────────────────────────────┐  │
│  │ Assistant:                   │  │
│  │ ROS 2 is an open-source...  │  │
│  │                              │  │
│  │ [Show English Original ▼]   │  │
│  │ [Translate to Japanese]     │  │
│  └─────────────────────────────┘  │
│                                     │
│  ┌─────────────────────────────┐  │
│  │ Type your question...       │  │
│  │                        [Send]│  │
│  └─────────────────────────────┘  │
└─────────────────────────────────────┘
```

#### Text Selection Translation Tooltip

```
User selects text on page:
"ROS 2 uses a Data Distribution Service (DDS)"

Tooltip appears:
┌──────────────────────────────┐
│ Translate to: [Spanish ▼]   │
│ [Translate Button]           │
└──────────────────────────────┘

After clicking "Translate":
┌───────────────────────────────────────────┐
│  Translation                         [X]  │
├───────────────────────────────────────────┤
│                                           │
│  Original (English):                      │
│  ROS 2 uses a Data Distribution Service  │
│  (DDS)                                    │
│                                           │
│  Translated (Spanish):                    │
│  ROS 2 utiliza un Servicio de           │
│  Distribución de Datos (DDS)             │
│                                           │
│  [Copy Translation]  [Close]              │
└───────────────────────────────────────────┘
```

---

## 5. Implementation Considerations

### 5.1 Technology Stack

**Backend**:
- **Framework**: FastAPI (existing)
- **Translation**: OpenAI Chat Completions API (GPT-4 or GPT-4-mini)
- **Models**:
  - `gpt-4-turbo-preview` for complex technical translations
  - `gpt-4-mini` for simple text (cost optimization)
- **Validation**: Pydantic v2
- **Async**: `AsyncOpenAI` client

**Frontend**:
- **Framework**: Docusaurus (React-based)
- **UI Components**: React hooks, custom modals
- **State Management**: React Context API for language preference
- **Storage**: localStorage for persisting language choice
- **Styling**: CSS modules with RTL support

---

### 5.2 Cost Analysis

**OpenAI API Pricing** (as of 2024):
- GPT-4-turbo: ~$0.01 per 1K input tokens, ~$0.03 per 1K output tokens
- GPT-4-mini: ~$0.0001 per 1K input tokens, ~$0.0003 per 1K output tokens

**Estimated Costs**:
- Average translation request: 200 input tokens, 300 output tokens
- Using GPT-4-turbo: $0.01 * 0.2 + $0.03 * 0.3 = $0.011 per request
- Using GPT-4-mini: $0.0001 * 0.2 + $0.0003 * 0.3 = $0.00011 per request

**Cost Optimization Strategy**:
1. Use GPT-4-mini for simple text translations (<100 words)
2. Use GPT-4-turbo for complex technical content (>100 words or RAG responses)
3. Implement client-side caching for repeated translations (future)
4. Rate limiting: 10 requests/minute/user

**Monthly Budget Estimate** (1000 users, 5 translations/user/month):
- 5000 translations/month
- Cost: 5000 * $0.001 = $5-50/month (depending on model usage)

---

### 5.3 Error Handling

**Error Scenarios**:

1. **OpenAI API Unavailable** (500/503):
   - Retry with exponential backoff (3 attempts)
   - Show user-friendly message: "Translation service temporarily unavailable"
   - Log error for monitoring

2. **Rate Limit Exceeded** (429):
   - Return error with retry-after header
   - Show message: "Too many translation requests. Please wait 60 seconds."
   - Disable translation button temporarily

3. **Invalid Language Code**:
   - Validate on backend before API call
   - Return 400 Bad Request with clear message
   - Frontend prevents this with dropdown validation

4. **Text Too Long** (>10,000 characters):
   - Reject on backend with 413 Payload Too Large
   - Show message: "Selected text is too long. Please select smaller portions."

5. **Network Timeout**:
   - Set timeout of 10 seconds for API calls
   - Show message: "Translation timed out. Please try again."

---

### 5.4 Testing Strategy

**Unit Tests**:
- `test_translation_service.py`: Test translation service methods
- `test_language_validation.py`: Test language code validation
- `test_prompt_building.py`: Test system prompt construction

**Integration Tests**:
- `test_translate_endpoint.py`: Test API endpoints end-to-end
- `test_openai_integration.py`: Test OpenAI API integration (mocked)

**End-to-End Tests**:
- `test_text_selection_translation.e2e.ts`: Test full text selection → translation flow
- `test_chatbot_translation.e2e.ts`: Test chatbot response translation

**Manual Testing**:
- Test all 6 target languages
- Test RTL languages (Arabic, Urdu) for UI rendering
- Test long text selections
- Test technical content accuracy

---

### 5.5 Monitoring & Observability

**Metrics to Track**:
- Translation request count (by language)
- Average latency (p50, p95, p99)
- Error rate (by error type)
- Token usage (cost tracking)
- Language preference distribution

**Logging**:
- Log all translation requests (text length, language, model used)
- Log errors with full context (user ID if available, error type, timestamp)
- Log translation latency for performance analysis

**Alerts**:
- Alert if error rate >5%
- Alert if average latency >3 seconds
- Alert if OpenAI API cost exceeds budget threshold

---

## 6. Security & Privacy

### 6.1 Data Privacy

**Principles**:
- No translation content is stored in database
- Translations are stateless (request-response only)
- OpenAI API logs are subject to OpenAI's privacy policy
- No user-identifiable information sent to OpenAI

**User Consent**:
- Display disclaimer: "Translations are generated by AI and sent to OpenAI for processing"
- Link to OpenAI privacy policy
- User can opt out by not using translation feature

---

### 6.2 Input Validation

**Backend Validation**:
```python
@field_validator("text")
@classmethod
def validate_text(cls, v: str) -> str:
    """Validate and sanitize translation text."""
    # Remove excessive whitespace
    v = v.strip()

    # Check length
    if len(v) < 1:
        raise ValueError("Text cannot be empty")
    if len(v) > 10000:
        raise ValueError("Text exceeds maximum length of 10,000 characters")

    # Check for malicious content
    if any(pattern in v.lower() for pattern in ["<script", "javascript:", "eval("]):
        raise ValueError("Text contains potentially malicious content")

    return v
```

---

### 6.3 Rate Limiting

**Implementation**:
```python
from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/translate/text")
@limiter.limit("10/minute")
async def translate_text_endpoint(
    request: Request,
    data: TranslateTextRequest
) -> TranslationResponse:
    # Translation logic
    pass
```

**Rate Limits**:
- Text translation: 10 requests/minute/IP
- Response translation: 10 requests/minute/IP
- Burst allowance: 3 requests (can exceed limit briefly)

---

## 7. Rollout Plan

### 7.1 Phased Rollout

**Phase 1: Internal Testing** (Week 1)
- Deploy to staging environment
- Test all 6 languages with team
- Fix bugs and refine prompts

**Phase 2: Beta Release** (Week 2-3)
- Enable for 10% of users (feature flag)
- Collect feedback via survey
- Monitor error rates and latency

**Phase 3: General Availability** (Week 4)
- Enable for all users
- Announce feature in documentation
- Publish blog post with usage examples

---

### 7.2 Success Criteria for Launch

**Must Have**:
- [ ] Translation latency <2 seconds (p95)
- [ ] Error rate <1%
- [ ] All 6 languages tested and working
- [ ] RTL languages render correctly
- [ ] Rate limiting prevents abuse

**Nice to Have**:
- [ ] User feedback >4/5 stars
- [ ] Translation accuracy >90% (sampled manually)
- [ ] Cost per translation <$0.01

---

## 8. Future Enhancements

### 8.1 Roadmap (Post-MVP)

**Version 2.0** (3-6 months):
- Browser-side translation caching (IndexedDB)
- Automatic language detection (detect input language)
- Translation glossary for technical terms
- User feedback mechanism ("Was this translation helpful?")

**Version 3.0** (6-12 months):
- Support for 10+ additional languages
- Translation memory (reuse previous translations)
- Custom terminology dictionaries per book module
- Audio translation (text-to-speech)

**Version 4.0** (12+ months):
- Real-time collaborative translation editing
- Community-contributed translation improvements
- Offline translation support (pre-downloaded models)

---

## 9. Dependencies

### 9.1 Internal Dependencies

**Backend**:
- Existing FastAPI application structure
- OpenAI client configuration
- Request/response models framework
- Logging infrastructure

**Frontend**:
- Docusaurus React components
- Chat widget integration
- Text selection detection mechanism

---

### 9.2 External Dependencies

**Required**:
- OpenAI API (Chat Completions)
- Internet connectivity (no offline support)

**Optional**:
- Font CDN for proper script rendering (Google Fonts)

---

## 10. Open Questions

1. **Q**: Should we support mixed-language input (e.g., English question with Spanish keywords)?
   **A**: Not in MVP. User must select language explicitly.

2. **Q**: How do we handle code blocks in translations?
   **A**: Keep code unchanged, translate only comments and explanations.

3. **Q**: Should translations be cached server-side to reduce costs?
   **A**: No, keep backend stateless. Client-side caching in future version.

4. **Q**: What if OpenAI API is down during critical use?
   **A**: Graceful degradation - show English content with "Translation unavailable" message.

5. **Q**: How do we measure translation quality/accuracy?
   **A**: Manual sampling + user feedback in future versions. MVP relies on GPT-4 quality.

---

## 11. Appendix

### 11.1 Language Metadata

```json
{
  "supported_languages": [
    {
      "code": "english",
      "name": "English",
      "native_name": "English",
      "iso_639_1": "en",
      "rtl": false,
      "font_family": "system-ui"
    },
    {
      "code": "urdu",
      "name": "Urdu",
      "native_name": "اردو",
      "iso_639_1": "ur",
      "rtl": true,
      "font_family": "Noto Nastaliq Urdu, serif"
    },
    {
      "code": "mandarin",
      "name": "Chinese (Mandarin)",
      "native_name": "中文",
      "iso_639_1": "zh",
      "rtl": false,
      "font_family": "Noto Sans SC, sans-serif"
    },
    {
      "code": "japanese",
      "name": "Japanese",
      "native_name": "日本語",
      "iso_639_1": "ja",
      "rtl": false,
      "font_family": "Noto Sans JP, sans-serif"
    },
    {
      "code": "spanish",
      "name": "Spanish",
      "native_name": "Español",
      "iso_639_1": "es",
      "rtl": false,
      "font_family": "system-ui"
    },
    {
      "code": "french",
      "name": "French",
      "native_name": "Français",
      "iso_639_1": "fr",
      "rtl": false,
      "font_family": "system-ui"
    },
    {
      "code": "arabic",
      "name": "Arabic",
      "native_name": "العربية",
      "iso_639_1": "ar",
      "rtl": true,
      "font_family": "Noto Sans Arabic, sans-serif"
    }
  ]
}
```

---

### 11.2 Example Translation Prompts

**System Prompt for Technical Translation**:
```
You are a professional technical translator specializing in AI and robotics content.

Translate the following text from English to Spanish (Español).

Guidelines:
1. Maintain technical accuracy - this is educational content about AI and robotics
2. Preserve the meaning and tone of the original text
3. Preserve technical terms (like ROS, URDF, SLAM) in English with transliteration if needed
4. Use proper terminology for the target language
5. Maintain formatting (line breaks, bullet points, etc.)
6. Do not add explanations or extra content
7. For code blocks or technical syntax, keep them unchanged

Context: This text is from a robotics textbook.
```

**User Prompt (Example)**:
```
ROS 2 is a flexible framework for writing robot software. It is a collection of tools, libraries, and conventions that aim to simplify the task of creating complex and robust robot behavior across a wide variety of robotic platforms.
```

**Expected Translation (Spanish)**:
```
ROS 2 es un framework flexible para escribir software de robots. Es una colección de herramientas, bibliotecas y convenciones que tienen como objetivo simplificar la tarea de crear comportamiento robótico complejo y robusto en una amplia variedad de plataformas robóticas.
```

---

## 12. Acceptance Criteria Summary

**Definition of Done**:

1. **Backend**:
   - [ ] POST `/api/v1/translate/text` endpoint implemented
   - [ ] POST `/api/v1/translate/response` endpoint implemented
   - [ ] TranslationService class with OpenAI integration
   - [ ] Input validation for all 6 target languages
   - [ ] Error handling with retry logic
   - [ ] Rate limiting (10 req/min/user)
   - [ ] Unit tests with >80% coverage

2. **Frontend**:
   - [ ] Language selector dropdown component
   - [ ] Text selection translation tooltip
   - [ ] Chatbot response translation UI
   - [ ] Translation modal/panel
   - [ ] RTL support for Arabic and Urdu
   - [ ] LocalStorage for language preference
   - [ ] Loading states and error messages

3. **Documentation**:
   - [ ] API documentation (OpenAPI/Swagger)
   - [ ] User guide (how to use translation feature)
   - [ ] Architecture diagram
   - [ ] Troubleshooting guide

4. **Testing**:
   - [ ] All 6 languages tested manually
   - [ ] Unit tests passing
   - [ ] Integration tests passing
   - [ ] E2E tests passing
   - [ ] Performance test (latency <2s)

5. **Deployment**:
   - [ ] Deployed to staging and tested
   - [ ] Feature flag implemented
   - [ ] Monitoring and alerts configured
   - [ ] Rollout plan executed

---

**End of Specification**

---

**Revision History**:
- **v1.0** (2025-12-24): Initial specification created
