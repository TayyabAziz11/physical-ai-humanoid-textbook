# Developer Guide: Multilingual Translation Feature

This guide provides technical documentation for developers working with or extending the multilingual translation feature.

## Architecture Overview

The translation feature is a full-stack implementation with three main components:

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Docusaurus/React)                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │ Language Selector │  │ Text Selection   │  │ Translation  │  │
│  │ Component         │  │ Handler          │  │ Modal        │  │
│  └────────┬─────────┘  └────────┬─────────┘  └──────▲───────┘  │
│           │                     │                    │          │
│           └──────────┬──────────┘                    │          │
│                      │                               │          │
│              ┌───────▼────────┐                      │          │
│              │ useTranslation │                      │          │
│              │ Hook           │                      │          │
│              └───────┬────────┘                      │          │
│                      │                               │          │
│              ┌───────▼────────┐                      │          │
│              │ localStorage   │──────────────────────┘          │
│              │ Cache          │                                 │
│              └────────────────┘                                 │
└──────────────────────┬──────────────────────────────────────────┘
                       │ HTTP/JSON
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│                  BACKEND (FastAPI on Railway)                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              API v1 Router (/api/v1)                     │  │
│  │  ┌─────────────────┐    ┌──────────────────┐           │  │
│  │  │ Rate Limiter    │───▶│ Translation      │           │  │
│  │  │ (10 req/min/IP) │    │ Endpoint         │           │  │
│  │  └─────────────────┘    └────────┬─────────┘           │  │
│  └──────────────────────────────────┼──────────────────────┘  │
│                                     │                          │
│                             ┌───────▼────────┐                 │
│                             │ Translation    │                 │
│                             │ Service        │                 │
│                             └───────┬────────┘                 │
│                                     │                          │
└─────────────────────────────────────┼──────────────────────────┘
                                      │
                              ┌───────▼────────┐
                              │ OpenAI API     │
                              │ GPT-4o-mini    │
                              └────────────────┘
```

## Technology Stack

### Backend
- **Framework**: FastAPI 0.104+
- **AI Model**: OpenAI GPT-4o-mini
- **Client**: AsyncOpenAI Python SDK
- **Validation**: Pydantic v2
- **Testing**: pytest
- **Deployment**: Railway

### Frontend
- **Framework**: Docusaurus 3.x
- **UI Library**: React 18
- **Language**: TypeScript 5.x
- **Styling**: CSS Modules
- **Testing**: Jest + React Testing Library (planned)
- **Deployment**: GitHub Pages

## Project Structure

```
physical-ai-humanoid-textbook/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/
│   │   │   └── translate.py          # Translation endpoints
│   │   ├── middleware/
│   │   │   └── rate_limit.py         # Rate limiting middleware
│   │   ├── models/
│   │   │   ├── request.py            # Request models
│   │   │   └── translation.py        # Response models + language types
│   │   ├── services/
│   │   │   └── translation.py        # TranslationService with OpenAI
│   │   └── main.py                   # FastAPI app
│   └── tests/
│       ├── api/                      # Endpoint tests
│       ├── middleware/               # Rate limiter tests
│       ├── models/                   # Model tests
│       └── services/                 # Service tests
├── src/
│   ├── components/translation/
│   │   ├── LanguageSelector.tsx      # Language dropdown
│   │   ├── TranslationModal.tsx      # Translation display
│   │   ├── TranslateButton.tsx       # Floating button
│   │   └── TextSelectionHandler.tsx  # Main orchestrator
│   ├── hooks/
│   │   ├── useTranslation.ts         # Main translation hook
│   │   └── useTranslationCache.ts    # Cache management
│   ├── utils/
│   │   ├── languageMetadata.ts       # Language types + metadata
│   │   ├── apiClient.ts              # API client
│   │   └── selection.ts              # Text selection utilities
│   └── theme/
│       └── Root.tsx                  # Docusaurus root with handler
├── docs/
│   ├── translation.md                # User documentation
│   └── developer-guide-translation.md # This file
└── specs/003-multilingual-translation/
    ├── spec.md                       # Feature specification
    ├── plan.md                       # Architecture plan
    └── tasks.md                      # Task breakdown
```

## Backend API

### Endpoint: POST /api/v1/translate/text

Translates text from one language to another.

**Request Body**:
```json
{
  "text": "string (1-10000 chars)",
  "target_language": "english | urdu | mandarin | japanese | spanish | french | arabic",
  "source_language": "english (optional, default: english)",
  "preserve_technical_terms": "boolean (optional, default: true)",
  "context": "string (optional, max 200 chars)"
}
```

**Response (200 OK)**:
```json
{
  "original_text": "string",
  "translated_text": "string",
  "source_language": "string",
  "target_language": "string",
  "rtl": "boolean"
}
```

**Error Responses**:
- `422 Unprocessable Entity`: Validation error (empty text, unsupported language, text too long)
- `429 Too Many Requests`: Rate limit exceeded (10 requests/minute/IP)
- `502 Bad Gateway`: Translation service error (OpenAI API failure)

**Rate Limiting**:
- Limit: 10 requests per minute per IP address
- Window: 60 seconds (sliding window)
- Applies to: All `/api/v1/translate/*` endpoints

### Translation Service

**Location**: `backend/app/services/translation.py`

**Key Components**:
```python
class TranslationService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"
        self.max_retries = 3
        self.base_delay = 1.0

    async def translate(
        self,
        text: str,
        source_language: SupportedLanguage,
        target_language: SupportedLanguage,
        preserve_technical_terms: bool = True
    ) -> dict:
        """
        Translate text with retry logic and exponential backoff.

        Returns:
            dict with keys: original_text, translated_text,
                           source_language, target_language
        """
```

**Features**:
- Exponential backoff retry (1s, 2s, 4s)
- Retries on: Rate limits, 500/502/503/504 errors, network timeouts
- No retry on: 401, 400, 413
- Custom error class: `TranslationServiceError`

## Frontend Components

### 1. LanguageSelector Component

**Location**: `src/components/translation/LanguageSelector.tsx`

**Props**:
```typescript
interface LanguageSelectorProps {
  currentLanguage: SupportedLanguage;
  onLanguageChange: (language: SupportedLanguage) => void;
  className?: string;
  label?: string;
  showLabel?: boolean;
}
```

**Usage**:
```tsx
<LanguageSelector
  currentLanguage={selectedLanguage}
  onLanguageChange={setSelectedLanguage}
/>
```

### 2. TranslationModal Component

**Location**: `src/components/translation/TranslationModal.tsx`

**Props**:
```typescript
interface TranslationModalProps {
  result: TranslationResult;
  onClose: () => void;
  showOriginal?: boolean;
}
```

**Features**:
- Side-by-side original/translated text
- RTL support via `dir` attribute
- Copy to clipboard
- Cache status indicator
- Keyboard navigation (Escape to close)

### 3. TextSelectionHandler Component

**Location**: `src/components/translation/TextSelectionHandler.tsx`

**Description**: Main orchestrator component that handles text selection events and coordinates all subcomponents.

**Features**:
- Text selection detection with debouncing (100ms)
- Selection validation (max 1500 characters)
- Language preference persistence in localStorage
- Error handling with user-friendly messages
- Click-outside to close

**Integration**:
```tsx
// In src/theme/Root.tsx
import TextSelectionHandler from '@site/src/components/translation/TextSelectionHandler';

export default function Root({ children }) {
  return (
    <>
      {children}
      <TextSelectionHandler />
    </>
  );
}
```

## Hooks

### useTranslation Hook

**Location**: `src/hooks/useTranslation.ts`

**API**:
```typescript
const {
  translate,      // (text, targetLang, options?) => Promise<TranslationResult | null>
  isTranslating,  // boolean
  error,          // string | null
  clearError,     // () => void
  clearCache,     // (targetLang?) => void
  getCacheStats,  // () => Record<SupportedLanguage, number>
} = useTranslation();
```

**Usage**:
```tsx
const { translate, isTranslating, error } = useTranslation();

const handleTranslate = async () => {
  const result = await translate("Hello world", "spanish");
  if (result) {
    console.log(result.translated_text); // "Hola mundo"
    console.log(result.fromCache);       // true/false
  }
};
```

### useTranslationCache Hook

**Location**: `src/hooks/useTranslationCache.ts`

**API**:
```typescript
const {
  get,        // (text, targetLang) => CacheEntry | null
  set,        // (text, targetLang, translatedText, sourceLang, rtl) => void
  clear,      // (targetLang?) => void
  getStats,   // () => Record<SupportedLanguage, number>
} = useTranslationCache();
```

**Cache Configuration**:
- **TTL**: 7 days (604,800,000 ms)
- **Max Entries**: 50 per language
- **Eviction Strategy**: LRU (Least Recently Used)
- **Storage**: localStorage with djb2 hash keys

## Data Flow

### Translation Request Flow

```
1. User selects text
   ↓
2. TextSelectionHandler detects selection
   ↓
3. User clicks Translate button
   ↓
4. useTranslation.translate() called
   ↓
5. Check cache (useTranslationCache.get())
   ├─ Cache HIT → Return immediately
   └─ Cache MISS → Continue to API
   ↓
6. translateText() API call (fetch)
   ↓
7. Backend: Rate limiter check
   ↓
8. Backend: TranslationService.translate()
   ↓
9. Backend: OpenAI API call (with retry logic)
   ↓
10. Response returned to frontend
   ↓
11. Cache result (useTranslationCache.set())
   ↓
12. Display TranslationModal
```

### Caching Strategy

**Cache Key Generation**:
```typescript
// Uses djb2 hash algorithm
function generateCacheKey(text: string, targetLanguage: SupportedLanguage): string {
  let hash = 5381;
  for (let i = 0; i < text.length; i++) {
    hash = (hash * 33) ^ text.charCodeAt(i);
  }
  return `translation_cache_${targetLanguage}_${hash >>> 0}`;
}
```

**Cache Entry Structure**:
```typescript
interface CacheEntry {
  originalText: string;
  translatedText: string;
  targetLanguage: SupportedLanguage;
  sourceLanguage: SupportedLanguage;
  timestamp: number;  // milliseconds since epoch
  rtl: boolean;
}
```

**Eviction Logic**:
1. On cache write, check entry count for target language
2. If > 50 entries, fetch all entries and sort by timestamp
3. Remove oldest entries until count ≤ 50
4. Expired entries (> 7 days old) removed automatically on read

## Environment Variables

### Backend (Required)

```bash
# OpenAI API Key (required)
OPENAI_API_KEY=sk-...

# Optional: Backend URL for CORS (default: allow all)
BACKEND_URL=https://your-backend.railway.app

# Optional: Port (default: 8000)
PORT=8000
```

### Frontend (Optional)

```javascript
// In docusaurus.config.js or set via window object
window.__TRANSLATION_API_BASE_URL__ = 'https://your-backend.railway.app';
```

If not set, defaults to: `https://physical-ai-humanoid-textbook-production.up.railway.app`

## Running Locally

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export OPENAI_API_KEY=sk-...

# Run development server
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: `http://localhost:8000`

API docs: `http://localhost:8000/docs`

### Frontend Setup

```bash
# Install dependencies
npm install

# Run development server
npm start
```

Frontend will be available at: `http://localhost:3000`

### Testing Backend

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/api/test_translate_endpoints.py -v
```

Current test coverage: **85+ tests passing**

## Extending Language Support

To add a new language:

### 1. Update Backend

**File**: `backend/app/models/translation.py`

```python
# Add new language to Literal type
SupportedLanguage = Literal[
    "english",
    "urdu",
    "mandarin",
    "japanese",
    "spanish",
    "french",
    "arabic",
    "german",  # NEW LANGUAGE
]

# Add to language metadata dictionary
LANGUAGE_METADATA: dict[SupportedLanguage, LanguageMetadata] = {
    # ... existing languages ...
    "german": LanguageMetadata(
        name="German",
        native_name="Deutsch",
        rtl=False
    ),
}
```

### 2. Update Frontend

**File**: `src/utils/languageMetadata.ts`

```typescript
export type SupportedLanguage =
  | 'english'
  | 'urdu'
  | 'mandarin'
  | 'japanese'
  | 'spanish'
  | 'french'
  | 'arabic'
  | 'german';  // NEW LANGUAGE

export const SUPPORTED_LANGUAGES: readonly LanguageInfo[] = [
  // ... existing languages ...
  {
    code: 'german',
    name: 'German',
    nativeName: 'Deutsch',
    rtl: false,
    flag: '🇩🇪',
  },
];
```

### 3. Update Tests

Add test cases for the new language in:
- `backend/tests/models/test_translation_models.py`
- `backend/tests/api/test_translate_endpoints.py`
- Frontend component tests (when implemented)

### 4. Update Documentation

Update `docs/translation.md` supported languages table.

## Performance Optimization

### Frontend

**Current Optimizations**:
- Debounced selection events (100ms)
- Memoized components
- CSS animations with GPU acceleration
- Lazy loading of translation modal

**Future Optimizations**:
- Code splitting for translation components
- Virtual scrolling for long translations
- Web Workers for cache operations

### Backend

**Current Optimizations**:
- Async/await for non-blocking I/O
- Sliding window rate limiting (in-memory)
- Retry logic with exponential backoff

**Future Optimizations**:
- Redis for distributed rate limiting
- Prometheus metrics
- CDN caching for static responses

## Deployment

### Backend (Railway)

Current deployment: `https://physical-ai-humanoid-textbook-production.up.railway.app`

**Deployment Steps**:
1. Push to `main` branch
2. Railway automatically builds and deploys
3. Environment variables configured in Railway dashboard

**Health Check**: `GET /health` (returns 200 OK)

### Frontend (GitHub Pages)

Current deployment: `https://[username].github.io/physical-ai-humanoid-textbook/`

**Deployment Steps**:
```bash
# Build for production
npm run build

# Deploy to GitHub Pages
npm run deploy
```

**Configuration** (`docusaurus.config.js`):
```javascript
const config = {
  url: 'https://[username].github.io',
  baseUrl: '/physical-ai-humanoid-textbook/',
  deploymentBranch: 'gh-pages',
};
```

## Troubleshooting

### Backend Issues

**OpenAI API errors**:
- Check API key is valid and has credits
- Verify network connectivity
- Check OpenAI status page

**Rate limiting not working**:
- Verify IP extraction logic in rate limiter
- Check for proxy/load balancer forwarding headers

**Tests failing**:
- Ensure `.env` file is NOT committed
- Check Python version (requires 3.11+)
- Verify all dependencies installed

### Frontend Issues

**TypeScript errors**:
- Run `npm run build` to check for type errors
- Ensure `tsconfig.json` includes all necessary paths

**Components not rendering**:
- Check browser console for errors
- Verify Docusaurus version compatibility
- Check for CSS module import issues

**Translations not working in production**:
- Verify backend URL is correctly configured
- Check CORS settings on backend
- Inspect network tab for failed requests

## Testing Strategy

### Backend Tests

**Current Coverage**: 85+ tests

**Test Types**:
- **Unit Tests**: Models, services, utilities
- **Integration Tests**: Endpoints with mocked TranslationService
- **E2E Tests**: Full translation flow (planned)

**Key Test Files**:
- `tests/models/test_translation_models.py` (43 tests)
- `tests/services/test_translation_service.py` (11 tests)
- `tests/api/test_translate_endpoints.py` (18 tests)
- `tests/middleware/test_rate_limit.py` (10 tests)
- `tests/api/test_rate_limiting_integration.py` (3 tests)

### Frontend Tests (Planned - Phase 5.6)

**Target Coverage**:
- Components: ≥75%
- Hooks: ≥80%

**Planned Test Files**:
- `src/components/translation/__tests__/LanguageSelector.test.tsx`
- `src/components/translation/__tests__/TranslationModal.test.tsx`
- `src/hooks/__tests__/useTranslation.test.ts`
- `src/hooks/__tests__/useTranslationCache.test.ts`

## Security Considerations

### Backend

- API key stored in environment variables (not in code)
- Rate limiting prevents abuse (10 req/min/IP)
- Input validation via Pydantic
- No persistent storage of user data

### Frontend

- No sensitive data in localStorage
- HTTPS-only API calls
- XSS protection via React's built-in escaping
- No eval() or dangerouslySetInnerHTML

### Privacy

- User text never logged on backend
- Translations not stored on server
- Client-side cache only (7-day TTL)
- No tracking or analytics

## Contributing

### Code Style

**Backend**:
- Follow PEP 8
- Use type hints
- Docstrings for all public functions

**Frontend**:
- Follow Airbnb React/TypeScript style guide
- Use functional components with hooks
- TypeScript strict mode enabled

### Pull Request Process

1. Create feature branch from `main`
2. Implement changes with tests
3. Run `pytest` (backend) and `npm test` (frontend)
4. Update documentation if needed
5. Submit PR with clear description
6. Pass all CI checks

## Additional Resources

- [Specification](https://github.com/TayyabAziz11/physical-ai-humanoid-textbook/blob/main/specs/003-multilingual-translation/spec.md)
- [Architecture Plan](https://github.com/TayyabAziz11/physical-ai-humanoid-textbook/blob/main/specs/003-multilingual-translation/plan.md)
- [Task Breakdown](https://github.com/TayyabAziz11/physical-ai-humanoid-textbook/blob/main/specs/003-multilingual-translation/tasks.md)
- [User Documentation](translation.md)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [Docusaurus Documentation](https://docusaurus.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Questions or Issues?**

Please open an issue on GitHub or contact the maintainers.
