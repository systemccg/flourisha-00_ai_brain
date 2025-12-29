"""
Cron Models

Pydantic models for cron job endpoints - internal scheduled task triggers.
These endpoints are called by pg_cron or systemd timers, not external services.
"""
from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class CronJobType(str, Enum):
    """Supported cron job types."""
    MORNING_REPORT = "morning_report"
    QUEUE_PROCESS = "queue_process"
    CLEANUP_EXPIRED = "cleanup_expired"
    SYNC_CLICKUP = "sync_clickup"
    HEALTH_CHECK = "health_check"
    DAILY_ANALYSIS = "daily_analysis"
    OKR_ROLLUP = "okr_rollup"
    EMBEDDING_REFRESH = "embedding_refresh"


class CronExecutionStatus(str, Enum):
    """Cron job execution status."""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    SKIPPED = "skipped"


class CronTriggerRequest(BaseModel):
    """Request payload for manual cron trigger.

    Used when triggering cron jobs via API instead of scheduler.
    """
    job_type: CronJobType = Field(..., description="Type of cron job to execute")
    force: bool = Field(default=False, description="Force execution even if recently run")
    params: Optional[dict] = Field(default=None, description="Optional parameters for job")


class CronExecutionResult(BaseModel):
    """Result of a cron job execution."""
    job_type: CronJobType = Field(..., description="Type of job executed")
    status: CronExecutionStatus = Field(..., description="Execution status")
    started_at: datetime = Field(..., description="Execution start time (Pacific)")
    completed_at: datetime = Field(..., description="Execution end time (Pacific)")
    duration_ms: int = Field(..., description="Execution duration in milliseconds")
    message: str = Field(..., description="Human-readable result message")
    details: Optional[dict] = Field(default=None, description="Additional execution details")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class CronJobInfo(BaseModel):
    """Information about a configured cron job."""
    job_type: CronJobType = Field(..., description="Job type")
    schedule: str = Field(..., description="Cron schedule expression")
    description: str = Field(..., description="Job description")
    enabled: bool = Field(default=True, description="Whether job is enabled")
    last_run: Optional[datetime] = Field(default=None, description="Last execution time")
    last_status: Optional[CronExecutionStatus] = Field(default=None, description="Last execution status")
    next_run: Optional[datetime] = Field(default=None, description="Next scheduled run")


class CronStatusResponse(BaseModel):
    """Response for cron status endpoint."""
    jobs: List[CronJobInfo] = Field(..., description="List of configured cron jobs")
    total_jobs: int = Field(..., description="Total number of jobs")
    enabled_jobs: int = Field(..., description="Number of enabled jobs")
    last_execution: Optional[CronExecutionResult] = Field(default=None, description="Most recent execution")


class CronLogEntry(BaseModel):
    """Log entry for cron job execution."""
    id: str = Field(..., description="Log entry ID")
    job_type: CronJobType = Field(..., description="Job type")
    status: CronExecutionStatus = Field(..., description="Execution status")
    executed_at: datetime = Field(..., description="Execution timestamp")
    duration_ms: int = Field(..., description="Duration in milliseconds")
    message: str = Field(..., description="Result message")
    error: Optional[str] = Field(default=None, description="Error if any")


class CronLogsResponse(BaseModel):
    """Response for cron logs endpoint."""
    logs: List[CronLogEntry] = Field(..., description="Execution logs")
    total: int = Field(..., description="Total log count")
    page: int = Field(default=1, description="Current page")
    page_size: int = Field(default=20, description="Items per page")
