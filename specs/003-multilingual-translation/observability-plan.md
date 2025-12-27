# Observability & Monitoring Implementation Plan
**Feature**: 003-multilingual-translation
**Task**: Observability & Monitoring (New Requirement)
**Created**: 2025-12-25
**Status**: Ready for Implementation
**Estimated Effort**: 4-6 hours
**Dependencies**: Tasks 1.1-1.6, 2.1, 2.8 (all complete)

---

## Executive Summary

Add structured logging and lightweight metrics to the translation API with **ZERO new infrastructure**. Use Python's built-in logging with JSON-like structured format, generate request IDs, track translation latency, and log all critical events (retries, failures, rate limits).

**Key Principle**: Observability without complexity - no Prometheus, no external services, just clean logs and in-memory metrics.

---

## Requirements

### 1. Structured Logging

**Technology**: Python `logging` module with structured format

**Log Levels**:
- `INFO`: Successful translations
- `WARNING`: Retries, rate limit hits
- `ERROR`: OpenAI failures, TranslationServiceError

**Log Format** (JSON-like structured):
```python
{
    "timestamp": "2025-12-25T10:30:45.123Z",
    "level": "INFO",
    "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "event": "translation_success",
    "source_language": "english",
    "target_language": "spanish",
    "text_length": 150,
    "latency_ms": 892,
    "retry_count": 0
}
```

**What to Log**:
- ✅ Request ID (UUID generated per request)
- ✅ Source and target languages
- ✅ Text length (NOT the full text - privacy!)
- ✅ Translation latency in milliseconds
- ✅ Retry count (if any)
- ✅ Rate limit violations (IP, endpoint)
- ✅ OpenAI errors (sanitized, no API keys)
- ❌ User text content (privacy concern)
- ❌ API keys or secrets

### 2. Integration Points

**A. TranslationService** (`backend/app/services/translation.py`):
- Log translation start
- Log each retry attempt with reason
- Log final success with latency
- Log errors with sanitized details

**B. FastAPI Endpoint** (`backend/app/api/v1/endpoints/translate.py`):
- Generate `request_id` (UUID4)
- Attach `request_id` to all logs in request context
- Log HTTP-level errors (422, 429, 502)

**C. RateLimiter** (`backend/app/middleware/rate_limit.py`):
- Log when rate limit is exceeded
- Include IP address and endpoint path

### 3. Lightweight Metrics

**In-Memory Counters** (module-level variables):
```python
# backend/app/utils/metrics.py
translation_metrics = {
    "total_requests": 0,
    "total_successes": 0,
    "total_failures": 0,
    "total_latency_ms": 0,
    "by_language": {
        "spanish": {"count": 0, "total_latency_ms": 0},
        "french": {"count": 0, "total_latency_ms": 0},
        # ... other languages
    }
}
```

**Metrics Endpoint** (optional, for debugging):
```
GET /api/v1/metrics
{
    "total_requests": 1234,
    "success_rate": 0.987,
    "avg_latency_ms": 892,
    "by_language": {
        "spanish": {"count": 456, "avg_latency_ms": 850},
        "french": {"count": 234, "avg_latency_ms": 920}
    }
}
```

---

## Implementation Plan (TDD)

### Phase 1: Logging Utilities (RED → GREEN → REFACTOR)

**File**: `backend/app/utils/logging.py`

**Tests**: `backend/tests/utils/test_logging.py`

**Steps**:
1. **RED**: Write tests for structured logger
   - Test log format includes all required fields
   - Test different log levels (INFO, WARNING, ERROR)
   - Test that user text is NOT logged
   - Test request_id attachment

2. **GREEN**: Implement structured logger
   ```python
   import logging
   import json
   from datetime import datetime
   from typing import Optional, Dict, Any

   class StructuredLogger:
       def __init__(self, name: str):
           self.logger = logging.getLogger(name)

       def log_translation_success(
           self,
           request_id: str,
           source_language: str,
           target_language: str,
           text_length: int,
           latency_ms: float,
           retry_count: int = 0
       ):
           self.logger.info(
               json.dumps({
                   "timestamp": datetime.utcnow().isoformat() + "Z",
                   "request_id": request_id,
                   "event": "translation_success",
                   "source_language": source_language,
                   "target_language": target_language,
                   "text_length": text_length,
                   "latency_ms": latency_ms,
                   "retry_count": retry_count
               })
           )

       def log_translation_retry(self, request_id: str, attempt: int, error: str):
           # ...

       def log_translation_error(self, request_id: str, error_type: str, error_msg: str):
           # ...

       def log_rate_limit_exceeded(self, ip: str, endpoint: str):
           # ...
   ```

3. **REFACTOR**: Add helper methods, improve readability

**Expected Tests**: 8-10 tests

---

### Phase 2: TranslationService Integration (RED → GREEN → REFACTOR)

**File**: `backend/app/services/translation.py`

**Tests**: `backend/tests/services/test_translation_logging.py`

**Steps**:
1. **RED**: Write tests for service logging
   - Test successful translation logs include latency
   - Test retry logs include attempt number
   - Test error logs sanitize OpenAI errors
   - Test request_id is propagated

2. **GREEN**: Add logging to TranslationService
   ```python
   class TranslationService:
       def __init__(self):
           self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
           self.logger = StructuredLogger("translation.service")
           # ... existing code

       async def translate(
           self,
           text: str,
           source_language: SupportedLanguage,
           target_language: SupportedLanguage,
           preserve_technical_terms: bool = True,
           request_id: Optional[str] = None  # NEW: accept request_id
       ) -> Dict[str, Any]:
           start_time = time.time()

           for attempt in range(self.max_retries):
               try:
                   # ... existing translation logic

                   latency_ms = (time.time() - start_time) * 1000

                   if request_id:
                       self.logger.log_translation_success(
                           request_id=request_id,
                           source_language=source_language,
                           target_language=target_language,
                           text_length=len(text),
                           latency_ms=latency_ms,
                           retry_count=attempt
                       )

                   return result

               except (RateLimitError, APIConnectionError) as e:
                   if request_id:
                       self.logger.log_translation_retry(
                           request_id=request_id,
                           attempt=attempt + 1,
                           error=str(e)
                       )
                   # ... existing retry logic
   ```

3. **REFACTOR**: Extract logging logic if needed

**Expected Tests**: 6-8 tests
**Key Concern**: Ensure no breaking changes to public API

---

### Phase 3: Endpoint Integration (RED → GREEN → REFACTOR)

**File**: `backend/app/api/v1/endpoints/translate.py`

**Tests**: `backend/tests/api/test_endpoint_logging.py`

**Steps**:
1. **RED**: Write tests for endpoint logging
   - Test request_id is generated for each request
   - Test request_id is passed to TranslationService
   - Test HTTP errors are logged

2. **GREEN**: Update endpoint
   ```python
   import uuid
   from app.utils.logging import StructuredLogger

   logger = StructuredLogger("translation.endpoint")

   @router.post("/text", ...)
   async def translate_text(
       request: TranslateTextRequest,
       http_request: Request  # NEW: inject Request for context
   ) -> TranslateTextResponse:
       # Generate request ID
       request_id = str(uuid.uuid4())

       translation_service = TranslationService()

       try:
           result = await translation_service.translate(
               text=request.text,
               source_language=request.source_language,
               target_language=request.target_language,
               preserve_technical_terms=request.preserve_technical_terms,
               request_id=request_id  # NEW: pass request_id
           )

           return TranslateTextResponse(**result)

       except TranslationServiceError as e:
           logger.log_translation_error(
               request_id=request_id,
               error_type="TranslationServiceError",
               error_msg=str(e)
           )
           raise HTTPException(
               status_code=status.HTTP_502_BAD_GATEWAY,
               detail=f"Translation service error: {str(e)}"
           )
   ```

3. **REFACTOR**: Clean up logging calls

**Expected Tests**: 5-7 tests

---

### Phase 4: Rate Limiter Logging (RED → GREEN → REFACTOR)

**File**: `backend/app/middleware/rate_limit.py`

**Tests**: `backend/tests/middleware/test_rate_limit_logging.py`

**Steps**:
1. **RED**: Write test for rate limit logging
   - Test rate limit violation is logged with IP
   - Test includes endpoint path

2. **GREEN**: Add logging to RateLimiter
   ```python
   from app.utils.logging import StructuredLogger

   class RateLimiter:
       def __init__(self, limit: int = 10, window_seconds: int = 60):
           # ... existing code
           self.logger = StructuredLogger("translation.ratelimit")

       def check_rate_limit(self, request: Request) -> None:
           client_ip = self._get_client_ip(request)
           # ... existing logic

           if len(self.request_timestamps[client_ip]) >= self.limit:
               self.logger.log_rate_limit_exceeded(
                   ip=client_ip,
                   endpoint=request.url.path
               )
               raise HTTPException(...)
   ```

3. **REFACTOR**: Minimal (already clean)

**Expected Tests**: 2-3 tests

---

### Phase 5: Lightweight Metrics (RED → GREEN → REFACTOR)

**File**: `backend/app/utils/metrics.py`

**Tests**: `backend/tests/utils/test_metrics.py`

**Steps**:
1. **RED**: Write tests for metrics tracking
   - Test counters increment correctly
   - Test latency aggregation
   - Test per-language tracking
   - Test thread safety (basic)

2. **GREEN**: Implement metrics
   ```python
   from threading import Lock
   from typing import Dict, Any

   class TranslationMetrics:
       def __init__(self):
           self._lock = Lock()
           self.data = {
               "total_requests": 0,
               "total_successes": 0,
               "total_failures": 0,
               "total_latency_ms": 0.0,
               "by_language": {}
           }

       def record_success(
           self,
           target_language: str,
           latency_ms: float
       ):
           with self._lock:
               self.data["total_requests"] += 1
               self.data["total_successes"] += 1
               self.data["total_latency_ms"] += latency_ms

               if target_language not in self.data["by_language"]:
                   self.data["by_language"][target_language] = {
                       "count": 0,
                       "total_latency_ms": 0.0
                   }

               self.data["by_language"][target_language]["count"] += 1
               self.data["by_language"][target_language]["total_latency_ms"] += latency_ms

       def record_failure(self):
           with self._lock:
               self.data["total_requests"] += 1
               self.data["total_failures"] += 1

       def get_summary(self) -> Dict[str, Any]:
           with self._lock:
               total = self.data["total_requests"]
               if total == 0:
                   return {"total_requests": 0}

               summary = {
                   "total_requests": total,
                   "success_rate": self.data["total_successes"] / total,
                   "failure_rate": self.data["total_failures"] / total,
                   "avg_latency_ms": (
                       self.data["total_latency_ms"] / self.data["total_successes"]
                       if self.data["total_successes"] > 0 else 0
                   ),
                   "by_language": {}
               }

               for lang, stats in self.data["by_language"].items():
                   summary["by_language"][lang] = {
                       "count": stats["count"],
                       "avg_latency_ms": stats["total_latency_ms"] / stats["count"]
                   }

               return summary

   # Module-level singleton
   metrics = TranslationMetrics()
   ```

3. **REFACTOR**: Add reset method for testing

**Expected Tests**: 6-8 tests

---

### Phase 6: Integration & Performance Testing

**Tests**: `backend/tests/integration/test_observability.py`

**Steps**:
1. **Integration Tests**:
   - Test end-to-end logging flow (endpoint → service)
   - Test metrics are updated on success/failure
   - Test request_id propagates through entire stack

2. **Performance Tests**:
   - Measure baseline latency (without logging)
   - Measure with logging enabled
   - Ensure < 5% regression
   - Test with 100 concurrent requests

**Expected Tests**: 4-6 tests

---

## File Structure

```
backend/
├── app/
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logging.py          # NEW: StructuredLogger
│   │   └── metrics.py          # NEW: TranslationMetrics
│   ├── services/
│   │   └── translation.py      # MODIFIED: add logging
│   ├── api/v1/endpoints/
│   │   └── translate.py        # MODIFIED: add request_id & logging
│   └── middleware/
│       └── rate_limit.py       # MODIFIED: add logging
├── tests/
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── test_logging.py     # NEW: 8-10 tests
│   │   └── test_metrics.py     # NEW: 6-8 tests
│   ├── services/
│   │   └── test_translation_logging.py  # NEW: 6-8 tests
│   ├── api/
│   │   └── test_endpoint_logging.py     # NEW: 5-7 tests
│   ├── middleware/
│   │   └── test_rate_limit_logging.py   # NEW: 2-3 tests
│   └── integration/
│       └── test_observability.py        # NEW: 4-6 tests
```

**Total New Tests**: 31-42 tests
**Total Test Count After**: 116-127 tests

---

## Testing Strategy

### Use `caplog` Fixture

```python
def test_translation_success_logs_event(caplog):
    """Test that successful translation creates structured log."""
    logger = StructuredLogger("test")

    with caplog.at_level(logging.INFO):
        logger.log_translation_success(
            request_id="test-123",
            source_language="english",
            target_language="spanish",
            text_length=100,
            latency_ms=892.5,
            retry_count=0
        )

    assert len(caplog.records) == 1
    log_message = json.loads(caplog.records[0].message)

    assert log_message["request_id"] == "test-123"
    assert log_message["event"] == "translation_success"
    assert log_message["latency_ms"] == 892.5
    assert "timestamp" in log_message
```

### Privacy Tests

```python
def test_user_text_not_logged(caplog):
    """CRITICAL: Ensure user text is never logged."""
    service = TranslationService()

    with caplog.at_level(logging.DEBUG):  # Even at DEBUG level
        # ... call translation with sensitive text
        pass

    for record in caplog.records:
        assert "SENSITIVE_TEXT_HERE" not in record.message
```

---

## Non-Breaking Changes Checklist

- [ ] `TranslationService.translate()` signature: `request_id` is **optional**
- [ ] Existing tests continue to pass without modifications
- [ ] Logging is silent if `request_id` is not provided
- [ ] No performance regression > 5%
- [ ] All 85 existing tests still pass

---

## Success Criteria

### Functional
- ✅ Structured logs in JSON format
- ✅ Request ID generated and propagated
- ✅ All critical events logged (success, retry, error, rate limit)
- ✅ User text is NEVER logged
- ✅ Metrics track success/failure/latency
- ✅ Metrics available via `get_summary()`

### Quality
- ✅ 31-42 new tests, all passing
- ✅ Total test suite: 116-127 tests, all passing
- ✅ No breaking changes to public APIs
- ✅ Performance regression < 5%

### Documentation
- ✅ Code comments explain logging strategy
- ✅ Docstrings on all new classes/methods
- ✅ tasks.md updated with completion status
- ✅ PHR created documenting implementation

---

## Future Enhancements (Out of Scope)

These are **NOT** part of this task:
- ❌ Distributed tracing (OpenTelemetry)
- ❌ Prometheus/Grafana integration
- ❌ External logging services (Datadog, Splunk)
- ❌ Persistent metrics storage
- ❌ Alerting system
- ❌ Log aggregation/shipping

---

## Implementation Checklist

### Phase 1: Setup
- [ ] Create `backend/app/utils/logging.py`
- [ ] Create `backend/app/utils/metrics.py`
- [ ] Create test directories

### Phase 2: TDD Cycle
- [ ] Write tests for StructuredLogger (RED)
- [ ] Implement StructuredLogger (GREEN)
- [ ] Refactor logging utilities
- [ ] Write tests for TranslationMetrics (RED)
- [ ] Implement TranslationMetrics (GREEN)
- [ ] Refactor metrics

### Phase 3: Service Integration
- [ ] Write tests for service logging (RED)
- [ ] Add logging to TranslationService (GREEN)
- [ ] Verify no breaking changes

### Phase 4: Endpoint Integration
- [ ] Write tests for endpoint logging (RED)
- [ ] Add request_id generation to endpoint (GREEN)
- [ ] Pass request_id to service

### Phase 5: Rate Limiter
- [ ] Write tests for rate limit logging (RED)
- [ ] Add logging to RateLimiter (GREEN)

### Phase 6: Validation
- [ ] Run full test suite (should be 116-127 tests)
- [ ] Performance testing (< 5% regression)
- [ ] Privacy audit (no user text in logs)

### Phase 7: Documentation
- [ ] Update tasks.md
- [ ] Create PHR
- [ ] Add code comments

---

## Estimated Timeline

- **Phase 1 (Setup)**: 30 minutes
- **Phase 2 (Utilities + Tests)**: 2 hours
- **Phase 3 (Service Integration)**: 1.5 hours
- **Phase 4 (Endpoint Integration)**: 1 hour
- **Phase 5 (Rate Limiter)**: 30 minutes
- **Phase 6 (Validation)**: 1 hour
- **Phase 7 (Documentation)**: 30 minutes

**Total**: ~6.5 hours

---

## Next Session Prompt

```
Continue implementation of Observability & Monitoring for Translation API (Task 2.4).

Reference: specs/003-multilingual-translation/observability-plan.md

Current status:
- 85 tests passing (Tasks 1.1-1.6, 2.1, 2.8 complete)
- All existing functionality working

Task: Implement structured logging and metrics as per the plan:
1. Start with Phase 1: Create logging utilities (TDD)
2. Follow RED → GREEN → REFACTOR for each phase
3. Ensure all 85 existing tests continue to pass
4. Target: 31-42 new tests, all passing
5. Verify < 5% performance regression

Start with: "I'll implement Phase 1 of the Observability plan..."
```
