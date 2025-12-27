"""
Transcript Service Models

Pydantic models for transcript API requests and responses.
"""
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field


class TranscriptSource(str, Enum):
    """Source of the transcript."""
    YOUTUBE_API = "youtube_api"
    WHISPER = "whisper"
    CACHE = "cache"
    FAILED = "failed"


class TranscriptRequest(BaseModel):
    """Request for transcript extraction."""
    video_id: str = Field(..., description="YouTube video ID or URL", min_length=1)
    languages: Optional[List[str]] = Field(
        default=None,
        description="Preferred languages in priority order (default: ['en', 'en-US'])"
    )
    skip_cache: bool = Field(
        default=False,
        description="Skip cache and fetch fresh transcript"
    )
    skip_api: bool = Field(
        default=False,
        description="Skip YouTube API and use Whisper directly"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "video_id": "dQw4w9WgXcQ",
                "languages": ["en", "en-US"],
                "skip_cache": False,
                "skip_api": False
            }
        }
    }


class TranscriptMetadata(BaseModel):
    """Metadata about the transcript."""
    char_count: int = Field(..., description="Number of characters in transcript")
    word_count: Optional[int] = Field(None, description="Approximate word count")
    duration: Optional[float] = Field(None, description="Audio duration in seconds (Whisper only)")
    audio_size_mb: Optional[float] = Field(None, description="Audio file size in MB (Whisper only)")
    cached_at: Optional[str] = Field(None, description="When the transcript was cached")
    expires_at: Optional[str] = Field(None, description="When cache expires")

    model_config = {
        "json_schema_extra": {
            "example": {
                "char_count": 15420,
                "word_count": 2570,
                "duration": 843.5,
                "cached_at": "2025-12-27T10:30:00-08:00",
                "expires_at": "2026-01-27T10:30:00-08:00"
            }
        }
    }


class TranscriptResult(BaseModel):
    """Result of transcript extraction."""
    success: bool = Field(..., description="Whether extraction succeeded")
    video_id: str = Field(..., description="YouTube video ID")
    transcript: Optional[str] = Field(None, description="The transcript text")
    source: TranscriptSource = Field(..., description="Where transcript came from")
    language: str = Field(default="en", description="Transcript language code")
    error: Optional[str] = Field(None, description="Error message if failed")
    metadata: Optional[TranscriptMetadata] = Field(None, description="Transcript metadata")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "video_id": "dQw4w9WgXcQ",
                "transcript": "Never gonna give you up, never gonna let you down...",
                "source": "youtube_api",
                "language": "en",
                "error": None,
                "metadata": {
                    "char_count": 2500,
                    "word_count": 450,
                    "cached_at": "2025-12-27T10:30:00-08:00"
                }
            }
        }
    }


class TranscriptCacheEntry(BaseModel):
    """A cached transcript entry."""
    video_id: str = Field(..., description="YouTube video ID")
    source: TranscriptSource = Field(..., description="Original source")
    language: str = Field(..., description="Language code")
    cached_at: str = Field(..., description="When cached (Pacific time)")
    expires_at: str = Field(..., description="When cache expires")
    char_count: int = Field(..., description="Transcript length")

    model_config = {
        "json_schema_extra": {
            "example": {
                "video_id": "dQw4w9WgXcQ",
                "source": "youtube_api",
                "language": "en",
                "cached_at": "2025-12-27T10:30:00-08:00",
                "expires_at": "2026-01-27T10:30:00-08:00",
                "char_count": 2500
            }
        }
    }


class TranscriptCacheStats(BaseModel):
    """Cache statistics."""
    total_entries: int = Field(..., description="Total cached transcripts")
    total_size_bytes: int = Field(..., description="Total cache size in bytes")
    oldest_entry: Optional[str] = Field(None, description="Oldest cached entry date")
    newest_entry: Optional[str] = Field(None, description="Newest cached entry date")
    by_source: Dict[str, int] = Field(default_factory=dict, description="Count by source")

    model_config = {
        "json_schema_extra": {
            "example": {
                "total_entries": 150,
                "total_size_bytes": 5242880,
                "oldest_entry": "2025-11-15T08:00:00-08:00",
                "newest_entry": "2025-12-27T10:30:00-08:00",
                "by_source": {
                    "youtube_api": 120,
                    "whisper": 30
                }
            }
        }
    }


class TranscriptBatchRequest(BaseModel):
    """Request for batch transcript extraction."""
    video_ids: List[str] = Field(
        ...,
        description="List of video IDs or URLs",
        min_length=1,
        max_length=10
    )
    languages: Optional[List[str]] = Field(default=None)
    skip_cache: bool = Field(default=False)

    model_config = {
        "json_schema_extra": {
            "example": {
                "video_ids": ["dQw4w9WgXcQ", "oHg5SJYRHA0"],
                "languages": ["en"],
                "skip_cache": False
            }
        }
    }


class TranscriptBatchResult(BaseModel):
    """Result of batch transcript extraction."""
    total: int = Field(..., description="Total videos requested")
    succeeded: int = Field(..., description="Successfully extracted")
    failed: int = Field(..., description="Failed extractions")
    from_cache: int = Field(..., description="Retrieved from cache")
    results: List[TranscriptResult] = Field(..., description="Individual results")

    model_config = {
        "json_schema_extra": {
            "example": {
                "total": 2,
                "succeeded": 2,
                "failed": 0,
                "from_cache": 1,
                "results": []
            }
        }
    }
