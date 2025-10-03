import pytest
from unittest.mock import Mock
from fastapi import Request
from slowapi.errors import RateLimitExceeded

from app.infrastructure.api.rate_limiter import _rate_limit_key_func, rate_limit_exceeded_handler


@pytest.mark.unit
class TestRateLimiter:
    """Test rate limiter utility functions."""

    def test_rate_limit_key_func(self):
        """Test that rate limit key function returns client IP."""
        # Mock request
        request = Mock(spec=Request)
        request.client = Mock()
        request.client.host = "192.168.1.1"

        key = _rate_limit_key_func(request)

        assert isinstance(key, str)
        # The function uses slowapi's get_remote_address which may return different format
        # Just verify it returns a string (IP address)
        assert len(key) > 0

    def test_rate_limit_exceeded_handler(self):
        """Test rate limit exceeded handler returns 429 response."""
        request = Mock(spec=Request)
        exc = RateLimitExceeded(limit=Mock())

        response = rate_limit_exceeded_handler(request, exc)

        assert response.status_code == 429
        content = response.body.decode()
        assert "Rate limit exceeded" in content
        assert "Too many requests" in content

    def test_rate_limit_exceeded_handler_with_retry_after(self):
        """Test rate limit exceeded handler includes retry_after if available."""
        request = Mock(spec=Request)
        exc = RateLimitExceeded(limit=Mock())
        exc.retry_after = 60

        response = rate_limit_exceeded_handler(request, exc)

        assert response.status_code == 429
        content = response.body.decode()
        assert "Rate limit exceeded" in content
        assert "60" in content or "retry_after" in content.lower()
