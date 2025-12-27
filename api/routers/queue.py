"""
Processing Queue Router

Endpoints for monitoring and managing the async processing queue.
Provides job status, progress tracking, and cancellation.
"""
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from zoneinfo import ZoneInfo
from enum import Enum

from fastapi import APIRouter, Depends, Request, Query, HTTPException
from pydantic import BaseModel, Field

from models.response import APIResponse, ResponseMeta
from middleware.auth import get_current_user, UserContext


router = APIRouter(prefix="/api/queue", tags=["Processing Queue"])

# Pacific timezone for timestamps
PACIFIC = ZoneInfo("America/Los_Angeles")


# === Enums ===

class JobStatus(str, Enum):
    """Processing job status."""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(str, Enum):
    """Type of processing job."""
    DOCUMENT = "document"
    YOUTUBE = "youtube"
    GMAIL = "gmail"
    EMBEDDING = "embedding"
    GRAPH = "graph"
    GENERAL = "general"


# === Request/Response Models ===

class ProcessingJob(BaseModel):
    """A single processing job."""
    id: str = Field(..., description="Job ID")
    content_id: Optional[str] = Field(None, description="Associated content ID")
    job_type: str = Field(default="general", description="Type of job")
    title: Optional[str] = Field(None, description="Job title/description")
    status: str = Field(..., description="Job status")
    priority: int = Field(default=5, description="Priority 1-10 (10 = highest)")
    progress_percent: Optional[float] = Field(None, ge=0, le=100, description="Progress percentage")
    progress_message: Optional[str] = Field(None, description="Current progress message")
    retry_count: int = Field(default=0, description="Retry attempts")
    max_retries: int = Field(default=3, description="Maximum retries")
    created_at: str = Field(..., description="When job was created")
    started_at: Optional[str] = Field(None, description="When processing started")
    completed_at: Optional[str] = Field(None, description="When processing completed")
    error_message: Optional[str] = Field(None, description="Error if failed")


class QueueStats(BaseModel):
    """Queue statistics."""
    total_jobs: int = Field(default=0, description="Total jobs in queue")
    pending: int = Field(default=0, description="Pending jobs")
    queued: int = Field(default=0, description="Queued jobs")
    processing: int = Field(default=0, description="Currently processing")
    completed: int = Field(default=0, description="Completed jobs")
    failed: int = Field(default=0, description="Failed jobs")
    cancelled: int = Field(default=0, description="Cancelled jobs")
    avg_processing_time_ms: Optional[float] = Field(None, description="Average processing time")


class QueueStatusResponse(BaseModel):
    """Complete queue status."""
    stats: QueueStats = Field(..., description="Queue statistics")
    jobs: List[ProcessingJob] = Field(..., description="Jobs matching filter")
    last_updated: str = Field(..., description="Status timestamp")


class JobListResponse(BaseModel):
    """Paginated job list."""
    jobs: List[ProcessingJob] = Field(..., description="Jobs")
    total: int = Field(..., description="Total matching jobs")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")
    has_more: bool = Field(..., description="More pages available")


class CancelJobResponse(BaseModel):
    """Response for job cancellation."""
    job_id: str = Field(..., description="Job ID")
    success: bool = Field(..., description="Whether cancellation succeeded")
    message: str = Field(..., description="Result message")
    previous_status: str = Field(..., description="Status before cancellation")


# === Helper Functions ===

def get_supabase():
    """Get Supabase client instance."""
    sys.path.insert(0, "/root/flourisha/00_AI_Brain")
    from services.supabase_client import SupabaseService
    return SupabaseService()


def format_timestamp(dt) -> str:
    """Format datetime to ISO string."""
    if isinstance(dt, str):
        return dt
    if dt:
        return dt.isoformat()
    return None


def parse_db_job(item: Dict[str, Any]) -> ProcessingJob:
    """Parse database row to ProcessingJob model."""
    # Handle different possible column names
    job_id = item.get("id") or item.get("job_id") or ""
    content_id = item.get("content_id")

    # Extract job title from content if available
    title = item.get("title")
    if not title and "processed_content" in item:
        title = item["processed_content"].get("title")

    # Determine job type from source_type
    source_type = item.get("source_type", "general")
    if source_type in ["youtube", "video"]:
        job_type = "youtube"
    elif source_type in ["gmail", "email"]:
        job_type = "gmail"
    elif source_type in ["upload", "document", "pdf"]:
        job_type = "document"
    elif source_type in ["embedding"]:
        job_type = "embedding"
    else:
        job_type = source_type or "general"

    # Map status
    status = item.get("status") or item.get("processing_status") or "pending"

    # Calculate progress based on status
    progress_percent = item.get("progress_percent")
    if progress_percent is None:
        if status == "completed":
            progress_percent = 100.0
        elif status == "processing":
            progress_percent = 50.0  # Default for in-progress
        elif status in ["pending", "queued"]:
            progress_percent = 0.0
        elif status == "failed":
            progress_percent = item.get("failed_at_percent", 0.0)

    return ProcessingJob(
        id=str(job_id),
        content_id=str(content_id) if content_id else None,
        job_type=job_type,
        title=title,
        status=status,
        priority=item.get("priority", 5),
        progress_percent=progress_percent,
        progress_message=item.get("progress_message"),
        retry_count=item.get("retry_count", 0),
        max_retries=item.get("max_retries", 3),
        created_at=format_timestamp(item.get("created_at")) or datetime.now(PACIFIC).isoformat(),
        started_at=format_timestamp(item.get("started_at") or item.get("processing_started_at")),
        completed_at=format_timestamp(item.get("completed_at") or item.get("processed_at")),
        error_message=item.get("error_message") or item.get("error"),
    )


# === Endpoints ===

@router.get("/status", response_model=APIResponse[QueueStatusResponse])
async def get_queue_status(
    request: Request,
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    job_type: Optional[str] = Query(None, description="Filter by job type"),
    limit: int = Query(default=20, ge=1, le=100, description="Max jobs to return"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[QueueStatusResponse]:
    """
    Get processing queue status overview.

    Returns queue statistics and recent jobs.

    **Query Parameters:**
    - status_filter: Filter jobs by status (pending, processing, completed, failed)
    - job_type: Filter by job type (document, youtube, gmail, etc.)
    - limit: Max jobs to return (default 20, max 100)

    **Response:**
    - stats: Queue statistics (counts by status)
    - jobs: Recent jobs matching filter
    - last_updated: Timestamp

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or "default"
    now = datetime.now(PACIFIC)

    supabase = get_supabase()

    # Get queue statistics from processing_queue table
    stats = QueueStats()

    try:
        # First try the processing_queue table
        queue_result = supabase.client.table("processing_queue").select(
            "id, content_id, priority, retry_count, status, created_at"
        ).eq("tenant_id", tenant_id).execute()

        queue_data = queue_result.data or []

        # Count by status
        for item in queue_data:
            status = item.get("status", "pending").lower()
            if status == "pending":
                stats.pending += 1
            elif status == "queued":
                stats.queued += 1
            elif status == "processing":
                stats.processing += 1
            elif status == "completed":
                stats.completed += 1
            elif status == "failed":
                stats.failed += 1
            elif status == "cancelled":
                stats.cancelled += 1

        stats.total_jobs = len(queue_data)

    except Exception:
        # Fall back to processed_content table
        try:
            content_result = supabase.client.table("processed_content").select(
                "id, processing_status, source_type, title, created_at, updated_at"
            ).eq("tenant_id", tenant_id).limit(500).execute()

            content_data = content_result.data or []

            for item in content_data:
                status = item.get("processing_status", "pending").lower()
                if status == "pending":
                    stats.pending += 1
                elif status == "processing":
                    stats.processing += 1
                elif status == "completed":
                    stats.completed += 1
                elif status == "failed":
                    stats.failed += 1

            stats.total_jobs = len(content_data)
            queue_data = content_data

        except Exception as e:
            # Return empty stats if both fail
            queue_data = []

    # Build job list
    jobs = []

    # Apply filters to queue data
    filtered_data = queue_data

    if status_filter:
        filtered_data = [
            item for item in filtered_data
            if (item.get("status") or item.get("processing_status", "")).lower() == status_filter.lower()
        ]

    if job_type:
        filtered_data = [
            item for item in filtered_data
            if (item.get("source_type") or "").lower() == job_type.lower()
        ]

    # Convert to ProcessingJob models
    for item in filtered_data[:limit]:
        jobs.append(parse_db_job(item))

    response_data = QueueStatusResponse(
        stats=stats,
        jobs=jobs,
        last_updated=now.isoformat(),
    )

    return APIResponse(
        success=True,
        data=response_data,
        meta=ResponseMeta(**meta_dict),
    )


@router.get("/jobs", response_model=APIResponse[JobListResponse])
async def list_jobs(
    request: Request,
    status: Optional[str] = Query(None, description="Filter by status"),
    job_type: Optional[str] = Query(None, description="Filter by job type"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[JobListResponse]:
    """
    List processing jobs with pagination.

    **Query Parameters:**
    - status: Filter by job status
    - job_type: Filter by job type
    - page: Page number (1-indexed)
    - page_size: Items per page (max 100)

    **Response:**
    - jobs: List of jobs
    - total: Total matching jobs
    - page: Current page
    - page_size: Page size
    - has_more: More pages available

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or "default"

    supabase = get_supabase()

    offset = (page - 1) * page_size

    try:
        # Build query
        query = supabase.client.table("processed_content").select(
            "id, title, source_type, processing_status, created_at, updated_at",
            count="exact"
        ).eq("tenant_id", tenant_id)

        if status:
            query = query.eq("processing_status", status)

        if job_type:
            query = query.eq("source_type", job_type)

        # Execute with pagination
        result = query.range(offset, offset + page_size - 1).order(
            "created_at", desc=True
        ).execute()

        total = result.count or 0
        jobs = [parse_db_job(item) for item in (result.data or [])]

    except Exception as e:
        # Return empty results on error
        jobs = []
        total = 0

    response_data = JobListResponse(
        jobs=jobs,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(offset + page_size) < total,
    )

    return APIResponse(
        success=True,
        data=response_data,
        meta=ResponseMeta(**meta_dict),
    )


@router.get("/jobs/{job_id}", response_model=APIResponse[ProcessingJob])
async def get_job_status(
    request: Request,
    job_id: str,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[ProcessingJob]:
    """
    Get status of a specific processing job.

    **Path Parameters:**
    - job_id: The job ID to query

    **Response:**
    - Full job details with progress percentage

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or "default"

    supabase = get_supabase()

    try:
        # Try processing_queue first
        result = supabase.client.table("processing_queue").select(
            "*"
        ).eq("id", job_id).eq("tenant_id", tenant_id).execute()

        if result.data:
            job = parse_db_job(result.data[0])
            return APIResponse(
                success=True,
                data=job,
                meta=ResponseMeta(**meta_dict),
            )

        # Fall back to processed_content
        result = supabase.client.table("processed_content").select(
            "*"
        ).eq("id", job_id).eq("tenant_id", tenant_id).execute()

        if result.data:
            job = parse_db_job(result.data[0])
            return APIResponse(
                success=True,
                data=job,
                meta=ResponseMeta(**meta_dict),
            )

        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job: {str(e)}")


@router.post("/jobs/{job_id}/cancel", response_model=APIResponse[CancelJobResponse])
async def cancel_job(
    request: Request,
    job_id: str,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[CancelJobResponse]:
    """
    Cancel a pending processing job.

    Only jobs with status 'pending' or 'queued' can be cancelled.
    Jobs already 'processing' cannot be cancelled.

    **Path Parameters:**
    - job_id: The job ID to cancel

    **Response:**
    - job_id: The cancelled job ID
    - success: Whether cancellation succeeded
    - message: Result message
    - previous_status: Status before cancellation

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or "default"

    supabase = get_supabase()

    try:
        # Get current job status - try processing_queue first
        result = supabase.client.table("processing_queue").select(
            "id, status"
        ).eq("id", job_id).eq("tenant_id", tenant_id).execute()

        table_name = "processing_queue"
        status_column = "status"

        if not result.data:
            # Fall back to processed_content
            result = supabase.client.table("processed_content").select(
                "id, processing_status"
            ).eq("id", job_id).eq("tenant_id", tenant_id).execute()
            table_name = "processed_content"
            status_column = "processing_status"

        if not result.data:
            raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

        current_status = result.data[0].get(status_column, "unknown")

        # Check if cancellable
        cancellable_statuses = ["pending", "queued"]

        if current_status.lower() not in cancellable_statuses:
            return APIResponse(
                success=True,
                data=CancelJobResponse(
                    job_id=job_id,
                    success=False,
                    message=f"Cannot cancel job with status '{current_status}'. Only pending or queued jobs can be cancelled.",
                    previous_status=current_status,
                ),
                meta=ResponseMeta(**meta_dict),
            )

        # Update status to cancelled
        update_result = supabase.client.table(table_name).update({
            status_column: "cancelled",
            "updated_at": datetime.now(PACIFIC).isoformat(),
        }).eq("id", job_id).execute()

        return APIResponse(
            success=True,
            data=CancelJobResponse(
                job_id=job_id,
                success=True,
                message="Job cancelled successfully",
                previous_status=current_status,
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel job: {str(e)}")


@router.post("/jobs/{job_id}/retry", response_model=APIResponse[ProcessingJob])
async def retry_job(
    request: Request,
    job_id: str,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[ProcessingJob]:
    """
    Retry a failed processing job.

    Only jobs with status 'failed' can be retried.
    Resets the job to 'pending' status and increments retry count.

    **Path Parameters:**
    - job_id: The job ID to retry

    **Response:**
    - Updated job details

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or "default"

    supabase = get_supabase()

    try:
        # Get current job
        result = supabase.client.table("processed_content").select(
            "*"
        ).eq("id", job_id).eq("tenant_id", tenant_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

        job_data = result.data[0]
        current_status = job_data.get("processing_status", "unknown")

        # Check if retriable
        if current_status.lower() != "failed":
            raise HTTPException(
                status_code=400,
                detail=f"Only failed jobs can be retried. Current status: {current_status}"
            )

        # Update to pending with incremented retry count
        current_retries = job_data.get("retry_count", 0)
        max_retries = 3

        if current_retries >= max_retries:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum retries ({max_retries}) exceeded"
            )

        update_result = supabase.client.table("processed_content").update({
            "processing_status": "pending",
            "retry_count": current_retries + 1,
            "error_message": None,
            "updated_at": datetime.now(PACIFIC).isoformat(),
        }).eq("id", job_id).execute()

        # Return updated job
        updated_data = update_result.data[0] if update_result.data else job_data
        updated_data["processing_status"] = "pending"
        updated_data["retry_count"] = current_retries + 1

        job = parse_db_job(updated_data)

        return APIResponse(
            success=True,
            data=job,
            meta=ResponseMeta(**meta_dict),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retry job: {str(e)}")


@router.get("/stats", response_model=APIResponse[QueueStats])
async def get_queue_stats(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[QueueStats]:
    """
    Get queue statistics only.

    Lightweight endpoint for quick stats display.

    **Response:**
    - Queue statistics (counts by status)

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or "default"

    supabase = get_supabase()
    stats = QueueStats()

    try:
        # Get counts from processed_content
        result = supabase.client.table("processed_content").select(
            "processing_status"
        ).eq("tenant_id", tenant_id).execute()

        for item in (result.data or []):
            status = item.get("processing_status", "pending").lower()
            if status == "pending":
                stats.pending += 1
            elif status == "processing":
                stats.processing += 1
            elif status == "completed":
                stats.completed += 1
            elif status == "failed":
                stats.failed += 1
            elif status == "cancelled":
                stats.cancelled += 1

        stats.total_jobs = len(result.data or [])

    except Exception:
        # Return zeros on error
        pass

    return APIResponse(
        success=True,
        data=stats,
        meta=ResponseMeta(**meta_dict),
    )
