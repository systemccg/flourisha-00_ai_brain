"""
Agent Execution Models

Pydantic models for Agent Execution API.
Handles agent job submission, status tracking, and log retrieval.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class AgentType(str, Enum):
    """Available agent types from PAI system."""
    GENERAL_PURPOSE = "general-purpose"
    ENGINEER = "engineer"
    ARCHITECT = "architect"
    DESIGNER = "designer"
    PENTESTER = "pentester"
    RESEARCHER = "researcher"
    PERPLEXITY_RESEARCHER = "perplexity-researcher"
    CLAUDE_RESEARCHER = "claude-researcher"
    GEMINI_RESEARCHER = "gemini-researcher"
    EXPLORE = "Explore"
    PLAN = "Plan"
    WRITER = "writer"
    ARTIST = "artist"


class AgentModel(str, Enum):
    """AI model selection for agents."""
    OPUS = "opus"
    SONNET = "sonnet"
    HAIKU = "haiku"


class AgentJobStatus(str, Enum):
    """Agent job execution status."""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class AgentJobLogEntry(BaseModel):
    """A single log entry from an agent execution."""
    timestamp: str = Field(..., description="ISO timestamp of log entry")
    level: str = Field(default="info", description="Log level (info, warn, error)")
    message: str = Field(..., description="Log message")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class AgentJobProgress(BaseModel):
    """Progress tracking for agent jobs."""
    percent: float = Field(default=0.0, ge=0, le=100, description="Progress percentage")
    current_step: Optional[str] = Field(None, description="Current step description")
    steps_completed: int = Field(default=0, description="Number of steps completed")
    steps_total: Optional[int] = Field(None, description="Total steps (if known)")


class AgentExecuteRequest(BaseModel):
    """Request to execute an agent."""
    agent_type: AgentType = Field(..., description="Type of agent to execute")
    prompt: str = Field(..., min_length=1, max_length=50000, description="Task prompt for the agent")
    model: Optional[AgentModel] = Field(None, description="Model to use (defaults based on agent type)")
    priority: int = Field(default=5, ge=1, le=10, description="Job priority 1-10 (10 = highest)")
    run_in_background: bool = Field(default=True, description="Run asynchronously in background")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context to provide to agent")
    timeout_minutes: int = Field(default=30, ge=1, le=120, description="Timeout in minutes")
    tags: List[str] = Field(default_factory=list, description="Tags for filtering/organizing jobs")
    notify_on_complete: bool = Field(default=False, description="Send voice notification on completion")

    model_config = {
        "json_schema_extra": {
            "example": {
                "agent_type": "engineer",
                "prompt": "Implement a function to calculate fibonacci numbers",
                "model": "sonnet",
                "priority": 7,
                "run_in_background": True,
                "timeout_minutes": 30,
                "notify_on_complete": True
            }
        }
    }


class AgentJob(BaseModel):
    """An agent execution job."""
    id: str = Field(..., description="Unique job ID")
    agent_type: str = Field(..., description="Type of agent executing")
    model: Optional[str] = Field(None, description="AI model used")
    prompt: str = Field(..., description="Task prompt")
    status: str = Field(..., description="Current job status")
    priority: int = Field(default=5, description="Job priority")
    progress: AgentJobProgress = Field(default_factory=AgentJobProgress, description="Progress tracking")
    result: Optional[str] = Field(None, description="Agent output when completed")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    context: Optional[Dict[str, Any]] = Field(None, description="Job context")
    tags: List[str] = Field(default_factory=list, description="Job tags")
    created_at: str = Field(..., description="Job creation timestamp")
    started_at: Optional[str] = Field(None, description="When job started executing")
    completed_at: Optional[str] = Field(None, description="When job completed")
    timeout_minutes: int = Field(default=30, description="Timeout setting")
    notify_on_complete: bool = Field(default=False, description="Voice notification setting")
    logs: List[AgentJobLogEntry] = Field(default_factory=list, description="Execution logs")


class AgentJobSummary(BaseModel):
    """Summary view of an agent job."""
    id: str = Field(..., description="Job ID")
    agent_type: str = Field(..., description="Agent type")
    status: str = Field(..., description="Status")
    progress_percent: float = Field(default=0, description="Progress percentage")
    created_at: str = Field(..., description="Creation time")
    tags: List[str] = Field(default_factory=list, description="Tags")


class AgentJobListResponse(BaseModel):
    """Response for listing agent jobs."""
    jobs: List[AgentJobSummary] = Field(..., description="List of jobs")
    total: int = Field(..., description="Total matching jobs")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")
    has_more: bool = Field(..., description="More pages available")


class AgentJobLogsResponse(BaseModel):
    """Response for job logs."""
    job_id: str = Field(..., description="Job ID")
    agent_type: str = Field(..., description="Agent type")
    status: str = Field(..., description="Current status")
    logs: List[AgentJobLogEntry] = Field(..., description="Log entries")
    total_entries: int = Field(..., description="Total log entries")


class AgentJobCancelResponse(BaseModel):
    """Response for job cancellation."""
    job_id: str = Field(..., description="Job ID")
    success: bool = Field(..., description="Whether cancellation succeeded")
    message: str = Field(..., description="Result message")
    previous_status: str = Field(..., description="Status before cancellation")


class AgentStatsResponse(BaseModel):
    """Agent execution statistics."""
    total_jobs: int = Field(default=0, description="Total jobs")
    pending: int = Field(default=0, description="Pending jobs")
    running: int = Field(default=0, description="Running jobs")
    completed: int = Field(default=0, description="Completed jobs")
    failed: int = Field(default=0, description="Failed jobs")
    cancelled: int = Field(default=0, description="Cancelled jobs")
    by_agent_type: Dict[str, int] = Field(default_factory=dict, description="Jobs by agent type")
    avg_execution_time_seconds: Optional[float] = Field(None, description="Average execution time")


class AgentTypesResponse(BaseModel):
    """Available agent types with descriptions."""
    agents: List[Dict[str, Any]] = Field(..., description="Available agents with metadata")
    total: int = Field(..., description="Total agent types")
