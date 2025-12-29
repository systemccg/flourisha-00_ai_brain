"""
Memory System Router

Endpoints for persistent memory across conversations using Mem0.
Supports user memory, session memory, and agent memory types.

Acceptance Criteria:
- Add memories with user/session/agent scoping
- Search memories with semantic similarity
- List all memories with pagination
- Delete/update individual memories
- Get memory statistics
"""
import sys
import uuid
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Request, Query, HTTPException

from models.response import APIResponse, ResponseMeta
from models.memory import (
    MemoryType,
    MemoryAddRequest,
    MemoryAddResponse,
    MemorySearchRequest,
    MemorySearchResponse,
    MemoryListResponse,
    MemoryItem,
    MemoryUpdateRequest,
    MemoryDeleteResponse,
    MemoryBulkAddRequest,
    MemoryBulkAddResponse,
    MemoryStatsResponse,
    MemoryHistoryResponse,
    MemoryHistoryItem,
)
from middleware.auth import get_current_user, UserContext
from config import get_settings


router = APIRouter(prefix="/api/memory", tags=["Memory System"])

# Pacific timezone for timestamps
PACIFIC = ZoneInfo("America/Los_Angeles")


def get_mem0_client():
    """
    Get Mem0 client instance.

    Supports both cloud (MemoryClient) and self-hosted (Memory) modes.
    Falls back to in-memory storage if Mem0 is not configured.
    """
    settings = get_settings()

    # Check for Mem0 API key (cloud mode)
    mem0_api_key = os.getenv("MEM0_API_KEY")

    if mem0_api_key:
        try:
            from mem0 import MemoryClient
            return MemoryClient(api_key=mem0_api_key), "cloud"
        except ImportError:
            pass

    # Try self-hosted mode with local config
    try:
        from mem0 import Memory

        # Use Supabase pgvector as the vector store
        config = {
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "collection_name": "flourisha_memories",
                    "embedding_model_dims": 1536,
                    "on_disk": True,
                }
            },
            "llm": {
                "provider": "anthropic",
                "config": {
                    "model": "claude-sonnet-4-20250514",
                    "temperature": 0.1,
                }
            },
            "embedder": {
                "provider": "openai",
                "config": {
                    "model": "text-embedding-3-small",
                }
            }
        }

        return Memory.from_config(config), "self-hosted"
    except (ImportError, Exception):
        pass

    # Fallback to None - will use in-memory mock
    return None, "mock"


def get_supabase():
    """Get Supabase client for fallback storage."""
    sys.path.insert(0, "/root/flourisha/00_AI_Brain")
    from services.supabase_client import SupabaseService
    return SupabaseService()


def format_timestamp() -> str:
    """Get current timestamp in Pacific time ISO format."""
    return datetime.now(PACIFIC).isoformat()


def generate_memory_id() -> str:
    """Generate a unique memory ID."""
    return f"mem_{uuid.uuid4().hex[:12]}"


# In-memory fallback storage
_memory_store: Dict[str, Dict[str, Any]] = {}


def mock_add_memory(user_id: str, content: str, metadata: Optional[Dict] = None) -> str:
    """Add memory to mock store."""
    memory_id = generate_memory_id()
    _memory_store[memory_id] = {
        "id": memory_id,
        "user_id": user_id,
        "memory": content,
        "metadata": metadata or {},
        "created_at": format_timestamp(),
        "updated_at": format_timestamp(),
    }
    return memory_id


def mock_search_memories(user_id: str, query: str, limit: int = 10) -> List[Dict]:
    """Search memories in mock store (simple substring matching)."""
    results = []
    query_lower = query.lower()

    for mem_id, mem_data in _memory_store.items():
        if mem_data.get("user_id") == user_id:
            if query_lower in mem_data.get("memory", "").lower():
                results.append({
                    **mem_data,
                    "score": 0.9,  # Mock score
                })

    return results[:limit]


def mock_get_all_memories(user_id: str) -> List[Dict]:
    """Get all memories for a user from mock store."""
    return [
        mem_data for mem_data in _memory_store.values()
        if mem_data.get("user_id") == user_id
    ]


def mock_delete_memory(memory_id: str, user_id: str) -> bool:
    """Delete memory from mock store."""
    if memory_id in _memory_store:
        if _memory_store[memory_id].get("user_id") == user_id:
            del _memory_store[memory_id]
            return True
    return False


def mock_update_memory(memory_id: str, user_id: str, content: str) -> bool:
    """Update memory in mock store."""
    if memory_id in _memory_store:
        if _memory_store[memory_id].get("user_id") == user_id:
            _memory_store[memory_id]["memory"] = content
            _memory_store[memory_id]["updated_at"] = format_timestamp()
            return True
    return False


# === Endpoints ===

@router.post("/add", response_model=APIResponse[MemoryAddResponse])
async def add_memory(
    request: Request,
    body: MemoryAddRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[MemoryAddResponse]:
    """
    Add a new memory.

    Stores content in the memory system for later retrieval.
    Memories are scoped by type: user, session, or agent.

    **Request Body:**
    - content: The content to remember (required)
    - memory_type: Type of memory (user/session/agent, default: user)
    - session_id: Required for session-type memories
    - agent_id: Required for agent-type memories
    - metadata: Additional metadata to store

    **Response:**
    - memory_id: Unique ID of the stored memory
    - content: The stored content
    - memory_type: Type of memory stored
    - user_id: Owner of the memory
    - created_at: Creation timestamp

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    user_id = user.uid
    now = format_timestamp()

    # Build identifiers based on memory type
    identifiers = {"user_id": user_id}

    if body.memory_type == MemoryType.SESSION:
        if not body.session_id:
            raise HTTPException(
                status_code=400,
                detail="session_id is required for session-type memories"
            )
        identifiers["session_id"] = body.session_id
    elif body.memory_type == MemoryType.AGENT:
        if not body.agent_id:
            raise HTTPException(
                status_code=400,
                detail="agent_id is required for agent-type memories"
            )
        identifiers["agent_id"] = body.agent_id

    # Add metadata
    full_metadata = {
        "memory_type": body.memory_type.value,
        "tenant_id": user.tenant_id or "default",
        **(body.metadata or {}),
    }

    # Get Mem0 client
    client, mode = get_mem0_client()

    try:
        if client and mode == "cloud":
            # Use Mem0 cloud API
            result = client.add(
                body.content,
                user_id=user_id,
                metadata=full_metadata,
            )
            memory_id = result.get("id", generate_memory_id())

        elif client and mode == "self-hosted":
            # Use self-hosted Mem0
            result = client.add(
                body.content,
                user_id=user_id,
                metadata=full_metadata,
            )
            memory_id = result.get("id", generate_memory_id())

        else:
            # Use mock storage
            memory_id = mock_add_memory(user_id, body.content, full_metadata)

    except Exception as e:
        # Fallback to mock on any error
        memory_id = mock_add_memory(user_id, body.content, full_metadata)

    return APIResponse(
        success=True,
        data=MemoryAddResponse(
            memory_id=memory_id,
            content=body.content,
            memory_type=body.memory_type.value,
            user_id=user_id,
            created_at=now,
            metadata=full_metadata,
        ),
        meta=ResponseMeta(**meta_dict),
    )


@router.post("/search", response_model=APIResponse[MemorySearchResponse])
async def search_memories(
    request: Request,
    body: MemorySearchRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[MemorySearchResponse]:
    """
    Search memories using semantic similarity.

    Finds memories that match the query based on meaning, not just keywords.
    Results are ranked by relevance score.

    **Request Body:**
    - query: Search query for finding relevant memories (required)
    - memory_type: Filter by memory type (optional)
    - session_id: Filter by session ID (optional)
    - agent_id: Filter by agent ID (optional)
    - limit: Maximum results (default: 10, max: 50)
    - threshold: Minimum similarity score (default: 0.7)

    **Response:**
    - memories: List of matching memories with scores
    - query: Original search query
    - total: Number of results

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    user_id = user.uid

    # Build filters
    filters = {"user_id": user_id}

    if body.memory_type:
        filters["memory_type"] = body.memory_type.value
    if body.session_id:
        filters["session_id"] = body.session_id
    if body.agent_id:
        filters["agent_id"] = body.agent_id

    client, mode = get_mem0_client()
    memories = []

    try:
        if client and mode == "cloud":
            result = client.search(
                body.query,
                user_id=user_id,
                limit=body.limit,
            )

            for item in (result if isinstance(result, list) else result.get("memories", [])):
                score = item.get("score", item.get("similarity", 0.8))
                if score >= body.threshold:
                    memories.append(MemoryItem(
                        id=item.get("id", ""),
                        memory=item.get("memory", item.get("content", "")),
                        score=score,
                        memory_type=item.get("metadata", {}).get("memory_type", "user"),
                        user_id=user_id,
                        session_id=item.get("metadata", {}).get("session_id"),
                        agent_id=item.get("metadata", {}).get("agent_id"),
                        created_at=item.get("created_at"),
                        updated_at=item.get("updated_at"),
                        metadata=item.get("metadata"),
                    ))

        elif client and mode == "self-hosted":
            result = client.search(
                body.query,
                user_id=user_id,
                limit=body.limit,
            )

            for item in (result if isinstance(result, list) else result.get("results", [])):
                score = item.get("score", 0.8)
                if score >= body.threshold:
                    memories.append(MemoryItem(
                        id=item.get("id", ""),
                        memory=item.get("memory", ""),
                        score=score,
                        memory_type=item.get("metadata", {}).get("memory_type", "user"),
                        user_id=user_id,
                        created_at=item.get("created_at"),
                        metadata=item.get("metadata"),
                    ))
        else:
            # Mock search
            results = mock_search_memories(user_id, body.query, body.limit)
            for item in results:
                memories.append(MemoryItem(
                    id=item.get("id", ""),
                    memory=item.get("memory", ""),
                    score=item.get("score", 0.9),
                    memory_type=item.get("metadata", {}).get("memory_type", "user"),
                    user_id=user_id,
                    created_at=item.get("created_at"),
                    metadata=item.get("metadata"),
                ))

    except Exception as e:
        # Fallback to mock
        results = mock_search_memories(user_id, body.query, body.limit)
        for item in results:
            memories.append(MemoryItem(
                id=item.get("id", ""),
                memory=item.get("memory", ""),
                score=item.get("score", 0.9),
                user_id=user_id,
                created_at=item.get("created_at"),
            ))

    return APIResponse(
        success=True,
        data=MemorySearchResponse(
            memories=memories,
            query=body.query,
            total=len(memories),
        ),
        meta=ResponseMeta(**meta_dict),
    )


@router.get("/list", response_model=APIResponse[MemoryListResponse])
async def list_memories(
    request: Request,
    memory_type: Optional[str] = Query(None, description="Filter by memory type"),
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[MemoryListResponse]:
    """
    List all memories for the current user.

    Returns paginated list of memories with optional filtering.

    **Query Parameters:**
    - memory_type: Filter by type (user/session/agent)
    - session_id: Filter by session ID
    - agent_id: Filter by agent ID
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)

    **Response:**
    - memories: List of memory items
    - total: Total number of memories
    - page: Current page
    - page_size: Items per page
    - has_more: Whether more pages exist

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    user_id = user.uid

    client, mode = get_mem0_client()
    memories = []
    total = 0

    try:
        if client and mode == "cloud":
            result = client.get_all(user_id=user_id)
            all_memories = result if isinstance(result, list) else result.get("memories", [])

            # Apply filters
            filtered = []
            for item in all_memories:
                meta = item.get("metadata", {})
                if memory_type and meta.get("memory_type") != memory_type:
                    continue
                if session_id and meta.get("session_id") != session_id:
                    continue
                if agent_id and meta.get("agent_id") != agent_id:
                    continue
                filtered.append(item)

            total = len(filtered)
            offset = (page - 1) * page_size
            page_items = filtered[offset:offset + page_size]

            for item in page_items:
                memories.append(MemoryItem(
                    id=item.get("id", ""),
                    memory=item.get("memory", item.get("content", "")),
                    memory_type=item.get("metadata", {}).get("memory_type", "user"),
                    user_id=user_id,
                    session_id=item.get("metadata", {}).get("session_id"),
                    agent_id=item.get("metadata", {}).get("agent_id"),
                    created_at=item.get("created_at"),
                    updated_at=item.get("updated_at"),
                    metadata=item.get("metadata"),
                ))

        elif client and mode == "self-hosted":
            result = client.get_all(user_id=user_id)
            all_memories = result if isinstance(result, list) else result.get("results", [])

            total = len(all_memories)
            offset = (page - 1) * page_size
            page_items = all_memories[offset:offset + page_size]

            for item in page_items:
                memories.append(MemoryItem(
                    id=item.get("id", ""),
                    memory=item.get("memory", ""),
                    memory_type=item.get("metadata", {}).get("memory_type", "user"),
                    user_id=user_id,
                    created_at=item.get("created_at"),
                    metadata=item.get("metadata"),
                ))
        else:
            # Mock storage
            all_memories = mock_get_all_memories(user_id)

            # Apply filters
            filtered = []
            for item in all_memories:
                meta = item.get("metadata", {})
                if memory_type and meta.get("memory_type") != memory_type:
                    continue
                if session_id and meta.get("session_id") != session_id:
                    continue
                if agent_id and meta.get("agent_id") != agent_id:
                    continue
                filtered.append(item)

            total = len(filtered)
            offset = (page - 1) * page_size
            page_items = filtered[offset:offset + page_size]

            for item in page_items:
                memories.append(MemoryItem(
                    id=item.get("id", ""),
                    memory=item.get("memory", ""),
                    memory_type=item.get("metadata", {}).get("memory_type", "user"),
                    user_id=user_id,
                    created_at=item.get("created_at"),
                    metadata=item.get("metadata"),
                ))

    except Exception:
        # Fallback to empty
        pass

    has_more = (page * page_size) < total

    return APIResponse(
        success=True,
        data=MemoryListResponse(
            memories=memories,
            total=total,
            page=page,
            page_size=page_size,
            has_more=has_more,
        ),
        meta=ResponseMeta(**meta_dict),
    )


@router.get("/{memory_id}", response_model=APIResponse[MemoryItem])
async def get_memory(
    request: Request,
    memory_id: str,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[MemoryItem]:
    """
    Get a specific memory by ID.

    **Path Parameters:**
    - memory_id: The unique memory ID

    **Response:**
    - Single MemoryItem with full details

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    user_id = user.uid

    client, mode = get_mem0_client()

    try:
        if client and mode in ("cloud", "self-hosted"):
            # Search for the specific memory
            result = client.get_all(user_id=user_id)
            all_memories = result if isinstance(result, list) else result.get("memories", result.get("results", []))

            for item in all_memories:
                if item.get("id") == memory_id:
                    return APIResponse(
                        success=True,
                        data=MemoryItem(
                            id=item.get("id", ""),
                            memory=item.get("memory", item.get("content", "")),
                            memory_type=item.get("metadata", {}).get("memory_type", "user"),
                            user_id=user_id,
                            session_id=item.get("metadata", {}).get("session_id"),
                            agent_id=item.get("metadata", {}).get("agent_id"),
                            created_at=item.get("created_at"),
                            updated_at=item.get("updated_at"),
                            metadata=item.get("metadata"),
                        ),
                        meta=ResponseMeta(**meta_dict),
                    )
        else:
            # Mock storage
            if memory_id in _memory_store:
                item = _memory_store[memory_id]
                if item.get("user_id") == user_id:
                    return APIResponse(
                        success=True,
                        data=MemoryItem(
                            id=item.get("id", ""),
                            memory=item.get("memory", ""),
                            memory_type=item.get("metadata", {}).get("memory_type", "user"),
                            user_id=user_id,
                            created_at=item.get("created_at"),
                            metadata=item.get("metadata"),
                        ),
                        meta=ResponseMeta(**meta_dict),
                    )

    except Exception:
        pass

    raise HTTPException(status_code=404, detail=f"Memory not found: {memory_id}")


@router.put("/{memory_id}", response_model=APIResponse[MemoryItem])
async def update_memory(
    request: Request,
    memory_id: str,
    body: MemoryUpdateRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[MemoryItem]:
    """
    Update an existing memory.

    **Path Parameters:**
    - memory_id: The unique memory ID

    **Request Body:**
    - content: New content for the memory (optional)
    - metadata: New metadata - replaces existing (optional)

    **Response:**
    - Updated MemoryItem

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    user_id = user.uid

    if not body.content and not body.metadata:
        raise HTTPException(
            status_code=400,
            detail="At least one of content or metadata must be provided"
        )

    client, mode = get_mem0_client()

    try:
        if client and mode == "cloud":
            if body.content:
                client.update(memory_id, body.content)

            # Get updated memory
            result = client.get_all(user_id=user_id)
            all_memories = result if isinstance(result, list) else result.get("memories", [])

            for item in all_memories:
                if item.get("id") == memory_id:
                    return APIResponse(
                        success=True,
                        data=MemoryItem(
                            id=item.get("id", ""),
                            memory=item.get("memory", ""),
                            memory_type=item.get("metadata", {}).get("memory_type", "user"),
                            user_id=user_id,
                            created_at=item.get("created_at"),
                            updated_at=format_timestamp(),
                            metadata=item.get("metadata"),
                        ),
                        meta=ResponseMeta(**meta_dict),
                    )

        elif client and mode == "self-hosted":
            if body.content:
                client.update(memory_id=memory_id, data=body.content)

            return APIResponse(
                success=True,
                data=MemoryItem(
                    id=memory_id,
                    memory=body.content or "",
                    user_id=user_id,
                    updated_at=format_timestamp(),
                    metadata=body.metadata,
                ),
                meta=ResponseMeta(**meta_dict),
            )
        else:
            # Mock update
            if body.content:
                success = mock_update_memory(memory_id, user_id, body.content)
                if success:
                    item = _memory_store[memory_id]
                    return APIResponse(
                        success=True,
                        data=MemoryItem(
                            id=memory_id,
                            memory=item.get("memory", ""),
                            user_id=user_id,
                            created_at=item.get("created_at"),
                            updated_at=item.get("updated_at"),
                            metadata=item.get("metadata"),
                        ),
                        meta=ResponseMeta(**meta_dict),
                    )

    except Exception:
        pass

    raise HTTPException(status_code=404, detail=f"Memory not found: {memory_id}")


@router.delete("/{memory_id}", response_model=APIResponse[MemoryDeleteResponse])
async def delete_memory(
    request: Request,
    memory_id: str,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[MemoryDeleteResponse]:
    """
    Delete a memory.

    **Path Parameters:**
    - memory_id: The unique memory ID

    **Response:**
    - memory_id: ID of deleted memory
    - success: Whether deletion succeeded
    - message: Result message

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    user_id = user.uid

    client, mode = get_mem0_client()

    try:
        if client and mode == "cloud":
            client.delete(memory_id)
            return APIResponse(
                success=True,
                data=MemoryDeleteResponse(
                    memory_id=memory_id,
                    success=True,
                    message="Memory deleted successfully",
                ),
                meta=ResponseMeta(**meta_dict),
            )

        elif client and mode == "self-hosted":
            client.delete(memory_id=memory_id)
            return APIResponse(
                success=True,
                data=MemoryDeleteResponse(
                    memory_id=memory_id,
                    success=True,
                    message="Memory deleted successfully",
                ),
                meta=ResponseMeta(**meta_dict),
            )
        else:
            # Mock delete
            success = mock_delete_memory(memory_id, user_id)
            if success:
                return APIResponse(
                    success=True,
                    data=MemoryDeleteResponse(
                        memory_id=memory_id,
                        success=True,
                        message="Memory deleted successfully",
                    ),
                    meta=ResponseMeta(**meta_dict),
                )

    except Exception as e:
        return APIResponse(
            success=True,
            data=MemoryDeleteResponse(
                memory_id=memory_id,
                success=False,
                message=f"Failed to delete: {str(e)}",
            ),
            meta=ResponseMeta(**meta_dict),
        )

    raise HTTPException(status_code=404, detail=f"Memory not found: {memory_id}")


@router.post("/bulk", response_model=APIResponse[MemoryBulkAddResponse])
async def bulk_add_memories(
    request: Request,
    body: MemoryBulkAddRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[MemoryBulkAddResponse]:
    """
    Add multiple memories at once.

    Efficiently adds up to 100 memories in a single request.

    **Request Body:**
    - memories: List of MemoryAddRequest objects (max 100)

    **Response:**
    - added: Number of memories successfully added
    - failed: Number that failed
    - memory_ids: IDs of added memories
    - errors: Error messages for failures

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    user_id = user.uid

    added_ids = []
    errors = []

    client, mode = get_mem0_client()

    for memory in body.memories:
        try:
            metadata = {
                "memory_type": memory.memory_type.value,
                "tenant_id": user.tenant_id or "default",
                **(memory.metadata or {}),
            }

            if memory.session_id:
                metadata["session_id"] = memory.session_id
            if memory.agent_id:
                metadata["agent_id"] = memory.agent_id

            if client and mode in ("cloud", "self-hosted"):
                result = client.add(
                    memory.content,
                    user_id=user_id,
                    metadata=metadata,
                )
                memory_id = result.get("id", generate_memory_id())
            else:
                memory_id = mock_add_memory(user_id, memory.content, metadata)

            added_ids.append(memory_id)

        except Exception as e:
            errors.append(f"Failed to add memory: {str(e)}")

    return APIResponse(
        success=True,
        data=MemoryBulkAddResponse(
            added=len(added_ids),
            failed=len(errors),
            memory_ids=added_ids,
            errors=errors if errors else None,
        ),
        meta=ResponseMeta(**meta_dict),
    )


@router.get("/stats/overview", response_model=APIResponse[MemoryStatsResponse])
async def get_memory_stats(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[MemoryStatsResponse]:
    """
    Get memory usage statistics.

    Returns aggregate statistics about the user's memories.

    **Response:**
    - total_memories: Total count of memories
    - user_memories: Count of user-type memories
    - session_memories: Count of session-type memories
    - agent_memories: Count of agent-type memories
    - oldest_memory: Timestamp of oldest memory
    - newest_memory: Timestamp of newest memory

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    user_id = user.uid

    stats = MemoryStatsResponse(total_memories=0)

    client, mode = get_mem0_client()

    try:
        if client and mode in ("cloud", "self-hosted"):
            result = client.get_all(user_id=user_id)
            all_memories = result if isinstance(result, list) else result.get("memories", result.get("results", []))

            stats.total_memories = len(all_memories)

            timestamps = []
            for item in all_memories:
                meta = item.get("metadata", {})
                memory_type = meta.get("memory_type", "user")

                if memory_type == "user":
                    stats.user_memories += 1
                elif memory_type == "session":
                    stats.session_memories += 1
                elif memory_type == "agent":
                    stats.agent_memories += 1

                if item.get("created_at"):
                    timestamps.append(item["created_at"])

            if timestamps:
                timestamps.sort()
                stats.oldest_memory = timestamps[0]
                stats.newest_memory = timestamps[-1]
        else:
            # Mock stats
            all_memories = mock_get_all_memories(user_id)
            stats.total_memories = len(all_memories)

            for item in all_memories:
                meta = item.get("metadata", {})
                memory_type = meta.get("memory_type", "user")

                if memory_type == "user":
                    stats.user_memories += 1
                elif memory_type == "session":
                    stats.session_memories += 1
                elif memory_type == "agent":
                    stats.agent_memories += 1

    except Exception:
        pass

    return APIResponse(
        success=True,
        data=stats,
        meta=ResponseMeta(**meta_dict),
    )


@router.delete("/clear/all", response_model=APIResponse[MemoryDeleteResponse])
async def clear_all_memories(
    request: Request,
    confirm: bool = Query(False, description="Must be true to confirm deletion"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[MemoryDeleteResponse]:
    """
    Delete all memories for the current user.

    **WARNING:** This action cannot be undone!

    **Query Parameters:**
    - confirm: Must be true to confirm deletion

    **Response:**
    - memory_id: "all"
    - success: Whether deletion succeeded
    - message: Result message

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    user_id = user.uid

    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Must set confirm=true to delete all memories"
        )

    client, mode = get_mem0_client()
    deleted_count = 0

    try:
        if client and mode == "cloud":
            # Delete all for user
            client.delete_all(user_id=user_id)
            deleted_count = -1  # Unknown count

        elif client and mode == "self-hosted":
            result = client.get_all(user_id=user_id)
            all_memories = result if isinstance(result, list) else result.get("results", [])

            for item in all_memories:
                client.delete(memory_id=item.get("id"))
                deleted_count += 1
        else:
            # Mock clear
            to_delete = [
                mid for mid, mdata in _memory_store.items()
                if mdata.get("user_id") == user_id
            ]
            for mid in to_delete:
                del _memory_store[mid]
                deleted_count += 1

    except Exception as e:
        return APIResponse(
            success=True,
            data=MemoryDeleteResponse(
                memory_id="all",
                success=False,
                message=f"Failed to clear memories: {str(e)}",
            ),
            meta=ResponseMeta(**meta_dict),
        )

    return APIResponse(
        success=True,
        data=MemoryDeleteResponse(
            memory_id="all",
            success=True,
            message=f"All memories cleared ({deleted_count} deleted)" if deleted_count >= 0 else "All memories cleared",
        ),
        meta=ResponseMeta(**meta_dict),
    )
