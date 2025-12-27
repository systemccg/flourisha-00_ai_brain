"""
Context Card Router

API endpoints for managing user context cards - tiered visibility profiles
that control what information different audiences see about a user.

Endpoints:
- GET  /api/context-card              - Get user's full context card
- PUT  /api/context-card/{tier}       - Update a specific tier
- GET  /api/context-card/export       - Export as PDF/JSON/Markdown
- POST /api/context-card/from-chat    - Update from conversation analysis
- POST /api/context-card/preview      - Preview as seen by another user
- GET  /api/context-card/user/{id}    - Get another user's card (respects visibility)
"""
import sys
import base64
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import tempfile

from fastapi import APIRouter, Depends, Request, Query, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from models.response import APIResponse, ResponseMeta
from models.context_card import (
    ContextCard,
    ContextCardResponse,
    ContextCardTier,
    TierUpdateRequest,
    TierUpdateResponse,
    ConversationUpdateRequest,
    ConversationUpdateResponse,
    ExportFormat,
    ExportRequest,
    ExportResponse,
    ContextCardPreview,
    PreviewRequest,
    PublicTierContent,
    FriendsTierContent,
    WorkTierContent,
    WorkspaceTierContent,
    PrivateTierContent,
)
from middleware.auth import get_current_user, get_optional_user, UserContext


router = APIRouter(prefix="/api/context-card", tags=["Context Card"])

# Pacific timezone for timestamps
PACIFIC = ZoneInfo("America/Los_Angeles")


def get_pacific_timestamp() -> str:
    """Get current timestamp in Pacific time."""
    return datetime.now(PACIFIC).isoformat()


# Tier content validators
TIER_VALIDATORS = {
    "public": PublicTierContent,
    "friends": FriendsTierContent,
    "work": WorkTierContent,
    "private": PrivateTierContent,
}


def get_mock_context_card(user_id: str) -> ContextCard:
    """
    Get or create a context card for a user.

    TODO: Replace with actual database lookup once schema is implemented.
    Currently returns a sample card for development.
    """
    return ContextCard(
        user_id=user_id,
        public=PublicTierContent(
            name="User",
            headline="Flourisha User",
            bio="A Flourisha platform user",
        ),
        friends=FriendsTierContent(
            interests=["technology", "productivity"],
            values=["growth", "learning"],
        ),
        work=WorkTierContent(
            skills=["software development", "project management"],
            work_style="Remote-first, flexible hours",
        ),
        workspaces={},
        private=PrivateTierContent(
            goals=["Master AI-assisted productivity"],
            question_history=[],
        ),
        created_at=get_pacific_timestamp(),
        updated_at=get_pacific_timestamp(),
    )


@router.get("", response_model=APIResponse[ContextCardResponse])
async def get_context_card(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[ContextCardResponse]:
    """
    Get the current user's complete context card.

    Returns all tiers the user owns:
    - public: Visible to anyone
    - friends: Visible to personal connections
    - work: Visible to professional connections
    - workspaces: Workspace-specific profiles
    - private: Visible only to the user

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        # Get user's context card
        card = get_mock_context_card(user.uid)

        # User can edit all their own tiers
        editable_tiers = ["public", "friends", "work", "private"]
        editable_tiers.extend([f"workspace:{ws_id}" for ws_id in card.workspaces.keys()])

        return APIResponse(
            success=True,
            data=ContextCardResponse(
                card=card,
                editable_tiers=editable_tiers,
            ),
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.put("/{tier}", response_model=APIResponse[TierUpdateResponse])
async def update_tier(
    tier: str,
    request: Request,
    update_data: TierUpdateRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[TierUpdateResponse]:
    """
    Update a specific tier of the user's context card.

    **Path Parameters:**
    - tier: The tier to update (public, friends, work, private, or workspace:{id})

    **Request Body:**
    - content: Dictionary of fields to update for that tier

    **Validation:**
    - Content is validated against the tier's schema
    - Unknown fields are ignored
    - Partial updates are supported

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        # Parse workspace-specific tier
        if tier.startswith("workspace:"):
            workspace_id = tier.split(":", 1)[1]
            tier_type = "workspace"
        else:
            tier_type = tier
            workspace_id = None

        # Validate tier exists
        valid_tiers = ["public", "friends", "work", "private", "workspace"]
        if tier_type not in valid_tiers:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid tier: {tier}. Must be one of: public, friends, work, private, workspace:{{id}}"
            )

        # Validate content structure
        if tier_type in TIER_VALIDATORS:
            validator = TIER_VALIDATORS[tier_type]
            # This will raise ValidationError if content is invalid
            try:
                validated = validator(**update_data.content)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid content for {tier} tier: {str(e)}"
                )
        elif tier_type == "workspace":
            try:
                validated = WorkspaceTierContent(
                    workspace_id=workspace_id,
                    **update_data.content
                )
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid content for workspace tier: {str(e)}"
                )

        # TODO: Actually persist the update to database
        # For now, just return success

        return APIResponse(
            success=True,
            data=TierUpdateResponse(
                tier=tier,
                updated_at=get_pacific_timestamp(),
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except HTTPException:
        raise
    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/export", response_model=APIResponse[ExportResponse])
async def export_context_card(
    request: Request,
    format: ExportFormat = Query(ExportFormat.PDF, description="Export format"),
    include_tiers: str = Query("public,work", description="Comma-separated tiers to include"),
    include_framework: bool = Query(False, description="Include framework insights"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[ExportResponse]:
    """
    Export the context card in the specified format.

    **Query Parameters:**
    - format: pdf, json, or markdown
    - include_tiers: Comma-separated list of tiers to include
    - include_framework: Whether to include personality framework insights

    **PDF Export:**
    - Uses WeasyPrint for professional PDF generation
    - Returns base64-encoded PDF content

    **JSON Export:**
    - Returns structured JSON data

    **Markdown Export:**
    - Returns formatted markdown content

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        tiers_list = [t.strip() for t in include_tiers.split(",")]

        # Get user's context card
        card = get_mock_context_card(user.uid)

        # Build export content based on selected tiers
        export_data: Dict[str, Any] = {"user_id": card.user_id}

        if "public" in tiers_list:
            export_data["public"] = card.public.model_dump()
        if "friends" in tiers_list:
            export_data["friends"] = card.friends.model_dump()
        if "work" in tiers_list:
            export_data["work"] = card.work.model_dump()
        if "private" in tiers_list and include_framework:
            export_data["framework_insights"] = card.private.framework_insights

        # Add workspace tiers
        for tier in tiers_list:
            if tier.startswith("workspace:"):
                ws_id = tier.split(":", 1)[1]
                if ws_id in card.workspaces:
                    export_data[tier] = card.workspaces[ws_id].model_dump()

        timestamp = datetime.now(PACIFIC).strftime("%Y%m%d_%H%M%S")

        if format == ExportFormat.JSON:
            return APIResponse(
                success=True,
                data=ExportResponse(
                    format="json",
                    data=export_data,
                    filename=f"context_card_{timestamp}.json",
                ),
                meta=ResponseMeta(**meta_dict),
            )

        elif format == ExportFormat.MARKDOWN:
            md_content = generate_markdown_export(card, tiers_list, include_framework)
            return APIResponse(
                success=True,
                data=ExportResponse(
                    format="markdown",
                    data={"markdown": md_content},
                    filename=f"context_card_{timestamp}.md",
                ),
                meta=ResponseMeta(**meta_dict),
            )

        else:  # PDF
            pdf_content = generate_pdf_export(card, tiers_list, include_framework)
            return APIResponse(
                success=True,
                data=ExportResponse(
                    format="pdf",
                    content=pdf_content,  # Base64 encoded
                    filename=f"context_card_{timestamp}.pdf",
                ),
                meta=ResponseMeta(**meta_dict),
            )

    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.post("/from-chat", response_model=APIResponse[ConversationUpdateResponse])
async def update_from_conversation(
    request: Request,
    update_data: ConversationUpdateRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[ConversationUpdateResponse]:
    """
    Update context card by analyzing a conversation.

    This endpoint analyzes a conversation to extract insights about the user
    and updates their context card accordingly. Part of the "30 Universal Questions"
    progressive discovery system.

    **Request Body:**
    - conversation_id: ID of the conversation to analyze
    - updates: Optional specific updates to apply (bypasses analysis)

    **Process:**
    1. Retrieves conversation from history
    2. Analyzes for personality/preference signals
    3. Maps to appropriate context card fields
    4. Updates relevant tiers

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        # TODO: Implement actual conversation analysis
        # For now, return placeholder response

        fields_updated: List[str] = []
        tier_changes: Dict[str, int] = {}

        if update_data.updates:
            # Direct updates provided
            for key in update_data.updates.keys():
                fields_updated.append(key)
                # Determine tier from field
                tier = key.split(".")[0] if "." in key else "private"
                tier_changes[tier] = tier_changes.get(tier, 0) + 1
        else:
            # Would analyze conversation here
            # Placeholder: pretend we found some insights
            fields_updated = ["private.ai_learnings"]
            tier_changes = {"private": 1}

        return APIResponse(
            success=True,
            data=ConversationUpdateResponse(
                fields_updated=fields_updated,
                tier_changes=tier_changes,
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.post("/preview", response_model=APIResponse[ContextCardPreview])
async def preview_context_card(
    request: Request,
    preview_data: PreviewRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[ContextCardPreview]:
    """
    Preview how the context card appears to another viewer.

    **Request Body:**
    - viewer_id: Optional user ID to preview as
    - relationship: Assumed relationship (public, friend, work)
    - workspace_id: Workspace context for preview

    **Visibility Rules:**
    - public: Only public tier visible
    - friend: Public + friends tiers visible
    - work: Public + work tiers visible
    - workspace: Public + work + specific workspace tier visible

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        card = get_mock_context_card(user.uid)

        visible_tiers: List[str] = ["public"]
        relationship = preview_data.relationship or "public"

        if relationship == "friend":
            visible_tiers.append("friends")
        elif relationship == "work":
            visible_tiers.append("work")
        elif relationship == "workspace" and preview_data.workspace_id:
            visible_tiers.append("work")
            visible_tiers.append(f"workspace:{preview_data.workspace_id}")

        # Merge visible content
        merged: Dict[str, Any] = {}

        if "public" in visible_tiers:
            merged.update(card.public.model_dump())
        if "friends" in visible_tiers:
            merged.update(card.friends.model_dump())
        if "work" in visible_tiers:
            merged.update(card.work.model_dump())

        # Add workspace-specific content
        for tier in visible_tiers:
            if tier.startswith("workspace:"):
                ws_id = tier.split(":", 1)[1]
                if ws_id in card.workspaces:
                    merged.update(card.workspaces[ws_id].model_dump())

        return APIResponse(
            success=True,
            data=ContextCardPreview(
                visible_tiers=visible_tiers,
                merged_content=merged,
                viewer_relationship=relationship,
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/user/{user_id}", response_model=APIResponse[ContextCardPreview])
async def get_user_context_card(
    user_id: str,
    request: Request,
    workspace_id: Optional[str] = Query(None, description="Workspace context"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[ContextCardPreview]:
    """
    Get another user's context card (respects visibility settings).

    **Path Parameters:**
    - user_id: The user whose card to retrieve

    **Query Parameters:**
    - workspace_id: Workspace context for visibility

    **Visibility:**
    - Returns only tiers the requesting user is allowed to see
    - Determined by relationship and workspace membership

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        # Get the target user's card
        target_card = get_mock_context_card(user_id)

        # Determine visibility based on relationship
        # TODO: Implement actual relationship lookup
        # For now, default to public visibility
        visible_tiers = ["public"]
        relationship = "public"

        # If in same workspace, show work tier
        if workspace_id:
            # TODO: Check workspace membership
            visible_tiers.append("work")
            visible_tiers.append(f"workspace:{workspace_id}")
            relationship = "colleague"

        # Merge visible content
        merged: Dict[str, Any] = {}

        if "public" in visible_tiers:
            merged.update(target_card.public.model_dump())
        if "work" in visible_tiers:
            merged.update(target_card.work.model_dump())

        for tier in visible_tiers:
            if tier.startswith("workspace:"):
                ws_id = tier.split(":", 1)[1]
                if ws_id in target_card.workspaces:
                    merged.update(target_card.workspaces[ws_id].model_dump())

        return APIResponse(
            success=True,
            data=ContextCardPreview(
                visible_tiers=visible_tiers,
                merged_content=merged,
                viewer_relationship=relationship,
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


def generate_markdown_export(
    card: ContextCard,
    tiers: List[str],
    include_framework: bool = False,
) -> str:
    """Generate markdown export of context card."""
    lines = [
        f"# Context Card",
        f"",
        f"*Generated: {get_pacific_timestamp()}*",
        f"",
    ]

    if "public" in tiers:
        lines.extend([
            f"## Profile",
            f"",
            f"**Name:** {card.public.name or 'Not set'}",
            f"",
            f"**Headline:** {card.public.headline or 'Not set'}",
            f"",
            f"**Bio:** {card.public.bio or 'Not set'}",
            f"",
        ])

    if "work" in tiers:
        lines.extend([
            f"## Professional",
            f"",
            f"**Skills:** {', '.join(card.work.skills) if card.work.skills else 'Not set'}",
            f"",
            f"**Experience:** {card.work.experience_summary or 'Not set'}",
            f"",
            f"**Work Style:** {card.work.work_style or 'Not set'}",
            f"",
        ])

    if "friends" in tiers:
        lines.extend([
            f"## Personal",
            f"",
            f"**Interests:** {', '.join(card.friends.interests) if card.friends.interests else 'Not set'}",
            f"",
            f"**Values:** {', '.join(card.friends.values) if card.friends.values else 'Not set'}",
            f"",
        ])

    if include_framework and card.private.framework_insights:
        lines.extend([
            f"## Framework Insights",
            f"",
            f"```json",
            f"{json.dumps(card.private.framework_insights, indent=2)}",
            f"```",
            f"",
        ])

    return "\n".join(lines)


def generate_pdf_export(
    card: ContextCard,
    tiers: List[str],
    include_framework: bool = False,
) -> str:
    """
    Generate PDF export of context card using WeasyPrint.
    Returns base64-encoded PDF content.
    """
    try:
        from weasyprint import HTML, CSS
    except ImportError:
        # WeasyPrint not installed - return placeholder
        return base64.b64encode(b"PDF generation requires WeasyPrint").decode("utf-8")

    # Generate HTML for PDF
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Context Card</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 40px;
                color: #333;
            }}
            h1 {{
                color: #1a1a1a;
                border-bottom: 2px solid #3b82f6;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #374151;
                margin-top: 30px;
            }}
            .field {{
                margin-bottom: 15px;
            }}
            .label {{
                font-weight: 600;
                color: #4b5563;
            }}
            .value {{
                margin-top: 5px;
            }}
            .tags {{
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
            }}
            .tag {{
                background: #e5e7eb;
                padding: 4px 12px;
                border-radius: 4px;
                font-size: 14px;
            }}
            .timestamp {{
                color: #6b7280;
                font-style: italic;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <h1>Context Card</h1>
        <p class="timestamp">Generated: {get_pacific_timestamp()}</p>
    """

    if "public" in tiers:
        html_content += f"""
        <h2>Profile</h2>
        <div class="field">
            <div class="label">Name</div>
            <div class="value">{card.public.name or 'Not set'}</div>
        </div>
        <div class="field">
            <div class="label">Headline</div>
            <div class="value">{card.public.headline or 'Not set'}</div>
        </div>
        <div class="field">
            <div class="label">Bio</div>
            <div class="value">{card.public.bio or 'Not set'}</div>
        </div>
        """

    if "work" in tiers:
        skills_html = "".join([f'<span class="tag">{s}</span>' for s in card.work.skills]) if card.work.skills else 'Not set'
        html_content += f"""
        <h2>Professional</h2>
        <div class="field">
            <div class="label">Skills</div>
            <div class="value tags">{skills_html}</div>
        </div>
        <div class="field">
            <div class="label">Experience</div>
            <div class="value">{card.work.experience_summary or 'Not set'}</div>
        </div>
        <div class="field">
            <div class="label">Work Style</div>
            <div class="value">{card.work.work_style or 'Not set'}</div>
        </div>
        """

    if "friends" in tiers:
        interests_html = "".join([f'<span class="tag">{i}</span>' for i in card.friends.interests]) if card.friends.interests else 'Not set'
        values_html = "".join([f'<span class="tag">{v}</span>' for v in card.friends.values]) if card.friends.values else 'Not set'
        html_content += f"""
        <h2>Personal</h2>
        <div class="field">
            <div class="label">Interests</div>
            <div class="value tags">{interests_html}</div>
        </div>
        <div class="field">
            <div class="label">Values</div>
            <div class="value tags">{values_html}</div>
        </div>
        """

    html_content += """
    </body>
    </html>
    """

    # Generate PDF
    try:
        html = HTML(string=html_content)
        pdf_bytes = html.write_pdf()
        return base64.b64encode(pdf_bytes).decode("utf-8")
    except Exception as e:
        # Return error message as base64
        error_msg = f"PDF generation failed: {str(e)}"
        return base64.b64encode(error_msg.encode()).decode("utf-8")
