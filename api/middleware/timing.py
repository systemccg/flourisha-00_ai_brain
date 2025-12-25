"""
Request Timing Middleware

Adds timing metadata to requests for performance monitoring.
"""
import time
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


# Pacific timezone for consistent timestamps
PACIFIC = ZoneInfo("America/Los_Angeles")


class TimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that tracks request timing and generates request IDs.

    Adds to request.state:
    - request_id: Unique identifier for the request
    - start_time: Request start timestamp
    - get_meta(): Function to get ResponseMeta dict

    Usage in endpoint:
        @app.get("/example")
        async def example(request: Request):
            meta = request.state.get_meta()
            return APIResponse(success=True, data=..., meta=meta)
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Generate request ID and record start time
        request_id = f"req_{uuid.uuid4().hex[:12]}"
        start_time = time.perf_counter()

        # Store in request state
        request.state.request_id = request_id
        request.state.start_time = start_time

        # Helper to get meta dict
        def get_meta():
            duration_ms = (time.perf_counter() - start_time) * 1000
            timestamp = datetime.now(PACIFIC).isoformat()
            return {
                "request_id": request_id,
                "duration_ms": round(duration_ms, 2),
                "timestamp": timestamp,
            }

        request.state.get_meta = get_meta

        # Process request
        response = await call_next(request)

        # Add headers for debugging
        duration_ms = (time.perf_counter() - start_time) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

        return response
