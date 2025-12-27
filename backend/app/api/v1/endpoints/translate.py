"""
Translation endpoints for multilingual text translation.

This module provides REST API endpoints for translating text and query responses
between supported languages using OpenAI GPT-4o-mini. The translation service
supports 7 languages with automatic RTL (right-to-left) detection for Arabic and Urdu.

Integration:
- POST /text: Translates text using TranslationService with OpenAI GPT-4o-mini
- POST /response: Placeholder for future RAG integration (returns 501)

Supported languages:
- English (english)
- Spanish (spanish)
- French (french)
- Mandarin Chinese (mandarin)
- Japanese (japanese)
- Urdu (urdu) - RTL
- Arabic (arabic) - RTL

Rate limiting:
- Limit: 10 requests per minute per IP address
- Applies to: All /api/v1/translate/* endpoints
- Error: HTTP 429 Too Many Requests when limit exceeded

Error handling:
- 422: Validation errors (empty text, unsupported language, text too long)
- 429: Rate limit exceeded (too many requests from same IP)
- 502: Translation service errors (OpenAI API failures, rate limits, network errors)

Task 1.4: Translation router and endpoint stubs.
Task 1.6: Rate limiting middleware integration.
Task 2.2/2.8: TranslationService integration with OpenAI GPT-4o-mini.
"""

from fastapi import APIRouter, HTTPException, Request, status, Depends
from app.models.request import TranslateTextRequest
from app.models.translation import TranslateTextResponse
from app.services.translation import TranslationService, TranslationServiceError
from app.middleware.rate_limit import RateLimiter

# Create translation router with tags for OpenAPI documentation
router = APIRouter()

# Initialize rate limiter (10 requests per minute per IP)
rate_limiter = RateLimiter(limit=10, window_seconds=60)


def check_rate_limit(request: Request):
    """
    Dependency to check rate limit for translation endpoints.

    Raises:
        HTTPException: HTTP 429 if rate limit exceeded
    """
    rate_limiter.check_rate_limit(request)


@router.post(
    "/text",
    response_model=TranslateTextResponse,
    status_code=status.HTTP_200_OK,
    summary="Translate text between languages",
    response_description="Translated text with language metadata and RTL flag",
    dependencies=[Depends(check_rate_limit)]
)
async def translate_text(request: TranslateTextRequest) -> TranslateTextResponse:
    """
    Translate text from one language to another using OpenAI GPT-4o-mini.

    This endpoint translates arbitrary text between supported languages using the
    TranslationService, which integrates with OpenAI's API for high-quality translations.
    Technical terms can be preserved in the original language if requested
    (controlled by the `preserve_technical_terms` flag, default: True).

    The response includes:
    - Original and translated text
    - Source and target languages
    - RTL flag (automatically derived from target language metadata)

    Example request:
    ```json
    {
        "text": "Hello world",
        "target_language": "spanish",
        "preserve_technical_terms": true
    }
    ```

    Example response:
    ```json
    {
        "original_text": "Hello world",
        "translated_text": "Hola mundo",
        "source_language": "english",
        "target_language": "spanish",
        "rtl": false
    }
    ```

    Args:
        request: Translation request with text and language parameters

    Returns:
        TranslateTextResponse with translated text and metadata

    Raises:
        HTTPException: 422 if validation fails (empty text, unsupported language, etc.)
        HTTPException: 502 if translation service fails (OpenAI API errors, rate limits, etc.)
    """
    # Initialize translation service
    translation_service = TranslationService()

    try:
        # Call translation service
        result = await translation_service.translate(
            text=request.text,
            source_language=request.source_language,
            target_language=request.target_language,
            preserve_technical_terms=request.preserve_technical_terms
        )

        # Return response using the dict from TranslationService
        return TranslateTextResponse(**result)

    except TranslationServiceError as e:
        # Map translation service errors to HTTP 502 Bad Gateway
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Translation service error: {str(e)}"
        )


@router.post(
    "/response",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    summary="Translate query response (not implemented)",
    response_description="501 Not Implemented - reserved for future RAG integration"
)
async def translate_response(request_body: dict):
    """
    Translate a RAG query response (placeholder for future implementation).

    This endpoint is reserved for future RAG integration. It will translate
    entire query responses including:
    - Answer text
    - Citations and references
    - Metadata fields

    The translated response will maintain citation accuracy and preserve
    technical terminology in the original language when appropriate.

    **Status**: Not yet implemented (returns 501)

    **Future structure** (tentative):
    ```json
    {
        "original_response": {
            "answer": "The answer text...",
            "citations": [...]
        },
        "target_language": "urdu"
    }
    ```

    Args:
        request_body: JSON payload (structure to be defined in future tasks)

    Returns:
        HTTPException with 501 status code

    Raises:
        HTTPException: 501 indicating endpoint is not yet implemented
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Response translation endpoint is not yet implemented. This feature is reserved for future RAG integration."
    )
