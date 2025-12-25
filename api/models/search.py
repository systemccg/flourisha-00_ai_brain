"""
Search Request/Response Models
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Request model for unified search."""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query text")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum results to return")
    threshold: float = Field(
        default=0.7,
        ge=0.5,
        le=0.99,
        description="Minimum similarity score threshold (0.5-0.99)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "How to implement authentication in FastAPI",
                "limit": 10,
                "threshold": 0.7
            }
        }
    }


class SearchResult(BaseModel):
    """Individual search result."""
    id: str = Field(..., description="Content ID")
    title: str = Field(..., description="Content title")
    content_type: str = Field(..., description="Type of content (youtube_video, document, etc.)")
    summary: Optional[str] = Field(None, description="Content summary")
    preview: Optional[str] = Field(None, description="Text preview (first 200 chars)")
    tags: List[str] = Field(default=[], description="Content tags")
    similarity: float = Field(..., ge=0, le=1, description="Similarity score (0-1)")
    source_url: Optional[str] = Field(None, description="Original source URL")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "abc123",
                "title": "FastAPI Authentication Guide",
                "content_type": "youtube_video",
                "summary": "Comprehensive guide to JWT auth in FastAPI...",
                "preview": "In this video we cover the basics of...",
                "tags": ["fastapi", "authentication", "python"],
                "similarity": 0.87,
                "source_url": "https://youtube.com/watch?v=xyz"
            }
        }
    }


class SearchResponse(BaseModel):
    """Search response with results and metadata."""
    results: List[SearchResult] = Field(..., description="Matching content")
    query: str = Field(..., description="Original query")
    total: int = Field(..., description="Number of results returned")

    model_config = {
        "json_schema_extra": {
            "example": {
                "results": [
                    {
                        "id": "abc123",
                        "title": "FastAPI Authentication",
                        "content_type": "youtube_video",
                        "similarity": 0.87
                    }
                ],
                "query": "FastAPI auth",
                "total": 1
            }
        }
    }
