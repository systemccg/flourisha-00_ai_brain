"""
Memory System Models

Pydantic models for the Mem0 memory integration.
Supports user memory, session memory, and agent memory types.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    """Type of memory to store."""
    USER = "user"       # Persists across all conversations with a user
    SESSION = "session" # Tracks context within a single conversation
    AGENT = "agent"     # Stores info specific to an AI agent instance


class MemoryAddRequest(BaseModel):
    """Request to add a memory."""
    content: str = Field(
        ...,
        description="The content to remember",
        min_length=1,
        max_length=10000,
    )
    memory_type: MemoryType = Field(
        default=MemoryType.USER,
        description="Type of memory (user, session, agent)",
    )
    session_id: Optional[str] = Field(
        None,
        description="Session ID for session-type memories",
    )
    agent_id: Optional[str] = Field(
        None,
        description="Agent ID for agent-type memories",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata to store with the memory",
    )


class MemoryAddResponse(BaseModel):
    """Response after adding a memory."""
    memory_id: str = Field(..., description="Unique ID of the stored memory")
    content: str = Field(..., description="The stored content")
    memory_type: str = Field(..., description="Type of memory stored")
    user_id: str = Field(..., description="User who owns this memory")
    created_at: str = Field(..., description="When the memory was created")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Associated metadata")


class MemorySearchRequest(BaseModel):
    """Request to search memories."""
    query: str = Field(
        ...,
        description="Search query for finding relevant memories",
        min_length=1,
        max_length=1000,
    )
    memory_type: Optional[MemoryType] = Field(
        None,
        description="Filter by memory type",
    )
    session_id: Optional[str] = Field(
        None,
        description="Filter by session ID",
    )
    agent_id: Optional[str] = Field(
        None,
        description="Filter by agent ID",
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of memories to return",
    )
    threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum similarity threshold for results",
    )


class MemoryItem(BaseModel):
    """A single memory item."""
    id: str = Field(..., description="Memory ID")
    memory: str = Field(..., description="Memory content")
    score: Optional[float] = Field(None, description="Relevance score (0-1)")
    memory_type: Optional[str] = Field(None, description="Type of memory")
    user_id: Optional[str] = Field(None, description="Owner user ID")
    session_id: Optional[str] = Field(None, description="Session ID if applicable")
    agent_id: Optional[str] = Field(None, description="Agent ID if applicable")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Associated metadata")


class MemorySearchResponse(BaseModel):
    """Response from memory search."""
    memories: List[MemoryItem] = Field(..., description="Matching memories")
    query: str = Field(..., description="Original search query")
    total: int = Field(..., description="Number of results returned")


class MemoryListResponse(BaseModel):
    """Response for listing all memories."""
    memories: List[MemoryItem] = Field(..., description="List of memories")
    total: int = Field(..., description="Total number of memories")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    has_more: bool = Field(..., description="Whether more pages exist")


class MemoryUpdateRequest(BaseModel):
    """Request to update a memory."""
    content: Optional[str] = Field(
        None,
        description="New content for the memory",
        min_length=1,
        max_length=10000,
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="New metadata (replaces existing)",
    )


class MemoryDeleteResponse(BaseModel):
    """Response after deleting a memory."""
    memory_id: str = Field(..., description="ID of deleted memory")
    success: bool = Field(..., description="Whether deletion succeeded")
    message: str = Field(..., description="Result message")


class MemoryBulkAddRequest(BaseModel):
    """Request to add multiple memories at once."""
    memories: List[MemoryAddRequest] = Field(
        ...,
        description="List of memories to add",
        min_length=1,
        max_length=100,
    )


class MemoryBulkAddResponse(BaseModel):
    """Response after adding multiple memories."""
    added: int = Field(..., description="Number of memories successfully added")
    failed: int = Field(..., description="Number of memories that failed")
    memory_ids: List[str] = Field(..., description="IDs of added memories")
    errors: Optional[List[str]] = Field(None, description="Error messages for failures")


class MemoryStatsResponse(BaseModel):
    """Statistics about memory usage."""
    total_memories: int = Field(..., description="Total number of memories")
    user_memories: int = Field(default=0, description="Count of user-type memories")
    session_memories: int = Field(default=0, description="Count of session-type memories")
    agent_memories: int = Field(default=0, description="Count of agent-type memories")
    oldest_memory: Optional[str] = Field(None, description="Timestamp of oldest memory")
    newest_memory: Optional[str] = Field(None, description="Timestamp of newest memory")


class MemoryHistoryItem(BaseModel):
    """A memory history entry showing changes over time."""
    memory_id: str = Field(..., description="Memory ID")
    old_memory: Optional[str] = Field(None, description="Previous content")
    new_memory: str = Field(..., description="New content")
    action: str = Field(..., description="Action type (add, update, delete)")
    timestamp: str = Field(..., description="When the action occurred")


class MemoryHistoryResponse(BaseModel):
    """Response for memory history query."""
    memory_id: str = Field(..., description="Memory ID")
    history: List[MemoryHistoryItem] = Field(..., description="History entries")
    total: int = Field(..., description="Total history entries")
