"""
YouTube API Models

Pydantic models for YouTube playlist management and processing API.
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class YouTubeChannel(BaseModel):
    """YouTube channel information."""
    id: str = Field(..., description="Channel ID")
    name: str = Field(..., description="Channel name")
    is_default: bool = Field(False, description="Whether this is the default channel")
    token_valid: bool = Field(True, description="Whether the OAuth token is valid")
    authenticated_at: Optional[str] = Field(None, description="When the channel was authenticated")
    subscribers: Optional[str] = Field(None, description="Subscriber count (if public)")
    description: Optional[str] = Field(None, description="Channel description")


class YouTubePlaylist(BaseModel):
    """YouTube playlist information."""
    id: str = Field(..., description="Playlist ID")
    title: str = Field(..., description="Playlist title")
    description: Optional[str] = Field(None, description="Playlist description")
    video_count: int = Field(0, description="Number of videos in playlist")
    published_at: Optional[str] = Field(None, description="Playlist creation date")
    thumbnail_url: Optional[str] = Field(None, description="Playlist thumbnail URL")


class YouTubeVideo(BaseModel):
    """YouTube video information."""
    video_id: str = Field(..., description="Video ID")
    title: str = Field(..., description="Video title")
    description: Optional[str] = Field(None, description="Video description")
    channel_title: Optional[str] = Field(None, description="Channel that uploaded the video")
    published_at: Optional[str] = Field(None, description="Video publish date")
    position: int = Field(0, description="Position in playlist")
    thumbnail_url: Optional[str] = Field(None, description="Video thumbnail URL")


class YouTubeProcessRequest(BaseModel):
    """Request to process a YouTube playlist."""
    playlist_id: str = Field(..., description="YouTube playlist ID to process")
    channel_name: Optional[str] = Field(
        None,
        description="Channel name to use for authentication. Uses default if not specified."
    )
    limit: int = Field(
        5,
        description="Maximum number of videos to process",
        ge=1,
        le=50
    )
    dry_run: bool = Field(
        False,
        description="Preview processing without saving files"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "playlist_id": "PLxxxxxx",
                "limit": 5,
                "dry_run": False
            }
        }
    }


class YouTubeProcessJob(BaseModel):
    """Processing job information."""
    job_id: str = Field(..., description="Unique job ID for tracking")
    status: str = Field(
        ...,
        description="Job status: queued, processing, completed, failed"
    )
    playlist_id: str = Field(..., description="Playlist being processed")
    playlist_name: Optional[str] = Field(None, description="Playlist name")
    videos_total: int = Field(0, description="Total videos to process")
    videos_processed: int = Field(0, description="Videos processed so far")
    videos_skipped: int = Field(0, description="Videos skipped")
    videos_failed: int = Field(0, description="Videos that failed")
    created_at: str = Field(..., description="Job creation timestamp")
    completed_at: Optional[str] = Field(None, description="Job completion timestamp")
    error: Optional[str] = Field(None, description="Error message if failed")


class YouTubeChannelsResponse(BaseModel):
    """Response with list of authenticated channels."""
    channels: List[YouTubeChannel] = Field(..., description="Authenticated channels")
    default_channel: Optional[str] = Field(None, description="Name of default channel")
    total: int = Field(..., description="Total number of channels")


class YouTubePlaylistsResponse(BaseModel):
    """Response with list of playlists."""
    playlists: List[YouTubePlaylist] = Field(..., description="Playlists")
    channel_name: str = Field(..., description="Channel the playlists belong to")
    total: int = Field(..., description="Total number of playlists")


class YouTubeVideosResponse(BaseModel):
    """Response with list of videos from a playlist."""
    videos: List[YouTubeVideo] = Field(..., description="Videos in playlist")
    playlist_id: str = Field(..., description="Playlist ID")
    playlist_title: Optional[str] = Field(None, description="Playlist title")
    total: int = Field(..., description="Total videos returned")


class YouTubeTemplate(BaseModel):
    """Processing template information."""
    key: str = Field(..., description="Template key/identifier")
    name: str = Field(..., description="Template display name")
    description: Optional[str] = Field(None, description="Template description")
    output_dir: Optional[str] = Field(None, description="Output directory for processed files")


class YouTubeTemplatesResponse(BaseModel):
    """Response with available processing templates."""
    templates: List[YouTubeTemplate] = Field(..., description="Available templates")
    total: int = Field(..., description="Total number of templates")
