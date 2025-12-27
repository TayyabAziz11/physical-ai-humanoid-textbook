"""
Tests for translation API endpoints.

Task 1.4: Test translation router endpoints (RED phase).
Task 2.2/2.8: Test TranslationService integration (RED phase).
"""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.services.translation import TranslationServiceError
from app.middleware.rate_limit import RateLimiter

# Create test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset rate limiter before each test to ensure test isolation."""
    from app.api.v1.endpoints import translate
    translate.rate_limiter = RateLimiter(limit=10, window_seconds=60)
    yield


class TestTranslateTextEndpoint:
    """Test suite for POST /api/v1/translate/text endpoint."""

    def test_translate_text_success_with_minimal_request(self):
        """Test successful translation with minimal required fields."""
        request_data = {
            "text": "Hello world",
            "target_language": "spanish"
        }

        response = client.post("/api/v1/translate/text", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "original_text" in data
        assert "translated_text" in data
        assert "source_language" in data
        assert "target_language" in data
        assert "rtl" in data
        assert data["original_text"] == "Hello world"
        assert data["target_language"] == "spanish"
        assert data["source_language"] == "english"  # Default
        assert data["rtl"] is False  # Spanish is LTR

    def test_translate_text_success_with_all_fields(self):
        """Test successful translation with all optional fields."""
        request_data = {
            "text": "The robot uses ROS 2 for navigation",
            "target_language": "urdu",
            "source_language": "english",
            "preserve_technical_terms": True,
            "context": "robotics documentation"
        }

        response = client.post("/api/v1/translate/text", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["target_language"] == "urdu"
        assert data["source_language"] == "english"
        assert data["rtl"] is True  # Urdu is RTL

    def test_translate_text_to_arabic_sets_rtl_true(self):
        """Test that Arabic target language sets RTL flag to True."""
        request_data = {
            "text": "Hello",
            "target_language": "arabic"
        }

        response = client.post("/api/v1/translate/text", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["rtl"] is True
        assert data["target_language"] == "arabic"

    def test_translate_text_validation_empty_text_rejected(self):
        """Test that empty text is rejected with 422 validation error."""
        request_data = {
            "text": "",
            "target_language": "spanish"
        }

        response = client.post("/api/v1/translate/text", json=request_data)

        assert response.status_code == 422
        error_detail = response.json()
        assert "detail" in error_detail

    def test_translate_text_validation_text_too_long_rejected(self):
        """Test that text exceeding 10000 characters is rejected."""
        request_data = {
            "text": "x" * 10001,
            "target_language": "spanish"
        }

        response = client.post("/api/v1/translate/text", json=request_data)

        assert response.status_code == 422

    def test_translate_text_validation_unsupported_target_language(self):
        """Test that unsupported target language is rejected."""
        request_data = {
            "text": "Hello",
            "target_language": "german"  # Not in SupportedLanguage
        }

        response = client.post("/api/v1/translate/text", json=request_data)

        assert response.status_code == 422
        error_detail = response.json()
        assert "detail" in error_detail

    def test_translate_text_validation_unsupported_source_language(self):
        """Test that unsupported source language is rejected."""
        request_data = {
            "text": "Hello",
            "target_language": "spanish",
            "source_language": "russian"  # Not in SupportedLanguage
        }

        response = client.post("/api/v1/translate/text", json=request_data)

        assert response.status_code == 422

    def test_translate_text_validation_missing_text_field(self):
        """Test that missing text field is rejected."""
        request_data = {
            "target_language": "spanish"
            # Missing "text" field
        }

        response = client.post("/api/v1/translate/text", json=request_data)

        assert response.status_code == 422

    def test_translate_text_validation_missing_target_language(self):
        """Test that missing target_language field is rejected."""
        request_data = {
            "text": "Hello"
            # Missing "target_language" field
        }

        response = client.post("/api/v1/translate/text", json=request_data)

        assert response.status_code == 422

    def test_translate_text_all_supported_languages(self):
        """Test translation to all supported languages."""
        supported_languages = ["english", "urdu", "mandarin", "japanese", "spanish", "french", "arabic"]

        for lang in supported_languages:
            request_data = {
                "text": "Test translation",
                "target_language": lang
            }

            response = client.post("/api/v1/translate/text", json=request_data)

            assert response.status_code == 200, f"Failed for language: {lang}"
            data = response.json()
            assert data["target_language"] == lang

    def test_translate_text_context_field_optional(self):
        """Test that context field is optional."""
        request_data = {
            "text": "Hello",
            "target_language": "spanish"
            # No context field
        }

        response = client.post("/api/v1/translate/text", json=request_data)

        assert response.status_code == 200

    def test_translate_text_preserve_technical_terms_defaults_to_true(self):
        """Test that preserve_technical_terms defaults to True when not specified."""
        request_data = {
            "text": "ROS 2 navigation",
            "target_language": "spanish"
            # No preserve_technical_terms field
        }

        response = client.post("/api/v1/translate/text", json=request_data)

        assert response.status_code == 200
        # Default behavior should preserve technical terms (tested in service layer)

    def test_translate_text_calls_translation_service(self):
        """Test that endpoint calls TranslationService.translate() with correct parameters."""
        request_data = {
            "text": "Hello world",
            "target_language": "spanish",
            "source_language": "english",
            "preserve_technical_terms": True
        }

        # Mock TranslationService.translate() to return a translation dict
        mock_translation_result = {
            "original_text": "Hello world",
            "translated_text": "Hola mundo",
            "source_language": "english",
            "target_language": "spanish"
        }

        with patch('app.api.v1.endpoints.translate.TranslationService') as MockService:
            mock_instance = MockService.return_value
            mock_instance.translate = AsyncMock(return_value=mock_translation_result)

            response = client.post("/api/v1/translate/text", json=request_data)

            assert response.status_code == 200
            data = response.json()
            assert data["translated_text"] == "Hola mundo"
            assert data["original_text"] == "Hello world"
            assert data["rtl"] is False  # Spanish is LTR

            # Verify TranslationService.translate was called with correct args
            mock_instance.translate.assert_called_once_with(
                text="Hello world",
                source_language="english",
                target_language="spanish",
                preserve_technical_terms=True
            )

    def test_translate_text_handles_translation_service_error(self):
        """Test that TranslationServiceError is mapped to HTTP 502 Bad Gateway."""
        request_data = {
            "text": "Hello",
            "target_language": "spanish"
        }

        # Mock TranslationService to raise TranslationServiceError
        with patch('app.api.v1.endpoints.translate.TranslationService') as MockService:
            mock_instance = MockService.return_value
            mock_instance.translate = AsyncMock(
                side_effect=TranslationServiceError("OpenAI API error: Rate limit exceeded")
            )

            response = client.post("/api/v1/translate/text", json=request_data)

            assert response.status_code == 502
            data = response.json()
            assert "detail" in data
            # Should contain error information
            detail_lower = data["detail"].lower()
            assert "translation" in detail_lower or "error" in detail_lower or "failed" in detail_lower

    def test_translate_text_real_translation_returns_actual_text(self):
        """Test that real translation (not stub) returns actual translated text."""
        request_data = {
            "text": "Hello world",
            "target_language": "french"
        }

        # Mock TranslationService to return French translation
        mock_translation_result = {
            "original_text": "Hello world",
            "translated_text": "Bonjour le monde",
            "source_language": "english",
            "target_language": "french"
        }

        with patch('app.api.v1.endpoints.translate.TranslationService') as MockService:
            mock_instance = MockService.return_value
            mock_instance.translate = AsyncMock(return_value=mock_translation_result)

            response = client.post("/api/v1/translate/text", json=request_data)

            assert response.status_code == 200
            data = response.json()
            # Should NOT be stub format like "[TRANSLATED TO FRENCH]: Hello world"
            assert not data["translated_text"].startswith("[TRANSLATED TO")
            # Should be actual translation
            assert data["translated_text"] == "Bonjour le monde"


class TestTranslateResponseEndpoint:
    """Test suite for POST /api/v1/translate/response endpoint."""

    def test_translate_response_returns_501_not_implemented(self):
        """Test that /translate/response returns 501 Not Implemented."""
        request_data = {
            "original_response": {"answer": "Test answer", "citations": []},
            "target_language": "urdu"
        }

        response = client.post("/api/v1/translate/response", json=request_data)

        assert response.status_code == 501
        data = response.json()
        assert "detail" in data
        # Check that message indicates not implemented status
        detail_lower = data["detail"].lower()
        assert "not" in detail_lower and "implemented" in detail_lower

    def test_translate_response_placeholder_has_proper_json_structure(self):
        """Test that 501 response has proper JSON structure."""
        request_data = {
            "original_response": {},
            "target_language": "spanish"
        }

        response = client.post("/api/v1/translate/response", json=request_data)

        assert response.status_code == 501
        data = response.json()
        assert isinstance(data, dict)
        assert "detail" in data

    def test_translate_response_accepts_any_json_payload(self):
        """Test that endpoint accepts request even though not implemented."""
        request_data = {
            "any_field": "any_value"
        }

        response = client.post("/api/v1/translate/response", json=request_data)

        # Should return 501, not 422 (validation error)
        assert response.status_code == 501
