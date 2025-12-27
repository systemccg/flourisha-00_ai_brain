"""
Voice Notification Router

ElevenLabs voice notification API for text-to-speech.
Triggers TTS on server speakers and manages agent voice mappings.
"""
import os
import logging
from typing import Optional
from pathlib import Path

import httpx
from fastapi import APIRouter, Depends, Request, HTTPException, status
from pydantic import BaseModel, Field

from models.response import APIResponse, ResponseMeta
from middleware.auth import get_current_user, UserContext


logger = logging.getLogger("flourisha.api.voice")

router = APIRouter(prefix="/api/voice", tags=["Voice"])


# === Voice ID Mappings (from CORE skill) ===
AGENT_VOICE_MAPPINGS = {
    "kai": "gNbIwdcnM3B17qzBs2JY",
    "perplexity-researcher": "gNbIwdcnM3B17qzBs2JY",
    "claude-researcher": "gNbIwdcnM3B17qzBs2JY",
    "gemini-researcher": "gNbIwdcnM3B17qzBs2JY",
    "pentester": "gNbIwdcnM3B17qzBs2JY",
    "engineer": "gNbIwdcnM3B17qzBs2JY",
    "principal-engineer": "gNbIwdcnM3B17qzBs2JY",
    "designer": "gNbIwdcnM3B17qzBs2JY",
    "architect": "gNbIwdcnM3B17qzBs2JY",
    "artist": "gNbIwdcnM3B17qzBs2JY",
    "writer": "gNbIwdcnM3B17qzBs2JY",
    "pai": "s3TPKV1kjDlVtZbl4Ksh",  # PAI's dedicated voice
}

# Default voice for unknown agents
DEFAULT_VOICE_ID = "gNbIwdcnM3B17qzBs2JY"

# Voice server configuration
VOICE_SERVER_URL = os.getenv("VOICE_SERVER_URL", "http://localhost:8888")


# === Request/Response Models ===

class NotifyRequest(BaseModel):
    """Request to trigger voice notification."""
    message: str = Field(..., min_length=1, max_length=5000, description="Text to speak")
    voice_id: Optional[str] = Field(None, description="ElevenLabs voice ID (optional)")
    agent: Optional[str] = Field(None, description="Agent name for voice lookup (optional)")
    title: Optional[str] = Field("Flourisha", description="Notification title")


class VoiceMapping(BaseModel):
    """Agent to voice ID mapping."""
    agent: str
    voice_id: str


class VoiceListResponse(BaseModel):
    """Response containing all voice mappings."""
    voices: list[VoiceMapping]
    default_voice_id: str


class TestRequest(BaseModel):
    """Request to test a specific voice."""
    voice_id: str = Field(..., description="ElevenLabs voice ID to test")
    text: Optional[str] = Field(
        "Hello! This is a test of the ElevenLabs voice system.",
        description="Sample text to speak"
    )


class NotifyResponse(BaseModel):
    """Response from voice notification."""
    success: bool
    message: str
    voice_id: str


# === Helper Functions ===

def get_voice_id(agent: Optional[str], voice_id: Optional[str]) -> str:
    """Resolve voice ID from agent name or explicit voice_id.

    Priority:
    1. Explicit voice_id if provided
    2. Agent lookup in AGENT_VOICE_MAPPINGS
    3. Default voice ID
    """
    if voice_id:
        return voice_id
    if agent and agent.lower() in AGENT_VOICE_MAPPINGS:
        return AGENT_VOICE_MAPPINGS[agent.lower()]
    return DEFAULT_VOICE_ID


async def send_to_voice_server(
    message: str,
    voice_id: str,
    title: str = "Flourisha"
) -> dict:
    """Send notification to the voice server.

    The voice server runs on localhost:8888 and handles TTS via ElevenLabs.

    Args:
        message: Text to speak
        voice_id: ElevenLabs voice ID
        title: Notification title

    Returns:
        Response from voice server

    Raises:
        HTTPException: If voice server is unavailable
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{VOICE_SERVER_URL}/notify",
                json={
                    "message": message,
                    "voice_id": voice_id,
                    "title": title,
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Voice server not available. Ensure voice server is running on port 8888."
            )
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Voice server timeout - TTS may be processing a large message."
            )
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Voice server error: {e.response.text}"
            )


# === API Endpoints ===

@router.post("/notify", response_model=APIResponse[NotifyResponse])
async def trigger_notification(
    request: Request,
    notify_request: NotifyRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[NotifyResponse]:
    """
    Trigger a voice notification.

    Sends text to the ElevenLabs TTS system to play on server speakers.

    **Request Body:**
    - message: Text to speak (required, max 5000 chars)
    - voice_id: ElevenLabs voice ID (optional)
    - agent: Agent name for voice lookup (optional, e.g., "kai", "pai")
    - title: Notification title (optional, default "Flourisha")

    **Voice Resolution:**
    1. If voice_id provided, use it
    2. Else if agent provided, lookup in voice mappings
    3. Else use default voice

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    # Resolve voice ID
    resolved_voice_id = get_voice_id(
        agent=notify_request.agent,
        voice_id=notify_request.voice_id
    )

    try:
        # Send to voice server
        result = await send_to_voice_server(
            message=notify_request.message,
            voice_id=resolved_voice_id,
            title=notify_request.title or "Flourisha"
        )

        return APIResponse(
            success=True,
            data=NotifyResponse(
                success=True,
                message=f"Voice notification sent: {notify_request.message[:50]}...",
                voice_id=resolved_voice_id,
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice notification failed: {e}")
        return APIResponse(
            success=False,
            error=f"Voice notification failed: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/voices", response_model=APIResponse[VoiceListResponse])
async def list_voices(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[VoiceListResponse]:
    """
    Get agent-to-voice mappings.

    Returns all configured agent voice IDs for the ElevenLabs TTS system.

    **Response:**
    - voices: List of agent/voice_id pairs
    - default_voice_id: Voice ID used when no agent match

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    voices = [
        VoiceMapping(agent=agent, voice_id=vid)
        for agent, vid in AGENT_VOICE_MAPPINGS.items()
    ]

    return APIResponse(
        success=True,
        data=VoiceListResponse(
            voices=voices,
            default_voice_id=DEFAULT_VOICE_ID,
        ),
        meta=ResponseMeta(**meta_dict),
    )


@router.post("/test", response_model=APIResponse[NotifyResponse])
async def test_voice(
    request: Request,
    test_request: TestRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[NotifyResponse]:
    """
    Test a specific voice ID.

    Plays a sample message using the specified ElevenLabs voice ID.
    Useful for previewing voices before configuring agents.

    **Request Body:**
    - voice_id: ElevenLabs voice ID to test (required)
    - text: Sample text to speak (optional, has default)

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        # Send test message to voice server
        result = await send_to_voice_server(
            message=test_request.text,
            voice_id=test_request.voice_id,
            title="Voice Test"
        )

        return APIResponse(
            success=True,
            data=NotifyResponse(
                success=True,
                message=f"Test played for voice: {test_request.voice_id}",
                voice_id=test_request.voice_id,
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice test failed: {e}")
        return APIResponse(
            success=False,
            error=f"Voice test failed: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/health", response_model=APIResponse[dict])
async def voice_health(
    request: Request,
) -> APIResponse[dict]:
    """
    Check voice server health.

    Pings the voice server to verify it's available.
    Does not require authentication - used by monitoring.
    """
    meta_dict = request.state.get_meta()

    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(f"{VOICE_SERVER_URL}/health")
            response.raise_for_status()

            return APIResponse(
                success=True,
                data={
                    "voice_server": "healthy",
                    "url": VOICE_SERVER_URL,
                    "available_agents": len(AGENT_VOICE_MAPPINGS),
                },
                meta=ResponseMeta(**meta_dict),
            )
        except Exception as e:
            return APIResponse(
                success=False,
                data={
                    "voice_server": "unavailable",
                    "url": VOICE_SERVER_URL,
                    "error": str(e),
                },
                meta=ResponseMeta(**meta_dict),
            )
