"""
Integration tests for rate limiting on translation endpoints.

Task 1.6: Rate limiting integration tests.
"""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.middleware.rate_limit import RateLimiter

# Create test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset rate limiter before each test to ensure test isolation."""
    # Import the module-level rate_limiter and reset its state
    from app.api.v1.endpoints import translate
    translate.rate_limiter = RateLimiter(limit=10, window_seconds=60)
    yield
    # No cleanup needed


class TestRateLimitingIntegration:
    """Test suite for rate limiting integration with translation endpoints."""

    def test_rate_limit_allows_10_requests(self):
        """Test that 10 requests within window are allowed."""
        # Mock TranslationService to avoid real OpenAI calls
        with patch('app.api.v1.endpoints.translate.TranslationService') as MockService:
            mock_instance = MockService.return_value
            mock_instance.translate = AsyncMock(return_value={
                "original_text": "Test",
                "translated_text": "Prueba",
                "source_language": "english",
                "target_language": "spanish"
            })

            request_data = {
                "text": "Test",
                "target_language": "spanish"
            }

            # Make 10 requests - all should succeed
            for i in range(10):
                response = client.post("/api/v1/translate/text", json=request_data)
                assert response.status_code == 200, f"Request {i+1} failed"

    def test_rate_limit_blocks_11th_request(self):
        """Test that 11th request within window returns HTTP 429."""
        # Mock TranslationService
        with patch('app.api.v1.endpoints.translate.TranslationService') as MockService:
            mock_instance = MockService.return_value
            mock_instance.translate = AsyncMock(return_value={
                "original_text": "Test",
                "translated_text": "Prueba",
                "source_language": "english",
                "target_language": "spanish"
            })

            request_data = {
                "text": "Test",
                "target_language": "spanish"
            }

            # Make 10 requests
            for i in range(10):
                response = client.post("/api/v1/translate/text", json=request_data)
                assert response.status_code == 200

            # 11th request should be rate limited
            response = client.post("/api/v1/translate/text", json=request_data)
            assert response.status_code == 429
            data = response.json()
            assert "detail" in data
            assert "rate limit" in data["detail"].lower() or "too many requests" in data["detail"].lower()

    def test_rate_limit_error_message_includes_limit_info(self):
        """Test that rate limit error message includes helpful information."""
        # Mock TranslationService
        with patch('app.api.v1.endpoints.translate.TranslationService') as MockService:
            mock_instance = MockService.return_value
            mock_instance.translate = AsyncMock(return_value={
                "original_text": "Test",
                "translated_text": "Prueba",
                "source_language": "english",
                "target_language": "spanish"
            })

            request_data = {
                "text": "Test",
                "target_language": "spanish"
            }

            # Exceed rate limit
            for i in range(10):
                client.post("/api/v1/translate/text", json=request_data)

            response = client.post("/api/v1/translate/text", json=request_data)
            assert response.status_code == 429

            data = response.json()
            detail = data["detail"]

            # Should mention the limit (10) and window (60 seconds)
            assert "10" in detail
            assert "60" in detail or "minute" in detail.lower()
