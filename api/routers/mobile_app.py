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
import hashlib
import httpx
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode, quote, urlparse, parse_qs
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
    # Deep Links
    DeepLinkType, DeepLinkParams,
    CreateDeepLinkRequest, CreateDeepLinkResponse,
    ResolveDeepLinkRequest, ResolveDeepLinkResponse, DeepLinkDestination,
    BatchDeepLinksRequest, BatchDeepLinksResponse,
    DeepLinkAnalyticsRequest, DeepLinkAnalyticsResponse, DeepLinkStats,
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

# Firebase Dynamic Links Configuration
# NOTE: These should be moved to environment variables in production
FIREBASE_DYNAMIC_LINKS_DOMAIN = os.getenv("FIREBASE_DYNAMIC_LINKS_DOMAIN", "flourisha.page.link")
FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_WEB_API_KEY", "")
FIREBASE_DYNAMIC_LINKS_API_URL = "https://firebasedynamiclinks.googleapis.com/v1/shortLinks"
IOS_BUNDLE_ID = os.getenv("IOS_BUNDLE_ID", "com.flourisha.app")
IOS_APP_STORE_ID = os.getenv("IOS_APP_STORE_ID", "")
ANDROID_PACKAGE_NAME = os.getenv("ANDROID_PACKAGE_NAME", "com.flourisha.app")
DEEP_LINKS_FILE = SCRATCHPAD_DIR / "deep_links_registry.json"

# App URL scheme for custom deep links
APP_URL_SCHEME = "flourisha"
# Base URL for web fallback
WEB_FALLBACK_URL = os.getenv("WEB_FALLBACK_URL", "https://flourisha.app")

# Screen mapping for deep link types
DEEP_LINK_SCREEN_MAP = {
    "capture": "CaptureDetail",
    "task": "TaskDetail",
    "okr": "OKRDetail",
    "search": "Search",
    "energy": "EnergyCheckin",
    "dashboard": "Dashboard",
    "profile": "Profile",
    "settings": "Settings",
    "voice_note": "VoiceNoteDetail",
    "document": "DocumentDetail",
    "share": "ShareContent",
}


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


# === Deep Link Helper Functions ===

def load_deep_links_registry() -> Dict[str, Any]:
    """Load the deep links registry from file."""
    if DEEP_LINKS_FILE.exists():
        try:
            return json.loads(DEEP_LINKS_FILE.read_text())
        except Exception:
            pass
    return {"links": {}, "analytics": {}}


def save_deep_links_registry(registry: Dict[str, Any]) -> None:
    """Save the deep links registry to file."""
    DEEP_LINKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    DEEP_LINKS_FILE.write_text(json.dumps(registry, indent=2))


def generate_deep_link_id() -> str:
    """Generate a unique deep link ID."""
    return hashlib.sha256(
        f"{uuid.uuid4().hex}{datetime.now().isoformat()}".encode()
    ).hexdigest()[:12]


def build_app_link(link_type: str, target_id: Optional[str], params: Optional[Dict[str, Any]]) -> str:
    """Build the internal app link URL.

    Format: flourisha://[type]/[id]?[params]
    """
    path = f"{APP_URL_SCHEME}://{link_type}"
    if target_id:
        path += f"/{target_id}"

    if params:
        query_string = urlencode({k: str(v) for k, v in params.items()})
        path += f"?{query_string}"

    return path


def build_firebase_dynamic_link(
    app_link: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    image_url: Optional[str] = None,
    fallback_url: Optional[str] = None,
) -> str:
    """Build a Firebase Dynamic Link URL (long format).

    This creates the full dynamic link URL that Firebase can process.
    """
    # Build the link parameter
    link_param = quote(app_link, safe='')

    # Start building the dynamic link
    dynamic_link_params = {
        "link": app_link,
        "apn": ANDROID_PACKAGE_NAME,
        "ibi": IOS_BUNDLE_ID,
    }

    # Add iOS App Store ID if configured
    if IOS_APP_STORE_ID:
        dynamic_link_params["isi"] = IOS_APP_STORE_ID

    # Add fallback URL for users without the app
    if fallback_url:
        dynamic_link_params["ofl"] = fallback_url
    else:
        dynamic_link_params["ofl"] = f"{WEB_FALLBACK_URL}/open?link={link_param}"

    # Add social media preview parameters
    if title:
        dynamic_link_params["st"] = title
    if description:
        dynamic_link_params["sd"] = description
    if image_url:
        dynamic_link_params["si"] = image_url

    # Build the full dynamic link URL
    query_string = urlencode(dynamic_link_params)
    long_link = f"https://{FIREBASE_DYNAMIC_LINKS_DOMAIN}/?{query_string}"

    return long_link


async def create_short_link_via_api(
    long_link: str,
    suffix_option: str = "SHORT"
) -> Optional[str]:
    """Create a short link using Firebase Dynamic Links REST API.

    Args:
        long_link: The long Firebase Dynamic Link URL
        suffix_option: "SHORT" for 4-char suffix, "UNGUESSABLE" for 17-char

    Returns:
        Short link URL or None if API call fails
    """
    if not FIREBASE_WEB_API_KEY:
        logger.warning("Firebase Web API Key not configured, cannot create short links")
        return None

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{FIREBASE_DYNAMIC_LINKS_API_URL}?key={FIREBASE_WEB_API_KEY}",
                json={
                    "longDynamicLink": long_link,
                    "suffix": {"option": suffix_option}
                },
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("shortLink")
            else:
                logger.error(f"Firebase API error: {response.status_code} - {response.text}")
                return None

    except Exception as e:
        logger.error(f"Failed to create short link: {e}")
        return None


def parse_deep_link_url(url: str) -> Optional[Dict[str, Any]]:
    """Parse a deep link URL and extract components.

    Handles both:
    - Custom scheme: flourisha://task/abc123?foo=bar
    - Firebase Dynamic Links: https://flourisha.page.link/xyz
    - Web links: https://flourisha.app/open?link=...

    Returns:
        Dict with 'type', 'target_id', 'params' or None if invalid
    """
    try:
        parsed = urlparse(url)

        # Handle custom scheme (flourisha://)
        if parsed.scheme == APP_URL_SCHEME:
            link_type = parsed.netloc or parsed.path.split('/')[0]
            path_parts = parsed.path.strip('/').split('/')

            target_id = None
            if len(path_parts) > 0 and path_parts[0]:
                # If netloc is the type, path[0] is the ID
                if parsed.netloc:
                    target_id = path_parts[0] if path_parts[0] else None
                else:
                    # Type is in path
                    link_type = path_parts[0]
                    target_id = path_parts[1] if len(path_parts) > 1 else None

            params = dict(parse_qs(parsed.query))
            # Flatten single-value params
            params = {k: v[0] if len(v) == 1 else v for k, v in params.items()}

            return {
                "type": link_type,
                "target_id": target_id,
                "params": params,
            }

        # Handle Firebase Dynamic Links domain
        if FIREBASE_DYNAMIC_LINKS_DOMAIN in parsed.netloc:
            # The actual link is in the 'link' query parameter
            query_params = dict(parse_qs(parsed.query))
            if 'link' in query_params:
                actual_link = query_params['link'][0]
                return parse_deep_link_url(actual_link)

            # Short links need to be resolved via API or registry
            # For now, return the path as a reference
            short_id = parsed.path.strip('/')
            return {
                "type": "short_link",
                "target_id": short_id,
                "params": {},
            }

        # Handle web fallback links
        if parsed.netloc in [WEB_FALLBACK_URL.replace("https://", ""), "flourisha.app"]:
            query_params = dict(parse_qs(parsed.query))
            if 'link' in query_params:
                actual_link = query_params['link'][0]
                return parse_deep_link_url(actual_link)

        return None

    except Exception as e:
        logger.error(f"Failed to parse deep link URL: {e}")
        return None


def record_deep_link_click(
    link_id: str,
    platform: Optional[str] = None,
    is_install: bool = False,
    is_first_open: bool = False
) -> None:
    """Record a click on a deep link for analytics."""
    try:
        registry = load_deep_links_registry()

        if link_id not in registry.get("analytics", {}):
            registry.setdefault("analytics", {})[link_id] = {
                "clicks_total": 0,
                "clicks_ios": 0,
                "clicks_android": 0,
                "clicks_web": 0,
                "installs_total": 0,
                "first_opens": 0,
                "re_opens": 0,
            }

        stats = registry["analytics"][link_id]
        stats["clicks_total"] += 1

        if platform == "ios":
            stats["clicks_ios"] += 1
        elif platform == "android":
            stats["clicks_android"] += 1
        else:
            stats["clicks_web"] += 1

        if is_install:
            stats["installs_total"] += 1
        if is_first_open:
            stats["first_opens"] += 1
        elif not is_install:
            stats["re_opens"] += 1

        save_deep_links_registry(registry)

    except Exception as e:
        logger.error(f"Failed to record deep link click: {e}")


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


# === Deep Links ===

@router.post("/deep-links/create", response_model=APIResponse[CreateDeepLinkResponse])
async def create_deep_link(
    request: Request,
    link_request: CreateDeepLinkRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[CreateDeepLinkResponse]:
    """
    Create a Firebase Dynamic Link for sharing content.

    Generates a shareable link that:
    - Opens the app directly on mobile (if installed)
    - Falls back to app store for installation
    - Falls back to web for desktop users
    - Supports social media previews (title, description, image)

    **Requires:** Valid Firebase JWT

    **Link Types:**
    - `task`: Link to a specific task
    - `capture`: Link to a capture/note
    - `okr`: Link to an OKR
    - `search`: Pre-filled search query
    - `dashboard`: Go to dashboard
    - `energy`: Open energy check-in
    - `profile`: View profile
    - `settings`: Open settings
    - `share`: Generic share content

    **Suffix Options:**
    - `SHORT`: 4-character suffix (easier to share)
    - `UNGUESSABLE`: 17-character suffix (more secure)
    """
    meta_dict = request.state.get_meta()

    try:
        now = get_pacific_now()
        params = link_request.link_params

        # Build the internal app link
        app_link = build_app_link(
            link_type=params.link_type.value,
            target_id=params.target_id,
            params=params.params,
        )

        # Build the long Firebase Dynamic Link
        long_link = build_firebase_dynamic_link(
            app_link=app_link,
            title=params.title,
            description=params.description,
            image_url=params.image_url,
            fallback_url=params.fallback_url,
        )

        short_link = None
        warning = None

        # Try to create a short link if requested
        if link_request.short_link:
            short_link = await create_short_link_via_api(
                long_link=long_link,
                suffix_option=link_request.suffix_option,
            )
            if not short_link:
                warning = "Short link creation failed. Firebase API key may not be configured. Using long link."

        # Generate a link ID for tracking
        link_id = generate_deep_link_id()

        # Save to registry for analytics
        registry = load_deep_links_registry()
        registry.setdefault("links", {})[link_id] = {
            "short_link": short_link,
            "long_link": long_link,
            "app_link": app_link,
            "type": params.link_type.value,
            "target_id": params.target_id,
            "created_by": user.uid,
            "created_at": now.isoformat(),
        }
        save_deep_links_registry(registry)

        response_data = CreateDeepLinkResponse(
            short_link=short_link,
            long_link=long_link,
            preview_link=f"{WEB_FALLBACK_URL}/preview/{link_id}" if short_link else None,
            warning=warning,
        )

        logger.info(f"Created deep link {link_id} for {params.link_type.value}/{params.target_id}")

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Deep link creation failed: {e}")
        return APIResponse(
            success=False,
            error=f"Failed to create deep link: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.post("/deep-links/resolve", response_model=APIResponse[ResolveDeepLinkResponse])
async def resolve_deep_link(
    request: Request,
    resolve_request: ResolveDeepLinkRequest,
    user: Optional[UserContext] = Depends(get_optional_user),
) -> APIResponse[ResolveDeepLinkResponse]:
    """
    Resolve a deep link URL to its destination.

    Call this when the app receives a deep link to determine:
    - Which screen to navigate to
    - What parameters to pass
    - Whether this is a deferred deep link (post-install)

    **Authentication:** Optional - unauthenticated users get limited resolution

    **Supported URL Formats:**
    - `flourisha://task/abc123` - Custom scheme
    - `https://flourisha.page.link/xyz` - Firebase short link
    - `https://flourisha.app/open?link=...` - Web fallback
    """
    meta_dict = request.state.get_meta()

    try:
        now = get_pacific_now()

        # Parse the deep link URL
        parsed = parse_deep_link_url(resolve_request.link_url)

        if not parsed:
            return APIResponse(
                success=True,
                data=ResolveDeepLinkResponse(
                    valid=False,
                    error="Invalid deep link URL format",
                ),
                meta=ResponseMeta(**meta_dict),
            )

        link_type = parsed.get("type", "")
        target_id = parsed.get("target_id")
        params = parsed.get("params", {})

        # Handle short links by looking up in registry
        if link_type == "short_link" and target_id:
            registry = load_deep_links_registry()
            # Try to find the original link
            for link_id, link_data in registry.get("links", {}).items():
                short_url = link_data.get("short_link", "")
                if target_id in short_url:
                    link_type = link_data.get("type", "dashboard")
                    target_id = link_data.get("target_id")
                    break

        # Map link type to screen name
        screen = DEEP_LINK_SCREEN_MAP.get(link_type, "Dashboard")

        # Build the destination
        destination = DeepLinkDestination(
            screen=screen,
            params=params,
            resource_id=target_id,
            resource_type=link_type,
            deferred=False,  # Would check if this is a post-install link
        )

        # Record the click for analytics
        if resolve_request.device_id:
            record_deep_link_click(
                link_id=target_id or link_type,
                platform="mobile",
                is_first_open=False,
            )

        response_data = ResolveDeepLinkResponse(
            valid=True,
            destination=destination,
            attribution={
                "source": "deep_link",
                "medium": "link",
                "campaign": params.get("utm_campaign"),
                "resolved_at": now.isoformat(),
            },
        )

        logger.info(f"Resolved deep link to {screen}/{target_id}")

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Deep link resolution failed: {e}")
        return APIResponse(
            success=False,
            error=f"Failed to resolve deep link: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.post("/deep-links/batch", response_model=APIResponse[BatchDeepLinksResponse])
async def create_batch_deep_links(
    request: Request,
    batch_request: BatchDeepLinksRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[BatchDeepLinksResponse]:
    """
    Create multiple deep links in a single request.

    Useful for:
    - Sharing multiple tasks
    - Creating links for a list of items
    - Batch operations

    Limited to 10 links per request.

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        now = get_pacific_now()
        results: List[CreateDeepLinkResponse] = []
        success_count = 0
        error_count = 0

        for params in batch_request.links:
            try:
                # Build the internal app link
                app_link = build_app_link(
                    link_type=params.link_type.value,
                    target_id=params.target_id,
                    params=params.params,
                )

                # Build the long Firebase Dynamic Link
                long_link = build_firebase_dynamic_link(
                    app_link=app_link,
                    title=params.title,
                    description=params.description,
                    image_url=params.image_url,
                    fallback_url=params.fallback_url,
                )

                short_link = None
                if batch_request.short_links:
                    short_link = await create_short_link_via_api(long_link, "SHORT")

                # Save to registry
                link_id = generate_deep_link_id()
                registry = load_deep_links_registry()
                registry.setdefault("links", {})[link_id] = {
                    "short_link": short_link,
                    "long_link": long_link,
                    "app_link": app_link,
                    "type": params.link_type.value,
                    "target_id": params.target_id,
                    "created_by": user.uid,
                    "created_at": now.isoformat(),
                }
                save_deep_links_registry(registry)

                results.append(CreateDeepLinkResponse(
                    short_link=short_link,
                    long_link=long_link,
                ))
                success_count += 1

            except Exception as e:
                logger.error(f"Batch link creation failed for {params.link_type}: {e}")
                results.append(CreateDeepLinkResponse(
                    long_link="",
                    warning=str(e),
                ))
                error_count += 1

        response_data = BatchDeepLinksResponse(
            links=results,
            success_count=success_count,
            error_count=error_count,
        )

        logger.info(f"Created batch of {success_count} deep links ({error_count} errors)")

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Batch deep link creation failed: {e}")
        return APIResponse(
            success=False,
            error=f"Batch creation failed: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.post("/deep-links/analytics", response_model=APIResponse[DeepLinkAnalyticsResponse])
async def get_deep_link_analytics(
    request: Request,
    analytics_request: DeepLinkAnalyticsRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[DeepLinkAnalyticsResponse]:
    """
    Get analytics for deep links.

    Returns click statistics, installs, and opens for:
    - A specific link (by link_id)
    - All links (if no link_id specified)

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        now = get_pacific_now()
        period_start = (now - timedelta(days=analytics_request.days)).isoformat()
        period_end = now.isoformat()

        registry = load_deep_links_registry()
        analytics = registry.get("analytics", {})
        links_data = registry.get("links", {})

        stats_list: List[DeepLinkStats] = []
        total_clicks = 0
        total_installs = 0

        for link_id, stats in analytics.items():
            # Filter by specific link if requested
            if analytics_request.link_id and link_id != analytics_request.link_id:
                continue

            link_info = links_data.get(link_id, {})

            stats_list.append(DeepLinkStats(
                link_url=link_info.get("short_link") or link_info.get("long_link", link_id),
                clicks_total=stats.get("clicks_total", 0),
                clicks_ios=stats.get("clicks_ios", 0),
                clicks_android=stats.get("clicks_android", 0),
                clicks_web=stats.get("clicks_web", 0),
                installs_total=stats.get("installs_total", 0),
                first_opens=stats.get("first_opens", 0),
                re_opens=stats.get("re_opens", 0),
                created_at=link_info.get("created_at", ""),
            ))

            total_clicks += stats.get("clicks_total", 0)
            total_installs += stats.get("installs_total", 0)

        response_data = DeepLinkAnalyticsResponse(
            links=stats_list,
            period_start=period_start,
            period_end=period_end,
            total_clicks=total_clicks,
            total_installs=total_installs,
        )

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Deep link analytics failed: {e}")
        return APIResponse(
            success=False,
            error=f"Failed to get analytics: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/deep-links/schemes")
async def get_deep_link_schemes() -> Dict[str, Any]:
    """
    Get the URL schemes and supported link types.

    Use this to understand what deep link formats are supported.
    No authentication required.
    """
    return {
        "custom_scheme": APP_URL_SCHEME,
        "dynamic_links_domain": FIREBASE_DYNAMIC_LINKS_DOMAIN,
        "web_fallback": WEB_FALLBACK_URL,
        "supported_types": list(DEEP_LINK_SCREEN_MAP.keys()),
        "screen_mapping": DEEP_LINK_SCREEN_MAP,
        "url_format": f"{APP_URL_SCHEME}://[type]/[id]?[params]",
        "examples": {
            "task": f"{APP_URL_SCHEME}://task/task_abc123",
            "search": f"{APP_URL_SCHEME}://search?q=test",
            "okr": f"{APP_URL_SCHEME}://okr/okr_xyz789",
            "dashboard": f"{APP_URL_SCHEME}://dashboard",
        },
    }


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
            "deep_links",
        ],
    }
