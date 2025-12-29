"""
Chrome Extension API Router

Endpoints optimized for browser extension use cases:
- Quick capture (notes, ideas, bookmarks)
- Page saving and ingestion
- Extension state sync
- Context menu actions
- URL intelligence
"""
import os
import json
import logging
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Request, Query, HTTPException
from pydantic import BaseModel

from models.response import APIResponse, ResponseMeta
from models.chrome_extension import (
    QuickCaptureRequest, QuickCaptureResponse,
    PageSaveRequest, PageSaveResponse,
    SyncRequest, SyncResponse, QuickAction, ActiveOKRSummary,
    ContextMenuAction, ContextMenuResponse,
    URLAnalysisRequest, URLAnalysisResponse,
    AuthStatusResponse, ExtensionSession,
    ExtensionState,
)
from middleware.auth import get_current_user, get_optional_user, UserContext


logger = logging.getLogger("flourisha.api.chrome_extension")
router = APIRouter(prefix="/api/extension", tags=["Chrome Extension"])

PACIFIC = ZoneInfo("America/Los_Angeles")
SCRATCHPAD_DIR = Path(os.path.expanduser("/root/flourisha/00_AI_Brain/scratchpad"))
CLICKUP_SCRATCHPAD_LIST_ID = "901112609506"  # Idea Scratchpad list


# === Helper Functions ===

def generate_capture_id() -> str:
    """Generate unique capture ID."""
    return f"cap_{uuid.uuid4().hex[:12]}"


def get_pacific_now() -> datetime:
    """Get current time in Pacific timezone."""
    return datetime.now(PACIFIC)


def save_to_scratchpad(content: str, content_type: str, metadata: Dict[str, Any]) -> str:
    """Save content to scratchpad directory.

    Returns the capture ID.
    """
    now = get_pacific_now()
    date_dir = now.strftime("%Y-%m-%d")
    timestamp = now.strftime("%H%M%S")
    capture_id = generate_capture_id()

    # Create directory
    capture_dir = SCRATCHPAD_DIR / "extension_captures" / date_dir
    capture_dir.mkdir(parents=True, exist_ok=True)

    # Create capture file
    filename = f"{timestamp}_{content_type}_{capture_id[:8]}.json"
    capture_path = capture_dir / filename

    capture_data = {
        "id": capture_id,
        "type": content_type,
        "content": content,
        "metadata": metadata,
        "captured_at": now.isoformat(),
        "processed": False,
    }

    capture_path.write_text(json.dumps(capture_data, indent=2))
    logger.info(f"Saved capture {capture_id} to {capture_path}")

    return capture_id


async def create_clickup_idea(title: str, content: str, tags: List[str]) -> Optional[str]:
    """Create a task in ClickUp Idea Scratchpad list.

    Returns task ID if successful, None otherwise.
    """
    try:
        import sys
        sys.path.insert(0, '/root/flourisha/00_AI_Brain/skills/clickup-tasks/reference')
        from clickup_api import ClickUpClient

        client = ClickUpClient()

        # Format description with tags
        description = content
        if tags:
            description += f"\n\nTags: {', '.join(tags)}"

        result = client.create_task(
            list_id=CLICKUP_SCRATCHPAD_LIST_ID,
            name=title[:100],  # ClickUp task name limit
            description=description,
        )

        if result.success:
            return result.data.get('id')
        return None
    except Exception as e:
        logger.error(f"Failed to create ClickUp task: {e}")
        return None


def get_default_quick_actions() -> List[QuickAction]:
    """Get default quick actions for extension popup."""
    return [
        QuickAction(
            id="quick_note",
            label="Quick Note",
            icon="📝",
            keyboard_shortcut="Ctrl+Shift+N"
        ),
        QuickAction(
            id="save_page",
            label="Save Page",
            icon="📄",
            keyboard_shortcut="Ctrl+Shift+S"
        ),
        QuickAction(
            id="capture_selection",
            label="Capture Selection",
            icon="✂️",
            keyboard_shortcut="Ctrl+Shift+C"
        ),
        QuickAction(
            id="energy_check",
            label="Energy Check-in",
            icon="⚡",
            keyboard_shortcut="Ctrl+Shift+E"
        ),
        QuickAction(
            id="search_knowledge",
            label="Search Knowledge",
            icon="🔍",
            keyboard_shortcut="Ctrl+Shift+K"
        ),
    ]


def is_energy_check_due(last_check: Optional[datetime] = None) -> tuple[bool, Optional[datetime]]:
    """Check if energy check-in is due (90-minute intervals).

    Returns (is_due, next_check_time).
    """
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


# === Endpoints ===

@router.post("/capture", response_model=APIResponse[QuickCaptureResponse])
async def quick_capture(
    request: Request,
    capture_request: QuickCaptureRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[QuickCaptureResponse]:
    """
    Quickly capture content from the browser extension.

    Supports multiple content types:
    - **note**: Quick note/thought
    - **idea**: Idea for later (creates ClickUp task)
    - **bookmark**: URL bookmark with notes
    - **selection**: Selected text from page
    - **page**: Full page reference

    Content is saved to scratchpad and optionally synced to ClickUp.

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        # Prepare metadata
        metadata = {
            "url": capture_request.url,
            "title": capture_request.title,
            "tags": capture_request.tags,
            "context": capture_request.context,
            "user_id": user.uid,
        }

        # Save to scratchpad
        capture_id = save_to_scratchpad(
            content=capture_request.content,
            content_type=capture_request.content_type,
            metadata=metadata,
        )

        stored_in = "scratchpad"
        clickup_task_id = None
        knowledge_id = None

        # For ideas, also create ClickUp task
        if capture_request.content_type == "idea":
            title = capture_request.title or capture_request.content[:50]
            clickup_task_id = await create_clickup_idea(
                title=title,
                content=capture_request.content,
                tags=capture_request.tags,
            )
            if clickup_task_id:
                stored_in = "clickup"

        response_data = QuickCaptureResponse(
            capture_id=capture_id,
            stored_in=stored_in,
            clickup_task_id=clickup_task_id,
            knowledge_id=knowledge_id,
        )

        logger.info(f"Captured {capture_request.content_type} as {capture_id}")

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Quick capture failed: {e}")
        return APIResponse(
            success=False,
            error=f"Capture failed: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.post("/page", response_model=APIResponse[PageSaveResponse])
async def save_page(
    request: Request,
    page_request: PageSaveRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[PageSaveResponse]:
    """
    Save a full web page for later processing.

    Options:
    - **process_immediately**: Ingest into knowledge store right away
    - **extract_links**: Extract and catalog links from page

    Large pages are queued for background processing.

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        page_id = f"page_{uuid.uuid4().hex[:12]}"
        status = "saved"
        queue_position = None
        knowledge_id = None
        links_extracted = 0

        # Prepare page data
        page_data = {
            "id": page_id,
            "url": page_request.url,
            "title": page_request.title,
            "content": page_request.content,
            "tags": page_request.tags,
            "user_id": user.uid,
            "saved_at": get_pacific_now().isoformat(),
        }

        # Save to scratchpad
        now = get_pacific_now()
        page_dir = SCRATCHPAD_DIR / "saved_pages" / now.strftime("%Y-%m-%d")
        page_dir.mkdir(parents=True, exist_ok=True)

        page_file = page_dir / f"{page_id}.json"
        page_file.write_text(json.dumps(page_data, indent=2))

        # If immediate processing requested, queue for ingestion
        if page_request.process_immediately:
            status = "queued"
            # Would add to processing queue here
            # For now, just mark as queued
            queue_position = 1

        # Extract links if requested
        if page_request.extract_links and page_request.html:
            # Simple link extraction (in production, use BeautifulSoup)
            import re
            links = re.findall(r'href="(https?://[^"]+)"', page_request.html or "")
            links_extracted = len(set(links))

        response_data = PageSaveResponse(
            page_id=page_id,
            status=status,
            queue_position=queue_position,
            knowledge_id=knowledge_id,
            links_extracted=links_extracted,
        )

        logger.info(f"Saved page {page_id}: {page_request.title}")

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Page save failed: {e}")
        return APIResponse(
            success=False,
            error=f"Failed to save page: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.post("/sync", response_model=APIResponse[SyncResponse])
async def sync_extension(
    request: Request,
    sync_request: SyncRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[SyncResponse]:
    """
    Sync extension state with server.

    Receives current extension state (energy, focus, task) and returns:
    - Available quick actions
    - Active OKR summary
    - Pending notifications
    - Energy check-in status

    Call this on extension popup open or periodic sync.

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        # Process extension state if provided
        if sync_request.extension_state:
            state = sync_request.extension_state
            if state.energy_level:
                logger.info(
                    f"User {user.uid} energy: {state.energy_level}, "
                    f"focus: {state.focus_quality}"
                )

        # Check if energy check is due
        last_sync_dt = None
        if sync_request.last_sync:
            try:
                last_sync_dt = datetime.fromisoformat(sync_request.last_sync)
            except ValueError:
                pass

        energy_due, next_check = is_energy_check_due(last_sync_dt)

        # Get pending captures count
        pending_captures = 0
        capture_dir = SCRATCHPAD_DIR / "extension_captures"
        if capture_dir.exists():
            for date_dir in capture_dir.iterdir():
                if date_dir.is_dir():
                    for f in date_dir.glob("*.json"):
                        try:
                            data = json.loads(f.read_text())
                            if not data.get("processed", False):
                                pending_captures += 1
                        except Exception:
                            pass

        # Build response
        response_data = SyncResponse(
            quick_actions=get_default_quick_actions(),
            active_okr=None,  # Would fetch from OKR service
            pending_captures=pending_captures,
            energy_reminder_due=energy_due,
            next_energy_check=next_check.isoformat() if next_check else None,
            notifications=[],  # Would fetch pending notifications
        )

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Sync failed: {e}")
        return APIResponse(
            success=False,
            error=f"Sync failed: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.post("/context-action", response_model=APIResponse[ContextMenuResponse])
async def context_menu_action(
    request: Request,
    action: ContextMenuAction,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[ContextMenuResponse]:
    """
    Handle browser context menu actions.

    Action types:
    - **save_selection**: Save selected text
    - **save_image**: Save image URL reference
    - **save_link**: Save link for later
    - **add_to_task**: Add selection to existing task

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        item_id = None
        message = ""

        if action.action_type == "save_selection":
            if not action.selection_text:
                return APIResponse(
                    success=False,
                    error="No text selected",
                    meta=ResponseMeta(**meta_dict),
                )

            # Save as capture
            item_id = save_to_scratchpad(
                content=action.selection_text,
                content_type="selection",
                metadata={
                    "url": action.page_url,
                    "title": action.page_title,
                    "user_id": user.uid,
                },
            )
            message = "Selection saved"

        elif action.action_type == "save_link":
            if not action.link_url:
                return APIResponse(
                    success=False,
                    error="No link URL provided",
                    meta=ResponseMeta(**meta_dict),
                )

            item_id = save_to_scratchpad(
                content=action.link_url,
                content_type="bookmark",
                metadata={
                    "source_url": action.page_url,
                    "source_title": action.page_title,
                    "user_id": user.uid,
                },
            )
            message = "Link saved"

        elif action.action_type == "save_image":
            if not action.image_url:
                return APIResponse(
                    success=False,
                    error="No image URL provided",
                    meta=ResponseMeta(**meta_dict),
                )

            item_id = save_to_scratchpad(
                content=action.image_url,
                content_type="image",
                metadata={
                    "source_url": action.page_url,
                    "source_title": action.page_title,
                    "user_id": user.uid,
                },
            )
            message = "Image reference saved"

        elif action.action_type == "add_to_task":
            if not action.task_id:
                return APIResponse(
                    success=False,
                    error="No task ID provided",
                    meta=ResponseMeta(**meta_dict),
                )

            # Would add comment to ClickUp task here
            item_id = action.task_id
            message = "Added to task"

        else:
            return APIResponse(
                success=False,
                error=f"Unknown action type: {action.action_type}",
                meta=ResponseMeta(**meta_dict),
            )

        response_data = ContextMenuResponse(
            success=True,
            message=message,
            item_id=item_id,
            undo_available=True,
        )

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Context action failed: {e}")
        return APIResponse(
            success=False,
            error=f"Action failed: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.post("/analyze-url", response_model=APIResponse[URLAnalysisResponse])
async def analyze_url(
    request: Request,
    analysis_request: URLAnalysisRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[URLAnalysisResponse]:
    """
    Analyze current URL for intelligence.

    Returns:
    - Whether URL was previously visited/saved
    - Related content from knowledge store
    - AI-suggested tags
    - Domain-specific notes

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        url = analysis_request.url
        previously_visited = False
        related_knowledge = []
        suggested_tags = []
        domain_notes = None
        save_recommended = False

        # Check saved pages for this URL
        pages_dir = SCRATCHPAD_DIR / "saved_pages"
        if pages_dir.exists():
            for date_dir in pages_dir.iterdir():
                if date_dir.is_dir():
                    for page_file in date_dir.glob("*.json"):
                        try:
                            data = json.loads(page_file.read_text())
                            if data.get("url") == url:
                                previously_visited = True
                                break
                        except Exception:
                            pass
                if previously_visited:
                    break

        # Extract domain for tag suggestions
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "")

        # Simple domain-based tag suggestions
        domain_tag_map = {
            "github.com": ["code", "development"],
            "youtube.com": ["video", "learning"],
            "medium.com": ["article", "blog"],
            "arxiv.org": ["research", "paper"],
            "stackoverflow.com": ["code", "reference"],
            "docs.python.org": ["python", "documentation"],
            "fastapi.tiangolo.com": ["api", "python", "documentation"],
        }

        for d, tags in domain_tag_map.items():
            if d in domain:
                suggested_tags.extend(tags)
                break

        if not suggested_tags:
            suggested_tags = ["web", "reference"]

        # Recommend save for certain domains
        valuable_domains = ["github.com", "arxiv.org", "docs.", "documentation"]
        save_recommended = any(vd in domain for vd in valuable_domains)

        response_data = URLAnalysisResponse(
            previously_visited=previously_visited,
            related_knowledge=related_knowledge,
            suggested_tags=list(set(suggested_tags)),
            domain_notes=domain_notes,
            save_recommended=save_recommended,
        )

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"URL analysis failed: {e}")
        return APIResponse(
            success=False,
            error=f"Analysis failed: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/auth-status", response_model=APIResponse[AuthStatusResponse])
async def get_auth_status(
    request: Request,
    user: Optional[UserContext] = Depends(get_optional_user),
) -> APIResponse[AuthStatusResponse]:
    """
    Get authentication status for extension.

    Returns current auth state and session info if authenticated.
    Use this on extension load to check if login is needed.

    **Authentication:** Optional - returns status either way
    """
    meta_dict = request.state.get_meta()

    try:
        if user:
            now = get_pacific_now()
            session = ExtensionSession(
                session_id=f"ext_{uuid.uuid4().hex[:8]}",
                started_at=now.isoformat(),
                expires_at=(now + timedelta(hours=24)).isoformat(),
                features_enabled=[
                    "quick_capture",
                    "page_save",
                    "sync",
                    "context_menu",
                    "url_analysis",
                ],
                rate_limit_remaining=1000,  # Would check actual rate limit
            )

            response_data = AuthStatusResponse(
                authenticated=True,
                user_name=user.name,
                user_email=user.email,
                session=session,
                login_url=None,
            )
        else:
            response_data = AuthStatusResponse(
                authenticated=False,
                user_name=None,
                user_email=None,
                session=None,
                login_url="https://flourisha.app/login?from=extension",
            )

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Auth status check failed: {e}")
        return APIResponse(
            success=False,
            error=f"Auth check failed: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/health")
async def extension_health() -> Dict[str, Any]:
    """
    Health check for extension API.

    No authentication required - used for connectivity check.
    """
    return {
        "status": "healthy",
        "service": "chrome-extension-api",
        "timestamp": get_pacific_now().isoformat(),
        "features": [
            "quick_capture",
            "page_save",
            "sync",
            "context_menu",
            "url_analysis",
        ],
    }


@router.post("/energy", response_model=APIResponse[Dict[str, Any]])
async def submit_energy(
    request: Request,
    energy_level: int = Query(..., ge=1, le=10, description="Energy level 1-10"),
    focus_quality: str = Query(..., description="Focus: deep, shallow, scattered"),
    current_task: Optional[str] = Query(None, description="Current task description"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[Dict[str, Any]]:
    """
    Submit energy check-in from extension.

    Quick endpoint for energy tracking:
    - energy_level: 1-10 scale
    - focus_quality: deep, shallow, or scattered
    - current_task: What you're working on (optional)

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        now = get_pacific_now()

        # Save energy entry
        energy_dir = SCRATCHPAD_DIR / "energy_entries" / now.strftime("%Y-%m-%d")
        energy_dir.mkdir(parents=True, exist_ok=True)

        entry = {
            "timestamp": now.isoformat(),
            "user_id": user.uid,
            "energy_level": energy_level,
            "focus_quality": focus_quality,
            "current_task": current_task,
        }

        entry_file = energy_dir / f"{now.strftime('%H%M%S')}.json"
        entry_file.write_text(json.dumps(entry, indent=2))

        # Calculate next check time
        _, next_check = is_energy_check_due(now)

        response_data = {
            "recorded": True,
            "timestamp": now.isoformat(),
            "next_check": next_check.isoformat() if next_check else None,
            "message": f"Energy {energy_level}/10, focus {focus_quality} recorded",
        }

        logger.info(f"Energy entry from {user.uid}: {energy_level}/{focus_quality}")

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
