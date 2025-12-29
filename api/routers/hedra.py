"""
Hedra Avatar Integration Router

API endpoints for Hedra Character API integration.
Enables avatar generation, realtime avatars, and asset management.

Based on Hedra API: https://www.hedra.com/docs/api-reference/

Task: [4.2] Hedra Avatar Integration
Pillar: GROW - System continuously improves with interactive avatars
"""
import os
import sys
import uuid
import json
import logging
import httpx
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import (
    APIRouter, Depends, Request, Query, HTTPException, status,
    UploadFile, File, Form, BackgroundTasks
)
from pydantic import BaseModel, Field

from models.response import APIResponse, ResponseMeta
from models.hedra import (
    HedraGenerationStatus,
    HedraAssetType,
    HedraModelType,
    HedraVoiceGender,
    HedraAsset,
    HedraAssetListResponse,
    UploadImageRequest,
    UploadAudioRequest,
    HedraVoice,
    HedraVoiceListResponse,
    GenerateAvatarRequest,
    HedraGenerationJob,
    GenerationJobListResponse,
    RealtimeAvatarSession,
    CreateRealtimeSessionRequest,
    RealtimeSessionResponse,
    HedraCreditsInfo,
    HedraProject,
    HedraProjectListResponse,
    HedraConfigStatus,
    UpdateHedraConfigRequest,
    HedraWebhookEvent,
)
from middleware.auth import get_current_user, UserContext

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/hedra", tags=["Hedra Avatar"])

# Pacific timezone
PACIFIC = ZoneInfo("America/Los_Angeles")

# Hedra API base URL
HEDRA_API_BASE = "https://api.hedra.com/v1"


def get_response_meta() -> ResponseMeta:
    """Generate response metadata."""
    return ResponseMeta(
        request_id=f"req_{uuid.uuid4().hex[:12]}",
        duration_ms=0,
        timestamp=datetime.now(PACIFIC).isoformat()
    )


def get_hedra_headers() -> Dict[str, str]:
    """Get Hedra API headers with authentication."""
    api_key = os.environ.get("HEDRA_API_KEY", "")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Hedra API key not configured. Set HEDRA_API_KEY environment variable."
        )
    return {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }


# === Configuration Endpoints ===

@router.get("/config/status")
async def get_config_status(
    user: UserContext = Depends(get_current_user)
) -> APIResponse:
    """
    Get Hedra API configuration status.

    Returns whether API is configured and current credits/models available.
    """
    api_key = os.environ.get("HEDRA_API_KEY", "")

    if not api_key:
        return APIResponse(
            success=True,
            data=HedraConfigStatus(
                is_configured=False,
                available_models=[]
            ).model_dump(),
            meta=get_response_meta()
        )

    # Mask API key for display
    key_preview = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "***"

    # Try to get credits info
    credits_info = None
    available_models = [HedraModelType.CHARACTER_2.value, HedraModelType.CHARACTER_3.value]

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{HEDRA_API_BASE}/credits",
                headers=get_hedra_headers()
            )
            if response.status_code == 200:
                data = response.json()
                credits_info = HedraCreditsInfo(
                    balance=data.get("balance", 0),
                    used_this_month=data.get("used_this_month", 0),
                    monthly_limit=data.get("monthly_limit"),
                    plan_name=data.get("plan_name")
                )

            # Get available models
            models_response = await client.get(
                f"{HEDRA_API_BASE}/models",
                headers=get_hedra_headers()
            )
            if models_response.status_code == 200:
                models_data = models_response.json()
                if isinstance(models_data, list):
                    available_models = [m.get("id", m) for m in models_data]
    except Exception as e:
        logger.warning(f"Failed to fetch Hedra config details: {e}")

    return APIResponse(
        success=True,
        data=HedraConfigStatus(
            is_configured=True,
            api_key_preview=key_preview,
            credits=credits_info,
            available_models=available_models,
            last_verified=datetime.now(PACIFIC)
        ).model_dump(),
        meta=get_response_meta()
    )


# === Asset Management Endpoints ===

@router.get("/assets")
async def list_assets(
    asset_type: Optional[HedraAssetType] = Query(None, description="Filter by asset type"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    user: UserContext = Depends(get_current_user)
) -> APIResponse:
    """
    List Hedra assets (images, audio, videos).

    Assets are files uploaded or generated in Hedra.
    """
    try:
        params = {"page": page, "limit": limit}
        if asset_type:
            params["type"] = asset_type.value

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{HEDRA_API_BASE}/assets",
                headers=get_hedra_headers(),
                params=params
            )

            if response.status_code != 200:
                return APIResponse(
                    success=False,
                    error=f"Hedra API error: {response.status_code} - {response.text}",
                    meta=get_response_meta()
                )

            data = response.json()
            assets = [
                HedraAsset(
                    id=a.get("id"),
                    type=HedraAssetType(a.get("type", "image")),
                    name=a.get("name"),
                    url=a.get("url"),
                    thumbnail_url=a.get("thumbnail_url"),
                    created_at=a.get("created_at"),
                    duration_seconds=a.get("duration"),
                    width=a.get("width"),
                    height=a.get("height"),
                    file_size_bytes=a.get("size"),
                    metadata=a.get("metadata", {})
                ).model_dump()
                for a in data.get("assets", [])
            ]

            return APIResponse(
                success=True,
                data=HedraAssetListResponse(
                    assets=assets,
                    total=data.get("total", len(assets)),
                    page=page,
                    limit=limit
                ).model_dump(),
                meta=get_response_meta()
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list Hedra assets: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=get_response_meta()
        )


@router.post("/assets/upload/image")
async def upload_image(
    file: UploadFile = File(..., description="Image file (JPEG, PNG)"),
    name: Optional[str] = Form(None, description="Optional name for the asset"),
    user: UserContext = Depends(get_current_user)
) -> APIResponse:
    """
    Upload an image for avatar creation.

    Accepts JPEG or PNG images. The image should contain a humanoid face
    (can be photorealistic or animated style). Hedra automatically crops
    around the face.
    """
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_types:
        return APIResponse(
            success=False,
            error=f"Invalid file type. Allowed: {allowed_types}",
            meta=get_response_meta()
        )

    try:
        file_content = await file.read()

        # Prepare multipart form
        files = {
            "file": (file.filename or "image.png", file_content, file.content_type)
        }
        data = {}
        if name:
            data["name"] = name

        headers = get_hedra_headers()
        del headers["Content-Type"]  # Let httpx set multipart boundary

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{HEDRA_API_BASE}/assets/upload",
                headers=headers,
                files=files,
                data=data
            )

            if response.status_code not in [200, 201]:
                return APIResponse(
                    success=False,
                    error=f"Hedra upload failed: {response.status_code} - {response.text}",
                    meta=get_response_meta()
                )

            asset_data = response.json()
            asset = HedraAsset(
                id=asset_data.get("id"),
                type=HedraAssetType.IMAGE,
                name=name or file.filename,
                url=asset_data.get("url"),
                thumbnail_url=asset_data.get("thumbnail_url"),
                created_at=datetime.now(PACIFIC),
                width=asset_data.get("width"),
                height=asset_data.get("height"),
                file_size_bytes=len(file_content)
            )

            return APIResponse(
                success=True,
                data=asset.model_dump(),
                meta=get_response_meta()
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload image to Hedra: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=get_response_meta()
        )


@router.post("/assets/upload/audio")
async def upload_audio(
    file: UploadFile = File(..., description="Audio file (WAV, MP3, M4A)"),
    name: Optional[str] = Form(None, description="Optional name for the asset"),
    user: UserContext = Depends(get_current_user)
) -> APIResponse:
    """
    Upload audio for lip-sync avatar generation.

    Accepts WAV, MP3, or M4A audio files. Audio will be synced to
    avatar lip movements.
    """
    allowed_types = ["audio/wav", "audio/mpeg", "audio/mp3", "audio/mp4", "audio/x-m4a"]
    if file.content_type not in allowed_types:
        return APIResponse(
            success=False,
            error=f"Invalid file type. Allowed: WAV, MP3, M4A",
            meta=get_response_meta()
        )

    try:
        file_content = await file.read()

        files = {
            "file": (file.filename or "audio.mp3", file_content, file.content_type)
        }
        data = {}
        if name:
            data["name"] = name

        headers = get_hedra_headers()
        del headers["Content-Type"]

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{HEDRA_API_BASE}/assets/upload",
                headers=headers,
                files=files,
                data=data
            )

            if response.status_code not in [200, 201]:
                return APIResponse(
                    success=False,
                    error=f"Hedra upload failed: {response.status_code} - {response.text}",
                    meta=get_response_meta()
                )

            asset_data = response.json()
            asset = HedraAsset(
                id=asset_data.get("id"),
                type=HedraAssetType.AUDIO,
                name=name or file.filename,
                url=asset_data.get("url"),
                created_at=datetime.now(PACIFIC),
                duration_seconds=asset_data.get("duration"),
                file_size_bytes=len(file_content)
            )

            return APIResponse(
                success=True,
                data=asset.model_dump(),
                meta=get_response_meta()
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload audio to Hedra: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=get_response_meta()
        )


@router.delete("/assets/{asset_id}")
async def delete_asset(
    asset_id: str,
    user: UserContext = Depends(get_current_user)
) -> APIResponse:
    """Delete a Hedra asset."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(
                f"{HEDRA_API_BASE}/assets/{asset_id}",
                headers=get_hedra_headers()
            )

            if response.status_code not in [200, 204]:
                return APIResponse(
                    success=False,
                    error=f"Failed to delete asset: {response.status_code}",
                    meta=get_response_meta()
                )

            return APIResponse(
                success=True,
                data={"deleted": asset_id},
                meta=get_response_meta()
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete Hedra asset: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=get_response_meta()
        )


# === Voice Management ===

@router.get("/voices")
async def list_voices(
    gender: Optional[HedraVoiceGender] = Query(None, description="Filter by gender"),
    language: str = Query("en", description="Language code"),
    user: UserContext = Depends(get_current_user)
) -> APIResponse:
    """
    List available Hedra TTS voices.

    Use these voices for text-to-speech avatar generation.
    """
    try:
        params = {"language": language}
        if gender:
            params["gender"] = gender.value

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{HEDRA_API_BASE}/voices",
                headers=get_hedra_headers(),
                params=params
            )

            if response.status_code != 200:
                return APIResponse(
                    success=False,
                    error=f"Hedra API error: {response.status_code}",
                    meta=get_response_meta()
                )

            data = response.json()
            voices = [
                HedraVoice(
                    id=v.get("id"),
                    name=v.get("name"),
                    gender=HedraVoiceGender(v.get("gender", "neutral")),
                    language=v.get("language", "en"),
                    accent=v.get("accent"),
                    preview_url=v.get("preview_url"),
                    description=v.get("description")
                ).model_dump()
                for v in data.get("voices", [])
            ]

            return APIResponse(
                success=True,
                data=HedraVoiceListResponse(
                    voices=voices,
                    total=len(voices)
                ).model_dump(),
                meta=get_response_meta()
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list Hedra voices: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=get_response_meta()
        )


# === Avatar Generation ===

@router.post("/generate")
async def generate_avatar(
    request: GenerateAvatarRequest,
    background_tasks: BackgroundTasks,
    user: UserContext = Depends(get_current_user)
) -> APIResponse:
    """
    Generate an avatar video.

    Creates a talking avatar video from an image and either:
    - Uploaded audio (for custom voice/lip-sync)
    - Text + voice ID (for TTS generation)

    Generation runs asynchronously. Poll /generate/{job_id}/status for updates.
    """
    # Validate input
    if not request.audio_asset_id and not request.text:
        return APIResponse(
            success=False,
            error="Either audio_asset_id or text must be provided",
            meta=get_response_meta()
        )

    if request.text and not request.voice_id:
        return APIResponse(
            success=False,
            error="voice_id is required when using text-to-speech",
            meta=get_response_meta()
        )

    try:
        payload = {
            "image_asset_id": request.image_asset_id,
            "model": request.model.value,
            "aspect_ratio": request.aspect_ratio
        }

        if request.audio_asset_id:
            payload["audio_asset_id"] = request.audio_asset_id
        else:
            payload["text"] = request.text
            payload["voice_id"] = request.voice_id

        if request.seed:
            payload["seed"] = request.seed
        if request.webhook_url:
            payload["webhook_url"] = request.webhook_url

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{HEDRA_API_BASE}/generate",
                headers=get_hedra_headers(),
                json=payload
            )

            if response.status_code not in [200, 201, 202]:
                return APIResponse(
                    success=False,
                    error=f"Generation failed: {response.status_code} - {response.text}",
                    meta=get_response_meta()
                )

            job_data = response.json()
            job = HedraGenerationJob(
                id=job_data.get("id") or job_data.get("job_id"),
                status=HedraGenerationStatus(job_data.get("status", "pending")),
                model=request.model,
                image_asset_id=request.image_asset_id,
                audio_asset_id=request.audio_asset_id,
                created_at=datetime.now(PACIFIC),
                progress_percent=0
            )

            return APIResponse(
                success=True,
                data=job.model_dump(),
                meta=get_response_meta()
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start Hedra generation: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=get_response_meta()
        )


@router.get("/generate/{job_id}/status")
async def get_generation_status(
    job_id: str,
    user: UserContext = Depends(get_current_user)
) -> APIResponse:
    """
    Get status of a generation job.

    Poll this endpoint until status is 'completed' or 'failed'.
    When completed, output_asset_id will contain the video.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{HEDRA_API_BASE}/generate/{job_id}",
                headers=get_hedra_headers()
            )

            if response.status_code != 200:
                return APIResponse(
                    success=False,
                    error=f"Failed to get job status: {response.status_code}",
                    meta=get_response_meta()
                )

            data = response.json()
            job = HedraGenerationJob(
                id=job_id,
                status=HedraGenerationStatus(data.get("status", "pending")),
                model=HedraModelType(data.get("model", "character-2")),
                image_asset_id=data.get("image_asset_id", ""),
                audio_asset_id=data.get("audio_asset_id"),
                output_asset_id=data.get("output_asset_id"),
                created_at=data.get("created_at", datetime.now(PACIFIC)),
                started_at=data.get("started_at"),
                completed_at=data.get("completed_at"),
                error_message=data.get("error"),
                progress_percent=data.get("progress", 0),
                credits_used=data.get("credits_used")
            )

            return APIResponse(
                success=True,
                data=job.model_dump(),
                meta=get_response_meta()
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get Hedra job status: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=get_response_meta()
        )


@router.get("/generate")
async def list_generation_jobs(
    status_filter: Optional[HedraGenerationStatus] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user: UserContext = Depends(get_current_user)
) -> APIResponse:
    """List generation jobs with optional status filter."""
    try:
        params = {"page": page, "limit": limit}
        if status_filter:
            params["status"] = status_filter.value

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{HEDRA_API_BASE}/generate",
                headers=get_hedra_headers(),
                params=params
            )

            if response.status_code != 200:
                return APIResponse(
                    success=False,
                    error=f"Failed to list jobs: {response.status_code}",
                    meta=get_response_meta()
                )

            data = response.json()
            jobs = [
                HedraGenerationJob(
                    id=j.get("id"),
                    status=HedraGenerationStatus(j.get("status", "pending")),
                    model=HedraModelType(j.get("model", "character-2")),
                    image_asset_id=j.get("image_asset_id", ""),
                    audio_asset_id=j.get("audio_asset_id"),
                    output_asset_id=j.get("output_asset_id"),
                    created_at=j.get("created_at", datetime.now(PACIFIC)),
                    completed_at=j.get("completed_at"),
                    error_message=j.get("error"),
                    progress_percent=j.get("progress", 0),
                    credits_used=j.get("credits_used")
                ).model_dump()
                for j in data.get("jobs", [])
            ]

            return APIResponse(
                success=True,
                data=GenerationJobListResponse(
                    jobs=jobs,
                    total=data.get("total", len(jobs)),
                    page=page,
                    limit=limit
                ).model_dump(),
                meta=get_response_meta()
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list Hedra jobs: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=get_response_meta()
        )


@router.delete("/generate/{job_id}")
async def cancel_generation(
    job_id: str,
    user: UserContext = Depends(get_current_user)
) -> APIResponse:
    """Cancel a pending/processing generation job."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(
                f"{HEDRA_API_BASE}/generate/{job_id}",
                headers=get_hedra_headers()
            )

            if response.status_code not in [200, 204]:
                return APIResponse(
                    success=False,
                    error=f"Failed to cancel job: {response.status_code}",
                    meta=get_response_meta()
                )

            return APIResponse(
                success=True,
                data={"cancelled": job_id},
                meta=get_response_meta()
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel Hedra job: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=get_response_meta()
        )


# === Realtime Avatar (LiveKit Integration) ===

@router.post("/realtime/sessions")
async def create_realtime_session(
    request: CreateRealtimeSessionRequest,
    user: UserContext = Depends(get_current_user)
) -> APIResponse:
    """
    Create a realtime avatar session.

    Starts a LiveKit-based realtime avatar session for interactive
    voice conversations. Returns connection info for WebRTC client.

    Requires LiveKit integration to be configured.
    """
    try:
        payload = {
            "avatar_id": request.avatar_id,
            "max_duration_minutes": request.max_duration_minutes
        }
        if request.session_name:
            payload["name"] = request.session_name
        if request.webhook_url:
            payload["webhook_url"] = request.webhook_url

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{HEDRA_API_BASE}/realtime/sessions",
                headers=get_hedra_headers(),
                json=payload
            )

            if response.status_code not in [200, 201]:
                return APIResponse(
                    success=False,
                    error=f"Failed to create session: {response.status_code} - {response.text}",
                    meta=get_response_meta()
                )

            data = response.json()
            session = RealtimeAvatarSession(
                session_id=data.get("session_id") or data.get("id"),
                avatar_id=request.avatar_id,
                status="active",
                livekit_room=data.get("room_name"),
                livekit_token=data.get("token"),
                created_at=datetime.now(PACIFIC)
            )

            return APIResponse(
                success=True,
                data=RealtimeSessionResponse(
                    session=session,
                    connection_info={
                        "websocket_url": data.get("ws_url"),
                        "room_name": data.get("room_name"),
                        "token": data.get("token"),
                        "ice_servers": data.get("ice_servers", [])
                    }
                ).model_dump(),
                meta=get_response_meta()
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create realtime session: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=get_response_meta()
        )


@router.get("/realtime/sessions/{session_id}")
async def get_realtime_session(
    session_id: str,
    user: UserContext = Depends(get_current_user)
) -> APIResponse:
    """Get details of a realtime avatar session."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{HEDRA_API_BASE}/realtime/sessions/{session_id}",
                headers=get_hedra_headers()
            )

            if response.status_code != 200:
                return APIResponse(
                    success=False,
                    error=f"Failed to get session: {response.status_code}",
                    meta=get_response_meta()
                )

            data = response.json()
            session = RealtimeAvatarSession(
                session_id=session_id,
                avatar_id=data.get("avatar_id", ""),
                status=data.get("status", "unknown"),
                livekit_room=data.get("room_name"),
                created_at=data.get("created_at", datetime.now(PACIFIC)),
                ended_at=data.get("ended_at")
            )

            return APIResponse(
                success=True,
                data=session.model_dump(),
                meta=get_response_meta()
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get realtime session: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=get_response_meta()
        )


@router.delete("/realtime/sessions/{session_id}")
async def end_realtime_session(
    session_id: str,
    user: UserContext = Depends(get_current_user)
) -> APIResponse:
    """End a realtime avatar session."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(
                f"{HEDRA_API_BASE}/realtime/sessions/{session_id}",
                headers=get_hedra_headers()
            )

            if response.status_code not in [200, 204]:
                return APIResponse(
                    success=False,
                    error=f"Failed to end session: {response.status_code}",
                    meta=get_response_meta()
                )

            return APIResponse(
                success=True,
                data={"ended": session_id, "ended_at": datetime.now(PACIFIC).isoformat()},
                meta=get_response_meta()
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to end realtime session: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=get_response_meta()
        )


# === Projects ===

@router.get("/projects")
async def list_projects(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user: UserContext = Depends(get_current_user)
) -> APIResponse:
    """List Hedra projects."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{HEDRA_API_BASE}/projects",
                headers=get_hedra_headers(),
                params={"page": page, "limit": limit}
            )

            if response.status_code != 200:
                return APIResponse(
                    success=False,
                    error=f"Failed to list projects: {response.status_code}",
                    meta=get_response_meta()
                )

            data = response.json()
            projects = [
                HedraProject(
                    id=p.get("id"),
                    name=p.get("name", "Untitled"),
                    description=p.get("description"),
                    created_at=p.get("created_at", datetime.now(PACIFIC)),
                    updated_at=p.get("updated_at"),
                    generation_count=p.get("generation_count", 0),
                    is_shared=p.get("is_shared", False),
                    share_url=p.get("share_url")
                ).model_dump()
                for p in data.get("projects", [])
            ]

            return APIResponse(
                success=True,
                data=HedraProjectListResponse(
                    projects=projects,
                    total=data.get("total", len(projects))
                ).model_dump(),
                meta=get_response_meta()
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list Hedra projects: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=get_response_meta()
        )


@router.get("/projects/{project_id}")
async def get_project(
    project_id: str,
    user: UserContext = Depends(get_current_user)
) -> APIResponse:
    """Get project details."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{HEDRA_API_BASE}/projects/{project_id}",
                headers=get_hedra_headers()
            )

            if response.status_code != 200:
                return APIResponse(
                    success=False,
                    error=f"Failed to get project: {response.status_code}",
                    meta=get_response_meta()
                )

            p = response.json()
            project = HedraProject(
                id=p.get("id"),
                name=p.get("name", "Untitled"),
                description=p.get("description"),
                created_at=p.get("created_at", datetime.now(PACIFIC)),
                updated_at=p.get("updated_at"),
                generation_count=p.get("generation_count", 0),
                is_shared=p.get("is_shared", False),
                share_url=p.get("share_url")
            )

            return APIResponse(
                success=True,
                data=project.model_dump(),
                meta=get_response_meta()
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get Hedra project: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=get_response_meta()
        )


@router.post("/projects/{project_id}/share")
async def share_project(
    project_id: str,
    share: bool = Query(True, description="True to share, False to unshare"),
    user: UserContext = Depends(get_current_user)
) -> APIResponse:
    """Share or unshare a Hedra project."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{HEDRA_API_BASE}/projects/{project_id}/share",
                headers=get_hedra_headers(),
                json={"share": share}
            )

            if response.status_code not in [200, 201]:
                return APIResponse(
                    success=False,
                    error=f"Failed to update sharing: {response.status_code}",
                    meta=get_response_meta()
                )

            data = response.json()
            return APIResponse(
                success=True,
                data={
                    "project_id": project_id,
                    "is_shared": share,
                    "share_url": data.get("share_url") if share else None
                },
                meta=get_response_meta()
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to share Hedra project: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=get_response_meta()
        )


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: str,
    user: UserContext = Depends(get_current_user)
) -> APIResponse:
    """Delete a Hedra project and its generations."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(
                f"{HEDRA_API_BASE}/projects/{project_id}",
                headers=get_hedra_headers()
            )

            if response.status_code not in [200, 204]:
                return APIResponse(
                    success=False,
                    error=f"Failed to delete project: {response.status_code}",
                    meta=get_response_meta()
                )

            return APIResponse(
                success=True,
                data={"deleted": project_id},
                meta=get_response_meta()
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete Hedra project: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=get_response_meta()
        )


# === Credits ===

@router.get("/credits")
async def get_credits(
    user: UserContext = Depends(get_current_user)
) -> APIResponse:
    """Get current Hedra credit balance and usage."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{HEDRA_API_BASE}/credits",
                headers=get_hedra_headers()
            )

            if response.status_code != 200:
                return APIResponse(
                    success=False,
                    error=f"Failed to get credits: {response.status_code}",
                    meta=get_response_meta()
                )

            data = response.json()
            credits = HedraCreditsInfo(
                balance=data.get("balance", 0),
                used_this_month=data.get("used_this_month", 0),
                monthly_limit=data.get("monthly_limit"),
                plan_name=data.get("plan_name"),
                renewal_date=data.get("renewal_date")
            )

            return APIResponse(
                success=True,
                data=credits.model_dump(),
                meta=get_response_meta()
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get Hedra credits: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=get_response_meta()
        )


# === Webhook Handler ===

@router.post("/webhooks")
async def handle_webhook(
    request: Request,
    background_tasks: BackgroundTasks
) -> APIResponse:
    """
    Handle incoming Hedra webhooks.

    Hedra sends webhooks for:
    - generation.started
    - generation.progress
    - generation.completed
    - generation.failed
    - session.started
    - session.ended
    """
    try:
        body = await request.json()

        event = HedraWebhookEvent(
            event_type=body.get("event_type", body.get("type", "unknown")),
            job_id=body.get("job_id"),
            session_id=body.get("session_id"),
            status=body.get("status"),
            data=body.get("data", body),
            timestamp=datetime.now(PACIFIC)
        )

        logger.info(f"Received Hedra webhook: {event.event_type} - {event.job_id or event.session_id}")

        # Process webhook in background
        # In a full implementation, this would update local state,
        # notify connected clients via WebSocket, etc.

        return APIResponse(
            success=True,
            data={"received": event.event_type},
            meta=get_response_meta()
        )
    except Exception as e:
        logger.error(f"Failed to process Hedra webhook: {e}")
        return APIResponse(
            success=False,
            error=str(e),
            meta=get_response_meta()
        )


# === Available Models ===

@router.get("/models")
async def list_models(
    user: UserContext = Depends(get_current_user)
) -> APIResponse:
    """List available Hedra generation models."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{HEDRA_API_BASE}/models",
                headers=get_hedra_headers()
            )

            if response.status_code == 200:
                models = response.json()
                return APIResponse(
                    success=True,
                    data={"models": models},
                    meta=get_response_meta()
                )
            else:
                # Fallback to known models
                return APIResponse(
                    success=True,
                    data={
                        "models": [
                            {
                                "id": "character-2",
                                "name": "Character-2",
                                "description": "Flexible, fast character generation",
                                "capabilities": ["lip_sync", "tts", "emotions"]
                            },
                            {
                                "id": "character-3",
                                "name": "Character-3",
                                "description": "Latest model with improved realism",
                                "capabilities": ["lip_sync", "tts", "emotions", "realtime"]
                            }
                        ]
                    },
                    meta=get_response_meta()
                )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list Hedra models: {e}")
        # Return fallback
        return APIResponse(
            success=True,
            data={
                "models": [
                    {"id": "character-2", "name": "Character-2"},
                    {"id": "character-3", "name": "Character-3"}
                ]
            },
            meta=get_response_meta()
        )
