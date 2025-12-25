"""
Standard API Response Models

All API responses should use these models for consistency.
"""
from typing import Any, Optional, TypeVar, Generic
from pydantic import BaseModel, Field


T = TypeVar("T")


class ResponseMeta(BaseModel):
    """Metadata included with every response."""
    request_id: Optional[str] = Field(None, description="Unique request identifier for tracing")
    duration_ms: Optional[float] = Field(None, description="Request processing time in milliseconds")
    timestamp: str = Field(..., description="Response timestamp (Pacific time)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "request_id": "req_abc123",
                "duration_ms": 45.2,
                "timestamp": "2025-12-24T10:30:00-08:00"
            }
        }
    }


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper.

    All endpoints should return responses in this format:
    - success: bool - Whether the operation succeeded
    - data: Optional[T] - The response data (if success)
    - error: Optional[str] - Error message (if failure)
    - meta: ResponseMeta - Request metadata with timing
    """
    success: bool = Field(..., description="Whether the operation succeeded")
    data: Optional[T] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if success=false")
    meta: Optional[ResponseMeta] = Field(None, description="Request metadata")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "data": {"status": "healthy"},
                    "error": None,
                    "meta": {
                        "request_id": "req_abc123",
                        "duration_ms": 12.5,
                        "timestamp": "2025-12-24T10:30:00-08:00"
                    }
                },
                {
                    "success": False,
                    "data": None,
                    "error": "Resource not found",
                    "meta": {
                        "request_id": "req_xyz789",
                        "duration_ms": 8.1,
                        "timestamp": "2025-12-24T10:30:05-08:00"
                    }
                }
            ]
        }
    }


class ErrorDetail(BaseModel):
    """Detailed error information."""
    code: str = Field(..., description="Error code for programmatic handling")
    message: str = Field(..., description="Human-readable error message")
    field: Optional[str] = Field(None, description="Field that caused the error (for validation)")
    details: Optional[dict] = Field(None, description="Additional error context")


class HealthStatus(BaseModel):
    """Health check response data."""
    status: str = Field(..., description="Current health status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current server time (Pacific)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "version": "0.1.0",
                "timestamp": "2025-12-24T10:30:00-08:00"
            }
        }
    }


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list response."""
    items: list[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total count of items")
    page: int = Field(..., description="Current page number (1-based)")
    page_size: int = Field(..., description="Items per page")
    has_more: bool = Field(..., description="Whether more pages exist")
