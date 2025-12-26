"""
Knowledge Ingestion Status Models

Pydantic models for knowledge ingestion status API.
"""
from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field


class ContentTypeCount(BaseModel):
    """Count of items by content type."""
    source_type: str = Field(..., description="Content source type (upload, youtube, gmail, etc.)")
    count: int = Field(..., description="Number of items")

    model_config = {
        "json_schema_extra": {
            "example": {
                "source_type": "upload",
                "count": 42
            }
        }
    }


class QueueItem(BaseModel):
    """Item in the processing queue."""
    content_id: str = Field(..., description="Content ID")
    title: Optional[str] = Field(None, description="Content title")
    source_type: str = Field(..., description="Source type")
    priority: int = Field(..., description="Processing priority (1-10)")
    status: str = Field(..., description="Queue status")
    created_at: str = Field(..., description="When queued")
    retry_count: int = Field(default=0, description="Number of retry attempts")

    model_config = {
        "json_schema_extra": {
            "example": {
                "content_id": "doc_abc123",
                "title": "Medical Records Q4",
                "source_type": "upload",
                "priority": 5,
                "status": "queued",
                "created_at": "2025-12-26T10:00:00-08:00",
                "retry_count": 0
            }
        }
    }


class RecentItem(BaseModel):
    """Recently processed content item."""
    content_id: str = Field(..., description="Content ID")
    title: Optional[str] = Field(None, description="Content title")
    source_type: str = Field(..., description="Source type")
    status: str = Field(..., description="Processing status")
    processed_at: str = Field(..., description="When processing completed")
    has_embedding: bool = Field(default=False, description="Whether embedding was generated")
    has_graph: bool = Field(default=False, description="Whether added to knowledge graph")
    error_message: Optional[str] = Field(None, description="Error if failed")

    model_config = {
        "json_schema_extra": {
            "example": {
                "content_id": "doc_xyz789",
                "title": "Meeting Notes",
                "source_type": "upload",
                "status": "completed",
                "processed_at": "2025-12-26T09:45:00-08:00",
                "has_embedding": True,
                "has_graph": True,
                "error_message": None
            }
        }
    }


class IngestionStats(BaseModel):
    """Overall ingestion statistics."""
    total_items: int = Field(..., description="Total content items")
    completed: int = Field(..., description="Successfully processed items")
    pending: int = Field(..., description="Items awaiting processing")
    processing: int = Field(..., description="Items currently being processed")
    failed: int = Field(..., description="Failed items")

    model_config = {
        "json_schema_extra": {
            "example": {
                "total_items": 150,
                "completed": 142,
                "pending": 5,
                "processing": 2,
                "failed": 1
            }
        }
    }


class IngestionStatusResponse(BaseModel):
    """Complete ingestion status dashboard data."""
    stats: IngestionStats = Field(..., description="Overall statistics")
    by_content_type: List[ContentTypeCount] = Field(..., description="Counts by content type")
    queue: List[QueueItem] = Field(..., description="Pending queue items")
    recent: List[RecentItem] = Field(..., description="Recently processed items")
    last_updated: str = Field(..., description="When this status was generated")

    model_config = {
        "json_schema_extra": {
            "example": {
                "stats": {
                    "total_items": 150,
                    "completed": 142,
                    "pending": 5,
                    "processing": 2,
                    "failed": 1
                },
                "by_content_type": [
                    {"source_type": "upload", "count": 50},
                    {"source_type": "youtube", "count": 80},
                    {"source_type": "gmail", "count": 20}
                ],
                "queue": [],
                "recent": [],
                "last_updated": "2025-12-26T10:30:00-08:00"
            }
        }
    }
