"""
Transcript Service API Router

REST API for YouTube transcript extraction with caching.
Wraps transcript_service.py with file-based caching layer.

Acceptance Criteria:
- Returns cached if exists
- Tries YouTube API first, Whisper fallback
- Indicates source (API/Whisper/Cache)
"""
import sys
import os
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Optional, List

from fastapi import APIRouter, Depends, Request, Query, BackgroundTasks
from pydantic import BaseModel

from models.response import APIResponse, ResponseMeta
from models.transcript import (
    TranscriptRequest,
    TranscriptResult,
    TranscriptSource,
    TranscriptMetadata,
    TranscriptCacheEntry,
    TranscriptCacheStats,
    TranscriptBatchRequest,
    TranscriptBatchResult,
)
from middleware.auth import get_current_user, UserContext

# Add services to path for imports
services_path = Path(__file__).parent.parent.parent / "services"
sys.path.insert(0, str(services_path))

router = APIRouter(prefix="/api/transcripts", tags=["Transcripts"])

# Pacific timezone for timestamps
PACIFIC = ZoneInfo("America/Los_Angeles")

# Cache configuration
CACHE_DIR = Path("/root/flourisha/00_AI_Brain/data/transcripts")
CACHE_EXPIRY_DAYS = 30  # Cache transcripts for 30 days


def ensure_cache_dir():
    """Ensure cache directory exists."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_cache_path(video_id: str) -> Path:
    """Get cache file path for a video ID."""
    # Use MD5 hash to handle any special characters
    safe_id = hashlib.md5(video_id.encode()).hexdigest()[:16]
    return CACHE_DIR / f"{video_id}_{safe_id}.json"


def read_from_cache(video_id: str) -> Optional[dict]:
    """Read transcript from cache if exists and not expired."""
    cache_path = get_cache_path(video_id)

    if not cache_path.exists():
        return None

    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Check expiry
        expires_at = datetime.fromisoformat(data.get('expires_at', ''))
        if datetime.now(PACIFIC) > expires_at:
            # Cache expired
            cache_path.unlink(missing_ok=True)
            return None

        return data
    except (json.JSONDecodeError, ValueError, KeyError):
        return None


def write_to_cache(video_id: str, transcript: str, source: str, language: str, metadata: dict = None):
    """Write transcript to cache."""
    ensure_cache_dir()
    cache_path = get_cache_path(video_id)

    now = datetime.now(PACIFIC)
    expires = now + timedelta(days=CACHE_EXPIRY_DAYS)

    cache_data = {
        'video_id': video_id,
        'transcript': transcript,
        'source': source,
        'language': language,
        'cached_at': now.isoformat(),
        'expires_at': expires.isoformat(),
        'metadata': metadata or {}
    }

    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)


def delete_from_cache(video_id: str) -> bool:
    """Delete transcript from cache."""
    cache_path = get_cache_path(video_id)
    if cache_path.exists():
        cache_path.unlink()
        return True
    return False


def get_transcript_service():
    """Lazy import TranscriptService."""
    from transcript_service import TranscriptService
    return TranscriptService()


def extract_video_id(video_id_or_url: str) -> str:
    """Extract video ID from URL or return as-is."""
    import re

    # If it's already a video ID (11 chars)
    if re.match(r'^[0-9A-Za-z_-]{11}$', video_id_or_url):
        return video_id_or_url

    # Extract from various URL formats
    patterns = [
        r'(?:v=|/)([0-9A-Za-z_-]{11})(?:[&?]|$)',
        r'(?:embed/)([0-9A-Za-z_-]{11})',
        r'(?:youtu\.be/)([0-9A-Za-z_-]{11})',
    ]

    for pattern in patterns:
        match = re.search(pattern, video_id_or_url)
        if match:
            return match.group(1)

    return video_id_or_url  # Return as-is if no pattern matches


@router.get("/{video_id}", response_model=APIResponse[TranscriptResult])
async def get_transcript(
    video_id: str,
    request: Request,
    skip_cache: bool = Query(False, description="Skip cache and fetch fresh"),
    skip_api: bool = Query(False, description="Skip YouTube API, use Whisper"),
    languages: Optional[str] = Query(None, description="Comma-separated language codes"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[TranscriptResult]:
    """
    Get transcript for a YouTube video.

    Extraction priority:
    1. Return from cache if exists (unless skip_cache=true)
    2. Try YouTube Transcript API via Tor proxy
    3. Fall back to Whisper transcription

    **Requires:** Valid Firebase JWT

    **Path Parameters:**
    - video_id: YouTube video ID or full URL

    **Query Parameters:**
    - skip_cache: Bypass cache and fetch fresh (default: false)
    - skip_api: Skip YouTube API and use Whisper directly (default: false)
    - languages: Comma-separated language codes (default: en,en-US)

    **Returns:**
    - transcript: The full transcript text
    - source: Where it came from (cache, youtube_api, whisper)
    - metadata: Character count, word count, cache info
    """
    meta_dict = request.state.get_meta()

    try:
        # Clean video ID
        clean_video_id = extract_video_id(video_id)

        # Parse languages
        lang_list = languages.split(',') if languages else ['en', 'en-US', 'a.en']

        # Check cache first (unless skipping)
        if not skip_cache:
            cached = read_from_cache(clean_video_id)
            if cached:
                char_count = len(cached['transcript'])
                word_count = len(cached['transcript'].split())

                result = TranscriptResult(
                    success=True,
                    video_id=clean_video_id,
                    transcript=cached['transcript'],
                    source=TranscriptSource.CACHE,
                    language=cached.get('language', 'en'),
                    metadata=TranscriptMetadata(
                        char_count=char_count,
                        word_count=word_count,
                        cached_at=cached.get('cached_at'),
                        expires_at=cached.get('expires_at'),
                        duration=cached.get('metadata', {}).get('duration'),
                        audio_size_mb=cached.get('metadata', {}).get('audio_size_mb'),
                    )
                )

                return APIResponse(
                    success=True,
                    data=result,
                    meta=ResponseMeta(**meta_dict),
                )

        # Fetch from service
        service = get_transcript_service()
        transcript_result = service.get_transcript(
            video_id=clean_video_id,
            languages=lang_list,
            skip_tier1=skip_api,
        )

        if transcript_result.success:
            # Cache the result
            write_to_cache(
                video_id=clean_video_id,
                transcript=transcript_result.transcript,
                source=transcript_result.source.value,
                language=transcript_result.language,
                metadata=transcript_result.metadata,
            )

            # Build metadata
            char_count = len(transcript_result.transcript)
            word_count = len(transcript_result.transcript.split())
            now = datetime.now(PACIFIC)
            expires = now + timedelta(days=CACHE_EXPIRY_DAYS)

            # Map service source to API source
            source_map = {
                'youtube_api': TranscriptSource.YOUTUBE_API,
                'whisper': TranscriptSource.WHISPER,
                'failed': TranscriptSource.FAILED,
            }
            api_source = source_map.get(
                transcript_result.source.value,
                TranscriptSource.YOUTUBE_API
            )

            result = TranscriptResult(
                success=True,
                video_id=clean_video_id,
                transcript=transcript_result.transcript,
                source=api_source,
                language=transcript_result.language,
                metadata=TranscriptMetadata(
                    char_count=char_count,
                    word_count=word_count,
                    duration=transcript_result.metadata.get('duration') if transcript_result.metadata else None,
                    audio_size_mb=transcript_result.metadata.get('audio_size_mb') if transcript_result.metadata else None,
                    cached_at=now.isoformat(),
                    expires_at=expires.isoformat(),
                )
            )
        else:
            result = TranscriptResult(
                success=False,
                video_id=clean_video_id,
                transcript=None,
                source=TranscriptSource.FAILED,
                error=transcript_result.error or "Failed to extract transcript",
            )

        return APIResponse(
            success=result.success,
            data=result,
            error=result.error if not result.success else None,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            data=TranscriptResult(
                success=False,
                video_id=video_id,
                source=TranscriptSource.FAILED,
                error=str(e),
            ),
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.post("/extract", response_model=APIResponse[TranscriptResult])
async def extract_transcript(
    request: Request,
    body: TranscriptRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[TranscriptResult]:
    """
    Extract transcript with full options.

    Same as GET /{video_id} but allows more control via POST body.

    **Requires:** Valid Firebase JWT

    **Request Body:**
    - video_id: YouTube video ID or URL
    - languages: List of preferred languages
    - skip_cache: Skip cache lookup
    - skip_api: Skip YouTube API
    """
    meta_dict = request.state.get_meta()

    try:
        # Clean video ID
        clean_video_id = extract_video_id(body.video_id)
        lang_list = body.languages or ['en', 'en-US', 'a.en']

        # Check cache first (unless skipping)
        if not body.skip_cache:
            cached = read_from_cache(clean_video_id)
            if cached:
                char_count = len(cached['transcript'])
                word_count = len(cached['transcript'].split())

                result = TranscriptResult(
                    success=True,
                    video_id=clean_video_id,
                    transcript=cached['transcript'],
                    source=TranscriptSource.CACHE,
                    language=cached.get('language', 'en'),
                    metadata=TranscriptMetadata(
                        char_count=char_count,
                        word_count=word_count,
                        cached_at=cached.get('cached_at'),
                        expires_at=cached.get('expires_at'),
                    )
                )

                return APIResponse(
                    success=True,
                    data=result,
                    meta=ResponseMeta(**meta_dict),
                )

        # Fetch from service
        service = get_transcript_service()
        transcript_result = service.get_transcript(
            video_id=clean_video_id,
            languages=lang_list,
            skip_tier1=body.skip_api,
        )

        if transcript_result.success:
            # Cache the result
            write_to_cache(
                video_id=clean_video_id,
                transcript=transcript_result.transcript,
                source=transcript_result.source.value,
                language=transcript_result.language,
                metadata=transcript_result.metadata,
            )

            char_count = len(transcript_result.transcript)
            word_count = len(transcript_result.transcript.split())
            now = datetime.now(PACIFIC)
            expires = now + timedelta(days=CACHE_EXPIRY_DAYS)

            source_map = {
                'youtube_api': TranscriptSource.YOUTUBE_API,
                'whisper': TranscriptSource.WHISPER,
                'failed': TranscriptSource.FAILED,
            }
            api_source = source_map.get(
                transcript_result.source.value,
                TranscriptSource.YOUTUBE_API
            )

            result = TranscriptResult(
                success=True,
                video_id=clean_video_id,
                transcript=transcript_result.transcript,
                source=api_source,
                language=transcript_result.language,
                metadata=TranscriptMetadata(
                    char_count=char_count,
                    word_count=word_count,
                    duration=transcript_result.metadata.get('duration') if transcript_result.metadata else None,
                    audio_size_mb=transcript_result.metadata.get('audio_size_mb') if transcript_result.metadata else None,
                    cached_at=now.isoformat(),
                    expires_at=expires.isoformat(),
                )
            )
        else:
            result = TranscriptResult(
                success=False,
                video_id=clean_video_id,
                source=TranscriptSource.FAILED,
                error=transcript_result.error or "Failed to extract transcript",
            )

        return APIResponse(
            success=result.success,
            data=result,
            error=result.error if not result.success else None,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            data=TranscriptResult(
                success=False,
                video_id=body.video_id,
                source=TranscriptSource.FAILED,
                error=str(e),
            ),
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.post("/batch", response_model=APIResponse[TranscriptBatchResult])
async def batch_extract_transcripts(
    request: Request,
    body: TranscriptBatchRequest,
    background_tasks: BackgroundTasks,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[TranscriptBatchResult]:
    """
    Extract transcripts for multiple videos.

    Limited to 10 videos per request. Results returned inline.
    For larger batches, consider processing videos one at a time.

    **Requires:** Valid Firebase JWT

    **Request Body:**
    - video_ids: List of video IDs or URLs (max 10)
    - languages: Preferred languages
    - skip_cache: Skip cache lookups
    """
    meta_dict = request.state.get_meta()

    try:
        lang_list = body.languages or ['en', 'en-US', 'a.en']
        results = []
        succeeded = 0
        failed = 0
        from_cache = 0

        for vid in body.video_ids:
            clean_video_id = extract_video_id(vid)

            # Check cache first
            if not body.skip_cache:
                cached = read_from_cache(clean_video_id)
                if cached:
                    char_count = len(cached['transcript'])
                    word_count = len(cached['transcript'].split())

                    result = TranscriptResult(
                        success=True,
                        video_id=clean_video_id,
                        transcript=cached['transcript'],
                        source=TranscriptSource.CACHE,
                        language=cached.get('language', 'en'),
                        metadata=TranscriptMetadata(
                            char_count=char_count,
                            word_count=word_count,
                            cached_at=cached.get('cached_at'),
                            expires_at=cached.get('expires_at'),
                        )
                    )
                    results.append(result)
                    succeeded += 1
                    from_cache += 1
                    continue

            # Fetch from service
            try:
                service = get_transcript_service()
                transcript_result = service.get_transcript(
                    video_id=clean_video_id,
                    languages=lang_list,
                )

                if transcript_result.success:
                    # Cache the result
                    write_to_cache(
                        video_id=clean_video_id,
                        transcript=transcript_result.transcript,
                        source=transcript_result.source.value,
                        language=transcript_result.language,
                        metadata=transcript_result.metadata,
                    )

                    char_count = len(transcript_result.transcript)
                    word_count = len(transcript_result.transcript.split())
                    now = datetime.now(PACIFIC)
                    expires = now + timedelta(days=CACHE_EXPIRY_DAYS)

                    source_map = {
                        'youtube_api': TranscriptSource.YOUTUBE_API,
                        'whisper': TranscriptSource.WHISPER,
                    }
                    api_source = source_map.get(
                        transcript_result.source.value,
                        TranscriptSource.YOUTUBE_API
                    )

                    result = TranscriptResult(
                        success=True,
                        video_id=clean_video_id,
                        transcript=transcript_result.transcript,
                        source=api_source,
                        language=transcript_result.language,
                        metadata=TranscriptMetadata(
                            char_count=char_count,
                            word_count=word_count,
                            cached_at=now.isoformat(),
                            expires_at=expires.isoformat(),
                        )
                    )
                    succeeded += 1
                else:
                    result = TranscriptResult(
                        success=False,
                        video_id=clean_video_id,
                        source=TranscriptSource.FAILED,
                        error=transcript_result.error,
                    )
                    failed += 1

            except Exception as e:
                result = TranscriptResult(
                    success=False,
                    video_id=clean_video_id,
                    source=TranscriptSource.FAILED,
                    error=str(e),
                )
                failed += 1

            results.append(result)

        batch_result = TranscriptBatchResult(
            total=len(body.video_ids),
            succeeded=succeeded,
            failed=failed,
            from_cache=from_cache,
            results=results,
        )

        return APIResponse(
            success=True,
            data=batch_result,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/cache/{video_id}", response_model=APIResponse[TranscriptCacheEntry])
async def get_cache_entry(
    video_id: str,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[TranscriptCacheEntry]:
    """
    Check if a video transcript is cached.

    Returns cache metadata without the full transcript.

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        clean_video_id = extract_video_id(video_id)
        cached = read_from_cache(clean_video_id)

        if cached:
            source_map = {
                'youtube_api': TranscriptSource.YOUTUBE_API,
                'whisper': TranscriptSource.WHISPER,
                'cache': TranscriptSource.CACHE,
            }

            entry = TranscriptCacheEntry(
                video_id=clean_video_id,
                source=source_map.get(cached.get('source'), TranscriptSource.YOUTUBE_API),
                language=cached.get('language', 'en'),
                cached_at=cached.get('cached_at'),
                expires_at=cached.get('expires_at'),
                char_count=len(cached.get('transcript', '')),
            )

            return APIResponse(
                success=True,
                data=entry,
                meta=ResponseMeta(**meta_dict),
            )
        else:
            return APIResponse(
                success=False,
                error="Transcript not in cache",
                meta=ResponseMeta(**meta_dict),
            )

    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.delete("/cache/{video_id}", response_model=APIResponse[dict])
async def delete_cache_entry(
    video_id: str,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[dict]:
    """
    Delete a cached transcript.

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        clean_video_id = extract_video_id(video_id)
        deleted = delete_from_cache(clean_video_id)

        if deleted:
            return APIResponse(
                success=True,
                data={"deleted": True, "video_id": clean_video_id},
                meta=ResponseMeta(**meta_dict),
            )
        else:
            return APIResponse(
                success=False,
                error="Transcript not in cache",
                meta=ResponseMeta(**meta_dict),
            )

    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/cache", response_model=APIResponse[TranscriptCacheStats])
async def get_cache_stats(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[TranscriptCacheStats]:
    """
    Get transcript cache statistics.

    Returns total entries, size, and breakdown by source.

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        ensure_cache_dir()

        cache_files = list(CACHE_DIR.glob("*.json"))
        total_size = 0
        by_source = {}
        dates = []

        for cache_file in cache_files:
            try:
                total_size += cache_file.stat().st_size

                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                source = data.get('source', 'unknown')
                by_source[source] = by_source.get(source, 0) + 1

                cached_at = data.get('cached_at')
                if cached_at:
                    dates.append(cached_at)

            except (json.JSONDecodeError, OSError):
                continue

        dates.sort()

        stats = TranscriptCacheStats(
            total_entries=len(cache_files),
            total_size_bytes=total_size,
            oldest_entry=dates[0] if dates else None,
            newest_entry=dates[-1] if dates else None,
            by_source=by_source,
        )

        return APIResponse(
            success=True,
            data=stats,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.post("/cache/clear", response_model=APIResponse[dict])
async def clear_cache(
    request: Request,
    expired_only: bool = Query(True, description="Only clear expired entries"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[dict]:
    """
    Clear transcript cache.

    By default only clears expired entries. Set expired_only=false to clear all.

    **Requires:** Valid Firebase JWT

    **Query Parameters:**
    - expired_only: Only clear expired entries (default: true)
    """
    meta_dict = request.state.get_meta()

    try:
        ensure_cache_dir()

        cache_files = list(CACHE_DIR.glob("*.json"))
        deleted_count = 0
        now = datetime.now(PACIFIC)

        for cache_file in cache_files:
            try:
                if expired_only:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    expires_at = datetime.fromisoformat(data.get('expires_at', ''))
                    if now <= expires_at:
                        continue  # Not expired, skip

                cache_file.unlink()
                deleted_count += 1

            except (json.JSONDecodeError, ValueError, OSError):
                # If we can't read it, delete it anyway
                try:
                    cache_file.unlink()
                    deleted_count += 1
                except OSError:
                    pass

        return APIResponse(
            success=True,
            data={
                "deleted": deleted_count,
                "expired_only": expired_only,
            },
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )
