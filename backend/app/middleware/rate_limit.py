"""
Rate limiting middleware for translation API.

This module provides in-memory rate limiting to prevent API abuse.
Rate limits are applied per IP address using a sliding window algorithm.

Task 1.6: Rate limiting middleware implementation.
"""

import time
from collections import defaultdict
from typing import Dict, List
from fastapi import HTTPException, Request, status


class RateLimiter:
    """
    In-memory rate limiter using sliding window algorithm.

    Tracks request timestamps per IP address and enforces a maximum number of requests
    within a specified time window.

    Features:
    - Per-IP rate limiting (isolated counters for each client)
    - Sliding window algorithm (old timestamps automatically cleaned)
    - Configurable limit and window duration
    - HTTP 429 Too Many Requests on limit exceeded

    Default configuration:
    - Limit: 10 requests per minute
    - Window: 60 seconds
    """

    def __init__(self, limit: int = 10, window_seconds: int = 60):
        """
        Initialize rate limiter with configurable limits.

        Args:
            limit: Maximum number of requests allowed within the window (default: 10)
            window_seconds: Time window in seconds (default: 60)
        """
        self.limit = limit
        self.window_seconds = window_seconds
        # Storage: {ip_address: [timestamp1, timestamp2, ...]}
        self.request_timestamps: Dict[str, List[float]] = defaultdict(list)

    def check_rate_limit(self, request: Request) -> None:
        """
        Check if request exceeds rate limit and raise HTTPException if so.

        This method:
        1. Extracts client IP address from request
        2. Removes timestamps older than the window
        3. Checks if request count exceeds limit
        4. Records new timestamp if under limit
        5. Raises HTTP 429 if over limit

        Args:
            request: FastAPI Request object with client information

        Raises:
            HTTPException: HTTP 429 Too Many Requests if limit exceeded
        """
        # Get client IP (use fallback for test clients without client info)
        client_ip = self._get_client_ip(request)

        # Get current time
        current_time = time.time()

        # Remove timestamps older than window
        self.request_timestamps[client_ip] = [
            ts for ts in self.request_timestamps[client_ip]
            if current_time - ts < self.window_seconds
        ]

        # Check if limit exceeded
        if len(self.request_timestamps[client_ip]) >= self.limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {self.limit} requests per {self.window_seconds} seconds. Please try again later."
            )

        # Record this request
        self.request_timestamps[client_ip].append(current_time)

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request.

        Args:
            request: FastAPI Request object

        Returns:
            Client IP address string, or "unknown" if not available
        """
        if request.client is None:
            return "unknown"
        return request.client.host
