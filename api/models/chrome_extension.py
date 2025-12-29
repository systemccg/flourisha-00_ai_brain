"""
Chrome Extension API Models

Pydantic models for Chrome extension-specific endpoints.
Optimized for browser extension use cases: quick capture, page saving, sync.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


# === Quick Capture Models ===

class QuickCaptureRequest(BaseModel):
    """Request to quickly capture content from extension."""
    content_type: str = Field(
        ...,
        description="Type of content: 'note', 'idea', 'bookmark', 'selection', 'page'"
    )
    content: str = Field(..., description="The captured content")
    url: Optional[str] = Field(None, description="Source URL")
    title: Optional[str] = Field(None, description="Page title or custom title")
    tags: List[str] = Field(default_factory=list, description="Tags to apply")
    context: Optional[str] = Field(
        None,
        description="Additional context (e.g., 'research', 'todo', 'reference')"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "content_type": "selection",
                "content": "This is an interesting quote I want to save.",
                "url": "https://example.com/article",
                "title": "Interesting Article",
                "tags": ["research", "ai"],
                "context": "research"
            }
        }
    }


class QuickCaptureResponse(BaseModel):
    """Response after capturing content."""
    capture_id: str = Field(..., description="Unique ID for the captured content")
    stored_in: str = Field(..., description="Where content was stored: 'scratchpad', 'clickup', 'knowledge'")
    clickup_task_id: Optional[str] = Field(None, description="ClickUp task ID if created")
    knowledge_id: Optional[str] = Field(None, description="Knowledge store ID if ingested")


# === Page Save Models ===

class PageSaveRequest(BaseModel):
    """Request to save a full page for later processing."""
    url: str = Field(..., description="Page URL to save")
    title: str = Field(..., description="Page title")
    content: Optional[str] = Field(None, description="Page text content (optional)")
    html: Optional[str] = Field(None, description="Full HTML (optional, for rich capture)")
    process_immediately: bool = Field(
        default=False,
        description="Whether to immediately ingest into knowledge store"
    )
    extract_links: bool = Field(
        default=False,
        description="Whether to extract and catalog links from page"
    )
    tags: List[str] = Field(default_factory=list, description="Tags to apply")

    model_config = {
        "json_schema_extra": {
            "example": {
                "url": "https://example.com/tutorial",
                "title": "Getting Started with FastAPI",
                "content": "FastAPI is a modern web framework...",
                "process_immediately": True,
                "tags": ["python", "api", "tutorial"]
            }
        }
    }


class PageSaveResponse(BaseModel):
    """Response after saving a page."""
    page_id: str = Field(..., description="Unique ID for the saved page")
    status: str = Field(..., description="Status: 'saved', 'queued', 'processing', 'ingested'")
    queue_position: Optional[int] = Field(None, description="Position in processing queue if queued")
    knowledge_id: Optional[str] = Field(None, description="Knowledge store ID if ingested")
    links_extracted: int = Field(default=0, description="Number of links extracted")


# === Extension Sync Models ===

class ExtensionState(BaseModel):
    """Current extension state for sync."""
    energy_level: Optional[int] = Field(None, ge=1, le=10, description="Current energy level 1-10")
    focus_quality: Optional[str] = Field(None, description="Focus quality: 'deep', 'shallow', 'scattered'")
    current_task: Optional[str] = Field(None, description="What the user is currently working on")
    active_okr: Optional[str] = Field(None, description="Active OKR ID for context")


class SyncRequest(BaseModel):
    """Request to sync extension state."""
    extension_state: Optional[ExtensionState] = Field(None, description="Current extension state")
    last_sync: Optional[str] = Field(None, description="ISO timestamp of last sync")

    model_config = {
        "json_schema_extra": {
            "example": {
                "extension_state": {
                    "energy_level": 7,
                    "focus_quality": "deep",
                    "current_task": "Writing API documentation"
                },
                "last_sync": "2025-12-29T10:00:00-08:00"
            }
        }
    }


class QuickAction(BaseModel):
    """Quick action available in extension popup."""
    id: str = Field(..., description="Action ID")
    label: str = Field(..., description="Display label")
    icon: Optional[str] = Field(None, description="Icon name or emoji")
    keyboard_shortcut: Optional[str] = Field(None, description="Keyboard shortcut")


class ActiveOKRSummary(BaseModel):
    """Summary of active OKR for extension display."""
    id: str = Field(..., description="OKR ID")
    objective: str = Field(..., description="Objective title")
    progress: float = Field(..., ge=0, le=100, description="Progress percentage")
    key_results_count: int = Field(..., description="Number of key results")


class SyncResponse(BaseModel):
    """Response with synced data for extension."""
    quick_actions: List[QuickAction] = Field(
        default_factory=list,
        description="Available quick actions"
    )
    active_okr: Optional[ActiveOKRSummary] = Field(None, description="Current active OKR")
    pending_captures: int = Field(default=0, description="Number of pending captures to process")
    energy_reminder_due: bool = Field(
        default=False,
        description="Whether energy check-in is due"
    )
    next_energy_check: Optional[str] = Field(
        None,
        description="ISO timestamp of next energy check"
    )
    notifications: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Pending notifications for user"
    )


# === Context Menu Models ===

class ContextMenuAction(BaseModel):
    """Action triggered from browser context menu."""
    action_type: str = Field(
        ...,
        description="Action: 'save_selection', 'save_image', 'save_link', 'add_to_task'"
    )
    selection_text: Optional[str] = Field(None, description="Selected text")
    page_url: str = Field(..., description="Current page URL")
    page_title: str = Field(..., description="Current page title")
    link_url: Optional[str] = Field(None, description="Right-clicked link URL")
    image_url: Optional[str] = Field(None, description="Right-clicked image URL")
    task_id: Optional[str] = Field(None, description="Task ID for 'add_to_task'")

    model_config = {
        "json_schema_extra": {
            "example": {
                "action_type": "save_selection",
                "selection_text": "Important information to save",
                "page_url": "https://example.com/doc",
                "page_title": "Documentation"
            }
        }
    }


class ContextMenuResponse(BaseModel):
    """Response from context menu action."""
    success: bool = Field(..., description="Whether action succeeded")
    message: str = Field(..., description="Status message for display")
    item_id: Optional[str] = Field(None, description="ID of created item")
    undo_available: bool = Field(default=False, description="Whether undo is available")


# === URL Intelligence Models ===

class URLAnalysisRequest(BaseModel):
    """Request to analyze current URL for intelligence."""
    url: str = Field(..., description="URL to analyze")
    title: Optional[str] = Field(None, description="Page title")


class URLAnalysisResponse(BaseModel):
    """Response with URL intelligence."""
    previously_visited: bool = Field(..., description="Whether URL was previously saved")
    related_knowledge: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Related items from knowledge store"
    )
    suggested_tags: List[str] = Field(
        default_factory=list,
        description="AI-suggested tags for this content"
    )
    domain_notes: Optional[str] = Field(
        None,
        description="Any saved notes about this domain"
    )
    save_recommended: bool = Field(
        default=False,
        description="Whether AI recommends saving this page"
    )


# === Session Models ===

class ExtensionSession(BaseModel):
    """Extension session information."""
    session_id: str = Field(..., description="Current session ID")
    started_at: str = Field(..., description="Session start time (Pacific)")
    expires_at: str = Field(..., description="Session expiration time")
    features_enabled: List[str] = Field(
        default_factory=list,
        description="Enabled extension features"
    )
    rate_limit_remaining: int = Field(..., description="API calls remaining")


class AuthStatusResponse(BaseModel):
    """Authentication status for extension."""
    authenticated: bool = Field(..., description="Whether user is authenticated")
    user_name: Optional[str] = Field(None, description="User display name")
    user_email: Optional[str] = Field(None, description="User email")
    session: Optional[ExtensionSession] = Field(None, description="Session info if authenticated")
    login_url: Optional[str] = Field(None, description="URL for login if not authenticated")
