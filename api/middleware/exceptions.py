"""
Exception Handlers

Ensures all errors return consistent APIResponse format.
"""
import logging
import traceback
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


PACIFIC = ZoneInfo("America/Los_Angeles")

# Configure logger
logger = logging.getLogger("flourisha.api")


def get_request_meta(request: Request) -> dict:
    """Get meta from request state or create default."""
    if hasattr(request.state, "get_meta"):
        return request.state.get_meta()
    return {
        "request_id": getattr(request.state, "request_id", None),
        "duration_ms": None,
        "timestamp": datetime.now(PACIFIC).isoformat(),
    }


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions with APIResponse format.

    Covers 404 Not Found, 403 Forbidden, 401 Unauthorized, etc.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "data": None,
            "error": exc.detail,
            "meta": get_request_meta(request),
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors with field-level details.

    Returns structured error information for each validation failure.
    """
    errors = exc.errors()

    # Build field-level error details
    field_errors = []
    for error in errors:
        # Skip "body" in location for cleaner field paths
        loc_parts = [str(l) for l in error["loc"] if l != "body"]
        field_path = ".".join(loc_parts) if loc_parts else "body"

        field_errors.append({
            "field": field_path,
            "message": error["msg"],
            "type": error["type"],
        })

    # Create summary message
    if len(field_errors) == 1:
        summary = f"Validation error in {field_errors[0]['field']}: {field_errors[0]['message']}"
    else:
        summary = f"Validation errors in {len(field_errors)} fields"

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "data": {"validation_errors": field_errors},
            "error": summary,
            "meta": get_request_meta(request),
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions.

    Logs full traceback for debugging but returns safe message to client.
    """
    request_id = getattr(request.state, "request_id", "unknown")

    # Log full traceback
    tb = traceback.format_exc()
    logger.error(
        f"Unhandled exception [request_id={request_id}]: "
        f"{type(exc).__name__}: {exc}\n{tb}"
    )

    # Also print for development visibility
    print(f"[{request_id}] Unhandled exception: {type(exc).__name__}: {exc}")
    print(tb)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "data": None,
            "error": "Internal server error",
            "meta": get_request_meta(request),
        },
    )
