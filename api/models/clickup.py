"""
ClickUp Integration Models

Pydantic models for ClickUp task management API.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class ClickUpTaskStatus(BaseModel):
    """ClickUp task status."""
    id: str = Field(..., description="Status ID")
    status: str = Field(..., description="Status name")
    color: Optional[str] = Field(None, description="Status color")


class ClickUpPriority(BaseModel):
    """ClickUp task priority."""
    id: str = Field(..., description="Priority ID")
    priority: str = Field(..., description="Priority level: urgent, high, normal, low")
    color: Optional[str] = Field(None, description="Priority color")


class ClickUpTask(BaseModel):
    """ClickUp task representation."""
    id: str = Field(..., description="Task ID")
    name: str = Field(..., description="Task name")
    description: Optional[str] = Field(None, description="Task description")
    status: Optional[ClickUpTaskStatus] = Field(None, description="Task status")
    priority: Optional[ClickUpPriority] = Field(None, description="Task priority")
    due_date: Optional[str] = Field(None, description="Due date timestamp")
    date_created: Optional[str] = Field(None, description="Creation timestamp")
    date_updated: Optional[str] = Field(None, description="Last update timestamp")
    list_id: Optional[str] = Field(None, description="List ID task belongs to")
    list_name: Optional[str] = Field(None, description="List name task belongs to")
    url: Optional[str] = Field(None, description="ClickUp URL to task")
    tags: List[str] = Field(default_factory=list, description="Tag names")


class ClickUpTaskCreate(BaseModel):
    """Request to create a ClickUp task."""
    name: str = Field(..., description="Task name", min_length=1)
    description: Optional[str] = Field(None, description="Task description")
    list_id: Optional[str] = Field(
        None,
        description="Target list ID. Defaults to Idea Scratchpad (901112609506)"
    )
    priority: Optional[int] = Field(
        None,
        description="Priority: 1=urgent, 2=high, 3=normal, 4=low",
        ge=1,
        le=4
    )
    due_date: Optional[str] = Field(
        None,
        description="Due date. Supports timestamps or natural language like 'tomorrow'"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Tag names to apply"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Implement new feature",
                "description": "Add dark mode support to the UI",
                "priority": 2,
                "due_date": "tomorrow",
                "tags": ["frontend", "enhancement"]
            }
        }
    }


class ClickUpTaskUpdate(BaseModel):
    """Request to update a ClickUp task."""
    name: Optional[str] = Field(None, description="New task name")
    description: Optional[str] = Field(None, description="New description")
    status: Optional[str] = Field(None, description="New status name")
    priority: Optional[int] = Field(
        None,
        description="Priority: 1=urgent, 2=high, 3=normal, 4=low",
        ge=1,
        le=4
    )
    due_date: Optional[str] = Field(
        None,
        description="Due date. Supports timestamps or natural language"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "in progress",
                "priority": 1
            }
        }
    }


class ClickUpListSummary(BaseModel):
    """ClickUp list summary."""
    id: str = Field(..., description="List ID")
    name: str = Field(..., description="List name")
    task_count: Optional[int] = Field(None, description="Number of tasks")
    space_id: Optional[str] = Field(None, description="Space ID")
    space_name: Optional[str] = Field(None, description="Space name")


class ClickUpTasksResponse(BaseModel):
    """Response with list of tasks."""
    tasks: List[ClickUpTask] = Field(..., description="List of tasks")
    total: int = Field(..., description="Total number of tasks")
    list_id: Optional[str] = Field(None, description="List ID if filtered")
    list_name: Optional[str] = Field(None, description="List name if filtered")


class ClickUpListsResponse(BaseModel):
    """Response with available lists."""
    lists: List[ClickUpListSummary] = Field(..., description="Available lists")
    total: int = Field(..., description="Total number of lists")
