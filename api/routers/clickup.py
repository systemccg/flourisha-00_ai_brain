"""
ClickUp Integration Router

REST API for ClickUp task management.
Uses the ClickUp API directly (no MCP wrapper) for reliable task operations.
"""
import os
import httpx
from typing import Optional, List

from fastapi import APIRouter, Depends, Request, Query
from pydantic import BaseModel

from models.response import APIResponse, ResponseMeta
from models.clickup import (
    ClickUpTask,
    ClickUpTaskCreate,
    ClickUpTaskUpdate,
    ClickUpTasksResponse,
    ClickUpListsResponse,
    ClickUpListSummary,
    ClickUpTaskStatus,
    ClickUpPriority,
)
from middleware.auth import get_current_user, UserContext


router = APIRouter(prefix="/api/clickup", tags=["ClickUp"])

# ClickUp API configuration
CLICKUP_API_BASE = "https://api.clickup.com/api/v2"
IDEA_SCRATCHPAD_LIST_ID = "901112609506"  # Default list for ideas


def get_clickup_headers() -> dict:
    """Get headers for ClickUp API requests."""
    api_key = os.environ.get("CLICKUP_API_KEY")
    if not api_key:
        raise ValueError("CLICKUP_API_KEY environment variable not set")
    return {"Authorization": api_key}


def parse_task(task_data: dict) -> ClickUpTask:
    """Parse ClickUp API task response into ClickUpTask model."""
    status_data = task_data.get("status")
    priority_data = task_data.get("priority")
    list_data = task_data.get("list", {})

    return ClickUpTask(
        id=task_data.get("id", ""),
        name=task_data.get("name", ""),
        description=task_data.get("text_content") or task_data.get("description"),
        status=ClickUpTaskStatus(
            id=status_data.get("id", ""),
            status=status_data.get("status", ""),
            color=status_data.get("color"),
        ) if status_data else None,
        priority=ClickUpPriority(
            id=priority_data.get("id", ""),
            priority=priority_data.get("priority", ""),
            color=priority_data.get("color"),
        ) if priority_data else None,
        due_date=task_data.get("due_date"),
        date_created=task_data.get("date_created"),
        date_updated=task_data.get("date_updated"),
        list_id=list_data.get("id"),
        list_name=list_data.get("name"),
        url=task_data.get("url"),
        tags=[t.get("name", "") for t in task_data.get("tags", [])],
    )


@router.get("/tasks", response_model=APIResponse[ClickUpTasksResponse])
async def get_tasks(
    request: Request,
    list_id: Optional[str] = Query(
        None,
        description="List ID to fetch tasks from. Defaults to Idea Scratchpad."
    ),
    status: Optional[str] = Query(
        None,
        description="Filter by status name (e.g., 'to do', 'in progress')"
    ),
    limit: int = Query(
        20,
        description="Maximum number of tasks to return",
        ge=1,
        le=100
    ),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[ClickUpTasksResponse]:
    """
    Get tasks from a ClickUp list.

    **Query Parameters:**
    - list_id: Optional list ID (defaults to Idea Scratchpad)
    - status: Filter by status name
    - limit: Max results (default 20, max 100)

    **Returns:** List of tasks with metadata

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    target_list_id = list_id or IDEA_SCRATCHPAD_LIST_ID

    try:
        headers = get_clickup_headers()

        # Build query params
        params = {}
        if status:
            params["statuses[]"] = status

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{CLICKUP_API_BASE}/list/{target_list_id}/task",
                headers=headers,
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

        tasks_data = data.get("tasks", [])[:limit]
        tasks = [parse_task(t) for t in tasks_data]

        # Get list name from first task or fetch separately
        list_name = tasks[0].list_name if tasks else None

        return APIResponse(
            success=True,
            data=ClickUpTasksResponse(
                tasks=tasks,
                total=len(tasks),
                list_id=target_list_id,
                list_name=list_name,
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except ValueError as e:
        return APIResponse(
            success=False,
            data=None,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )
    except httpx.HTTPStatusError as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"ClickUp API error: {e.response.status_code}",
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to fetch tasks: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/tasks/{task_id}", response_model=APIResponse[ClickUpTask])
async def get_task(
    request: Request,
    task_id: str,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[ClickUpTask]:
    """
    Get a single task by ID.

    **Path Parameters:**
    - task_id: The ClickUp task ID

    **Returns:** Task details

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        headers = get_clickup_headers()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{CLICKUP_API_BASE}/task/{task_id}",
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

        task = parse_task(data)

        return APIResponse(
            success=True,
            data=task,
            meta=ResponseMeta(**meta_dict),
        )

    except ValueError as e:
        return APIResponse(
            success=False,
            data=None,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return APIResponse(
                success=False,
                data=None,
                error=f"Task not found: {task_id}",
                meta=ResponseMeta(**meta_dict),
            )
        return APIResponse(
            success=False,
            data=None,
            error=f"ClickUp API error: {e.response.status_code}",
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to fetch task: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.post("/tasks", response_model=APIResponse[ClickUpTask])
async def create_task(
    request: Request,
    task_create: ClickUpTaskCreate,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[ClickUpTask]:
    """
    Create a new task in ClickUp.

    **Request Body:**
    - name: Task name (required)
    - description: Task description
    - list_id: Target list (defaults to Idea Scratchpad)
    - priority: 1=urgent, 2=high, 3=normal, 4=low
    - due_date: Due date (timestamp or natural language)
    - tags: List of tag names

    **Returns:** Created task with ID and URL

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    target_list_id = task_create.list_id or IDEA_SCRATCHPAD_LIST_ID

    try:
        headers = get_clickup_headers()
        headers["Content-Type"] = "application/json"

        # Build request body
        body = {"name": task_create.name}

        if task_create.description:
            body["description"] = task_create.description

        if task_create.priority:
            body["priority"] = task_create.priority

        if task_create.due_date:
            body["due_date"] = task_create.due_date

        if task_create.tags:
            body["tags"] = task_create.tags

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{CLICKUP_API_BASE}/list/{target_list_id}/task",
                headers=headers,
                json=body,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

        task = parse_task(data)

        return APIResponse(
            success=True,
            data=task,
            meta=ResponseMeta(**meta_dict),
        )

    except ValueError as e:
        return APIResponse(
            success=False,
            data=None,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )
    except httpx.HTTPStatusError as e:
        error_body = e.response.text
        return APIResponse(
            success=False,
            data=None,
            error=f"ClickUp API error: {e.response.status_code} - {error_body}",
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to create task: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.put("/tasks/{task_id}", response_model=APIResponse[ClickUpTask])
async def update_task(
    request: Request,
    task_id: str,
    task_update: ClickUpTaskUpdate,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[ClickUpTask]:
    """
    Update an existing task.

    **Path Parameters:**
    - task_id: The ClickUp task ID

    **Request Body (all optional):**
    - name: New task name
    - description: New description
    - status: New status name (e.g., 'in progress', 'complete')
    - priority: 1=urgent, 2=high, 3=normal, 4=low
    - due_date: New due date

    **Returns:** Updated task

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        headers = get_clickup_headers()
        headers["Content-Type"] = "application/json"

        # Build request body with only provided fields
        body = {}

        if task_update.name is not None:
            body["name"] = task_update.name

        if task_update.description is not None:
            body["description"] = task_update.description

        if task_update.status is not None:
            body["status"] = task_update.status

        if task_update.priority is not None:
            body["priority"] = task_update.priority

        if task_update.due_date is not None:
            body["due_date"] = task_update.due_date

        if not body:
            return APIResponse(
                success=False,
                data=None,
                error="No update fields provided",
                meta=ResponseMeta(**meta_dict),
            )

        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{CLICKUP_API_BASE}/task/{task_id}",
                headers=headers,
                json=body,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

        task = parse_task(data)

        return APIResponse(
            success=True,
            data=task,
            meta=ResponseMeta(**meta_dict),
        )

    except ValueError as e:
        return APIResponse(
            success=False,
            data=None,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return APIResponse(
                success=False,
                data=None,
                error=f"Task not found: {task_id}",
                meta=ResponseMeta(**meta_dict),
            )
        error_body = e.response.text
        return APIResponse(
            success=False,
            data=None,
            error=f"ClickUp API error: {e.response.status_code} - {error_body}",
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to update task: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.delete("/tasks/{task_id}", response_model=APIResponse[dict])
async def delete_task(
    request: Request,
    task_id: str,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[dict]:
    """
    Delete a task.

    **WARNING:** This permanently deletes the task.

    **Path Parameters:**
    - task_id: The ClickUp task ID

    **Returns:** Confirmation of deletion

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        headers = get_clickup_headers()

        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{CLICKUP_API_BASE}/task/{task_id}",
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()

        return APIResponse(
            success=True,
            data={"deleted": True, "task_id": task_id},
            meta=ResponseMeta(**meta_dict),
        )

    except ValueError as e:
        return APIResponse(
            success=False,
            data=None,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return APIResponse(
                success=False,
                data=None,
                error=f"Task not found: {task_id}",
                meta=ResponseMeta(**meta_dict),
            )
        return APIResponse(
            success=False,
            data=None,
            error=f"ClickUp API error: {e.response.status_code}",
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to delete task: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/lists", response_model=APIResponse[ClickUpListsResponse])
async def get_lists(
    request: Request,
    space_id: Optional[str] = Query(
        None,
        description="Space ID to get lists from. Uses default workspace if not provided."
    ),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[ClickUpListsResponse]:
    """
    Get available lists from ClickUp workspace.

    **Query Parameters:**
    - space_id: Optional space ID to filter lists

    **Returns:** List of available lists with task counts

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        headers = get_clickup_headers()
        team_id = os.environ.get("CLICKUP_TEAM_ID", "8655078")

        async with httpx.AsyncClient() as client:
            # Get spaces first
            response = await client.get(
                f"{CLICKUP_API_BASE}/team/{team_id}/space",
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            spaces_data = response.json()

        lists = []
        for space in spaces_data.get("spaces", []):
            if space_id and space.get("id") != space_id:
                continue

            space_name = space.get("name", "")

            # Get folders in space
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{CLICKUP_API_BASE}/space/{space['id']}/folder",
                    headers=headers,
                    timeout=30.0
                )
                if response.status_code == 200:
                    folders_data = response.json()
                    for folder in folders_data.get("folders", []):
                        for lst in folder.get("lists", []):
                            lists.append(ClickUpListSummary(
                                id=lst.get("id", ""),
                                name=lst.get("name", ""),
                                task_count=lst.get("task_count"),
                                space_id=space.get("id"),
                                space_name=space_name,
                            ))

            # Get folderless lists
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{CLICKUP_API_BASE}/space/{space['id']}/list",
                    headers=headers,
                    timeout=30.0
                )
                if response.status_code == 200:
                    lists_data = response.json()
                    for lst in lists_data.get("lists", []):
                        lists.append(ClickUpListSummary(
                            id=lst.get("id", ""),
                            name=lst.get("name", ""),
                            task_count=lst.get("task_count"),
                            space_id=space.get("id"),
                            space_name=space_name,
                        ))

        return APIResponse(
            success=True,
            data=ClickUpListsResponse(
                lists=lists,
                total=len(lists),
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except ValueError as e:
        return APIResponse(
            success=False,
            data=None,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to fetch lists: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/scratchpad", response_model=APIResponse[ClickUpTasksResponse])
async def get_scratchpad(
    request: Request,
    limit: int = Query(20, ge=1, le=100),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[ClickUpTasksResponse]:
    """
    Get tasks from the Idea Scratchpad list.

    Convenience endpoint for quickly accessing ideas/captures.

    **Query Parameters:**
    - limit: Max results (default 20, max 100)

    **Returns:** List of scratchpad tasks

    **Requires:** Valid Firebase JWT
    """
    # Delegate to get_tasks with scratchpad list
    return await get_tasks(
        request=request,
        list_id=IDEA_SCRATCHPAD_LIST_ID,
        status=None,
        limit=limit,
        user=user,
    )
