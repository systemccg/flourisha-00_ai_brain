"""
Daily Roadmap Router

AI-powered morning planning that synthesizes OKRs, energy data, and calendar
into a prioritized daily plan.
"""
import os
import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Request, Query
from pydantic import BaseModel, Field
from supabase import create_client, Client

from models.response import APIResponse, ResponseMeta
from middleware.auth import get_current_user, UserContext


# Add services to path for imports
services_path = Path(__file__).parent.parent.parent / "services"
sys.path.insert(0, str(services_path))


router = APIRouter(prefix="/api/roadmap", tags=["Daily Roadmap"])

# Pacific timezone for all time operations
PACIFIC = ZoneInfo("America/Los_Angeles")

# History paths
PAI_DIR = os.getenv("PAI_DIR", "/root/.claude")
HISTORY_DIR = Path(PAI_DIR) / "history"
ROADMAPS_DIR = HISTORY_DIR / "roadmaps"
SESSIONS_DIR = HISTORY_DIR / "sessions"


def get_supabase_client() -> Optional[Client]:
    """Get Supabase client for database operations."""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_KEY', os.getenv('SUPABASE_KEY'))

    if url and key:
        return create_client(url, key)
    return None


# === Request/Response Models ===

class PriorityItem(BaseModel):
    """Single priority item."""
    title: str = Field(..., description="Task title")
    reasoning: str = Field(..., description="Why this is a priority")
    time_estimate: Optional[str] = Field(None, description="Estimated time")
    okr_link: Optional[str] = Field(None, description="Related OKR if any")
    tier: int = Field(1, ge=1, le=3, description="Priority tier (1=must, 2=should, 3=could)")


class TimeBlock(BaseModel):
    """Recommended time block."""
    start_time: str = Field(..., description="Start time (e.g., '09:00')")
    end_time: str = Field(..., description="End time (e.g., '11:00')")
    activity: str = Field(..., description="What to work on")
    block_type: str = Field(..., description="deep_work, meetings, admin, breaks")


class RoadmapData(BaseModel):
    """Complete daily roadmap."""
    date: str = Field(..., description="Roadmap date (YYYY-MM-DD)")
    the_one_thing: str = Field(..., description="Single most critical task")
    the_one_thing_reasoning: str = Field(..., description="Why this is THE ONE THING")
    top_priorities: List[PriorityItem] = Field(..., description="Top 3 priorities")
    time_blocks: List[TimeBlock] = Field(..., description="Recommended time blocks")
    energy_insight: Optional[str] = Field(None, description="Energy-based recommendation")
    okr_context: Optional[str] = Field(None, description="Relevant OKR status")
    success_criteria: str = Field(..., description="What 'done' looks like today")


class RoadmapGenerateRequest(BaseModel):
    """Request to generate a roadmap."""
    user_context: Optional[str] = Field(None, description="User-provided context for today")
    focus_areas: Optional[List[str]] = Field(None, description="Specific areas to prioritize")
    available_hours: float = Field(default=8.0, ge=1, le=12, description="Hours available for work")


class RoadmapHistoryItem(BaseModel):
    """Roadmap history item."""
    date: str = Field(..., description="Roadmap date")
    the_one_thing: str = Field(..., description="THE ONE THING for that day")
    completed: bool = Field(False, description="Whether day was marked complete")


# === Helper Functions ===

def get_current_quarter() -> str:
    """Get current quarter string (e.g., Q1_2026)."""
    now = datetime.now(PACIFIC)
    quarter = (now.month - 1) // 3 + 1
    return f"Q{quarter}_{now.year}"


async def get_okr_summary(supabase: Client, user_id: str) -> Optional[dict]:
    """Get OKR summary for roadmap generation."""
    try:
        quarter = get_current_quarter()

        # Get objectives for current quarter
        result = supabase.table('objectives').select(
            'id, title, progress_pct'
        ).eq('quarter', quarter).eq('user_id', user_id).execute()

        if not result.data:
            return None

        objectives = result.data

        # Get lagging key results
        kr_result = supabase.table('key_results').select(
            'title, progress_pct, is_lagging, objective_id'
        ).eq('is_lagging', True).in_(
            'objective_id', [o['id'] for o in objectives]
        ).execute()

        lagging_krs = kr_result.data if kr_result.data else []

        return {
            "quarter": quarter,
            "total_objectives": len(objectives),
            "avg_progress": sum(o.get('progress_pct', 0) for o in objectives) / len(objectives) if objectives else 0,
            "lagging_count": len(lagging_krs),
            "lagging_krs": [kr['title'] for kr in lagging_krs[:3]]
        }
    except Exception:
        return None


async def get_energy_summary(supabase: Client, user_id: str) -> Optional[dict]:
    """Get recent energy data for roadmap optimization."""
    try:
        now = datetime.now(PACIFIC)
        week_ago = (now - timedelta(days=7)).isoformat()

        # Get energy entries from last week
        result = supabase.table('energy_tracking').select(
            'energy_level, focus_quality, timestamp'
        ).eq('user_id', user_id).gte('timestamp', week_ago).order(
            'timestamp', desc=True
        ).limit(20).execute()

        if not result.data:
            return None

        entries = result.data

        # Calculate averages
        avg_energy = sum(e['energy_level'] for e in entries) / len(entries)

        # Find peak hours (when energy is highest)
        hour_energy = {}
        for e in entries:
            ts = datetime.fromisoformat(e['timestamp'].replace('Z', '+00:00'))
            hour = ts.astimezone(PACIFIC).hour
            if hour not in hour_energy:
                hour_energy[hour] = []
            hour_energy[hour].append(e['energy_level'])

        # Find best hours
        hour_avgs = {h: sum(v)/len(v) for h, v in hour_energy.items() if len(v) >= 2}
        peak_hours = sorted(hour_avgs.keys(), key=lambda h: hour_avgs[h], reverse=True)[:3]

        return {
            "avg_energy": round(avg_energy, 1),
            "total_entries": len(entries),
            "peak_hours": peak_hours,
            "recommendation": f"Schedule deep work between {peak_hours[0]}:00-{(peak_hours[0]+2)%24}:00" if peak_hours else None
        }
    except Exception:
        return None


async def get_recent_sessions() -> list:
    """Get recent session logs for context."""
    sessions = []

    try:
        now = datetime.now(PACIFIC)
        current_month = now.strftime("%Y-%m")
        month_dir = SESSIONS_DIR / current_month

        if month_dir.exists():
            # Get last 3 session files
            session_files = sorted(month_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)[:3]

            for f in session_files:
                content = f.read_text()[:500]  # First 500 chars
                sessions.append({
                    "file": f.name,
                    "summary": content
                })
    except Exception:
        pass

    return sessions


def generate_time_blocks(
    available_hours: float,
    peak_hours: List[int],
    priorities: List[PriorityItem]
) -> List[TimeBlock]:
    """Generate recommended time blocks based on energy and priorities."""
    blocks = []

    # Default start at 9 AM
    current_hour = 9

    # Schedule deep work during peak hours if available
    if peak_hours and len(peak_hours) > 0:
        # 2-hour deep work block at peak
        peak = peak_hours[0]
        if 7 <= peak <= 16:  # Reasonable work hours
            blocks.append(TimeBlock(
                start_time=f"{peak:02d}:00",
                end_time=f"{(peak+2):02d}:00",
                activity=priorities[0].title if priorities else "Deep work on most important task",
                block_type="deep_work"
            ))

    # Add standard blocks
    blocks.extend([
        TimeBlock(
            start_time="09:00",
            end_time="09:15",
            activity="Review today's roadmap and prepare",
            block_type="admin"
        ),
        TimeBlock(
            start_time="12:00",
            end_time="13:00",
            activity="Lunch break",
            block_type="breaks"
        ),
        TimeBlock(
            start_time="15:00",
            end_time="15:15",
            activity="Energy check and refocus",
            block_type="admin"
        ),
    ])

    # Sort by start time
    blocks.sort(key=lambda b: b.start_time)

    return blocks


# === API Endpoints ===

@router.post("/generate", response_model=APIResponse[RoadmapData])
async def generate_roadmap(
    request: Request,
    generate_request: RoadmapGenerateRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[RoadmapData]:
    """
    Generate daily roadmap.

    Synthesizes OKRs, energy data, and optional user context
    into a prioritized daily plan.

    **Request Body:**
    - user_context: Optional context for today
    - focus_areas: Optional list of areas to prioritize
    - available_hours: Hours available for work (default 8)

    **Response:**
    - the_one_thing: Single most critical task
    - top_priorities: Top 3 prioritized items with reasoning
    - time_blocks: Recommended schedule
    - energy_insight: Energy-based recommendation
    - okr_context: Relevant OKR status

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        supabase = get_supabase_client()
        user_id = user.tenant_user_id or user.uid
        today = datetime.now(PACIFIC).strftime("%Y-%m-%d")

        # Gather context
        okr_summary = None
        energy_summary = None

        if supabase:
            okr_summary = await get_okr_summary(supabase, user_id)
            energy_summary = await get_energy_summary(supabase, user_id)

        # Get recent sessions for context
        sessions = await get_recent_sessions()

        # Generate priorities based on data
        priorities: List[PriorityItem] = []
        the_one_thing = "Complete your most important work for today"
        the_one_thing_reasoning = "Focus on the task that will have the biggest impact."

        # If we have lagging OKRs, prioritize those
        if okr_summary and okr_summary.get('lagging_krs'):
            lagging = okr_summary['lagging_krs']
            the_one_thing = f"Focus on: {lagging[0]}"
            the_one_thing_reasoning = f"This key result is lagging and needs attention to stay on track for {okr_summary['quarter']}."

            for i, kr in enumerate(lagging[:3]):
                priorities.append(PriorityItem(
                    title=kr,
                    reasoning="Lagging behind schedule - needs immediate focus",
                    tier=i + 1,
                    okr_link=okr_summary.get('quarter')
                ))

        # If user provided focus areas, incorporate them
        if generate_request.focus_areas:
            for i, area in enumerate(generate_request.focus_areas[:3]):
                if not any(p.title.lower() == area.lower() for p in priorities):
                    priorities.append(PriorityItem(
                        title=area,
                        reasoning="User-specified focus area",
                        tier=len(priorities) + 1
                    ))

        # Ensure we have at least 3 priorities
        while len(priorities) < 3:
            priorities.append(PriorityItem(
                title=f"Priority task {len(priorities) + 1}",
                reasoning="Placeholder - update with your actual priorities",
                tier=len(priorities) + 1
            ))

        # Generate energy insight
        energy_insight = None
        if energy_summary:
            energy_insight = (
                f"Your average energy this week is {energy_summary['avg_energy']}/10. "
                f"{energy_summary.get('recommendation', 'Schedule demanding tasks during your peak hours.')}"
            )

        # Generate OKR context
        okr_context = None
        if okr_summary:
            okr_context = (
                f"{okr_summary['quarter']}: {okr_summary['total_objectives']} objectives at "
                f"{okr_summary['avg_progress']:.0f}% average progress. "
                f"{okr_summary['lagging_count']} key results need attention."
            )

        # Generate time blocks
        peak_hours = energy_summary.get('peak_hours', [9, 10, 11]) if energy_summary else [9, 10, 11]
        time_blocks = generate_time_blocks(
            available_hours=generate_request.available_hours,
            peak_hours=peak_hours,
            priorities=priorities
        )

        # Success criteria
        success_criteria = f"Complete {the_one_thing}. Make progress on Tier 1 priorities."

        roadmap = RoadmapData(
            date=today,
            the_one_thing=the_one_thing,
            the_one_thing_reasoning=the_one_thing_reasoning,
            top_priorities=priorities[:3],
            time_blocks=time_blocks,
            energy_insight=energy_insight,
            okr_context=okr_context,
            success_criteria=success_criteria
        )

        # Save roadmap to file
        ROADMAPS_DIR.mkdir(parents=True, exist_ok=True)
        roadmap_file = ROADMAPS_DIR / f"{today}.md"
        roadmap_content = f"""# Daily Roadmap - {today}

## THE ONE THING
{the_one_thing}

**Why:** {the_one_thing_reasoning}

## Top Priorities
{"".join(f"- [{p.tier}] {p.title}: {p.reasoning}\\n" for p in priorities[:3])}

## Time Blocks
{"".join(f"- {b.start_time}-{b.end_time}: {b.activity} ({b.block_type})\\n" for b in time_blocks)}

## Energy Insight
{energy_insight or "No energy data available"}

## OKR Context
{okr_context or "No OKR data available"}

## Success Criteria
{success_criteria}
"""
        roadmap_file.write_text(roadmap_content)

        return APIResponse(
            success=True,
            data=roadmap,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=f"Failed to generate roadmap: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/today", response_model=APIResponse[RoadmapData])
async def get_today_roadmap(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[RoadmapData]:
    """
    Get today's roadmap if it exists.

    Returns the saved roadmap for today, or error if none exists.
    Use POST /generate to create one first.

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        today = datetime.now(PACIFIC).strftime("%Y-%m-%d")
        roadmap_file = ROADMAPS_DIR / f"{today}.md"

        if not roadmap_file.exists():
            return APIResponse(
                success=False,
                error=f"No roadmap exists for {today}. Use POST /generate to create one.",
                meta=ResponseMeta(**meta_dict),
            )

        # Parse existing roadmap (simplified - return basic data)
        content = roadmap_file.read_text()

        # Extract THE ONE THING
        the_one_thing = "Unknown"
        for line in content.split('\n'):
            if line.startswith('## THE ONE THING'):
                idx = content.index('## THE ONE THING')
                next_section = content.find('##', idx + 20)
                section = content[idx:next_section].strip().split('\n')
                if len(section) > 1:
                    the_one_thing = section[1].strip()
                break

        roadmap = RoadmapData(
            date=today,
            the_one_thing=the_one_thing,
            the_one_thing_reasoning="See saved roadmap for details",
            top_priorities=[],
            time_blocks=[],
            success_criteria="See saved roadmap"
        )

        return APIResponse(
            success=True,
            data=roadmap,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=f"Failed to load roadmap: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/history", response_model=APIResponse[List[RoadmapHistoryItem]])
async def get_roadmap_history(
    request: Request,
    days: int = Query(7, ge=1, le=30, description="Number of days to look back"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[List[RoadmapHistoryItem]]:
    """
    Get roadmap history.

    Returns list of past roadmaps with their THE ONE THING focus.

    **Query Parameters:**
    - days: Number of days to look back (default 7, max 30)

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        history: List[RoadmapHistoryItem] = []

        if ROADMAPS_DIR.exists():
            for f in sorted(ROADMAPS_DIR.glob("*.md"), reverse=True)[:days]:
                content = f.read_text()

                # Extract THE ONE THING
                the_one_thing = "Unknown"
                for line in content.split('\n'):
                    if line.startswith('## THE ONE THING'):
                        idx = content.index('## THE ONE THING')
                        section = content[idx:].split('\n')
                        if len(section) > 1:
                            the_one_thing = section[1].strip()
                        break

                history.append(RoadmapHistoryItem(
                    date=f.stem,  # filename without .md
                    the_one_thing=the_one_thing,
                    completed=False  # Could track this in future
                ))

        return APIResponse(
            success=True,
            data=history,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=f"Failed to load history: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/refocus", response_model=APIResponse[dict])
async def refocus(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[dict]:
    """
    Mid-day refocus endpoint.

    Returns the most important thing to work on right now
    based on today's roadmap and current time.

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        now = datetime.now(PACIFIC)
        today = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M")
        hours_remaining = max(0, 17 - now.hour)  # Assume 5 PM end

        roadmap_file = ROADMAPS_DIR / f"{today}.md"

        if not roadmap_file.exists():
            return APIResponse(
                success=True,
                data={
                    "focus": "No roadmap for today - generate one first",
                    "time": current_time,
                    "hours_remaining": hours_remaining,
                    "suggestion": "Create a roadmap with POST /api/roadmap/generate"
                },
                meta=ResponseMeta(**meta_dict),
            )

        # Parse roadmap
        content = roadmap_file.read_text()

        # Extract THE ONE THING
        the_one_thing = "Complete your most important task"
        for line in content.split('\n'):
            if line.startswith('## THE ONE THING'):
                idx = content.index('## THE ONE THING')
                section = content[idx:].split('\n')
                if len(section) > 1:
                    the_one_thing = section[1].strip()
                break

        # Determine appropriate suggestion based on time
        if hours_remaining <= 0:
            suggestion = "End of day - wrap up and plan for tomorrow"
        elif hours_remaining <= 2:
            suggestion = "Final hours - focus on closing tasks, not starting new ones"
        else:
            suggestion = f"You have {hours_remaining} hours. Focus on THE ONE THING."

        return APIResponse(
            success=True,
            data={
                "focus": the_one_thing,
                "time": current_time,
                "hours_remaining": hours_remaining,
                "suggestion": suggestion
            },
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=f"Refocus failed: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )
