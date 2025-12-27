"""
Tests for TranslationService.

Task 2.1: Test TranslationService with mocked OpenAI client (RED phase).
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from openai import OpenAIError, RateLimitError, APIConnectionError


class TestTranslationService:
    """Test suite for TranslationService class."""

    @pytest.mark.asyncio
    async def test_translate_success_with_mocked_openai(self):
        """Test successful translation with mocked OpenAI response."""
        from app.services.translation import TranslationService

        # Mock OpenAI client response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Hola mundo"

        service = TranslationService()

        with patch.object(service, '_call_openai', return_value=mock_response):
            result = await service.translate(
                text="Hello world",
                source_language="english",
                target_language="spanish"
            )

            assert result["original_text"] == "Hello world"
            assert result["translated_text"] == "Hola mundo"
            assert result["source_language"] == "english"
            assert result["target_language"] == "spanish"

    @pytest.mark.asyncio
    async def test_translate_returns_dict_compatible_with_response_model(self):
        """Test that translate returns dict compatible with TranslateTextResponse."""
        from app.services.translation import TranslationService
        from app.models.translation import TranslateTextResponse

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "مرحبا"

        service = TranslationService()

        with patch.object(service, '_call_openai', return_value=mock_response):
            result = await service.translate(
                text="Hello",
                source_language="english",
                target_language="arabic"
            )

            # Should be able to create TranslateTextResponse from result
            response = TranslateTextResponse(**result)
            assert response.original_text == "Hello"
            assert response.translated_text == "مرحبا"
            assert response.rtl is True  # Arabic is RTL

    @pytest.mark.asyncio
    async def test_translate_to_all_supported_languages(self):
        """Test translation to all 7 supported languages."""
        from app.services.translation import TranslationService

        languages = ["english", "urdu", "mandarin", "japanese", "spanish", "french", "arabic"]
        service = TranslationService()

        for lang in languages:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = f"Translated to {lang}"

            with patch.object(service, '_call_openai', return_value=mock_response):
                result = await service.translate(
                    text="Test",
                    source_language="english",
                    target_language=lang
                )

                assert result["target_language"] == lang
                assert "translated_text" in result

    @pytest.mark.asyncio
    async def test_translate_retry_on_rate_limit_error(self):
        """Test that service retries on RateLimitError."""
        from app.services.translation import TranslationService

        service = TranslationService()

        # First two calls fail with RateLimitError, third succeeds
        mock_success = Mock()
        mock_success.choices = [Mock()]
        mock_success.choices[0].message = Mock()
        mock_success.choices[0].message.content = "Success"

        call_count = 0
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                # Create proper RateLimitError with required arguments
                error = RateLimitError(
                    "Rate limit exceeded",
                    response=Mock(status_code=429),
                    body={"error": {"message": "Rate limit exceeded"}}
                )
                raise error
            return mock_success

        with patch.object(service, '_call_openai', side_effect=side_effect):
            result = await service.translate(
                text="Test",
                source_language="english",
                target_language="spanish"
            )

            assert call_count == 3  # Should have retried 2 times
            assert result["translated_text"] == "Success"

    @pytest.mark.asyncio
    async def test_translate_retry_on_connection_error(self):
        """Test that service retries on APIConnectionError."""
        from app.services.translation import TranslationService

        service = TranslationService()

        mock_success = Mock()
        mock_success.choices = [Mock()]
        mock_success.choices[0].message = Mock()
        mock_success.choices[0].message.content = "Success after retry"

        call_count = 0
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                # Create proper APIConnectionError
                error = APIConnectionError(request=Mock())
                raise error
            return mock_success

        with patch.object(service, '_call_openai', side_effect=side_effect):
            result = await service.translate(
                text="Test",
                source_language="english",
                target_language="french"
            )

            assert call_count == 2  # Should have retried once
            assert result["translated_text"] == "Success after retry"

    @pytest.mark.asyncio
    async def test_translate_fails_after_max_retries(self):
        """Test that service raises TranslationServiceError after max retries."""
        from app.services.translation import TranslationService, TranslationServiceError

        service = TranslationService()

        # Always fail with RateLimitError
        def side_effect(*args, **kwargs):
            error = RateLimitError(
                "Rate limit exceeded",
                response=Mock(status_code=429),
                body={"error": {"message": "Rate limit exceeded"}}
            )
            raise error

        with patch.object(service, '_call_openai', side_effect=side_effect):
            with pytest.raises(TranslationServiceError) as exc_info:
                await service.translate(
                    text="Test",
                    source_language="english",
                    target_language="spanish"
                )

            assert "max retries" in str(exc_info.value).lower() or "rate limit" in str(exc_info.value).lower() or "retries" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_translate_normalizes_openai_errors(self):
        """Test that OpenAI errors are normalized to TranslationServiceError."""
        from app.services.translation import TranslationService, TranslationServiceError

        service = TranslationService()

        # Simulate various OpenAI errors
        def side_effect(*args, **kwargs):
            raise OpenAIError("Some OpenAI error")

        with patch.object(service, '_call_openai', side_effect=side_effect):
            with pytest.raises(TranslationServiceError):
                await service.translate(
                    text="Test",
                    source_language="english",
                    target_language="spanish"
                )

    @pytest.mark.asyncio
    async def test_service_uses_gpt4o_mini_model(self):
        """Test that service uses GPT-4o-mini model."""
        from app.services.translation import TranslationService

        service = TranslationService()

        # Mock the OpenAI client
        with patch('app.services.translation.AsyncOpenAI') as mock_openai_class:
            mock_client = Mock()
            mock_openai_class.return_value = mock_client

            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = "Translated"

            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

            # Reinitialize service to use mocked client
            service = TranslationService()
            service.client = mock_client

            await service.translate(
                text="Test",
                source_language="english",
                target_language="spanish"
            )

            # Verify GPT-4o-mini was used
            call_args = mock_client.chat.completions.create.call_args
            assert call_args.kwargs["model"] == "gpt-4o-mini"

    @pytest.mark.asyncio
    async def test_system_prompt_instructs_to_preserve_technical_terms(self):
        """Test that system prompt instructs model to preserve technical terms."""
        from app.services.translation import TranslationService

        service = TranslationService()

        with patch('app.services.translation.AsyncOpenAI') as mock_openai_class:
            mock_client = Mock()
            mock_openai_class.return_value = mock_client

            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = "Translated"

            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

            service = TranslationService()
            service.client = mock_client

            await service.translate(
                text="ROS 2 uses Humble Hawksbill",
                source_language="english",
                target_language="urdu"
            )

            # Check that messages were passed with technical term preservation instruction
            call_args = mock_client.chat.completions.create.call_args
            messages = call_args.kwargs["messages"]

            # Should have system message with technical term instruction
            assert any("technical" in msg["content"].lower() for msg in messages if msg["role"] == "system")

    @pytest.mark.asyncio
    async def test_service_is_framework_agnostic(self):
        """Test that TranslationService has no FastAPI dependencies."""
        import sys
        from app.services.translation import TranslationService

        # Create service instance - should not require any web framework
        service = TranslationService()

        # Check that fastapi is not imported in the translation module
        import app.services.translation as translation_module
        module_globals = dir(translation_module)

        # Should not have FastAPI-specific classes
        fastapi_classes = ['FastAPI', 'Request', 'Response', 'HTTPException', 'Depends']
        for cls in fastapi_classes:
            assert cls not in module_globals, f"Found FastAPI class {cls} in translation module"

    @pytest.mark.asyncio
    async def test_exponential_backoff_timing(self):
        """Test that retry uses exponential backoff (1s, 2s, 4s)."""
        from app.services.translation import TranslationService
        import time

        service = TranslationService()

        call_times = []
        def side_effect(*args, **kwargs):
            call_times.append(time.time())
            if len(call_times) < 3:
                error = RateLimitError(
                    "Rate limit",
                    response=Mock(status_code=429),
                    body={"error": {"message": "Rate limit"}}
                )
                raise error
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = "Success"
            return mock_response

        with patch.object(service, '_call_openai', side_effect=side_effect):
            await service.translate(
                text="Test",
                source_language="english",
                target_language="spanish"
            )

            # Should have made 3 calls
            assert len(call_times) == 3

            # Check timing between calls (allow 0.8s tolerance for test flakiness)
            if len(call_times) >= 2:
                delay1 = call_times[1] - call_times[0]
                assert 0.2 <= delay1 <= 1.8  # Should be ~1s (more tolerant)

            if len(call_times) >= 3:
                delay2 = call_times[2] - call_times[1]
                assert 1.2 <= delay2 <= 2.8  # Should be ~2s (more tolerant)
