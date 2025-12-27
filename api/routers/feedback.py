"""
Extraction Feedback Router

Human review queue for document extraction quality.
Enables field-level corrections and building training examples.
"""
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from zoneinfo import ZoneInfo
from enum import Enum
import uuid

from fastapi import APIRouter, Depends, Request, Query, HTTPException
from pydantic import BaseModel, Field

from models.response import APIResponse, ResponseMeta
from middleware.auth import get_current_user, UserContext


router = APIRouter(prefix="/api/feedback", tags=["Extraction Feedback"])

# Pacific timezone for timestamps
PACIFIC = ZoneInfo("America/Los_Angeles")


# === Enums ===

class FeedbackStatus(str, Enum):
    """Feedback item status."""
    PENDING = "pending"           # Awaiting human review
    IN_REVIEW = "in_review"       # Currently being reviewed
    APPROVED = "approved"         # Extraction approved as-is
    CORRECTED = "corrected"       # Extraction corrected by human
    REJECTED = "rejected"         # Extraction rejected/needs re-do
    EXAMPLE = "example"           # Promoted to training example


class FeedbackPriority(str, Enum):
    """Review priority."""
    CRITICAL = "critical"   # Medical/legal docs, blocking
    HIGH = "high"           # Important, affects processing
    NORMAL = "normal"       # Standard review
    LOW = "low"             # Nice to have


class ConfidenceLevel(str, Enum):
    """Extraction confidence."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# === Request/Response Models ===

class ExtractedField(BaseModel):
    """A single extracted field with its value."""
    field_name: str = Field(..., description="Field name/key")
    field_type: str = Field(default="text", description="Field type")
    extracted_value: Optional[str] = Field(None, description="Extracted value")
    corrected_value: Optional[str] = Field(None, description="Human-corrected value")
    confidence: str = Field(default="medium", description="Extraction confidence")
    source_text: Optional[str] = Field(None, description="Source text snippet")
    has_correction: bool = Field(default=False, description="Whether field was corrected")


class ExtractedEntity(BaseModel):
    """An extracted entity."""
    entity_id: str = Field(..., description="Entity ID")
    entity_type: str = Field(..., description="Entity type (person, medication, etc.)")
    name: str = Field(..., description="Entity name")
    value: Optional[str] = Field(None, description="Entity value")
    confidence: str = Field(default="medium", description="Extraction confidence")
    corrected_name: Optional[str] = Field(None, description="Corrected name")
    corrected_value: Optional[str] = Field(None, description="Corrected value")
    has_correction: bool = Field(default=False, description="Whether entity was corrected")


class FeedbackItem(BaseModel):
    """An item in the feedback queue."""
    id: str = Field(..., description="Feedback item ID")
    content_id: str = Field(..., description="Source content ID")
    document_title: Optional[str] = Field(None, description="Document title")
    document_type: Optional[str] = Field(None, description="Document type")
    backend_used: str = Field(default="claude", description="Extraction backend")
    status: str = Field(default="pending", description="Review status")
    priority: str = Field(default="normal", description="Review priority")
    overall_confidence: str = Field(default="medium", description="Overall extraction confidence")
    fields: List[ExtractedField] = Field(default_factory=list, description="Extracted fields")
    entities: List[ExtractedEntity] = Field(default_factory=list, description="Extracted entities")
    raw_text_preview: Optional[str] = Field(None, description="Preview of raw text")
    reviewer_id: Optional[str] = Field(None, description="Assigned reviewer")
    reviewer_notes: Optional[str] = Field(None, description="Reviewer notes")
    created_at: str = Field(..., description="Created timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    reviewed_at: Optional[str] = Field(None, description="Review completion timestamp")


class FeedbackQueueResponse(BaseModel):
    """Response for feedback queue listing."""
    items: List[FeedbackItem] = Field(..., description="Queue items")
    total: int = Field(..., description="Total matching items")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")
    stats: Dict[str, int] = Field(default_factory=dict, description="Status counts")


class FieldCorrectionRequest(BaseModel):
    """Request to correct a specific field."""
    field_name: str = Field(..., description="Field to correct")
    corrected_value: str = Field(..., description="Corrected value")
    correction_reason: Optional[str] = Field(None, description="Why the correction")


class EntityCorrectionRequest(BaseModel):
    """Request to correct an entity."""
    entity_id: str = Field(..., description="Entity ID to correct")
    corrected_name: Optional[str] = Field(None, description="Corrected name")
    corrected_value: Optional[str] = Field(None, description="Corrected value")
    should_delete: bool = Field(default=False, description="Delete this entity")


class SubmitCorrectionsRequest(BaseModel):
    """Request to submit corrections for a feedback item."""
    field_corrections: List[FieldCorrectionRequest] = Field(default_factory=list)
    entity_corrections: List[EntityCorrectionRequest] = Field(default_factory=list)
    new_entities: List[Dict[str, Any]] = Field(default_factory=list, description="New entities to add")
    reviewer_notes: Optional[str] = Field(None, description="Notes about the review")
    mark_as_example: bool = Field(default=False, description="Promote to training example")


class ApproveExtractionRequest(BaseModel):
    """Request to approve extraction as-is."""
    mark_as_example: bool = Field(default=False, description="Promote to training example")
    reviewer_notes: Optional[str] = Field(None, description="Notes about the approval")


class TrainingExample(BaseModel):
    """A training example created from approved extraction."""
    id: str = Field(..., description="Example ID")
    feedback_id: str = Field(..., description="Source feedback ID")
    content_id: str = Field(..., description="Source content ID")
    document_type: Optional[str] = Field(None, description="Document type")
    backend_used: str = Field(..., description="Backend that was corrected")
    input_text: str = Field(..., description="Input text")
    expected_output: Dict[str, Any] = Field(..., description="Expected extraction output")
    corrections_made: int = Field(default=0, description="Number of corrections made")
    created_at: str = Field(..., description="Created timestamp")
    created_by: str = Field(..., description="Created by user ID")


# === Helper Functions ===

def get_supabase():
    """Get Supabase client instance."""
    sys.path.insert(0, "/root/flourisha/00_AI_Brain")
    from services.supabase_client import SupabaseService
    return SupabaseService()


def calculate_priority(confidence: str, document_type: Optional[str]) -> str:
    """Calculate review priority based on confidence and document type."""
    # Medical/legal documents get higher priority
    critical_types = {"medical", "legal", "financial", "health"}
    is_critical = document_type and document_type.lower() in critical_types

    if confidence == "low" or is_critical:
        return "critical" if is_critical else "high"
    elif confidence == "medium":
        return "normal"
    else:
        return "low"


# === Endpoints ===

@router.get("/queue", response_model=APIResponse[FeedbackQueueResponse])
async def get_feedback_queue(
    request: Request,
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[FeedbackQueueResponse]:
    """
    Get the extraction feedback queue.

    Returns items sorted by priority (critical first, then high, normal, low).

    **Query Parameters:**
    - status: Filter by status (pending, in_review, approved, corrected, rejected, example)
    - priority: Filter by priority (critical, high, normal, low)
    - document_type: Filter by document type
    - page: Page number (1-indexed)
    - page_size: Items per page (max 100)

    **Response:**
    - items: Queue items sorted by priority
    - total: Total matching items
    - stats: Count by status

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or "default"

    supabase = get_supabase()
    offset = (page - 1) * page_size

    # Priority sort order
    priority_order = {"critical": 1, "high": 2, "normal": 3, "low": 4}

    try:
        # Try extraction_feedback table
        query = supabase.client.table("extraction_feedback").select(
            "*", count="exact"
        ).eq("tenant_id", tenant_id)

        if status:
            query = query.eq("status", status)

        if priority:
            query = query.eq("priority", priority)

        if document_type:
            query = query.eq("document_type", document_type)

        result = query.range(offset, offset + page_size - 1).order(
            "priority"  # Will need custom sorting
        ).order("created_at", desc=True).execute()

        items_data = result.data or []
        total = result.count or 0

        # Get stats
        stats_result = supabase.client.table("extraction_feedback").select(
            "status"
        ).eq("tenant_id", tenant_id).execute()

        stats = {"pending": 0, "in_review": 0, "approved": 0, "corrected": 0, "rejected": 0, "example": 0}
        for item in (stats_result.data or []):
            s = item.get("status", "pending")
            if s in stats:
                stats[s] += 1

        # Parse items
        items = []
        for item in items_data:
            items.append(FeedbackItem(
                id=str(item.get("id", "")),
                content_id=str(item.get("content_id", "")),
                document_title=item.get("document_title"),
                document_type=item.get("document_type"),
                backend_used=item.get("backend_used", "claude"),
                status=item.get("status", "pending"),
                priority=item.get("priority", "normal"),
                overall_confidence=item.get("overall_confidence", "medium"),
                fields=item.get("fields", []),
                entities=item.get("entities", []),
                raw_text_preview=item.get("raw_text_preview"),
                reviewer_id=item.get("reviewer_id"),
                reviewer_notes=item.get("reviewer_notes"),
                created_at=str(item.get("created_at", datetime.now(PACIFIC).isoformat())),
                updated_at=str(item.get("updated_at")) if item.get("updated_at") else None,
                reviewed_at=str(item.get("reviewed_at")) if item.get("reviewed_at") else None,
            ))

    except Exception as e:
        # Table may not exist yet - return empty
        items = []
        total = 0
        stats = {"pending": 0, "in_review": 0, "approved": 0, "corrected": 0, "rejected": 0, "example": 0}

    response_data = FeedbackQueueResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        stats=stats,
    )

    return APIResponse(
        success=True,
        data=response_data,
        meta=ResponseMeta(**meta_dict),
    )


@router.get("/queue/{feedback_id}", response_model=APIResponse[FeedbackItem])
async def get_feedback_item(
    request: Request,
    feedback_id: str,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[FeedbackItem]:
    """
    Get a specific feedback item with full details.

    **Path Parameters:**
    - feedback_id: The feedback item ID

    **Response:**
    - Full feedback item with all fields and entities

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or "default"

    supabase = get_supabase()

    try:
        result = supabase.client.table("extraction_feedback").select(
            "*"
        ).eq("id", feedback_id).eq("tenant_id", tenant_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail=f"Feedback item not found: {feedback_id}")

        item = result.data[0]

        feedback_item = FeedbackItem(
            id=str(item.get("id", "")),
            content_id=str(item.get("content_id", "")),
            document_title=item.get("document_title"),
            document_type=item.get("document_type"),
            backend_used=item.get("backend_used", "claude"),
            status=item.get("status", "pending"),
            priority=item.get("priority", "normal"),
            overall_confidence=item.get("overall_confidence", "medium"),
            fields=item.get("fields", []),
            entities=item.get("entities", []),
            raw_text_preview=item.get("raw_text_preview"),
            reviewer_id=item.get("reviewer_id"),
            reviewer_notes=item.get("reviewer_notes"),
            created_at=str(item.get("created_at", datetime.now(PACIFIC).isoformat())),
            updated_at=str(item.get("updated_at")) if item.get("updated_at") else None,
            reviewed_at=str(item.get("reviewed_at")) if item.get("reviewed_at") else None,
        )

        return APIResponse(
            success=True,
            data=feedback_item,
            meta=ResponseMeta(**meta_dict),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get feedback item: {str(e)}")


@router.post("/queue/{feedback_id}/claim", response_model=APIResponse[FeedbackItem])
async def claim_feedback_item(
    request: Request,
    feedback_id: str,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[FeedbackItem]:
    """
    Claim a feedback item for review.

    Sets status to 'in_review' and assigns the current user as reviewer.

    **Path Parameters:**
    - feedback_id: The feedback item ID

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or "default"

    supabase = get_supabase()

    try:
        # Check current status
        result = supabase.client.table("extraction_feedback").select(
            "id, status"
        ).eq("id", feedback_id).eq("tenant_id", tenant_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail=f"Feedback item not found: {feedback_id}")

        current_status = result.data[0].get("status", "pending")

        if current_status not in ["pending"]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot claim item with status '{current_status}'. Only pending items can be claimed."
            )

        # Update status and assign reviewer
        update_result = supabase.client.table("extraction_feedback").update({
            "status": "in_review",
            "reviewer_id": user.uid,
            "updated_at": datetime.now(PACIFIC).isoformat(),
        }).eq("id", feedback_id).execute()

        # Return updated item
        updated = update_result.data[0] if update_result.data else result.data[0]

        feedback_item = FeedbackItem(
            id=str(updated.get("id", "")),
            content_id=str(updated.get("content_id", "")),
            document_title=updated.get("document_title"),
            document_type=updated.get("document_type"),
            backend_used=updated.get("backend_used", "claude"),
            status="in_review",
            priority=updated.get("priority", "normal"),
            overall_confidence=updated.get("overall_confidence", "medium"),
            fields=updated.get("fields", []),
            entities=updated.get("entities", []),
            raw_text_preview=updated.get("raw_text_preview"),
            reviewer_id=user.uid,
            reviewer_notes=updated.get("reviewer_notes"),
            created_at=str(updated.get("created_at", datetime.now(PACIFIC).isoformat())),
            updated_at=datetime.now(PACIFIC).isoformat(),
            reviewed_at=None,
        )

        return APIResponse(
            success=True,
            data=feedback_item,
            meta=ResponseMeta(**meta_dict),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to claim item: {str(e)}")


@router.post("/queue/{feedback_id}/correct", response_model=APIResponse[FeedbackItem])
async def submit_corrections(
    request: Request,
    feedback_id: str,
    corrections: SubmitCorrectionsRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[FeedbackItem]:
    """
    Submit field-level corrections for a feedback item.

    **Path Parameters:**
    - feedback_id: The feedback item ID

    **Request Body:**
    - field_corrections: List of field corrections
    - entity_corrections: List of entity corrections
    - new_entities: New entities to add
    - reviewer_notes: Optional notes
    - mark_as_example: Whether to promote to training example

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or "default"

    supabase = get_supabase()

    try:
        # Get current item
        result = supabase.client.table("extraction_feedback").select(
            "*"
        ).eq("id", feedback_id).eq("tenant_id", tenant_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail=f"Feedback item not found: {feedback_id}")

        item = result.data[0]
        current_fields = item.get("fields", [])
        current_entities = item.get("entities", [])

        # Apply field corrections
        for correction in corrections.field_corrections:
            for field in current_fields:
                if field.get("field_name") == correction.field_name:
                    field["corrected_value"] = correction.corrected_value
                    field["has_correction"] = True
                    if correction.correction_reason:
                        field["correction_reason"] = correction.correction_reason

        # Apply entity corrections
        for correction in corrections.entity_corrections:
            for entity in current_entities:
                if entity.get("entity_id") == correction.entity_id:
                    if correction.should_delete:
                        entity["deleted"] = True
                    else:
                        if correction.corrected_name:
                            entity["corrected_name"] = correction.corrected_name
                        if correction.corrected_value:
                            entity["corrected_value"] = correction.corrected_value
                        entity["has_correction"] = True

        # Add new entities
        for new_entity in corrections.new_entities:
            current_entities.append({
                "entity_id": str(uuid.uuid4()),
                "entity_type": new_entity.get("entity_type", "unknown"),
                "name": new_entity.get("name", ""),
                "value": new_entity.get("value"),
                "confidence": "high",  # Human-added
                "is_new": True,
            })

        # Determine new status
        new_status = "example" if corrections.mark_as_example else "corrected"

        # Count corrections
        num_field_corrections = len([f for f in current_fields if f.get("has_correction")])
        num_entity_corrections = len([e for e in current_entities if e.get("has_correction") or e.get("is_new")])
        total_corrections = num_field_corrections + num_entity_corrections + len(corrections.new_entities)

        # Update the item
        update_result = supabase.client.table("extraction_feedback").update({
            "status": new_status,
            "fields": current_fields,
            "entities": current_entities,
            "reviewer_id": user.uid,
            "reviewer_notes": corrections.reviewer_notes,
            "corrections_count": total_corrections,
            "updated_at": datetime.now(PACIFIC).isoformat(),
            "reviewed_at": datetime.now(PACIFIC).isoformat(),
        }).eq("id", feedback_id).execute()

        # If marked as example, create training example
        if corrections.mark_as_example:
            await _create_training_example(
                supabase, tenant_id, feedback_id, item, current_fields, current_entities, user.uid
            )

        updated = update_result.data[0] if update_result.data else item

        feedback_item = FeedbackItem(
            id=str(updated.get("id", "")),
            content_id=str(updated.get("content_id", "")),
            document_title=updated.get("document_title"),
            document_type=updated.get("document_type"),
            backend_used=updated.get("backend_used", "claude"),
            status=new_status,
            priority=updated.get("priority", "normal"),
            overall_confidence=updated.get("overall_confidence", "medium"),
            fields=current_fields,
            entities=current_entities,
            raw_text_preview=updated.get("raw_text_preview"),
            reviewer_id=user.uid,
            reviewer_notes=corrections.reviewer_notes,
            created_at=str(updated.get("created_at", datetime.now(PACIFIC).isoformat())),
            updated_at=datetime.now(PACIFIC).isoformat(),
            reviewed_at=datetime.now(PACIFIC).isoformat(),
        )

        return APIResponse(
            success=True,
            data=feedback_item,
            meta=ResponseMeta(**meta_dict),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit corrections: {str(e)}")


@router.post("/queue/{feedback_id}/approve", response_model=APIResponse[FeedbackItem])
async def approve_extraction(
    request: Request,
    feedback_id: str,
    approval: ApproveExtractionRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[FeedbackItem]:
    """
    Approve an extraction as-is (no corrections needed).

    **Path Parameters:**
    - feedback_id: The feedback item ID

    **Request Body:**
    - mark_as_example: Whether to promote to training example
    - reviewer_notes: Optional notes

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or "default"

    supabase = get_supabase()

    try:
        # Get current item
        result = supabase.client.table("extraction_feedback").select(
            "*"
        ).eq("id", feedback_id).eq("tenant_id", tenant_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail=f"Feedback item not found: {feedback_id}")

        item = result.data[0]
        new_status = "example" if approval.mark_as_example else "approved"

        # Update the item
        update_result = supabase.client.table("extraction_feedback").update({
            "status": new_status,
            "reviewer_id": user.uid,
            "reviewer_notes": approval.reviewer_notes,
            "corrections_count": 0,
            "updated_at": datetime.now(PACIFIC).isoformat(),
            "reviewed_at": datetime.now(PACIFIC).isoformat(),
        }).eq("id", feedback_id).execute()

        # If marked as example, create training example
        if approval.mark_as_example:
            await _create_training_example(
                supabase, tenant_id, feedback_id, item,
                item.get("fields", []), item.get("entities", []), user.uid
            )

        updated = update_result.data[0] if update_result.data else item

        feedback_item = FeedbackItem(
            id=str(updated.get("id", "")),
            content_id=str(updated.get("content_id", "")),
            document_title=updated.get("document_title"),
            document_type=updated.get("document_type"),
            backend_used=updated.get("backend_used", "claude"),
            status=new_status,
            priority=updated.get("priority", "normal"),
            overall_confidence=updated.get("overall_confidence", "medium"),
            fields=updated.get("fields", []),
            entities=updated.get("entities", []),
            raw_text_preview=updated.get("raw_text_preview"),
            reviewer_id=user.uid,
            reviewer_notes=approval.reviewer_notes,
            created_at=str(updated.get("created_at", datetime.now(PACIFIC).isoformat())),
            updated_at=datetime.now(PACIFIC).isoformat(),
            reviewed_at=datetime.now(PACIFIC).isoformat(),
        )

        return APIResponse(
            success=True,
            data=feedback_item,
            meta=ResponseMeta(**meta_dict),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to approve extraction: {str(e)}")


async def _create_training_example(
    supabase,
    tenant_id: str,
    feedback_id: str,
    item: Dict[str, Any],
    fields: List[Dict],
    entities: List[Dict],
    user_id: str,
) -> str:
    """Create a training example from approved/corrected feedback."""
    try:
        example_id = str(uuid.uuid4())

        # Build expected output from corrected values
        expected_fields = {}
        for field in fields:
            field_name = field.get("field_name", "")
            # Use corrected value if available, otherwise extracted
            value = field.get("corrected_value") or field.get("extracted_value")
            expected_fields[field_name] = value

        expected_entities = []
        for entity in entities:
            if entity.get("deleted"):
                continue
            expected_entities.append({
                "entity_type": entity.get("entity_type"),
                "name": entity.get("corrected_name") or entity.get("name"),
                "value": entity.get("corrected_value") or entity.get("value"),
            })

        example_data = {
            "id": example_id,
            "tenant_id": tenant_id,
            "feedback_id": feedback_id,
            "content_id": item.get("content_id"),
            "document_type": item.get("document_type"),
            "backend_used": item.get("backend_used", "claude"),
            "input_text": item.get("raw_text_preview", ""),
            "expected_output": {
                "fields": expected_fields,
                "entities": expected_entities,
            },
            "corrections_made": sum(1 for f in fields if f.get("has_correction")) + \
                               sum(1 for e in entities if e.get("has_correction") or e.get("is_new")),
            "created_at": datetime.now(PACIFIC).isoformat(),
            "created_by": user_id,
        }

        supabase.client.table("extraction_examples").insert(example_data).execute()

        return example_id

    except Exception as e:
        # Log but don't fail the main operation
        print(f"Warning: Failed to create training example: {e}")
        return ""


@router.get("/examples", response_model=APIResponse[List[TrainingExample]])
async def list_training_examples(
    request: Request,
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    limit: int = Query(default=50, ge=1, le=200, description="Max results"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[List[TrainingExample]]:
    """
    List training examples created from approved extractions.

    **Query Parameters:**
    - document_type: Filter by document type
    - limit: Max results (default 50, max 200)

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or "default"

    supabase = get_supabase()

    try:
        query = supabase.client.table("extraction_examples").select(
            "*"
        ).eq("tenant_id", tenant_id)

        if document_type:
            query = query.eq("document_type", document_type)

        result = query.limit(limit).order("created_at", desc=True).execute()

        examples = []
        for item in (result.data or []):
            examples.append(TrainingExample(
                id=str(item.get("id", "")),
                feedback_id=str(item.get("feedback_id", "")),
                content_id=str(item.get("content_id", "")),
                document_type=item.get("document_type"),
                backend_used=item.get("backend_used", "claude"),
                input_text=item.get("input_text", ""),
                expected_output=item.get("expected_output", {}),
                corrections_made=item.get("corrections_made", 0),
                created_at=str(item.get("created_at", datetime.now(PACIFIC).isoformat())),
                created_by=item.get("created_by", ""),
            ))

        return APIResponse(
            success=True,
            data=examples,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        # Table may not exist - return empty
        return APIResponse(
            success=True,
            data=[],
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/stats", response_model=APIResponse[Dict[str, Any]])
async def get_feedback_stats(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[Dict[str, Any]]:
    """
    Get feedback queue statistics.

    **Response:**
    - Queue stats by status and priority
    - Training example counts
    - Reviewer activity

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or "default"

    supabase = get_supabase()

    stats = {
        "queue": {
            "total": 0,
            "by_status": {"pending": 0, "in_review": 0, "approved": 0, "corrected": 0, "rejected": 0, "example": 0},
            "by_priority": {"critical": 0, "high": 0, "normal": 0, "low": 0},
        },
        "examples": {
            "total": 0,
            "with_corrections": 0,
        },
        "last_updated": datetime.now(PACIFIC).isoformat(),
    }

    try:
        # Queue stats
        queue_result = supabase.client.table("extraction_feedback").select(
            "status, priority"
        ).eq("tenant_id", tenant_id).execute()

        for item in (queue_result.data or []):
            stats["queue"]["total"] += 1
            status = item.get("status", "pending")
            priority = item.get("priority", "normal")
            if status in stats["queue"]["by_status"]:
                stats["queue"]["by_status"][status] += 1
            if priority in stats["queue"]["by_priority"]:
                stats["queue"]["by_priority"][priority] += 1

        # Example stats
        example_result = supabase.client.table("extraction_examples").select(
            "corrections_made"
        ).eq("tenant_id", tenant_id).execute()

        for item in (example_result.data or []):
            stats["examples"]["total"] += 1
            if item.get("corrections_made", 0) > 0:
                stats["examples"]["with_corrections"] += 1

    except Exception:
        # Tables may not exist
        pass

    return APIResponse(
        success=True,
        data=stats,
        meta=ResponseMeta(**meta_dict),
    )
