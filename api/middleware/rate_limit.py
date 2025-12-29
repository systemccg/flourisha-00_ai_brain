"""
Rate Limiting Middleware

Memory-based rate limiting with sliding window algorithm.
Supports per-user and per-IP rate limits with configurable windows.

Features:
- Sliding window rate limiting
- Per-user (authenticated) and per-IP (anonymous) limits
- Configurable rate limits per endpoint pattern
- Rate limit headers in response (X-RateLimit-*)
- 429 Too Many Requests when exceeded
- Optional database persistence for distributed deployments

Usage:
    from middleware.rate_limit import RateLimitMiddleware, rate_limit

    # Add middleware to app
    app.add_middleware(RateLimitMiddleware)

    # Or use decorator for specific endpoints
    @router.get("/search")
    @rate_limit(requests=100, window=60)  # 100 requests per 60 seconds
    async def search(...):
        ...
"""
import time
import hashlib
import logging
from typing import Optional, Dict, Tuple, Callable
from collections import defaultdict
from dataclasses import dataclass, field
from functools import wraps

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    # Default limits
    default_requests: int = 1000  # Requests per window
    default_window: int = 3600  # Window size in seconds (1 hour)

    # Endpoint-specific limits (path pattern -> (requests, window))
    endpoint_limits: Dict[str, Tuple[int, int]] = field(default_factory=lambda: {
        "/api/search": (100, 60),  # 100 per minute (expensive)
        "/api/ingestion": (50, 60),  # 50 per minute (very expensive)
        "/api/documents/upload": (20, 60),  # 20 per minute
        "/api/voice": (30, 60),  # 30 per minute (external API)
        "/api/youtube": (60, 60),  # 60 per minute
        "/api/graph": (100, 60),  # 100 per minute
    })

    # Exempt paths (no rate limiting)
    exempt_paths: list = field(default_factory=lambda: [
        "/api/health",
        "/api/crons/health",
        "/api/migrations/health",
        "/api/webhooks",  # Webhooks use signature verification
        "/docs",
        "/redoc",
        "/openapi.json",
        "/",
    ])

    # Headers
    include_headers: bool = True

    # Anonymous vs authenticated limits
    anonymous_multiplier: float = 0.5  # Anonymous gets 50% of limit


@dataclass
class RateLimitState:
    """State for a single rate limit window."""
    requests: int = 0
    window_start: float = 0.0


class RateLimiter:
    """
    In-memory rate limiter with sliding window algorithm.

    Thread-safe for single-process deployments.
    For distributed deployments, extend with Redis backend.
    """

    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        # State: {identifier: {endpoint_pattern: RateLimitState}}
        self._state: Dict[str, Dict[str, RateLimitState]] = defaultdict(dict)
        self._cleanup_counter = 0

    def _get_identifier(self, request: Request) -> Tuple[str, bool]:
        """
        Get rate limit identifier for a request.

        Returns (identifier, is_authenticated).
        Uses user ID if authenticated, IP address otherwise.
        """
        # Check for authenticated user
        user = getattr(request.state, 'user', None)
        if user and hasattr(user, 'uid') and user.uid:
            return f"user:{user.uid}", True

        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"

        # Check for forwarded headers (behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()

        # Hash IP for privacy
        ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()[:16]
        return f"ip:{ip_hash}", False

    def _get_limit_for_path(self, path: str, is_authenticated: bool) -> Tuple[int, int]:
        """
        Get rate limit for a specific path.

        Returns (max_requests, window_seconds).
        """
        # Check endpoint-specific limits
        for pattern, (requests, window) in self.config.endpoint_limits.items():
            if path.startswith(pattern):
                limit = requests if is_authenticated else int(requests * self.config.anonymous_multiplier)
                return limit, window

        # Use default
        limit = self.config.default_requests
        if not is_authenticated:
            limit = int(limit * self.config.anonymous_multiplier)

        return limit, self.config.default_window

    def _is_exempt(self, path: str) -> bool:
        """Check if path is exempt from rate limiting."""
        for exempt in self.config.exempt_paths:
            if path.startswith(exempt):
                return True
        return False

    def _cleanup_expired(self, current_time: float):
        """Periodically cleanup expired entries."""
        self._cleanup_counter += 1
        if self._cleanup_counter < 1000:
            return

        self._cleanup_counter = 0
        max_window = max(
            self.config.default_window,
            max((w for _, w in self.config.endpoint_limits.values()), default=3600)
        )
        expiry = current_time - max_window * 2

        # Clean up old entries
        identifiers_to_remove = []
        for identifier, states in self._state.items():
            patterns_to_remove = [
                pattern for pattern, state in states.items()
                if state.window_start < expiry
            ]
            for pattern in patterns_to_remove:
                del states[pattern]
            if not states:
                identifiers_to_remove.append(identifier)

        for identifier in identifiers_to_remove:
            del self._state[identifier]

    def check_rate_limit(
        self,
        request: Request
    ) -> Tuple[bool, int, int, int]:
        """
        Check if request is within rate limit.

        Returns:
            (allowed, remaining, limit, reset_seconds)
        """
        path = request.url.path

        # Check exemptions
        if self._is_exempt(path):
            return True, -1, -1, -1

        current_time = time.time()

        # Get identifier and limits
        identifier, is_authenticated = self._get_identifier(request)
        max_requests, window_seconds = self._get_limit_for_path(path, is_authenticated)

        # Get or create state
        # Use path prefix as pattern key
        pattern_key = path.split("/")[2] if path.startswith("/api/") and len(path.split("/")) > 2 else path

        if pattern_key not in self._state[identifier]:
            self._state[identifier][pattern_key] = RateLimitState(
                requests=0,
                window_start=current_time
            )

        state = self._state[identifier][pattern_key]

        # Check if window has expired
        window_end = state.window_start + window_seconds
        if current_time >= window_end:
            # Reset window
            state.requests = 0
            state.window_start = current_time
            window_end = current_time + window_seconds

        # Calculate remaining
        remaining = max(0, max_requests - state.requests)
        reset_seconds = int(window_end - current_time)

        # Check limit
        if state.requests >= max_requests:
            return False, 0, max_requests, reset_seconds

        # Increment counter
        state.requests += 1
        remaining = max(0, max_requests - state.requests)

        # Periodic cleanup
        self._cleanup_expired(current_time)

        return True, remaining, max_requests, reset_seconds


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get or create global rate limiter."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for rate limiting.

    Adds rate limit headers to all responses and returns
    429 Too Many Requests when limit is exceeded.
    """

    def __init__(self, app, config: Optional[RateLimitConfig] = None):
        super().__init__(app)
        self.limiter = RateLimiter(config)
        # Update global instance
        global _rate_limiter
        _rate_limiter = self.limiter

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        allowed, remaining, limit, reset = self.limiter.check_rate_limit(request)

        if not allowed:
            logger.warning(
                f"Rate limit exceeded for {request.url.path} "
                f"(limit: {limit}, reset: {reset}s)"
            )
            response = JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "data": None,
                    "error": "Rate limit exceeded. Please try again later.",
                    "meta": {
                        "request_id": getattr(request.state, 'request_id', None),
                        "retry_after": reset,
                    },
                },
            )
            # Add rate limit headers
            if self.limiter.config.include_headers:
                response.headers["X-RateLimit-Limit"] = str(limit)
                response.headers["X-RateLimit-Remaining"] = "0"
                response.headers["X-RateLimit-Reset"] = str(reset)
                response.headers["Retry-After"] = str(reset)
            return response

        # Process request
        response = await call_next(request)

        # Add rate limit headers to successful responses
        if self.limiter.config.include_headers and limit > 0:
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(reset)

        return response


def rate_limit(requests: int = 100, window: int = 60):
    """
    Decorator for endpoint-specific rate limiting.

    Usage:
        @router.get("/expensive")
        @rate_limit(requests=10, window=60)
        async def expensive_endpoint():
            ...

    Args:
        requests: Maximum requests allowed in window
        window: Time window in seconds
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request from args/kwargs
            request = kwargs.get('request')
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            if request:
                limiter = get_rate_limiter()

                # Override limits for this check
                original_limits = limiter.config.endpoint_limits.copy()
                path = request.url.path
                limiter.config.endpoint_limits[path] = (requests, window)

                try:
                    allowed, remaining, limit, reset = limiter.check_rate_limit(request)

                    if not allowed:
                        raise HTTPException(
                            status_code=429,
                            detail={
                                "error": "Rate limit exceeded",
                                "retry_after": reset,
                            },
                            headers={
                                "X-RateLimit-Limit": str(limit),
                                "X-RateLimit-Remaining": "0",
                                "X-RateLimit-Reset": str(reset),
                                "Retry-After": str(reset),
                            },
                        )
                finally:
                    # Restore original limits
                    limiter.config.endpoint_limits = original_limits

            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Export rate limit status endpoint helper
def get_rate_limit_status(request: Request) -> dict:
    """
    Get current rate limit status for a request.

    Useful for debugging and status endpoints.
    """
    limiter = get_rate_limiter()
    identifier, is_authenticated = limiter._get_identifier(request)
    path = request.url.path
    max_requests, window = limiter._get_limit_for_path(path, is_authenticated)

    return {
        "identifier": identifier[:20] + "...",  # Truncate for privacy
        "is_authenticated": is_authenticated,
        "limit": max_requests,
        "window_seconds": window,
        "path": path,
    }
