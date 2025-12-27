# ڈویلپر گائیڈ: کثیر لسانی ترجمے کی خصوصیت

یہ رہنما ان developers کے لیے تکنیکی documentation فراہم کرتی ہے جو کثیر لسانی ترجمے کی خصوصیت کے ساتھ کام کر رہے ہیں یا اسے بڑھا رہے ہیں۔

## فن تعمیر کا جائزہ

ترجمے کی خصوصیت تین اہم اجزاء کے ساتھ ایک full-stack implementation ہے:

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

## ٹیکنالوجی اسٹیک

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
- **Testing**: Jest + React Testing Library (منصوبہ بندی)
- **Deployment**: GitHub Pages

## پروجیکٹ کی ساخت

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

ایک زبان سے دوسری زبان میں متن کا ترجمہ کرتا ہے۔

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

**خرابی کے جوابات**:
- `422 Unprocessable Entity`: Validation خرابی (خالی متن، غیر معاون زبان، متن بہت لمبا)
- `429 Too Many Requests`: Rate limit تجاوز (10 requests/minute/IP)
- `502 Bad Gateway`: Translation service خرابی (OpenAI API ناکامی)

**Rate Limiting**:
- حد: فی IP address 10 requests فی منٹ
- Window: 60 سیکنڈ (sliding window)
- لاگو ہوتا ہے: تمام `/api/v1/translate/*` endpoints پر

## ڈیٹا کا بہاؤ

### ترجمے کی Request کا بہاؤ

```
1. صارف متن منتخب کرتا ہے
   ↓
2. TextSelectionHandler انتخاب کا پتہ لگاتا ہے
   ↓
3. صارف Translate بٹن پر کلک کرتا ہے
   ↓
4. useTranslation.translate() call ہوتا ہے
   ↓
5. Cache چیک کریں (useTranslationCache.get())
   ├─ Cache HIT → فوری طور پر واپس آئیں
   └─ Cache MISS → API پر جاری رکھیں
   ↓
6. translateText() API call (fetch)
   ↓
7. Backend: Rate limiter چیک
   ↓
8. Backend: TranslationService.translate()
   ↓
9. Backend: OpenAI API call (retry logic کے ساتھ)
   ↓
10. Response frontend کو واپس
   ↓
11. نتیجہ Cache کریں (useTranslationCache.set())
   ↓
12. TranslationModal ڈسپلے کریں
```

## Environment Variables

### Backend (ضروری)

```bash
# OpenAI API Key (ضروری)
OPENAI_API_KEY=sk-...

# اختیاری: CORS کے لیے Backend URL (default: سب کو allow کریں)
BACKEND_URL=https://your-backend.railway.app

# اختیاری: Port (default: 8000)
PORT=8000
```

### Frontend (اختیاری)

```javascript
// docusaurus.config.js میں یا window object کے ذریعے set کریں
window.__TRANSLATION_API_BASE_URL__ = 'https://your-backend.railway.app';
```

اگر set نہیں کیا گیا، default: `https://physical-ai-humanoid-textbook-production.up.railway.app`

## مقامی طور پر چلانا

### Backend سیٹ اپ

```bash
# Backend directory میں navigate کریں
cd backend

# Virtual environment بنائیں
python -m venv venv
source venv/bin/activate  # Windows پر: venv\Scripts\activate

# Dependencies install کریں
pip install -r requirements.txt

# Environment variable set کریں
export OPENAI_API_KEY=sk-...

# Development server چلائیں
uvicorn app.main:app --reload --port 8000
```

Backend یہاں دستیاب ہوگا: `http://localhost:8000`

API docs: `http://localhost:8000/docs`

### Frontend سیٹ اپ

```bash
# Dependencies install کریں
npm install

# Development server چلائیں
npm start
```

Frontend یہاں دستیاب ہوگا: `http://localhost:3000`

### Backend کی جانچ

```bash
cd backend

# تمام tests چلائیں
pytest

# Coverage کے ساتھ چلائیں
pytest --cov=app --cov-report=html

# مخصوص test فائل چلائیں
pytest tests/api/test_translate_endpoints.py -v
```

موجودہ test coverage: **85+ tests پاس ہو رہے ہیں**

## زبان کی سپورٹ بڑھانا

نئی زبان شامل کرنے کے لیے:

### 1. Backend کو Update کریں

**فائل**: `backend/app/models/translation.py`

```python
# Literal type میں نئی زبان شامل کریں
SupportedLanguage = Literal[
    "english",
    "urdu",
    "mandarin",
    "japanese",
    "spanish",
    "french",
    "arabic",
    "german",  # نئی زبان
]

# Language metadata dictionary میں شامل کریں
LANGUAGE_METADATA: dict[SupportedLanguage, LanguageMetadata] = {
    # ... موجودہ زبانیں ...
    "german": LanguageMetadata(
        name="German",
        native_name="Deutsch",
        rtl=False
    ),
}
```

### 2. Frontend کو Update کریں

**فائل**: `src/utils/languageMetadata.ts`

```typescript
export type SupportedLanguage =
  | 'english'
  | 'urdu'
  | 'mandarin'
  | 'japanese'
  | 'spanish'
  | 'french'
  | 'arabic'
  | 'german';  // نئی زبان

export const SUPPORTED_LANGUAGES: readonly LanguageInfo[] = [
  // ... موجودہ زبانیں ...
  {
    code: 'german',
    name: 'German',
    nativeName: 'Deutsch',
    rtl: false,
    flag: '🇩🇪',
  },
];
```

## سیکیورٹی کے تحفظات

### Backend

- API key environment variables میں محفوظ (code میں نہیں)
- Rate limiting غلط استعمال کو روکتی ہے (10 req/min/IP)
- Pydantic کے ذریعے Input validation
- صارف کے ڈیٹا کی کوئی مستقل storage نہیں

### Frontend

- localStorage میں کوئی حساس ڈیٹا نہیں
- صرف HTTPS API calls
- React کی built-in escaping کے ذریعے XSS protection
- کوئی eval() یا dangerouslySetInnerHTML نہیں

### رازداری

- صارف کا متن backend پر log نہیں ہوتا
- ترجمے server پر محفوظ نہیں ہوتے
- صرف Client-side cache (7-day TTL)
- کوئی tracking یا analytics نہیں

## تعاون کرنا

### Code Style

**Backend**:
- PEP 8 کی پیروی کریں
- Type hints استعمال کریں
- تمام public functions کے لیے Docstrings

**Frontend**:
- Airbnb React/TypeScript style guide کی پیروی کریں
- Hooks کے ساتھ functional components استعمال کریں
- TypeScript strict mode فعال

## اضافی وسائل

- [Specification](https://github.com/TayyabAziz11/physical-ai-humanoid-textbook/blob/main/specs/003-multilingual-translation/spec.md)
- [Architecture Plan](https://github.com/TayyabAziz11/physical-ai-humanoid-textbook/blob/main/specs/003-multilingual-translation/plan.md)
- [Task Breakdown](https://github.com/TayyabAziz11/physical-ai-humanoid-textbook/blob/main/specs/003-multilingual-translation/tasks.md)
- [User Documentation](translation.md)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [Docusaurus Documentation](https://docusaurus.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**سوالات یا مسائل؟**

براہ کرم GitHub پر ایک issue کھولیں یا maintainers سے رابطہ کریں۔
