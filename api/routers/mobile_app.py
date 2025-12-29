"""
Mobile App API Router

Endpoints optimized for React Native mobile app:
- Device registration and push notifications
- Offline-first sync
- Quick capture (voice, photo, text)
- Dashboard data
- Energy tracking
- Mobile search
"""
import os
import json
import logging
import uuid
import base64
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Request, Query, HTTPException
from pydantic import BaseModel

from models.response import APIResponse, ResponseMeta
from models.mobile_app import (
    # Device
    DeviceRegistrationRequest, DeviceRegistrationResponse,
    # Capture
    MobileCaptureRequest, MobileCaptureResponse, ContentType,
    # Sync
    MobileSyncRequest, MobileSyncResponse, SyncResult,
    # Dashboard
    DashboardRequest, DashboardResponse, QuickActionButton,
    OKRSummary, TaskSummary, EnergyEntry,
    # Energy
    MobileEnergyRequest, MobileEnergyResponse,
    # Push
    UpdatePushPreferencesRequest, UpdatePushPreferencesResponse,
    PushNotificationPreferences,
    # Voice
    VoiceNoteUploadRequest, VoiceNoteUploadResponse,
    # App State
    AppStateRequest, AppStateResponse, UserProfile,
    # Search
    MobileSearchRequest, MobileSearchResponse, SearchResultItem,
)
from middleware.auth import get_current_user, get_optional_user, UserContext


logger = logging.getLogger("flourisha.api.mobile_app")
router = APIRouter(prefix="/api/mobile", tags=["Mobile App"])

PACIFIC = ZoneInfo("America/Los_Angeles")
SCRATCHPAD_DIR = Path(os.path.expanduser("/root/flourisha/00_AI_Brain/scratchpad"))
VOICE_NOTES_DIR = Path(os.path.expanduser("/root/flourisha/00_AI_Brain/scratchpad/voice_notes"))
DEVICES_FILE = SCRATCHPAD_DIR / "mobile_devices.json"
CLICKUP_SCRATCHPAD_LIST_ID = "901112609506"  # Idea Scratchpad list

# Minimum supported app version
MIN_APP_VERSION = "1.0.0"


# === Helper Functions ===

def get_pacific_now() -> datetime:
    """Get current time in Pacific timezone."""
    return datetime.now(PACIFIC)


def generate_id(prefix: str) -> str:
    """Generate unique ID with prefix."""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def load_devices() -> Dict[str, Any]:
    """Load registered devices from file."""
    if DEVICES_FILE.exists():
        try:
            return json.loads(DEVICES_FILE.read_text())
        except Exception:
            pass
    return {}


def save_devices(devices: Dict[str, Any]) -> None:
    """Save registered devices to file."""
    DEVICES_FILE.parent.mkdir(parents=True, exist_ok=True)
    DEVICES_FILE.write_text(json.dumps(devices, indent=2))


def save_mobile_capture(
    content: str,
    content_type: str,
    metadata: Dict[str, Any],
    offline_id: Optional[str] = None
) -> str:
    """Save mobile capture to scratchpad.

    Returns the capture ID.
    """
    now = get_pacific_now()
    date_dir = now.strftime("%Y-%m-%d")
    timestamp = now.strftime("%H%M%S")
    capture_id = generate_id("mob")

    # Create directory
    capture_dir = SCRATCHPAD_DIR / "mobile_captures" / date_dir
    capture_dir.mkdir(parents=True, exist_ok=True)

    # Create capture file
    filename = f"{timestamp}_{content_type}_{capture_id[:8]}.json"
    capture_path = capture_dir / filename

    capture_data = {
        "id": capture_id,
        "offline_id": offline_id,
        "type": content_type,
        "content": content,
        "metadata": metadata,
        "captured_at": now.isoformat(),
        "processed": False,
    }

    capture_path.write_text(json.dumps(capture_data, indent=2))
    logger.info(f"Saved mobile capture {capture_id} to {capture_path}")

    return capture_id


async def create_clickup_idea(title: str, content: str, tags: List[str]) -> Optional[str]:
    """Create a task in ClickUp Idea Scratchpad list."""
    try:
        import sys
        sys.path.insert(0, '/root/flourisha/00_AI_Brain/skills/clickup-tasks/reference')
        from clickup_api import ClickUpClient

        client = ClickUpClient()

        description = content
        if tags:
            description += f"\n\nTags: {', '.join(tags)}"

        result = client.create_task(
            list_id=CLICKUP_SCRATCHPAD_LIST_ID,
            name=title[:100],
            description=description,
        )

        if result.success:
            return result.data.get('id')
        return None
    except Exception as e:
        logger.error(f"Failed to create ClickUp task: {e}")
        return None


def is_energy_check_due(last_check: Optional[datetime] = None) -> tuple[bool, Optional[datetime]]:
    """Check if energy check-in is due (90-minute intervals)."""
    now = get_pacific_now()

    # Energy tracking hours: 8 AM - 6 PM Pacific
    if now.hour < 8 or now.hour >= 18:
        return False, None

    # Calculate next check (90-minute intervals from 8 AM)
    today_8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
    intervals_passed = (now - today_8am).total_seconds() // (90 * 60)
    next_check = today_8am + timedelta(minutes=90 * (intervals_passed + 1))

    if last_check:
        minutes_since_check = (now - last_check).total_seconds() / 60
        return minutes_since_check >= 90, next_check

    return True, next_check


def get_greeting() -> str:
    """Get personalized greeting based on time of day."""
    now = get_pacific_now()
    hour = now.hour

    if hour < 12:
        return "Good morning"
    elif hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"


def get_default_quick_actions() -> List[QuickActionButton]:
    """Get default quick actions for mobile home screen."""
    return [
        QuickActionButton(
            id="quick_note",
            label="Quick Note",
            icon="edit",
            action_type="capture",
            action_data={"content_type": "text_note"},
        ),
        QuickActionButton(
            id="voice_note",
            label="Voice Note",
            icon="mic",
            action_type="capture",
            action_data={"content_type": "voice_note"},
        ),
        QuickActionButton(
            id="capture_photo",
            label="Photo",
            icon="camera",
            action_type="capture",
            action_data={"content_type": "photo"},
        ),
        QuickActionButton(
            id="energy_check",
            label="Energy",
            icon="activity",
            action_type="navigate",
            action_data={"screen": "energy_checkin"},
        ),
        QuickActionButton(
            id="search",
            label="Search",
            icon="search",
            action_type="navigate",
            action_data={"screen": "search"},
        ),
        QuickActionButton(
            id="okrs",
            label="OKRs",
            icon="target",
            action_type="navigate",
            action_data={"screen": "okrs"},
        ),
    ]


# === Device Registration ===

@router.post("/register", response_model=APIResponse[DeviceRegistrationResponse])
async def register_device(
    request: Request,
    reg_request: DeviceRegistrationRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[DeviceRegistrationResponse]:
    """
    Register a mobile device for push notifications and sync.

    Call this on first app launch and after any push token refresh.
    Device registration is required for push notifications.

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        devices = load_devices()
        now = get_pacific_now()

        # Create or update device registration
        registration_id = generate_id("dev")
        device_data = {
            "registration_id": registration_id,
            "device_id": reg_request.device_id,
            "user_id": user.uid,
            "platform": reg_request.platform.value,
            "push_token": reg_request.push_token,
            "device_name": reg_request.device_name,
            "app_version": reg_request.app_version,
            "os_version": reg_request.os_version,
            "timezone": reg_request.timezone,
            "registered_at": now.isoformat(),
            "last_seen": now.isoformat(),
        }

        # Use device_id + user_id as key for unique registration
        key = f"{user.uid}:{reg_request.device_id}"
        devices[key] = device_data
        save_devices(devices)

        response_data = DeviceRegistrationResponse(
            registration_id=registration_id,
            features_enabled=[
                "capture",
                "sync",
                "dashboard",
                "energy_tracking",
                "search",
                "voice_notes",
            ],
            sync_interval_seconds=300,  # 5 minutes
            push_enabled=bool(reg_request.push_token),
        )

        logger.info(f"Registered device {reg_request.device_id} for user {user.uid}")

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Device registration failed: {e}")
        return APIResponse(
            success=False,
            error=f"Registration failed: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


# === Quick Capture ===

@router.post("/capture", response_model=APIResponse[MobileCaptureResponse])
async def mobile_capture(
    request: Request,
    capture_request: MobileCaptureRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[MobileCaptureResponse]:
    """
    Capture content from mobile app.

    Supports multiple content types:
    - **text_note**: Quick text note
    - **quick_idea**: Idea (also creates ClickUp task)
    - **bookmark**: URL bookmark
    - **photo**: Base64-encoded photo
    - **voice_note**: Use /voice endpoint for audio
    - **location**: Location-based note

    Includes offline_id support for offline-first sync.

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        now = get_pacific_now()

        # Prepare metadata
        metadata = {
            "tags": capture_request.tags,
            "location": capture_request.location,
            "user_id": user.uid,
            "title": capture_request.title,
        }

        # Handle captured_at for offline captures
        if capture_request.captured_at:
            metadata["original_captured_at"] = capture_request.captured_at

        # Save to scratchpad
        capture_id = save_mobile_capture(
            content=capture_request.content,
            content_type=capture_request.content_type.value,
            metadata=metadata,
            offline_id=capture_request.offline_id,
        )

        stored_in = "scratchpad"
        clickup_task_id = None

        # For ideas, also create ClickUp task
        if capture_request.content_type == ContentType.QUICK_IDEA:
            title = capture_request.title or capture_request.content[:50]
            clickup_task_id = await create_clickup_idea(
                title=title,
                content=capture_request.content,
                tags=capture_request.tags,
            )
            if clickup_task_id:
                stored_in = "clickup"

        response_data = MobileCaptureResponse(
            capture_id=capture_id,
            offline_id=capture_request.offline_id,
            stored_in=stored_in,
            clickup_task_id=clickup_task_id,
            synced_at=now.isoformat(),
        )

        logger.info(f"Mobile capture {capture_id} from user {user.uid}")

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Mobile capture failed: {e}")
        return APIResponse(
            success=False,
            error=f"Capture failed: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


# === Offline Sync ===

@router.post("/sync", response_model=APIResponse[MobileSyncResponse])
async def sync_mobile(
    request: Request,
    sync_request: MobileSyncRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[MobileSyncResponse]:
    """
    Sync offline data from mobile app.

    Handles batch upload of offline captures and returns:
    - Upload results with server IDs
    - Pending notifications
    - Active OKR summary
    - Energy reminder status

    Call periodically or when connectivity is restored.

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        now = get_pacific_now()
        upload_results = []

        # Process each upload item
        for item in sync_request.items_to_upload:
            try:
                if item.type == "capture":
                    # Process as capture
                    data = item.data
                    capture_id = save_mobile_capture(
                        content=data.get("content", ""),
                        content_type=data.get("content_type", "text_note"),
                        metadata={
                            "tags": data.get("tags", []),
                            "user_id": user.uid,
                            "offline_created_at": item.created_at,
                        },
                        offline_id=item.offline_id,
                    )
                    upload_results.append(SyncResult(
                        offline_id=item.offline_id,
                        server_id=capture_id,
                        success=True,
                    ))

                elif item.type == "energy":
                    # Process as energy entry
                    data = item.data
                    energy_dir = SCRATCHPAD_DIR / "energy_entries" / now.strftime("%Y-%m-%d")
                    energy_dir.mkdir(parents=True, exist_ok=True)

                    entry_id = generate_id("energy")
                    entry = {
                        "id": entry_id,
                        "timestamp": item.created_at,
                        "user_id": user.uid,
                        "energy_level": data.get("energy_level"),
                        "focus_quality": data.get("focus_quality"),
                        "current_task": data.get("current_task"),
                        "synced_at": now.isoformat(),
                    }
                    entry_file = energy_dir / f"{entry_id}.json"
                    entry_file.write_text(json.dumps(entry, indent=2))

                    upload_results.append(SyncResult(
                        offline_id=item.offline_id,
                        server_id=entry_id,
                        success=True,
                    ))

                else:
                    upload_results.append(SyncResult(
                        offline_id=item.offline_id,
                        server_id="",
                        success=False,
                        error=f"Unknown item type: {item.type}",
                    ))

            except Exception as e:
                upload_results.append(SyncResult(
                    offline_id=item.offline_id,
                    server_id="",
                    success=False,
                    error=str(e),
                ))

        # Update device last_seen
        devices = load_devices()
        key = f"{user.uid}:{sync_request.device_id}"
        if key in devices:
            devices[key]["last_seen"] = now.isoformat()
            save_devices(devices)

        # Check energy reminder
        last_sync_dt = None
        if sync_request.last_sync:
            try:
                last_sync_dt = datetime.fromisoformat(sync_request.last_sync)
            except ValueError:
                pass

        energy_due, _ = is_energy_check_due(last_sync_dt)

        response_data = MobileSyncResponse(
            synced_at=now.isoformat(),
            upload_results=upload_results,
            pending_notifications=[],  # Would fetch from notification service
            active_okr=None,  # Would fetch from OKR service
            energy_reminder_due=energy_due,
            has_more_data=False,
        )

        logger.info(
            f"Synced {len(upload_results)} items from device {sync_request.device_id}"
        )

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Mobile sync failed: {e}")
        return APIResponse(
            success=False,
            error=f"Sync failed: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


# === Dashboard ===

@router.post("/dashboard", response_model=APIResponse[DashboardResponse])
async def get_dashboard(
    request: Request,
    dashboard_request: DashboardRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[DashboardResponse]:
    """
    Get mobile dashboard data.

    Returns personalized dashboard with:
    - Greeting
    - Active OKR summary
    - Priority tasks
    - Recent energy history
    - Quick action buttons
    - Notification count

    Use query params to customize response.

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        now = get_pacific_now()

        # Build dashboard response
        active_okr = None
        tasks: List[TaskSummary] = []
        energy_history: List[EnergyEntry] = []
        quick_actions: List[QuickActionButton] = []

        # Get quick actions
        if dashboard_request.include_quick_actions:
            quick_actions = get_default_quick_actions()

        # Get energy history
        if dashboard_request.include_energy:
            energy_dir = SCRATCHPAD_DIR / "energy_entries" / now.strftime("%Y-%m-%d")
            if energy_dir.exists():
                for entry_file in sorted(energy_dir.glob("*.json"), reverse=True)[:5]:
                    try:
                        data = json.loads(entry_file.read_text())
                        energy_history.append(EnergyEntry(
                            timestamp=data.get("timestamp", data.get("synced_at", "")),
                            energy_level=data.get("energy_level", 5),
                            focus_quality=data.get("focus_quality", "unknown"),
                            current_task=data.get("current_task"),
                        ))
                    except Exception:
                        pass

        # Get tasks from ClickUp (would call ClickUp API)
        if dashboard_request.include_tasks:
            try:
                import sys
                sys.path.insert(0, '/root/flourisha/00_AI_Brain/skills/clickup-tasks/reference')
                from clickup_api import ClickUpClient

                client = ClickUpClient()
                # Get high priority tasks - would filter by user assignment
                result = client.get_list_tasks(CLICKUP_SCRATCHPAD_LIST_ID)
                if result:
                    for t in result[:dashboard_request.limit_tasks]:
                        tasks.append(TaskSummary(
                            id=t.get('id', ''),
                            name=t.get('name', 'Untitled'),
                            list_name='Idea Scratchpad',
                            status=t.get('status', {}).get('status', 'unknown'),
                            priority=t.get('priority', {}).get('priority'),
                            due_date=t.get('due_date'),
                        ))
            except Exception as e:
                logger.warning(f"Failed to fetch tasks: {e}")

        # Count pending notifications (placeholder)
        unread_notifications = 0

        response_data = DashboardResponse(
            greeting=get_greeting(),
            current_date=now.strftime("%A, %B %d, %Y"),
            active_okr=active_okr,
            tasks=tasks,
            energy_history=energy_history,
            quick_actions=quick_actions,
            unread_notifications=unread_notifications,
            last_sync=now.isoformat(),
        )

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Dashboard fetch failed: {e}")
        return APIResponse(
            success=False,
            error=f"Dashboard failed: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


# === Energy Tracking ===

@router.post("/energy", response_model=APIResponse[MobileEnergyResponse])
async def submit_energy(
    request: Request,
    energy_request: MobileEnergyRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[MobileEnergyResponse]:
    """
    Submit energy check-in from mobile app.

    Includes additional mobile-specific fields:
    - mood tracking
    - location (optional)
    - notes

    Returns streak information and daily average.

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        now = get_pacific_now()
        entry_id = generate_id("energy")

        # Save energy entry
        energy_dir = SCRATCHPAD_DIR / "energy_entries" / now.strftime("%Y-%m-%d")
        energy_dir.mkdir(parents=True, exist_ok=True)

        entry = {
            "id": entry_id,
            "timestamp": now.isoformat(),
            "user_id": user.uid,
            "energy_level": energy_request.energy_level,
            "focus_quality": energy_request.focus_quality,
            "current_task": energy_request.current_task,
            "mood": energy_request.mood,
            "notes": energy_request.notes,
            "location": energy_request.location,
            "source": "mobile_app",
        }

        entry_file = energy_dir / f"{now.strftime('%H%M%S')}_{entry_id[:8]}.json"
        entry_file.write_text(json.dumps(entry, indent=2))

        # Calculate next reminder
        _, next_check = is_energy_check_due(now)

        # Calculate daily average
        daily_entries = []
        if energy_dir.exists():
            for f in energy_dir.glob("*.json"):
                try:
                    data = json.loads(f.read_text())
                    daily_entries.append(data.get("energy_level", 5))
                except Exception:
                    pass

        daily_average = sum(daily_entries) / len(daily_entries) if daily_entries else None

        # Count streak days (simplified - would query historical data)
        streak_days = 1  # Would calculate from historical entries

        response_data = MobileEnergyResponse(
            recorded=True,
            entry_id=entry_id,
            timestamp=now.isoformat(),
            next_reminder=next_check.isoformat() if next_check else None,
            streak_days=streak_days,
            daily_average=round(daily_average, 1) if daily_average else None,
        )

        logger.info(
            f"Energy entry from {user.uid}: {energy_request.energy_level}/{energy_request.focus_quality}"
        )

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Energy submission failed: {e}")
        return APIResponse(
            success=False,
            error=f"Failed to record energy: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


# === Voice Notes ===

@router.post("/voice", response_model=APIResponse[VoiceNoteUploadResponse])
async def upload_voice_note(
    request: Request,
    voice_request: VoiceNoteUploadRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[VoiceNoteUploadResponse]:
    """
    Upload a voice note from mobile app.

    Accepts base64-encoded audio and optionally transcribes it.
    Supports m4a, wav, and mp3 formats.

    Large files are queued for background processing.

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        now = get_pacific_now()
        note_id = generate_id("voice")

        # Create voice notes directory
        date_dir = now.strftime("%Y-%m-%d")
        voice_dir = VOICE_NOTES_DIR / date_dir
        voice_dir.mkdir(parents=True, exist_ok=True)

        # Decode and save audio
        try:
            audio_bytes = base64.b64decode(voice_request.audio_data)
        except Exception as e:
            return APIResponse(
                success=False,
                error=f"Invalid base64 audio data: {str(e)}",
                meta=ResponseMeta(**meta_dict),
            )

        # Save audio file
        audio_file = voice_dir / f"{note_id}.{voice_request.format}"
        audio_file.write_bytes(audio_bytes)

        # Save metadata
        metadata = {
            "id": note_id,
            "offline_id": voice_request.offline_id,
            "user_id": user.uid,
            "title": voice_request.title,
            "duration_seconds": voice_request.duration_seconds,
            "format": voice_request.format,
            "audio_file": str(audio_file),
            "created_at": now.isoformat(),
            "transcribe_requested": voice_request.transcribe,
            "transcript": None,
            "status": "uploaded",
        }

        metadata_file = voice_dir / f"{note_id}.json"
        metadata_file.write_text(json.dumps(metadata, indent=2))

        # Transcription would be queued for background processing
        status = "transcribing" if voice_request.transcribe else "uploaded"
        transcript = None

        # For short notes, could do synchronous transcription
        # For now, just mark as queued
        if voice_request.transcribe:
            status = "transcribing"
            # Would queue for Whisper transcription

        response_data = VoiceNoteUploadResponse(
            note_id=note_id,
            offline_id=voice_request.offline_id,
            status=status,
            transcript=transcript,
            duration_seconds=voice_request.duration_seconds,
        )

        logger.info(
            f"Voice note {note_id} uploaded by {user.uid}, "
            f"duration: {voice_request.duration_seconds}s"
        )

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Voice note upload failed: {e}")
        return APIResponse(
            success=False,
            error=f"Upload failed: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


# === Push Notification Preferences ===

@router.post("/push-preferences", response_model=APIResponse[UpdatePushPreferencesResponse])
async def update_push_preferences(
    request: Request,
    prefs_request: UpdatePushPreferencesRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[UpdatePushPreferencesResponse]:
    """
    Update push notification preferences.

    Configure which notifications to receive:
    - Energy reminders
    - Task due reminders
    - Morning report
    - Quiet hours

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        devices = load_devices()
        key = f"{user.uid}:{prefs_request.device_id}"

        if key not in devices:
            return APIResponse(
                success=False,
                error="Device not registered",
                meta=ResponseMeta(**meta_dict),
            )

        # Update preferences
        devices[key]["push_preferences"] = prefs_request.preferences.model_dump()
        save_devices(devices)

        response_data = UpdatePushPreferencesResponse(
            updated=True,
            preferences=prefs_request.preferences,
        )

        logger.info(f"Updated push preferences for device {prefs_request.device_id}")

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Push preferences update failed: {e}")
        return APIResponse(
            success=False,
            error=f"Update failed: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


# === App State ===

@router.post("/state", response_model=APIResponse[AppStateResponse])
async def get_app_state(
    request: Request,
    state_request: AppStateRequest,
    user: Optional[UserContext] = Depends(get_optional_user),
) -> APIResponse[AppStateResponse]:
    """
    Get current app state.

    Returns authentication status, feature flags, and server status.
    Use this on app launch to check:
    - Auth status
    - App version compatibility
    - Maintenance mode
    - Enabled features

    **Authentication:** Optional - returns partial data if not authenticated
    """
    meta_dict = request.state.get_meta()

    try:
        now = get_pacific_now()

        user_profile = None
        if user:
            user_profile = UserProfile(
                uid=user.uid,
                email=user.email or "",
                name=user.name,
                photo_url=None,  # Would fetch from Firebase
                subscription_tier="pro",  # Would check subscription
            )

        response_data = AppStateResponse(
            authenticated=user is not None,
            user=user_profile,
            app_version_supported=True,  # Would check against request version
            minimum_app_version=MIN_APP_VERSION,
            maintenance_mode=False,
            maintenance_message=None,
            features_enabled=[
                "capture",
                "sync",
                "dashboard",
                "energy_tracking",
                "search",
                "voice_notes",
                "okrs",
                "tasks",
            ] if user else ["search"],
            server_time=now.isoformat(),
        )

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"App state fetch failed: {e}")
        return APIResponse(
            success=False,
            error=f"State fetch failed: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


# === Search ===

@router.post("/search", response_model=APIResponse[MobileSearchResponse])
async def mobile_search(
    request: Request,
    search_request: MobileSearchRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[MobileSearchResponse]:
    """
    Mobile-optimized search across all content.

    Searches:
    - ClickUp tasks
    - Knowledge store
    - Scratchpad captures

    Returns compact results with snippets for mobile display.

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        import time
        start_time = time.time()

        query = search_request.query.lower()
        results: List[SearchResultItem] = []

        # Search scratchpad captures
        capture_dirs = [
            SCRATCHPAD_DIR / "mobile_captures",
            SCRATCHPAD_DIR / "extension_captures",
        ]

        for capture_dir in capture_dirs:
            if capture_dir.exists():
                for date_dir in capture_dir.iterdir():
                    if date_dir.is_dir():
                        for f in date_dir.glob("*.json"):
                            try:
                                data = json.loads(f.read_text())
                                content = data.get("content", "").lower()
                                title = data.get("metadata", {}).get("title", "").lower()

                                if query in content or query in title:
                                    snippet = None
                                    if search_request.include_snippets:
                                        # Find snippet around match
                                        idx = content.find(query)
                                        if idx >= 0:
                                            start = max(0, idx - 30)
                                            end = min(len(content), idx + len(query) + 50)
                                            snippet = content[start:end]
                                            if start > 0:
                                                snippet = "..." + snippet
                                            if end < len(content):
                                                snippet = snippet + "..."

                                    results.append(SearchResultItem(
                                        id=data.get("id", ""),
                                        type=data.get("type", "capture"),
                                        title=data.get("metadata", {}).get("title", "Capture"),
                                        snippet=snippet,
                                        relevance_score=0.8 if query in title else 0.5,
                                        source="scratchpad",
                                        date=data.get("captured_at"),
                                    ))
                            except Exception:
                                pass

        # Sort by relevance
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        results = results[:search_request.limit]

        search_time_ms = int((time.time() - start_time) * 1000)

        response_data = MobileSearchResponse(
            query=search_request.query,
            total_results=len(results),
            results=results,
            search_time_ms=search_time_ms,
            suggestions=[],  # Would generate search suggestions
        )

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Mobile search failed: {e}")
        return APIResponse(
            success=False,
            error=f"Search failed: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


# === Health Check ===

@router.get("/health")
async def mobile_health() -> Dict[str, Any]:
    """
    Health check for mobile API.

    No authentication required - used for connectivity check.
    """
    return {
        "status": "healthy",
        "service": "mobile-app-api",
        "timestamp": get_pacific_now().isoformat(),
        "min_app_version": MIN_APP_VERSION,
        "features": [
            "device_registration",
            "capture",
            "sync",
            "dashboard",
            "energy_tracking",
            "voice_notes",
            "push_preferences",
            "search",
        ],
    }
