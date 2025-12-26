"""
Ingestion Router

Knowledge ingestion status and monitoring endpoints.
Provides dashboard data for the content processing pipeline.
"""
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Request

from models.response import APIResponse, ResponseMeta
from models.ingestion import (
    IngestionStatusResponse,
    IngestionStats,
    ContentTypeCount,
    QueueItem,
    RecentItem,
)
from middleware.auth import get_current_user, UserContext


router = APIRouter(prefix="/api/ingestion", tags=["Ingestion"])
logger = logging.getLogger(__name__)

# Pacific timezone for timestamps
PACIFIC = ZoneInfo("America/Los_Angeles")


def get_supabase():
    """Get Supabase client instance."""
    import sys
    sys.path.insert(0, "/root/flourisha/00_AI_Brain")
    from services.supabase_client import SupabaseService
    return SupabaseService()


@router.get("/status", response_model=APIResponse[IngestionStatusResponse])
async def get_ingestion_status(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[IngestionStatusResponse]:
    """Get knowledge ingestion status dashboard.

    Returns comprehensive status including:
    - Overall statistics (total, completed, pending, failed)
    - Counts by content type (upload, youtube, gmail, etc.)
    - Current queue with pending items
    - Recently processed items (last 20)

    This endpoint is designed to power a dashboard UI showing
    the health and activity of the knowledge ingestion pipeline.
    """
    supabase = get_supabase()
    tenant_id = user.tenant_id or "default"
    now = datetime.now(PACIFIC)

    # Get overall stats by status
    content_query = supabase.client.table("processed_content").select(
        "processing_status",
        count="exact"
    ).eq("tenant_id", tenant_id)

    # Get counts by status
    stats_result = supabase.client.table("processed_content").select(
        "processing_status"
    ).eq("tenant_id", tenant_id).execute()

    status_counts = {
        "pending": 0,
        "processing": 0,
        "completed": 0,
        "failed": 0,
    }

    for item in stats_result.data or []:
        status = item.get("processing_status", "pending")
        if status in status_counts:
            status_counts[status] += 1
        else:
            status_counts["pending"] += 1

    total = sum(status_counts.values())

    stats = IngestionStats(
        total_items=total,
        completed=status_counts["completed"],
        pending=status_counts["pending"],
        processing=status_counts["processing"],
        failed=status_counts["failed"],
    )

    # Get counts by content type
    type_result = supabase.client.table("processed_content").select(
        "source_type"
    ).eq("tenant_id", tenant_id).execute()

    type_counts = {}
    for item in type_result.data or []:
        source_type = item.get("source_type", "unknown")
        type_counts[source_type] = type_counts.get(source_type, 0) + 1

    by_content_type = [
        ContentTypeCount(source_type=st, count=cnt)
        for st, cnt in sorted(type_counts.items(), key=lambda x: -x[1])
    ]

    # Get queue items
    queue_result = supabase.client.table("processing_queue").select(
        "content_id, priority, status, retry_count, created_at, metadata"
    ).eq("tenant_id", tenant_id).in_(
        "status", ["queued", "processing"]
    ).order("priority", desc=True).order("created_at").limit(20).execute()

    queue_items = []
    for item in queue_result.data or []:
        content_id = item.get("content_id")
        metadata = item.get("metadata", {}) or {}

        # Try to get title from content table
        title = None
        if content_id:
            content = supabase.client.table("processed_content").select(
                "title, source_type"
            ).eq("id", content_id).single().execute()
            if content.data:
                title = content.data.get("title")

        queue_items.append(QueueItem(
            content_id=content_id or "unknown",
            title=title,
            source_type=metadata.get("document_type") or "upload",
            priority=item.get("priority", 5),
            status=item.get("status", "queued"),
            created_at=item.get("created_at", now.isoformat()),
            retry_count=item.get("retry_count", 0),
        ))

    # Get recently processed items (last 20)
    recent_result = supabase.client.table("processed_content").select(
        "id, title, source_type, processing_status, updated_at, embedding, graph_node_id, error_message"
    ).eq("tenant_id", tenant_id).in_(
        "processing_status", ["completed", "failed"]
    ).order("updated_at", desc=True).limit(20).execute()

    recent_items = []
    for item in recent_result.data or []:
        recent_items.append(RecentItem(
            content_id=item.get("id", "unknown"),
            title=item.get("title"),
            source_type=item.get("source_type", "unknown"),
            status=item.get("processing_status", "unknown"),
            processed_at=item.get("updated_at", now.isoformat()),
            has_embedding=item.get("embedding") is not None,
            has_graph=item.get("graph_node_id") is not None,
            error_message=item.get("error_message"),
        ))

    meta_dict = request.state.get_meta()

    return APIResponse(
        success=True,
        data=IngestionStatusResponse(
            stats=stats,
            by_content_type=by_content_type,
            queue=queue_items,
            recent=recent_items,
            last_updated=now.isoformat(),
        ),
        meta=ResponseMeta(**meta_dict),
    )


@router.get("/queue", response_model=APIResponse[list[QueueItem]])
async def get_queue(
    request: Request,
    limit: int = 50,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[list[QueueItem]]:
    """Get current processing queue.

    Returns pending and processing items ordered by priority
    then by creation time.
    """
    supabase = get_supabase()
    tenant_id = user.tenant_id or "default"
    now = datetime.now(PACIFIC)

    queue_result = supabase.client.table("processing_queue").select(
        "content_id, priority, status, retry_count, created_at, metadata"
    ).eq("tenant_id", tenant_id).in_(
        "status", ["queued", "processing"]
    ).order("priority", desc=True).order("created_at").limit(limit).execute()

    queue_items = []
    for item in queue_result.data or []:
        content_id = item.get("content_id")
        metadata = item.get("metadata", {}) or {}

        # Try to get title from content table
        title = None
        source_type = "upload"
        if content_id:
            content = supabase.client.table("processed_content").select(
                "title, source_type"
            ).eq("id", content_id).single().execute()
            if content.data:
                title = content.data.get("title")
                source_type = content.data.get("source_type", "upload")

        queue_items.append(QueueItem(
            content_id=content_id or "unknown",
            title=title,
            source_type=source_type,
            priority=item.get("priority", 5),
            status=item.get("status", "queued"),
            created_at=item.get("created_at", now.isoformat()),
            retry_count=item.get("retry_count", 0),
        ))

    meta_dict = request.state.get_meta()

    return APIResponse(
        success=True,
        data=queue_items,
        meta=ResponseMeta(**meta_dict),
    )


@router.get("/recent", response_model=APIResponse[list[RecentItem]])
async def get_recent(
    request: Request,
    limit: int = 20,
    status: str = None,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[list[RecentItem]]:
    """Get recently processed items.

    Args:
        limit: Maximum items to return (default 20, max 100)
        status: Filter by status (completed, failed)

    Returns items ordered by processing time, most recent first.
    """
    supabase = get_supabase()
    tenant_id = user.tenant_id or "default"
    now = datetime.now(PACIFIC)

    # Clamp limit
    limit = max(1, min(100, limit))

    # Build query
    query = supabase.client.table("processed_content").select(
        "id, title, source_type, processing_status, updated_at, embedding, graph_node_id, error_message"
    ).eq("tenant_id", tenant_id)

    if status:
        query = query.eq("processing_status", status)
    else:
        query = query.in_("processing_status", ["completed", "failed"])

    result = query.order("updated_at", desc=True).limit(limit).execute()

    recent_items = []
    for item in result.data or []:
        recent_items.append(RecentItem(
            content_id=item.get("id", "unknown"),
            title=item.get("title"),
            source_type=item.get("source_type", "unknown"),
            status=item.get("processing_status", "unknown"),
            processed_at=item.get("updated_at", now.isoformat()),
            has_embedding=item.get("embedding") is not None,
            has_graph=item.get("graph_node_id") is not None,
            error_message=item.get("error_message"),
        ))

    meta_dict = request.state.get_meta()

    return APIResponse(
        success=True,
        data=recent_items,
        meta=ResponseMeta(**meta_dict),
    )


@router.get("/stats", response_model=APIResponse[IngestionStats])
async def get_stats(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[IngestionStats]:
    """Get ingestion statistics summary.

    Quick endpoint for just the stats without queue and recent items.
    Useful for lightweight polling or status indicators.
    """
    supabase = get_supabase()
    tenant_id = user.tenant_id or "default"

    # Get counts by status
    stats_result = supabase.client.table("processed_content").select(
        "processing_status"
    ).eq("tenant_id", tenant_id).execute()

    status_counts = {
        "pending": 0,
        "processing": 0,
        "completed": 0,
        "failed": 0,
    }

    for item in stats_result.data or []:
        status = item.get("processing_status", "pending")
        if status in status_counts:
            status_counts[status] += 1
        else:
            status_counts["pending"] += 1

    total = sum(status_counts.values())

    stats = IngestionStats(
        total_items=total,
        completed=status_counts["completed"],
        pending=status_counts["pending"],
        processing=status_counts["processing"],
        failed=status_counts["failed"],
    )

    meta_dict = request.state.get_meta()

    return APIResponse(
        success=True,
        data=stats,
        meta=ResponseMeta(**meta_dict),
    )
