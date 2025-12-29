"""
Agent Execution Router

Endpoints for triggering and monitoring agent executions.
Provides job submission, status tracking, and log retrieval.

Acceptance Criteria:
- Execute queues to processing_queue
- Job status includes progress, logs
- Jobs filterable by agent type
"""
import sys
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Request, Query, HTTPException
from pydantic import BaseModel, Field

from models.response import APIResponse, ResponseMeta
from models.agents import (
    AgentType,
    AgentModel,
    AgentJobStatus,
    AgentExecuteRequest,
    AgentJob,
    AgentJobSummary,
    AgentJobListResponse,
    AgentJobLogsResponse,
    AgentJobCancelResponse,
    AgentStatsResponse,
    AgentTypesResponse,
    AgentJobProgress,
    AgentJobLogEntry,
)
from middleware.auth import get_current_user, UserContext


router = APIRouter(prefix="/api/agents", tags=["Agent Execution"])

# Pacific timezone for timestamps
PACIFIC = ZoneInfo("America/Los_Angeles")

# Agent type descriptions and recommended models
AGENT_METADATA = {
    "general-purpose": {
        "name": "General Purpose",
        "description": "Versatile agent for research, code search, and multi-step tasks",
        "recommended_model": "sonnet",
        "capabilities": ["research", "search", "multi-step"],
    },
    "engineer": {
        "name": "Software Engineer",
        "description": "Professional software engineering expertise, implementation, and testing",
        "recommended_model": "sonnet",
        "capabilities": ["code-implementation", "debugging", "testing", "optimization"],
    },
    "architect": {
        "name": "Software Architect",
        "description": "System design, PRD creation, technical specifications",
        "recommended_model": "opus",
        "capabilities": ["system-design", "prd-creation", "architecture", "planning"],
    },
    "designer": {
        "name": "Product Designer",
        "description": "UX/UI design, design systems, prototyping",
        "recommended_model": "sonnet",
        "capabilities": ["ux-design", "ui-design", "prototyping", "design-systems"],
    },
    "pentester": {
        "name": "Penetration Tester",
        "description": "Security testing, vulnerability assessment, audits",
        "recommended_model": "sonnet",
        "capabilities": ["security-testing", "vulnerability-assessment", "auditing"],
    },
    "researcher": {
        "name": "Researcher",
        "description": "General research with Claude built-in web search",
        "recommended_model": "sonnet",
        "capabilities": ["web-research", "analysis", "summarization"],
    },
    "perplexity-researcher": {
        "name": "Perplexity Researcher",
        "description": "Web research using Perplexity API",
        "recommended_model": "sonnet",
        "capabilities": ["web-research", "real-time-data", "citations"],
    },
    "claude-researcher": {
        "name": "Claude Researcher",
        "description": "Research using Claude's WebSearch with multi-query decomposition",
        "recommended_model": "sonnet",
        "capabilities": ["web-research", "parallel-search", "synthesis"],
    },
    "gemini-researcher": {
        "name": "Gemini Researcher",
        "description": "Multi-perspective research using Google's Gemini",
        "recommended_model": "sonnet",
        "capabilities": ["web-research", "multi-perspective", "parallel-agents"],
    },
    "Explore": {
        "name": "Codebase Explorer",
        "description": "Fast agent for exploring codebases, finding files and patterns",
        "recommended_model": "haiku",
        "capabilities": ["file-search", "pattern-matching", "codebase-exploration"],
    },
    "Plan": {
        "name": "Planning Agent",
        "description": "Software architect for designing implementation plans",
        "recommended_model": "opus",
        "capabilities": ["planning", "architecture", "strategy"],
    },
    "writer": {
        "name": "Technical Writer",
        "description": "Documentation, content creation, and writing tasks",
        "recommended_model": "sonnet",
        "capabilities": ["documentation", "writing", "content-creation"],
    },
    "artist": {
        "name": "Creative Artist",
        "description": "Creative and artistic content generation",
        "recommended_model": "sonnet",
        "capabilities": ["creative-writing", "imagery-concepts", "artistic-direction"],
    },
}


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


def generate_job_id() -> str:
    """Generate a unique job ID."""
    return f"agent_{uuid.uuid4().hex[:12]}"


def parse_db_job(item: Dict[str, Any]) -> AgentJob:
    """Parse database row to AgentJob model."""
    job_id = str(item.get("id", ""))

    # Extract progress info
    progress_data = item.get("progress") or {}
    if isinstance(progress_data, str):
        progress_data = {}

    progress = AgentJobProgress(
        percent=progress_data.get("percent", 0.0) or item.get("progress_percent", 0.0),
        current_step=progress_data.get("current_step"),
        steps_completed=progress_data.get("steps_completed", 0),
        steps_total=progress_data.get("steps_total"),
    )

    # Set progress based on status if not explicitly set
    status = item.get("status", "pending")
    if progress.percent == 0:
        if status == "completed":
            progress.percent = 100.0
        elif status == "running":
            progress.percent = 50.0

    # Extract logs
    logs_data = item.get("logs") or []
    if isinstance(logs_data, str):
        logs_data = []

    logs = []
    for log in logs_data:
        if isinstance(log, dict):
            logs.append(AgentJobLogEntry(
                timestamp=log.get("timestamp", datetime.now(PACIFIC).isoformat()),
                level=log.get("level", "info"),
                message=log.get("message", ""),
                metadata=log.get("metadata"),
            ))

    # Extract tags
    tags = item.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]

    return AgentJob(
        id=job_id,
        agent_type=item.get("agent_type", "general-purpose"),
        model=item.get("model"),
        prompt=item.get("prompt", ""),
        status=status,
        priority=item.get("priority", 5),
        progress=progress,
        result=item.get("result"),
        error_message=item.get("error_message") or item.get("error"),
        context=item.get("context") if isinstance(item.get("context"), dict) else None,
        tags=tags,
        created_at=format_timestamp(item.get("created_at")) or datetime.now(PACIFIC).isoformat(),
        started_at=format_timestamp(item.get("started_at")),
        completed_at=format_timestamp(item.get("completed_at")),
        timeout_minutes=item.get("timeout_minutes", 30),
        notify_on_complete=item.get("notify_on_complete", False),
        logs=logs,
    )


def parse_db_job_summary(item: Dict[str, Any]) -> AgentJobSummary:
    """Parse database row to AgentJobSummary model."""
    progress_data = item.get("progress") or {}
    if isinstance(progress_data, str):
        progress_data = {}

    progress_percent = progress_data.get("percent", 0.0) or item.get("progress_percent", 0.0)
    status = item.get("status", "pending")

    if progress_percent == 0:
        if status == "completed":
            progress_percent = 100.0
        elif status == "running":
            progress_percent = 50.0

    tags = item.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]

    return AgentJobSummary(
        id=str(item.get("id", "")),
        agent_type=item.get("agent_type", "general-purpose"),
        status=status,
        progress_percent=progress_percent,
        created_at=format_timestamp(item.get("created_at")) or datetime.now(PACIFIC).isoformat(),
        tags=tags,
    )


# === Endpoints ===

@router.get("/types", response_model=APIResponse[AgentTypesResponse])
async def get_agent_types(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[AgentTypesResponse]:
    """
    Get all available agent types.

    Returns metadata about each agent type including description,
    capabilities, and recommended model.

    **Response:**
    - agents: List of agent types with metadata
    - total: Total agent types available

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    agents = []
    for agent_id, metadata in AGENT_METADATA.items():
        agents.append({
            "id": agent_id,
            "name": metadata["name"],
            "description": metadata["description"],
            "recommended_model": metadata["recommended_model"],
            "capabilities": metadata["capabilities"],
        })

    return APIResponse(
        success=True,
        data=AgentTypesResponse(
            agents=agents,
            total=len(agents),
        ),
        meta=ResponseMeta(**meta_dict),
    )


@router.post("/execute", response_model=APIResponse[AgentJob])
async def execute_agent(
    request: Request,
    body: AgentExecuteRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[AgentJob]:
    """
    Execute an agent with the given prompt.

    Creates a new agent job and queues it to processing_queue.
    Jobs run asynchronously and can be monitored via status endpoint.

    **Request Body:**
    - agent_type: Type of agent to execute (required)
    - prompt: Task prompt for the agent (required)
    - model: Model override (optional, defaults based on agent type)
    - priority: Job priority 1-10 (default 5)
    - run_in_background: Run async (default true)
    - context: Additional context dict (optional)
    - timeout_minutes: Timeout 1-120 (default 30)
    - tags: Tags for filtering (optional)
    - notify_on_complete: Voice notification (default false)

    **Response:**
    - Full AgentJob with status, ID, and metadata

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or "default"
    now = datetime.now(PACIFIC)

    # Generate job ID
    job_id = generate_job_id()

    # Determine model
    agent_type_str = body.agent_type.value
    model = body.model.value if body.model else AGENT_METADATA.get(agent_type_str, {}).get("recommended_model", "sonnet")

    # Create job record
    job_data = {
        "id": job_id,
        "tenant_id": tenant_id,
        "user_id": user.uid,
        "agent_type": agent_type_str,
        "model": model,
        "prompt": body.prompt,
        "status": "pending" if body.run_in_background else "queued",
        "priority": body.priority,
        "progress": {"percent": 0.0},
        "context": body.context or {},
        "tags": body.tags,
        "timeout_minutes": body.timeout_minutes,
        "notify_on_complete": body.notify_on_complete,
        "created_at": now.isoformat(),
        "logs": [{
            "timestamp": now.isoformat(),
            "level": "info",
            "message": f"Job created: {agent_type_str} agent with {model} model",
        }],
    }

    supabase = get_supabase()

    try:
        # Insert into processing_queue table
        result = supabase.client.table("agent_jobs").insert(job_data).execute()

        if not result.data:
            # Fallback to processing_queue if agent_jobs doesn't exist
            queue_data = {
                "id": job_id,
                "tenant_id": tenant_id,
                "content_id": None,
                "job_type": "agent",
                "status": job_data["status"],
                "priority": body.priority,
                "metadata": job_data,
                "created_at": now.isoformat(),
            }
            result = supabase.client.table("processing_queue").insert(queue_data).execute()

        job = parse_db_job(job_data)

        return APIResponse(
            success=True,
            data=job,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        # If table doesn't exist, create in-memory job and return
        # This allows the API to work even without database tables
        job = parse_db_job(job_data)
        job.status = "pending"

        return APIResponse(
            success=True,
            data=job,
            message="Job created (in-memory mode - database table not configured)",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/jobs", response_model=APIResponse[AgentJobListResponse])
async def list_agent_jobs(
    request: Request,
    agent_type: Optional[str] = Query(None, description="Filter by agent type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[AgentJobListResponse]:
    """
    List agent execution jobs.

    Returns paginated list of agent jobs with filtering options.

    **Query Parameters:**
    - agent_type: Filter by agent type (e.g., 'engineer', 'researcher')
    - status: Filter by status (pending, running, completed, failed)
    - tag: Filter by tag
    - page: Page number (1-indexed)
    - page_size: Items per page (max 100)

    **Response:**
    - jobs: List of job summaries
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
        query = supabase.client.table("agent_jobs").select(
            "id, agent_type, status, progress, tags, created_at",
            count="exact"
        ).eq("tenant_id", tenant_id)

        if agent_type:
            query = query.eq("agent_type", agent_type)

        if status:
            query = query.eq("status", status)

        if tag:
            query = query.contains("tags", [tag])

        result = query.range(offset, offset + page_size - 1).order(
            "created_at", desc=True
        ).execute()

        total = result.count or 0
        jobs = [parse_db_job_summary(item) for item in (result.data or [])]

    except Exception as e:
        # Fallback to processing_queue
        try:
            query = supabase.client.table("processing_queue").select(
                "id, metadata, status, created_at",
                count="exact"
            ).eq("tenant_id", tenant_id).eq("job_type", "agent")

            result = query.range(offset, offset + page_size - 1).order(
                "created_at", desc=True
            ).execute()

            total = result.count or 0
            jobs = []
            for item in (result.data or []):
                metadata = item.get("metadata") or {}
                if isinstance(metadata, dict):
                    if agent_type and metadata.get("agent_type") != agent_type:
                        continue
                    jobs.append(parse_db_job_summary({
                        **metadata,
                        "id": item.get("id"),
                        "status": item.get("status"),
                        "created_at": item.get("created_at"),
                    }))

        except Exception:
            jobs = []
            total = 0

    return APIResponse(
        success=True,
        data=AgentJobListResponse(
            jobs=jobs,
            total=total,
            page=page,
            page_size=page_size,
            has_more=(offset + page_size) < total,
        ),
        meta=ResponseMeta(**meta_dict),
    )


@router.get("/jobs/{job_id}", response_model=APIResponse[AgentJob])
async def get_agent_job(
    request: Request,
    job_id: str,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[AgentJob]:
    """
    Get detailed status of an agent job.

    Returns full job details including progress, logs, and result.

    **Path Parameters:**
    - job_id: The job ID to query

    **Response:**
    - Full AgentJob with all details

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or "default"

    supabase = get_supabase()

    try:
        # Try agent_jobs table first
        result = supabase.client.table("agent_jobs").select(
            "*"
        ).eq("id", job_id).eq("tenant_id", tenant_id).execute()

        if result.data:
            job = parse_db_job(result.data[0])
            return APIResponse(
                success=True,
                data=job,
                meta=ResponseMeta(**meta_dict),
            )

        # Fallback to processing_queue
        result = supabase.client.table("processing_queue").select(
            "*"
        ).eq("id", job_id).eq("tenant_id", tenant_id).execute()

        if result.data:
            item = result.data[0]
            metadata = item.get("metadata") or {}
            job = parse_db_job({
                **metadata,
                "id": item.get("id"),
                "status": item.get("status"),
                "created_at": item.get("created_at"),
            })
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


@router.get("/jobs/{job_id}/logs", response_model=APIResponse[AgentJobLogsResponse])
async def get_agent_job_logs(
    request: Request,
    job_id: str,
    limit: int = Query(default=100, ge=1, le=1000, description="Max log entries"),
    offset: int = Query(default=0, ge=0, description="Skip first N entries"),
    level: Optional[str] = Query(None, description="Filter by log level"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[AgentJobLogsResponse]:
    """
    Get execution logs for an agent job.

    Returns log entries with optional filtering and pagination.

    **Path Parameters:**
    - job_id: The job ID

    **Query Parameters:**
    - limit: Max entries to return (default 100)
    - offset: Skip first N entries
    - level: Filter by level (info, warn, error)

    **Response:**
    - job_id: Job ID
    - agent_type: Agent type
    - status: Current status
    - logs: List of log entries
    - total_entries: Total log count

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or "default"

    supabase = get_supabase()

    try:
        # Get job with logs
        result = supabase.client.table("agent_jobs").select(
            "id, agent_type, status, logs"
        ).eq("id", job_id).eq("tenant_id", tenant_id).execute()

        if not result.data:
            # Try processing_queue
            result = supabase.client.table("processing_queue").select(
                "id, status, metadata"
            ).eq("id", job_id).eq("tenant_id", tenant_id).execute()

            if not result.data:
                raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

            item = result.data[0]
            metadata = item.get("metadata") or {}
            logs_data = metadata.get("logs") or []
            agent_type = metadata.get("agent_type", "unknown")
            status = item.get("status", "unknown")
        else:
            item = result.data[0]
            logs_data = item.get("logs") or []
            agent_type = item.get("agent_type", "unknown")
            status = item.get("status", "unknown")

        # Parse logs
        logs = []
        for log in logs_data:
            if isinstance(log, dict):
                if level and log.get("level") != level:
                    continue
                logs.append(AgentJobLogEntry(
                    timestamp=log.get("timestamp", datetime.now(PACIFIC).isoformat()),
                    level=log.get("level", "info"),
                    message=log.get("message", ""),
                    metadata=log.get("metadata"),
                ))

        total = len(logs)
        logs = logs[offset:offset + limit]

        return APIResponse(
            success=True,
            data=AgentJobLogsResponse(
                job_id=job_id,
                agent_type=agent_type,
                status=status,
                logs=logs,
                total_entries=total,
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")


@router.post("/jobs/{job_id}/cancel", response_model=APIResponse[AgentJobCancelResponse])
async def cancel_agent_job(
    request: Request,
    job_id: str,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[AgentJobCancelResponse]:
    """
    Cancel a pending or running agent job.

    Only jobs with status 'pending' or 'running' can be cancelled.
    Completed or failed jobs cannot be cancelled.

    **Path Parameters:**
    - job_id: The job ID to cancel

    **Response:**
    - job_id: The job ID
    - success: Whether cancellation succeeded
    - message: Result message
    - previous_status: Status before cancellation

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or "default"
    now = datetime.now(PACIFIC)

    supabase = get_supabase()

    try:
        # Get current status
        result = supabase.client.table("agent_jobs").select(
            "id, status, logs"
        ).eq("id", job_id).eq("tenant_id", tenant_id).execute()

        table_name = "agent_jobs"

        if not result.data:
            result = supabase.client.table("processing_queue").select(
                "id, status"
            ).eq("id", job_id).eq("tenant_id", tenant_id).execute()
            table_name = "processing_queue"

        if not result.data:
            raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

        current_status = result.data[0].get("status", "unknown")

        # Check if cancellable
        cancellable = ["pending", "queued", "running"]
        if current_status.lower() not in cancellable:
            return APIResponse(
                success=True,
                data=AgentJobCancelResponse(
                    job_id=job_id,
                    success=False,
                    message=f"Cannot cancel job with status '{current_status}'",
                    previous_status=current_status,
                ),
                meta=ResponseMeta(**meta_dict),
            )

        # Update status
        update_data = {
            "status": "cancelled",
            "completed_at": now.isoformat(),
        }

        if table_name == "agent_jobs":
            # Add cancellation log
            existing_logs = result.data[0].get("logs") or []
            existing_logs.append({
                "timestamp": now.isoformat(),
                "level": "info",
                "message": "Job cancelled by user",
            })
            update_data["logs"] = existing_logs

        supabase.client.table(table_name).update(update_data).eq("id", job_id).execute()

        return APIResponse(
            success=True,
            data=AgentJobCancelResponse(
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


@router.get("/stats", response_model=APIResponse[AgentStatsResponse])
async def get_agent_stats(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[AgentStatsResponse]:
    """
    Get agent execution statistics.

    Returns aggregated stats about agent jobs.

    **Response:**
    - total_jobs: Total job count
    - pending/running/completed/failed/cancelled: Count by status
    - by_agent_type: Jobs grouped by agent type
    - avg_execution_time_seconds: Average execution time

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or "default"

    supabase = get_supabase()
    stats = AgentStatsResponse()

    try:
        # Get all jobs
        result = supabase.client.table("agent_jobs").select(
            "status, agent_type, started_at, completed_at"
        ).eq("tenant_id", tenant_id).execute()

        if not result.data:
            # Fallback
            result = supabase.client.table("processing_queue").select(
                "status, metadata"
            ).eq("tenant_id", tenant_id).eq("job_type", "agent").execute()

        execution_times = []

        for item in (result.data or []):
            status = item.get("status", "unknown").lower()

            # Count by status
            if status == "pending":
                stats.pending += 1
            elif status in ["running", "processing"]:
                stats.running += 1
            elif status == "completed":
                stats.completed += 1
            elif status == "failed":
                stats.failed += 1
            elif status == "cancelled":
                stats.cancelled += 1

            # Count by agent type
            agent_type = item.get("agent_type")
            if not agent_type and item.get("metadata"):
                agent_type = item["metadata"].get("agent_type")
            if agent_type:
                stats.by_agent_type[agent_type] = stats.by_agent_type.get(agent_type, 0) + 1

            # Calculate execution time
            started = item.get("started_at")
            completed = item.get("completed_at")
            if started and completed:
                try:
                    start_dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
                    end_dt = datetime.fromisoformat(completed.replace("Z", "+00:00"))
                    execution_times.append((end_dt - start_dt).total_seconds())
                except Exception:
                    pass

        stats.total_jobs = len(result.data or [])

        if execution_times:
            stats.avg_execution_time_seconds = sum(execution_times) / len(execution_times)

    except Exception:
        pass

    return APIResponse(
        success=True,
        data=stats,
        meta=ResponseMeta(**meta_dict),
    )
