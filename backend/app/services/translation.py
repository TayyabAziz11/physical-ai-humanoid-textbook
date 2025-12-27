"""
Translation service for multilingual text translation using OpenAI GPT-4o-mini.

This module provides a framework-agnostic translation service that:
- Translates text between 7 supported languages
- Uses OpenAI GPT-4o-mini for high-quality translations
- Implements retry logic with exponential backoff
- Preserves technical terminology and formatting
- Normalizes errors into custom exceptions

Task 2.1: TranslationService implementation.
"""

import asyncio
from typing import Dict, Any
from openai import AsyncOpenAI, OpenAIError, RateLimitError, APIConnectionError

from app.core.config import settings
from app.models.translation import SupportedLanguage


class TranslationServiceError(Exception):
    """Custom exception for translation service errors."""
    pass


class TranslationService:
    """
    Service for translating text between supported languages using OpenAI GPT-4o-mini.

    This service is framework-agnostic and does not depend on FastAPI or any web framework.
    It can be used in any Python application that needs translation capabilities.

    Features:
    - Supports 7 languages: English, Spanish, French, Mandarin, Japanese, Urdu, Arabic
    - Automatic retry with exponential backoff (1s, 2s, 4s)
    - Preserves technical terminology and formatting
    - Returns dict compatible with TranslateTextResponse model
    """

    def __init__(self):
        """Initialize the translation service with OpenAI client."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"
        self.max_retries = 3
        self.base_delay = 1.0  # Base delay for exponential backoff (seconds)

    async def translate(
        self,
        text: str,
        source_language: SupportedLanguage,
        target_language: SupportedLanguage,
        preserve_technical_terms: bool = True
    ) -> Dict[str, Any]:
        """
        Translate text from source language to target language.

        Args:
            text: Text to translate
            source_language: Source language code (e.g., 'english')
            target_language: Target language code (e.g., 'spanish')
            preserve_technical_terms: Whether to preserve technical terms (default: True)

        Returns:
            Dict compatible with TranslateTextResponse:
            {
                "original_text": str,
                "translated_text": str,
                "source_language": str,
                "target_language": str
            }

        Raises:
            TranslationServiceError: If translation fails after max retries
        """
        for attempt in range(self.max_retries):
            try:
                # Call OpenAI API
                response = await self._call_openai(
                    text=text,
                    source_language=source_language,
                    target_language=target_language,
                    preserve_technical_terms=preserve_technical_terms
                )

                # Extract translated text from response
                translated_text = response.choices[0].message.content

                # Return dict compatible with TranslateTextResponse
                return {
                    "original_text": text,
                    "translated_text": translated_text,
                    "source_language": source_language,
                    "target_language": target_language
                }

            except (RateLimitError, APIConnectionError) as e:
                # Retry on transient errors
                if attempt < self.max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    delay = self.base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                else:
                    # Max retries exceeded
                    raise TranslationServiceError(
                        f"Translation failed after {self.max_retries} retries: {str(e)}"
                    ) from e

            except OpenAIError as e:
                # Non-retryable OpenAI error
                raise TranslationServiceError(
                    f"OpenAI API error: {str(e)}"
                ) from e

            except Exception as e:
                # Unexpected error
                raise TranslationServiceError(
                    f"Unexpected translation error: {str(e)}"
                ) from e

        # Should never reach here, but just in case
        raise TranslationServiceError("Translation failed after max retries")

    async def _call_openai(
        self,
        text: str,
        source_language: str,
        target_language: str,
        preserve_technical_terms: bool
    ) -> Any:
        """
        Call OpenAI API to perform translation.

        This method is separated to make it easier to mock in tests.
        Uses GPT-4o-mini with low temperature for consistent translations.

        Args:
            text: Text to translate
            source_language: Source language
            target_language: Target language
            preserve_technical_terms: Whether to preserve technical terms

        Returns:
            OpenAI API response with translated text in choices[0].message.content
        """
        system_prompt = self._build_system_prompt(
            source_language=source_language,
            target_language=target_language,
            preserve_technical_terms=preserve_technical_terms
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,  # Lower temperature for more consistent translations
            max_tokens=2000
        )

        return response

    def _build_system_prompt(
        self,
        source_language: str,
        target_language: str,
        preserve_technical_terms: bool
    ) -> str:
        """
        Build system prompt for translation.

        Args:
            source_language: Source language
            target_language: Target language
            preserve_technical_terms: Whether to preserve technical terms

        Returns:
            System prompt string
        """
        technical_terms_instruction = ""
        if preserve_technical_terms:
            technical_terms_instruction = (
                "\n\nIMPORTANT: Preserve all technical terms, proper nouns, "
                "code snippets, mathematical notation, and specialized terminology "
                "in their original form. Only translate natural language text."
            )

        prompt = (
            f"You are a professional translator specializing in technical and educational content. "
            f"Translate the following text from {source_language} to {target_language}. "
            f"Maintain the original formatting, tone, and structure."
            f"{technical_terms_instruction}\n\n"
            f"Provide only the translated text without any explanations or notes."
        )

        return prompt
