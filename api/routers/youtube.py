"""
YouTube Playlist API Router

REST API for YouTube playlist management and processing.
Wraps youtube_channel_manager.py and youtube_playlist_processor.py services.
"""
import sys
import uuid
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional

from fastapi import APIRouter, Depends, Request, Query, HTTPException

from models.response import APIResponse, ResponseMeta
from models.youtube import (
    YouTubeChannel,
    YouTubePlaylist,
    YouTubeVideo,
    YouTubeProcessRequest,
    YouTubeProcessJob,
    YouTubeChannelsResponse,
    YouTubePlaylistsResponse,
    YouTubeVideosResponse,
    YouTubeTemplate,
    YouTubeTemplatesResponse,
)
from middleware.auth import get_current_user, UserContext

# Add services to path for imports
services_path = Path(__file__).parent.parent.parent / "services"
sys.path.insert(0, str(services_path))

router = APIRouter(prefix="/api/youtube", tags=["YouTube"])

# Pacific timezone for timestamps
PACIFIC = ZoneInfo("America/Los_Angeles")


def get_channel_manager():
    """Lazy import and instantiate YouTubeChannelManager."""
    from youtube_channel_manager import YouTubeChannelManager
    return YouTubeChannelManager()


def get_playlist_processor(channel_name: Optional[str] = None):
    """Lazy import and instantiate PlaylistProcessor."""
    from youtube_playlist_processor import PlaylistProcessor
    return PlaylistProcessor(channel_name=channel_name)


@router.get("/channels", response_model=APIResponse[YouTubeChannelsResponse])
async def get_channels(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[YouTubeChannelsResponse]:
    """
    Get all authenticated YouTube channels.

    Returns a list of all YouTube channels that have been authenticated
    for use with the playlist processor. Each channel can have its own
    OAuth tokens for accessing different YouTube accounts/brand channels.

    **Requires:** Valid Firebase JWT

    **Returns:**
    - channels: List of authenticated channels with metadata
    - default_channel: Name of the currently default channel
    - total: Number of authenticated channels
    """
    meta_dict = request.state.get_meta()

    try:
        manager = get_channel_manager()
        channels_data = manager.list_channels()

        channels = []
        for ch in channels_data:
            channels.append(YouTubeChannel(
                id=ch.get("id", ""),
                name=ch.get("name", ""),
                is_default=ch.get("is_default", False),
                token_valid=ch.get("token_valid", False),
                authenticated_at=ch.get("authenticated_at"),
            ))

        # Get default channel name from registry
        default_channel = manager.channels.get("default")

        response_data = YouTubeChannelsResponse(
            channels=channels,
            default_channel=default_channel,
            total=len(channels),
        )

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except FileNotFoundError:
        # No channels configured yet
        return APIResponse(
            success=True,
            data=YouTubeChannelsResponse(
                channels=[],
                default_channel=None,
                total=0,
            ),
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to get channels: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/playlists", response_model=APIResponse[YouTubePlaylistsResponse])
async def get_playlists(
    request: Request,
    channel: Optional[str] = Query(
        None,
        description="Channel name. Uses default channel if not specified."
    ),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[YouTubePlaylistsResponse]:
    """
    Get all playlists for a YouTube channel.

    Returns playlists with video counts for the specified channel
    (or the default channel if not specified).

    **Query Parameters:**
    - channel: Channel name (optional, uses default)

    **Requires:** Valid Firebase JWT

    **Returns:**
    - playlists: List of playlists with video counts
    - channel_name: The channel these playlists belong to
    - total: Number of playlists
    """
    meta_dict = request.state.get_meta()

    try:
        manager = get_channel_manager()

        # Get channel name (use default if not specified)
        channel_name = channel or manager.channels.get("default")
        if not channel_name:
            return APIResponse(
                success=False,
                data=None,
                error="No channel specified and no default channel configured",
                meta=ResponseMeta(**meta_dict),
            )

        # Get playlists from YouTube API
        playlists_data = manager.get_playlists(channel_name)

        playlists = []
        for pl in playlists_data:
            playlists.append(YouTubePlaylist(
                id=pl.get("id", ""),
                title=pl.get("title", ""),
                description=pl.get("description"),
                video_count=pl.get("video_count", 0),
                published_at=pl.get("published_at"),
            ))

        response_data = YouTubePlaylistsResponse(
            playlists=playlists,
            channel_name=channel_name,
            total=len(playlists),
        )

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except ValueError as e:
        return APIResponse(
            success=False,
            data=None,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to get playlists: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/playlists/{playlist_id}/videos", response_model=APIResponse[YouTubeVideosResponse])
async def get_playlist_videos(
    request: Request,
    playlist_id: str,
    channel: Optional[str] = Query(
        None,
        description="Channel name. Uses default channel if not specified."
    ),
    limit: int = Query(
        20,
        description="Maximum videos to return",
        ge=1,
        le=100
    ),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[YouTubeVideosResponse]:
    """
    Get videos from a YouTube playlist.

    Returns videos in the specified playlist with metadata.

    **Path Parameters:**
    - playlist_id: YouTube playlist ID

    **Query Parameters:**
    - channel: Channel name (optional, uses default)
    - limit: Max videos to return (default 20, max 100)

    **Requires:** Valid Firebase JWT

    **Returns:**
    - videos: List of videos with metadata
    - playlist_id: The playlist ID
    - total: Number of videos returned
    """
    meta_dict = request.state.get_meta()

    try:
        manager = get_channel_manager()
        channel_name = channel or manager.channels.get("default")

        if not channel_name:
            return APIResponse(
                success=False,
                data=None,
                error="No channel specified and no default channel configured",
                meta=ResponseMeta(**meta_dict),
            )

        # Get videos from YouTube API
        videos_data = manager.get_playlist_videos(
            playlist_id=playlist_id,
            channel_name=channel_name,
            max_results=limit,
        )

        videos = []
        for v in videos_data:
            videos.append(YouTubeVideo(
                video_id=v.get("video_id", ""),
                title=v.get("title", ""),
                description=v.get("description"),
                channel_title=v.get("channel_title"),
                published_at=v.get("published_at"),
                position=v.get("position", 0),
            ))

        response_data = YouTubeVideosResponse(
            videos=videos,
            playlist_id=playlist_id,
            playlist_title=None,  # Could fetch playlist details if needed
            total=len(videos),
        )

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except ValueError as e:
        return APIResponse(
            success=False,
            data=None,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to get videos: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/templates", response_model=APIResponse[YouTubeTemplatesResponse])
async def get_templates(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[YouTubeTemplatesResponse]:
    """
    Get available processing templates.

    Returns all configured templates that can be used for processing
    playlists. Templates define the AI prompt, output directory,
    and file naming conventions.

    **Requires:** Valid Firebase JWT

    **Returns:**
    - templates: List of available templates
    - total: Number of templates
    """
    meta_dict = request.state.get_meta()

    try:
        processor = get_playlist_processor()
        templates_data = processor.list_templates()

        templates = []
        for t in templates_data:
            templates.append(YouTubeTemplate(
                key=t.get("key", ""),
                name=t.get("name", ""),
                description=t.get("description"),
                output_dir=t.get("output_dir"),
            ))

        response_data = YouTubeTemplatesResponse(
            templates=templates,
            total=len(templates),
        )

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except FileNotFoundError as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Template configuration not found: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to get templates: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.post("/process", response_model=APIResponse[YouTubeProcessJob])
async def process_playlist(
    request: Request,
    process_request: YouTubeProcessRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[YouTubeProcessJob]:
    """
    Queue a playlist for processing.

    Queues the specified playlist for AI-powered processing using the
    configured template. Returns a job ID for tracking progress.

    **Note:** Processing is asynchronous. Use the job_id to check status
    via the /jobs/{job_id} endpoint.

    **Request Body:**
    - playlist_id: YouTube playlist ID to process
    - channel_name: Channel to use (optional, uses default)
    - limit: Max videos to process (default 5, max 50)
    - dry_run: Preview without saving (default false)

    **Requires:** Valid Firebase JWT

    **Returns:**
    - job_id: Unique job ID for tracking
    - status: Initial job status (queued)
    - playlist_id: The playlist being processed
    """
    meta_dict = request.state.get_meta()

    try:
        # Generate job ID
        job_id = str(uuid.uuid4())
        now = datetime.now(PACIFIC)

        # Get playlist info
        manager = get_channel_manager()
        channel_name = process_request.channel_name or manager.channels.get("default")

        if not channel_name:
            return APIResponse(
                success=False,
                data=None,
                error="No channel specified and no default channel configured",
                meta=ResponseMeta(**meta_dict),
            )

        # Find playlist name by ID
        playlists = manager.get_playlists(channel_name)
        playlist = next(
            (p for p in playlists if p["id"] == process_request.playlist_id),
            None
        )
        playlist_name = playlist["title"] if playlist else None

        # TODO: Store job in processing_queue table
        # For now, queue the job and return immediately
        # In production, this would be stored in Supabase processing_queue table
        # and processed by a background worker

        # Create job record
        job = YouTubeProcessJob(
            job_id=job_id,
            status="queued",
            playlist_id=process_request.playlist_id,
            playlist_name=playlist_name,
            videos_total=playlist["video_count"] if playlist else 0,
            videos_processed=0,
            videos_skipped=0,
            videos_failed=0,
            created_at=now.isoformat(),
            completed_at=None,
            error=None,
        )

        # TODO: Insert into processing_queue table
        # await supabase.table("processing_queue").insert({
        #     "id": job_id,
        #     "type": "youtube_playlist",
        #     "payload": {
        #         "playlist_id": process_request.playlist_id,
        #         "channel_name": channel_name,
        #         "limit": process_request.limit,
        #         "dry_run": process_request.dry_run,
        #     },
        #     "status": "queued",
        #     "created_at": now.isoformat(),
        # })

        return APIResponse(
            success=True,
            data=job,
            meta=ResponseMeta(**meta_dict),
        )

    except ValueError as e:
        return APIResponse(
            success=False,
            data=None,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to queue processing: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/jobs/{job_id}", response_model=APIResponse[YouTubeProcessJob])
async def get_job_status(
    request: Request,
    job_id: str,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[YouTubeProcessJob]:
    """
    Get processing job status.

    Returns the current status of a processing job.

    **Path Parameters:**
    - job_id: The job ID returned from /process

    **Requires:** Valid Firebase JWT

    **Returns:**
    - Job details with current status and progress
    """
    meta_dict = request.state.get_meta()

    # TODO: Fetch from processing_queue table
    # For now, return a placeholder
    # In production:
    # job_data = await supabase.table("processing_queue").select("*").eq("id", job_id).single()

    return APIResponse(
        success=False,
        data=None,
        error=f"Job tracking not yet implemented. Job ID: {job_id}",
        meta=ResponseMeta(**meta_dict),
    )


@router.get("/playlists/{playlist_id}/preview", response_model=APIResponse[dict])
async def preview_playlist(
    request: Request,
    playlist_id: str,
    channel: Optional[str] = Query(
        None,
        description="Channel name. Uses default channel if not specified."
    ),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[dict]:
    """
    Preview what processing a playlist would do.

    Returns the template that would be used, output directory,
    and sample videos without actually processing anything.

    **Path Parameters:**
    - playlist_id: YouTube playlist ID

    **Query Parameters:**
    - channel: Channel name (optional, uses default)

    **Requires:** Valid Firebase JWT

    **Returns:**
    - Preview of processing configuration and sample videos
    """
    meta_dict = request.state.get_meta()

    try:
        manager = get_channel_manager()
        channel_name = channel or manager.channels.get("default")

        if not channel_name:
            return APIResponse(
                success=False,
                data=None,
                error="No channel specified and no default channel configured",
                meta=ResponseMeta(**meta_dict),
            )

        # Find playlist by ID to get the name
        playlists = manager.get_playlists(channel_name)
        playlist = next(
            (p for p in playlists if p["id"] == playlist_id),
            None
        )

        if not playlist:
            return APIResponse(
                success=False,
                data=None,
                error=f"Playlist with ID '{playlist_id}' not found",
                meta=ResponseMeta(**meta_dict),
            )

        # Get preview using playlist name
        processor = get_playlist_processor(channel_name)
        preview = processor.preview_playlist(playlist["title"])

        return APIResponse(
            success=True,
            data=preview,
            meta=ResponseMeta(**meta_dict),
        )

    except ValueError as e:
        return APIResponse(
            success=False,
            data=None,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to preview: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )
