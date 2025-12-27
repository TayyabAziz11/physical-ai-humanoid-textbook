---
id: 0005
title: "Task 1.2: TranslateTextRequest Model Implementation"
stage: green
date: 2025-12-25
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-multilingual-translation
branch: 003-multilingual-translation
user: user
command: /sp.implement
labels: ["tdd", "green-phase", "backend", "pydantic", "validation", "task-1.2"]
links:
  spec: specs/003-multilingual-translation/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/app/models/request.py
  - backend/tests/models/test_translation_models.py
  - specs/003-multilingual-translation/tasks.md
tests:
  - test_create_valid_request_with_minimal_fields
  - test_create_valid_request_with_all_fields
  - test_default_source_language_is_english
  - test_default_preserve_technical_terms_is_true
  - test_text_min_length_validation
  - test_text_max_length_validation
  - test_text_exactly_10000_characters_is_valid
  - test_invalid_target_language_rejected
  - test_invalid_source_language_rejected
  - test_context_max_length_validation
  - test_context_exactly_200_characters_is_valid
  - test_same_source_and_target_language_allowed
  - test_all_supported_languages_as_target
  - test_all_supported_languages_as_source
  - test_preserve_technical_terms_boolean_validation
  - test_model_serialization
  - test_model_deserialization
---

## Prompt

```text
Implement Task 1.2 from specs/003-multilingual-translation/tasks.md.

Task:
Create the TranslateTextRequest Pydantic model for multilingual translation.

Context:
- Feature: 003-multilingual-translation
- Phase: 1 (Backend Foundation)
- Task ID: 1.2
- Stack: FastAPI + Pydantic + pytest
- Follows strict TDD (red → green → refactor)
- Depends on Task 1.1 (SupportedLanguage type defined)

Requirements:
1. Implement a Pydantic model named TranslateTextRequest with fields:
   - source_language: SupportedLanguage
   - target_language: SupportedLanguage
   - text: str (non-empty)
2. Ensure full validation with Field constraints
3. Follow TDD methodology strictly
4. Keep task atomic and commit-ready
5. No additional scope beyond Task 1.2

Implementation steps (must follow in order):
1. Write failing pytest tests first (RED phase)
2. Implement minimal code to pass tests (GREEN phase)
3. Refactor for clarity and documentation (REFACTOR phase)
4. Re-run tests and confirm all pass

File locations:
- Model: backend/app/models/request.py
- Tests: backend/tests/models/test_translation_models.py

Validation criteria:
- All required fields validated
- Unsupported languages rejected
- Text length constraints enforced
- Default values work correctly
- Tests must pass with pytest

Output:
- Show test code
- Show implementation code
- Confirm tests pass
- Do NOT implement any other tasks
```

## Response snapshot

### TDD Implementation: RED → GREEN → REFACTOR

**Phase 1: RED (Tests First)**

Created 17 comprehensive test cases in `backend/tests/models/test_translation_models.py`:

```python
class TestTranslateTextRequest:
    """Test suite for TranslateTextRequest Pydantic model."""

    def test_create_valid_request_with_minimal_fields(self):
        """Test creating a valid request with only required fields."""
        request = TranslateTextRequest(
            text="Hello world",
            target_language="spanish"
        )
        assert request.text == "Hello world"
        assert request.target_language == "spanish"
        assert request.source_language == "english"  # Default value
        assert request.preserve_technical_terms is True  # Default value
        assert request.context is None  # Default value

    def test_text_min_length_validation(self):
        """Test that empty text is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TranslateTextRequest(text="", target_language="spanish")
        assert "String should have at least 1 character" in str(exc_info.value)

    def test_text_max_length_validation(self):
        """Test that text exceeding 10000 characters is rejected."""
        long_text = "x" * 10001
        with pytest.raises(ValidationError) as exc_info:
            TranslateTextRequest(text=long_text, target_language="spanish")
        assert "String should have at most 10000 characters" in str(exc_info.value)

    # ... 14 more comprehensive tests
```

Initial test run: **FAILED** with `ImportError: cannot import name 'TranslateTextRequest'` (expected - no implementation yet)

**Phase 2: GREEN (Minimal Implementation)**

Added `TranslateTextRequest` to `backend/app/models/request.py`:

```python
from app.models.translation import SupportedLanguage

class TranslateTextRequest(BaseModel):
    """Request model for text translation endpoint."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Text to translate (1-10,000 characters)"
    )

    target_language: SupportedLanguage = Field(
        ...,
        description="Target language for translation"
    )

    source_language: SupportedLanguage = Field(
        default="english",
        description="Source language of the text (defaults to English)"
    )

    preserve_technical_terms: bool = Field(
        default=True,
        description="Whether to preserve technical terms in original language"
    )

    context: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Optional context hint for better translation (max 200 characters)"
    )
```

Test results: **17/17 new tests PASSED** ✅ (Total: 29/29 tests passing)

**Phase 3: REFACTOR (Enhanced Documentation)**

Enhanced the model with comprehensive docstring including:
- Detailed class description
- Usage example with doctest format
- Complete attribute documentation
- Validation constraints clearly documented

Final test results: **29/29 PASSED** ✅

**Note on Field Count Discrepancy:**
The user's command mentioned 3 fields (source_language, target_language, text), but tasks.md specification defines 5 fields. I followed the tasks.md specification as the authoritative source to ensure alignment with the architectural plan.

**Implementation Highlights:**
1. Used Pydantic Field() with descriptive messages and constraints
2. Applied SupportedLanguage type from Task 1.1 (dependency correctly handled)
3. Set sensible defaults: source_language="english", preserve_technical_terms=True
4. Enforced validation: text (1-10,000 chars), context (max 200 chars)
5. Comprehensive test coverage: defaults, boundaries, serialization, all 7 languages

## Outcome

- ✅ Impact: Successfully implemented Task 1.2 following strict TDD methodology. Created production-ready TranslateTextRequest Pydantic model with comprehensive validation, sensible defaults, and full test coverage. All 17 new tests passing (29/29 total). Model integrates correctly with SupportedLanguage type from Task 1.1.
- 🧪 Tests: 17/17 tests passing - Minimal fields (1 test), All fields (1 test), Defaults (2 tests), Text validation (3 tests), Language validation (2 tests), Context validation (2 tests), Language coverage (2 tests), Serialization (2 tests), Edge cases (2 tests). Test coverage: 100% of TranslateTextRequest model.
- 📁 Files: Modified backend/app/models/request.py (added TranslateTextRequest class, 56 lines), Extended backend/tests/models/test_translation_models.py (added 17 tests, 168 total lines). Updated specs/003-multilingual-translation/tasks.md (marked Task 1.2 complete).
- 🔁 Next prompts: Proceed to Task 1.3 (Create TranslateResponseRequest Model) which continues the Backend Foundation phase. Follow same TDD pattern. Then Task 1.4 (TranslationResponse Model) and Task 1.5 (TranslationError Exception).
- 🧠 Reflection: TDD workflow remains highly effective - tests clarified all edge cases including boundary validation (exactly 10,000 chars, exactly 200 chars) and default behavior. Following tasks.md as authoritative source (5 fields vs user's 3 fields) ensured architectural consistency. Pydantic Field() descriptors provide excellent validation with clear error messages. The preserve_technical_terms field adds important flexibility for technical documentation translation.

## Evaluation notes (flywheel)

- Failure modes observed: Minor specification discrepancy between user command (3 fields) and tasks.md (5 fields) - resolved by following tasks.md as canonical source. No runtime failures.
- Graders run and results (PASS/FAIL): PASS - All 17 tests passing. Validation criteria met: required fields validated, unsupported languages rejected (ValidationError raised), text length constraints enforced (1-10,000), context max length enforced (200), defaults working correctly (source_language="english", preserve_technical_terms=True, context=None).
- Prompt variant (if applicable): N/A - Standard /sp.implement workflow with TDD
- Next experiment (smallest change to try): For Task 1.3 (TranslateResponseRequest), consider adding a custom validator to prevent source_language == target_language if that's a business requirement. Also consider using Pydantic's model_validator for any cross-field validation needs in future models.
