"""
OKR Management Router

Endpoints for managing Objectives and Key Results (OKRs).
Wraps the okr_tracker service for quarterly goal management.
"""
import sys
import uuid
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Request, Query
from pydantic import BaseModel, Field

from models.response import APIResponse, ResponseMeta
from middleware.auth import get_current_user, UserContext

# Add services to path for imports
services_path = Path(__file__).parent.parent.parent / "services"
sys.path.insert(0, str(services_path))


router = APIRouter(prefix="/api/okrs", tags=["OKRs"])


# === Request/Response Models ===

class KeyResultData(BaseModel):
    """Key Result data model."""
    id: str = Field(..., description="Key Result identifier")
    title: str = Field(..., description="KR title")
    target: float = Field(..., description="Target value")
    current: float = Field(default=0.0, description="Current value")
    unit: str = Field(default="units", description="Unit of measurement")
    progress_pct: Optional[float] = Field(None, description="Progress percentage")
    is_lagging: Optional[bool] = Field(None, description="Whether KR is behind schedule")


class ObjectiveData(BaseModel):
    """Objective data model."""
    id: str = Field(..., description="Objective identifier")
    title: str = Field(..., description="Objective title")
    description: Optional[str] = Field(None, description="Objective description")
    owner: Optional[str] = Field(None, description="Objective owner")
    target_completion: Optional[str] = Field(None, description="Target completion date")
    key_results: List[KeyResultData] = Field(default_factory=list, description="Key Results")
    progress_pct: Optional[float] = Field(None, description="Overall progress percentage")


class OKRProgressResponse(BaseModel):
    """Response for OKR progress query."""
    quarter: str = Field(..., description="Quarter identifier (e.g., Q1_2026)")
    objectives: List[ObjectiveData] = Field(..., description="All objectives with progress")
    total_objectives: int = Field(..., description="Total number of objectives")
    average_progress: float = Field(..., description="Average progress across all objectives")


class FocusItem(BaseModel):
    """Weekly focus item for lagging KRs."""
    objective_id: str = Field(..., description="Objective identifier")
    objective_title: str = Field(..., description="Objective title")
    kr_id: str = Field(..., description="Key Result identifier")
    kr_title: str = Field(..., description="Key Result title")
    current: float = Field(..., description="Current value")
    target: float = Field(..., description="Target value")
    unit: str = Field(..., description="Unit of measurement")
    progress_pct: float = Field(..., description="Progress percentage")
    progress_gap: float = Field(..., description="Gap from expected progress")
    priority: str = Field(..., description="Priority level (high/medium)")


class WeeklyFocusResponse(BaseModel):
    """Response for weekly focus query."""
    quarter: str = Field(..., description="Quarter identifier")
    focus_items: List[FocusItem] = Field(..., description="Prioritized focus items")
    total_lagging: int = Field(..., description="Total lagging KRs")


class OneThingCandidate(BaseModel):
    """Candidate task for 'The One Thing' focus."""
    task: str = Field(..., description="Suggested task")
    project: str = Field(..., description="Project/Objective name")
    okr_id: str = Field(..., description="Objective identifier")
    okr_title: str = Field(..., description="Objective title")
    kr_id: str = Field(..., description="Key Result identifier")
    kr_title: str = Field(..., description="Key Result title")
    priority_score: float = Field(..., description="Priority score")
    rationale: str = Field(..., description="Why this task matters")


class OneThingResponse(BaseModel):
    """Response for 'The One Thing' candidates."""
    quarter: str = Field(..., description="Quarter identifier")
    candidates: List[OneThingCandidate] = Field(..., description="Top 3 candidates")


class UpdateProgressRequest(BaseModel):
    """Request to update KR progress."""
    objective_id: str = Field(..., description="Objective identifier")
    kr_id: str = Field(..., description="Key Result identifier")
    new_value: float = Field(..., ge=0, description="New current value")
    notes: Optional[str] = Field(None, description="Optional notes about the update")


class KeyResultCreate(BaseModel):
    """Key Result creation data."""
    title: str = Field(..., description="KR title")
    target: float = Field(..., description="Target value")
    unit: str = Field(default="units", description="Unit of measurement")
    initial_value: float = Field(default=0.0, description="Starting value")


class ObjectiveCreate(BaseModel):
    """Objective creation request."""
    title: str = Field(..., description="Objective title")
    description: Optional[str] = Field(None, description="Objective description")
    quarter: Optional[str] = Field(None, description="Quarter (defaults to current)")
    owner: Optional[str] = Field(None, description="Objective owner")
    target_completion: Optional[str] = Field(None, description="Target completion date")
    key_results: List[KeyResultCreate] = Field(default_factory=list, description="Key Results")


class ObjectiveUpdate(BaseModel):
    """Objective update request."""
    title: Optional[str] = Field(None, description="New title")
    description: Optional[str] = Field(None, description="New description")
    owner: Optional[str] = Field(None, description="New owner")
    target_completion: Optional[str] = Field(None, description="New target completion date")


class MeasurementRequest(BaseModel):
    """Measurement recording request."""
    value: float = Field(..., ge=0, description="Measurement value")
    notes: Optional[str] = Field(None, description="Notes about this measurement")


class OKRReportResponse(BaseModel):
    """Comprehensive OKR report response."""
    quarter: str = Field(..., description="Quarter identifier")
    period: str = Field(..., description="Report period")
    generated_at: str = Field(..., description="Report generation timestamp")
    summary: dict = Field(..., description="Summary statistics")
    objectives: List[dict] = Field(..., description="Objective details")
    weekly_focus: List[dict] = Field(..., description="Weekly focus items")
    recommendations: List[str] = Field(..., description="Action recommendations")


# Pacific timezone for timestamps
PACIFIC = ZoneInfo("America/Los_Angeles")


# === Endpoints ===

@router.post("", response_model=APIResponse[ObjectiveData])
async def create_objective(
    request: Request,
    objective_create: ObjectiveCreate,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[ObjectiveData]:
    """
    Create a new Objective with Key Results.

    Creates an objective with optional key results attached.
    The objective is assigned to the specified quarter (or current quarter).

    **Request Body:**
    - title: Objective title (required)
    - description: Optional description
    - quarter: Quarter identifier (defaults to current)
    - owner: Optional owner
    - target_completion: Optional target date
    - key_results: List of key results to create

    **Response:**
    - Created objective with assigned IDs

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or user.uid
    now = datetime.now(PACIFIC)

    try:
        from okr_tracker import OKRTrackerService

        tracker = OKRTrackerService()
        quarter = objective_create.quarter or tracker._get_current_quarter()

        # Generate IDs
        obj_id = f"obj_{uuid.uuid4().hex[:8]}"

        # Build key results
        key_results = []
        for kr in objective_create.key_results:
            kr_id = f"kr_{uuid.uuid4().hex[:8]}"
            key_results.append(KeyResultData(
                id=kr_id,
                title=kr.title,
                target=kr.target,
                current=kr.initial_value,
                unit=kr.unit,
                progress_pct=(kr.initial_value / kr.target * 100) if kr.target > 0 else 0.0,
                is_lagging=False,
            ))

        # Calculate overall progress
        overall_progress = (
            sum(kr.progress_pct or 0 for kr in key_results) / len(key_results)
            if key_results else 0.0
        )

        # Build objective data
        objective_data = ObjectiveData(
            id=obj_id,
            title=objective_create.title,
            description=objective_create.description,
            owner=objective_create.owner,
            target_completion=objective_create.target_completion,
            key_results=key_results,
            progress_pct=overall_progress,
        )

        # Persist to Supabase
        if tracker._client:
            # Insert objective
            tracker._client.table('okr_objectives').insert({
                'id': obj_id,
                'tenant_id': tenant_id,
                'quarter': quarter,
                'title': objective_create.title,
                'description': objective_create.description,
                'owner': objective_create.owner,
                'target_completion': objective_create.target_completion,
                'created_at': now.isoformat(),
                'updated_at': now.isoformat(),
            }).execute()

            # Insert key results
            for kr in key_results:
                tracker._client.table('okr_key_results').insert({
                    'id': kr.id,
                    'objective_id': obj_id,
                    'tenant_id': tenant_id,
                    'title': kr.title,
                    'target': kr.target,
                    'current': kr.current,
                    'unit': kr.unit,
                    'created_at': now.isoformat(),
                    'updated_at': now.isoformat(),
                }).execute()

        return APIResponse(
            success=True,
            data=objective_data,
            meta=ResponseMeta(**meta_dict),
        )

    except ImportError as e:
        return APIResponse(
            success=False,
            data=None,
            error="OKR tracker service not available",
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to create objective: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("", response_model=APIResponse[OKRProgressResponse])
async def list_objectives(
    request: Request,
    quarter: Optional[str] = Query(None, description="Quarter (e.g., Q1_2026). Defaults to current."),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[OKRProgressResponse]:
    """
    List all objectives for a quarter.

    Alias for /progress endpoint - returns all objectives with their key results.

    **Query Parameters:**
    - quarter: Quarter identifier (defaults to current quarter)

    **Requires:** Valid Firebase JWT
    """
    return await get_okr_progress(request, quarter, "weekly", user)


@router.get("/{objective_id}", response_model=APIResponse[ObjectiveData])
async def get_objective(
    request: Request,
    objective_id: str,
    quarter: Optional[str] = Query(None, description="Quarter (defaults to current)"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[ObjectiveData]:
    """
    Get a single objective by ID.

    Returns the objective with its key results and current progress.

    **Path Parameters:**
    - objective_id: Objective identifier

    **Query Parameters:**
    - quarter: Quarter identifier (defaults to current quarter)

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or user.uid

    try:
        from okr_tracker import OKRTrackerService

        tracker = OKRTrackerService()
        await tracker.load_okrs(quarter or tracker._get_current_quarter(), tenant_id)

        obj = tracker._okrs.get(objective_id)
        if not obj:
            return APIResponse(
                success=False,
                data=None,
                error=f"Objective {objective_id} not found",
                meta=ResponseMeta(**meta_dict),
            )

        key_results = []
        for kr in obj.key_results:
            key_results.append(KeyResultData(
                id=kr.id,
                title=kr.title,
                target=kr.target,
                current=kr.current,
                unit=kr.unit,
                progress_pct=kr.progress_pct,
                is_lagging=kr.is_lagging,
            ))

        objective_data = ObjectiveData(
            id=obj.id,
            title=obj.title,
            description=obj.description,
            owner=obj.owner,
            target_completion=obj.target_completion,
            key_results=key_results,
            progress_pct=obj.progress_pct,
        )

        return APIResponse(
            success=True,
            data=objective_data,
            meta=ResponseMeta(**meta_dict),
        )

    except ImportError as e:
        return APIResponse(
            success=False,
            data=None,
            error="OKR tracker service not available",
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to get objective: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.put("/{objective_id}", response_model=APIResponse[ObjectiveData])
async def update_objective(
    request: Request,
    objective_id: str,
    objective_update: ObjectiveUpdate,
    quarter: Optional[str] = Query(None, description="Quarter (defaults to current)"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[ObjectiveData]:
    """
    Update an objective.

    Updates objective properties (title, description, owner, target date).
    Does not update key results - use the measure endpoint for that.

    **Path Parameters:**
    - objective_id: Objective identifier

    **Request Body:**
    - title: New title (optional)
    - description: New description (optional)
    - owner: New owner (optional)
    - target_completion: New target date (optional)

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or user.uid
    now = datetime.now(PACIFIC)

    try:
        from okr_tracker import OKRTrackerService

        tracker = OKRTrackerService()
        quarter_str = quarter or tracker._get_current_quarter()
        await tracker.load_okrs(quarter_str, tenant_id)

        obj = tracker._okrs.get(objective_id)
        if not obj:
            return APIResponse(
                success=False,
                data=None,
                error=f"Objective {objective_id} not found",
                meta=ResponseMeta(**meta_dict),
            )

        # Build update payload
        updates = {}
        if objective_update.title is not None:
            updates['title'] = objective_update.title
            obj.title = objective_update.title
        if objective_update.description is not None:
            updates['description'] = objective_update.description
            obj.description = objective_update.description
        if objective_update.owner is not None:
            updates['owner'] = objective_update.owner
            obj.owner = objective_update.owner
        if objective_update.target_completion is not None:
            updates['target_completion'] = objective_update.target_completion
            obj.target_completion = objective_update.target_completion

        # Persist to Supabase
        if tracker._client and updates:
            updates['updated_at'] = now.isoformat()
            tracker._client.table('okr_objectives').update(updates).eq(
                'id', objective_id
            ).eq('tenant_id', tenant_id).execute()

        # Build response
        key_results = []
        for kr in obj.key_results:
            key_results.append(KeyResultData(
                id=kr.id,
                title=kr.title,
                target=kr.target,
                current=kr.current,
                unit=kr.unit,
                progress_pct=kr.progress_pct,
                is_lagging=kr.is_lagging,
            ))

        objective_data = ObjectiveData(
            id=obj.id,
            title=obj.title,
            description=obj.description,
            owner=obj.owner,
            target_completion=obj.target_completion,
            key_results=key_results,
            progress_pct=obj.progress_pct,
        )

        return APIResponse(
            success=True,
            data=objective_data,
            meta=ResponseMeta(**meta_dict),
        )

    except ImportError as e:
        return APIResponse(
            success=False,
            data=None,
            error="OKR tracker service not available",
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to update objective: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.post("/{objective_id}/measure", response_model=APIResponse[dict])
async def record_measurement(
    request: Request,
    objective_id: str,
    kr_id: str = Query(..., description="Key Result identifier"),
    measurement: MeasurementRequest = None,
    quarter: Optional[str] = Query(None, description="Quarter (defaults to current)"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[dict]:
    """
    Record a measurement for a Key Result.

    Updates the current value of a key result and records the measurement.
    This is the primary way to track progress on KRs.

    **Path Parameters:**
    - objective_id: Objective identifier

    **Query Parameters:**
    - kr_id: Key Result identifier (required)
    - quarter: Quarter identifier (defaults to current)

    **Request Body:**
    - value: The new measurement value
    - notes: Optional notes about this measurement

    **Response:**
    - updated: Whether update succeeded
    - objective_id: The objective
    - kr_id: The key result
    - new_value: The recorded value
    - progress_pct: New progress percentage

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or user.uid

    # Use the existing update_kr_progress logic
    update_request = UpdateProgressRequest(
        objective_id=objective_id,
        kr_id=kr_id,
        new_value=measurement.value if measurement else 0,
        notes=measurement.notes if measurement else None,
    )

    try:
        from okr_tracker import OKRTrackerService

        tracker = OKRTrackerService()
        await tracker.load_okrs(quarter or tracker._get_current_quarter(), tenant_id)

        success = await tracker.update_kr_progress(
            objective_id=update_request.objective_id,
            kr_id=update_request.kr_id,
            new_value=update_request.new_value,
            tenant_id=tenant_id,
            notes=update_request.notes,
        )

        if success:
            # Get updated progress
            obj = tracker._okrs.get(update_request.objective_id)
            kr_progress = None
            if obj:
                for kr in obj.key_results:
                    if kr.id == update_request.kr_id:
                        kr_progress = kr.progress_pct
                        break

            return APIResponse(
                success=True,
                data={
                    "updated": True,
                    "objective_id": update_request.objective_id,
                    "kr_id": update_request.kr_id,
                    "new_value": update_request.new_value,
                    "progress_pct": kr_progress,
                },
                meta=ResponseMeta(**meta_dict),
            )
        else:
            return APIResponse(
                success=False,
                data=None,
                error="Failed to record measurement - objective or KR not found",
                meta=ResponseMeta(**meta_dict),
            )

    except ImportError as e:
        return APIResponse(
            success=False,
            data=None,
            error="OKR tracker service not available",
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to record measurement: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/progress", response_model=APIResponse[OKRProgressResponse])
async def get_okr_progress(
    request: Request,
    quarter: Optional[str] = Query(None, description="Quarter (e.g., Q1_2026). Defaults to current."),
    period: str = Query("weekly", description="Period: weekly, monthly, quarterly"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[OKRProgressResponse]:
    """
    Get OKR progress for the specified quarter.

    Returns all objectives with their key results and progress percentages.
    Progress is calculated relative to time elapsed in the quarter.

    **Query Parameters:**
    - quarter: Quarter identifier (defaults to current quarter)
    - period: Aggregation period for progress calculation

    **Response:**
    - quarter: The quarter identifier
    - objectives: List of objectives with key results
    - total_objectives: Count of objectives
    - average_progress: Average progress percentage

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or user.uid

    try:
        from okr_tracker import OKRTrackerService

        tracker = OKRTrackerService()

        # Initialize with quarter
        await tracker.load_okrs(quarter or tracker._get_current_quarter(), tenant_id)

        # Get progress data
        progress_data = await tracker.get_okr_progress(period)

        # Transform to response
        objectives = []
        for obj_id, progress in progress_data.items():
            obj = tracker._okrs.get(obj_id)
            if obj:
                key_results = []
                for kr in obj.key_results:
                    key_results.append(KeyResultData(
                        id=kr.id,
                        title=kr.title,
                        target=kr.target,
                        current=kr.current,
                        unit=kr.unit,
                        progress_pct=kr.progress_pct,
                        is_lagging=kr.is_lagging,
                    ))

                objectives.append(ObjectiveData(
                    id=obj.id,
                    title=obj.title,
                    description=obj.description,
                    owner=obj.owner,
                    target_completion=obj.target_completion,
                    key_results=key_results,
                    progress_pct=obj.progress_pct,
                ))

        avg_progress = sum(o.progress_pct or 0 for o in objectives) / len(objectives) if objectives else 0

        response_data = OKRProgressResponse(
            quarter=tracker._quarter or quarter or tracker._get_current_quarter(),
            objectives=objectives,
            total_objectives=len(objectives),
            average_progress=round(avg_progress, 1),
        )

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except ImportError as e:
        return APIResponse(
            success=False,
            data=None,
            error="OKR tracker service not available",
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to get OKR progress: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/focus", response_model=APIResponse[WeeklyFocusResponse])
async def get_weekly_focus(
    request: Request,
    quarter: Optional[str] = Query(None, description="Quarter (defaults to current)"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[WeeklyFocusResponse]:
    """
    Get weekly focus items - Key Results that are lagging and need attention.

    Returns KRs that are behind schedule, sorted by priority.
    Use this for weekly planning and daily focus selection.

    **Query Parameters:**
    - quarter: Quarter identifier (defaults to current quarter)

    **Response:**
    - quarter: The quarter identifier
    - focus_items: Prioritized list of lagging KRs
    - total_lagging: Count of lagging KRs

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or user.uid

    try:
        from okr_tracker import OKRTrackerService

        tracker = OKRTrackerService()
        await tracker.load_okrs(quarter or tracker._get_current_quarter(), tenant_id)

        focus_items_raw = await tracker.get_weekly_focus()

        focus_items = [
            FocusItem(**item) for item in focus_items_raw
        ]

        response_data = WeeklyFocusResponse(
            quarter=tracker._quarter or quarter or tracker._get_current_quarter(),
            focus_items=focus_items,
            total_lagging=len(focus_items),
        )

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except ImportError as e:
        return APIResponse(
            success=False,
            data=None,
            error="OKR tracker service not available",
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to get weekly focus: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/one-thing", response_model=APIResponse[OneThingResponse])
async def get_one_thing_candidates(
    request: Request,
    quarter: Optional[str] = Query(None, description="Quarter (defaults to current)"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[OneThingResponse]:
    """
    Get 'The One Thing' candidates for daily focus.

    Returns top 3 tasks that advance lagging Key Results.
    Designed for integration with morning report/daily planning.

    **Query Parameters:**
    - quarter: Quarter identifier (defaults to current quarter)

    **Response:**
    - quarter: The quarter identifier
    - candidates: Top 3 task candidates with rationale

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or user.uid

    try:
        from okr_tracker import OKRTrackerService

        tracker = OKRTrackerService()
        await tracker.load_okrs(quarter or tracker._get_current_quarter(), tenant_id)

        candidates_raw = await tracker.get_one_thing_candidates()

        candidates = []
        for c in candidates_raw:
            candidates.append(OneThingCandidate(
                task=c.task,
                project=c.project,
                okr_id=c.okr_id,
                okr_title=c.okr_title,
                kr_id=c.kr_id,
                kr_title=c.kr_title,
                priority_score=c.priority_score,
                rationale=c.rationale,
            ))

        response_data = OneThingResponse(
            quarter=tracker._quarter or quarter or tracker._get_current_quarter(),
            candidates=candidates,
        )

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except ImportError as e:
        return APIResponse(
            success=False,
            data=None,
            error="OKR tracker service not available",
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to get one-thing candidates: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.put("/progress", response_model=APIResponse[dict])
async def update_kr_progress(
    request: Request,
    update_request: UpdateProgressRequest,
    quarter: Optional[str] = Query(None, description="Quarter (defaults to current)"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[dict]:
    """
    Update progress for a specific Key Result.

    Records the new value and persists to database.
    Progress history is tracked for trend analysis.

    **Request Body:**
    - objective_id: Objective identifier
    - kr_id: Key Result identifier
    - new_value: New current value
    - notes: Optional notes about the update

    **Query Parameters:**
    - quarter: Quarter identifier (defaults to current quarter)

    **Response:**
    - updated: Whether update succeeded
    - objective_id: The objective
    - kr_id: The key result
    - new_value: The new value
    - progress_pct: New progress percentage

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or user.uid

    try:
        from okr_tracker import OKRTrackerService

        tracker = OKRTrackerService()
        await tracker.load_okrs(quarter or tracker._get_current_quarter(), tenant_id)

        success = await tracker.update_kr_progress(
            objective_id=update_request.objective_id,
            kr_id=update_request.kr_id,
            new_value=update_request.new_value,
            tenant_id=tenant_id,
            notes=update_request.notes,
        )

        if success:
            # Get updated progress
            obj = tracker._okrs.get(update_request.objective_id)
            kr_progress = None
            if obj:
                for kr in obj.key_results:
                    if kr.id == update_request.kr_id:
                        kr_progress = kr.progress_pct
                        break

            return APIResponse(
                success=True,
                data={
                    "updated": True,
                    "objective_id": update_request.objective_id,
                    "kr_id": update_request.kr_id,
                    "new_value": update_request.new_value,
                    "progress_pct": kr_progress,
                },
                meta=ResponseMeta(**meta_dict),
            )
        else:
            return APIResponse(
                success=False,
                data=None,
                error="Failed to update KR progress - objective or KR not found",
                meta=ResponseMeta(**meta_dict),
            )

    except ImportError as e:
        return APIResponse(
            success=False,
            data=None,
            error="OKR tracker service not available",
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to update KR progress: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/report", response_model=APIResponse[OKRReportResponse])
async def get_okr_report(
    request: Request,
    quarter: Optional[str] = Query(None, description="Quarter (defaults to current)"),
    period: str = Query("weekly", description="Period: weekly, monthly, quarterly"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[OKRReportResponse]:
    """
    Generate comprehensive OKR report with progress, trends, and recommendations.

    Returns summary statistics, objective details, focus areas,
    and actionable recommendations for improving OKR progress.

    **Query Parameters:**
    - quarter: Quarter identifier (defaults to current quarter)
    - period: Report period aggregation

    **Response:**
    - quarter: The quarter identifier
    - period: Report period
    - generated_at: Generation timestamp
    - summary: Overall statistics (total, on track, at risk, behind)
    - objectives: Detailed objective progress
    - weekly_focus: Items needing attention
    - recommendations: Suggested actions

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or user.uid

    try:
        from okr_tracker import OKRTrackerService

        tracker = OKRTrackerService()
        await tracker.load_okrs(quarter or tracker._get_current_quarter(), tenant_id)

        report = await tracker.generate_okr_report(period)

        response_data = OKRReportResponse(
            quarter=report['quarter'],
            period=report['period'],
            generated_at=report['generated_at'],
            summary=report['summary'],
            objectives=report['objectives'],
            weekly_focus=report['weekly_focus'],
            recommendations=report['recommendations'],
        )

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except ImportError as e:
        return APIResponse(
            success=False,
            data=None,
            error="OKR tracker service not available",
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to generate OKR report: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/quarters", response_model=APIResponse[dict])
async def get_available_quarters(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[dict]:
    """
    Get available quarters with OKR data.

    Returns current quarter and list of quarters with existing OKR data.

    **Response:**
    - current_quarter: Current quarter identifier
    - available_quarters: List of quarters with data

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or user.uid

    try:
        from okr_tracker import OKRTrackerService

        tracker = OKRTrackerService()
        current_quarter = tracker._get_current_quarter()

        # Query Supabase for available quarters
        available = [current_quarter]

        if tracker._client:
            try:
                result = tracker._client.table('okr_tracking').select(
                    'quarter'
                ).eq('tenant_id', tenant_id).execute()

                if result.data:
                    quarters = set(row['quarter'] for row in result.data)
                    available = sorted(list(quarters), reverse=True)
            except Exception:
                pass

        return APIResponse(
            success=True,
            data={
                "current_quarter": current_quarter,
                "available_quarters": available,
            },
            meta=ResponseMeta(**meta_dict),
        )

    except ImportError as e:
        return APIResponse(
            success=False,
            data=None,
            error="OKR tracker service not available",
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to get quarters: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )
