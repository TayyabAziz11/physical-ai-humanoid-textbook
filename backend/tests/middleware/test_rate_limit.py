"""
Tests for rate limiting middleware.

Task 1.6: Rate limiting middleware implementation (RED phase).
"""

import pytest
import time
from unittest.mock import Mock
from fastapi import HTTPException

from app.middleware.rate_limit import RateLimiter


class TestRateLimiter:
    """Test suite for RateLimiter middleware."""

    def test_rate_limiter_allows_requests_under_limit(self):
        """Test that requests under the limit are allowed."""
        limiter = RateLimiter(limit=10, window_seconds=60)

        # Simulate 10 requests from same IP
        for i in range(10):
            mock_request = Mock()
            mock_request.client.host = "192.168.1.1"

            # Should not raise exception
            limiter.check_rate_limit(mock_request)

    def test_rate_limiter_blocks_requests_over_limit(self):
        """Test that 11th request within window is blocked with HTTP 429."""
        limiter = RateLimiter(limit=10, window_seconds=60)

        mock_request = Mock()
        mock_request.client.host = "192.168.1.1"

        # Make 10 requests (should succeed)
        for i in range(10):
            limiter.check_rate_limit(mock_request)

        # 11th request should raise HTTPException with 429
        with pytest.raises(HTTPException) as exc_info:
            limiter.check_rate_limit(mock_request)

        assert exc_info.value.status_code == 429
        assert "rate limit" in exc_info.value.detail.lower()

    def test_rate_limiter_isolates_different_ips(self):
        """Test that rate limits are isolated per IP address."""
        limiter = RateLimiter(limit=10, window_seconds=60)

        # IP 1 makes 10 requests
        ip1_request = Mock()
        ip1_request.client.host = "192.168.1.1"
        for i in range(10):
            limiter.check_rate_limit(ip1_request)

        # IP 2 should still be able to make requests
        ip2_request = Mock()
        ip2_request.client.host = "192.168.1.2"

        # Should not raise exception
        limiter.check_rate_limit(ip2_request)

    def test_rate_limiter_resets_after_window(self):
        """Test that rate limit resets after the time window expires."""
        limiter = RateLimiter(limit=3, window_seconds=1)

        mock_request = Mock()
        mock_request.client.host = "192.168.1.1"

        # Make 3 requests (should succeed)
        for i in range(3):
            limiter.check_rate_limit(mock_request)

        # 4th request should fail
        with pytest.raises(HTTPException):
            limiter.check_rate_limit(mock_request)

        # Wait for window to expire
        time.sleep(1.1)

        # Should be able to make requests again
        limiter.check_rate_limit(mock_request)

    def test_rate_limiter_cleans_old_timestamps(self):
        """Test that old timestamps are removed from storage."""
        limiter = RateLimiter(limit=5, window_seconds=1)

        mock_request = Mock()
        mock_request.client.host = "192.168.1.1"

        # Make 3 requests
        for i in range(3):
            limiter.check_rate_limit(mock_request)

        # Wait for window to expire
        time.sleep(1.1)

        # Make 5 more requests (old timestamps should be cleaned)
        for i in range(5):
            limiter.check_rate_limit(mock_request)

        # 6th request should fail (proving we're counting fresh timestamps)
        with pytest.raises(HTTPException):
            limiter.check_rate_limit(mock_request)

    def test_rate_limiter_default_values(self):
        """Test that RateLimiter uses default limit and window if not specified."""
        limiter = RateLimiter()

        # Should have default limit of 10 requests per 60 seconds
        assert limiter.limit == 10
        assert limiter.window_seconds == 60

    def test_rate_limiter_custom_limit_and_window(self):
        """Test that RateLimiter accepts custom limit and window values."""
        limiter = RateLimiter(limit=5, window_seconds=30)

        assert limiter.limit == 5
        assert limiter.window_seconds == 30

    def test_rate_limiter_handles_missing_client_gracefully(self):
        """Test that rate limiter handles requests without client info."""
        limiter = RateLimiter(limit=10, window_seconds=60)

        # Request without client info (e.g., test client)
        mock_request = Mock()
        mock_request.client = None

        # Should not raise exception (uses fallback IP)
        limiter.check_rate_limit(mock_request)

    def test_rate_limiter_error_message_format(self):
        """Test that HTTP 429 error has proper message format."""
        limiter = RateLimiter(limit=1, window_seconds=60)

        mock_request = Mock()
        mock_request.client.host = "192.168.1.1"

        # Make 1 request
        limiter.check_rate_limit(mock_request)

        # 2nd request should fail with formatted message
        with pytest.raises(HTTPException) as exc_info:
            limiter.check_rate_limit(mock_request)

        assert exc_info.value.status_code == 429
        detail = exc_info.value.detail
        assert "rate limit" in detail.lower() or "too many requests" in detail.lower()
        # Should mention the limit
        assert "1" in detail or "10" in detail

    def test_rate_limiter_concurrent_requests_same_ip(self):
        """Test that concurrent requests from same IP are properly counted."""
        limiter = RateLimiter(limit=5, window_seconds=60)

        mock_request = Mock()
        mock_request.client.host = "192.168.1.1"

        # Simulate 5 rapid concurrent requests
        for i in range(5):
            limiter.check_rate_limit(mock_request)

        # 6th request should be blocked
        with pytest.raises(HTTPException) as exc_info:
            limiter.check_rate_limit(mock_request)

        assert exc_info.value.status_code == 429
