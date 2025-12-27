"""
Energy Tracking Router

Endpoints for tracking energy levels and focus quality.
Works directly with Supabase energy_tracking table.
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


router = APIRouter(prefix="/api/energy", tags=["Energy Tracking"])

# Pacific timezone for all time operations
PACIFIC = ZoneInfo("America/Los_Angeles")


def get_supabase_client() -> Optional[Client]:
    """Get Supabase client for database operations."""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_KEY', os.getenv('SUPABASE_KEY'))

    if url and key:
        return create_client(url, key)
    return None


# === Request/Response Models ===

class EnergyTrackingRequest(BaseModel):
    """Request to record energy tracking."""
    energy_level: int = Field(..., ge=1, le=10, description="Energy level from 1 (exhausted) to 10 (peak)")
    focus_quality: str = Field(..., pattern="^(deep|shallow|distracted)$", description="Focus quality: deep, shallow, or distracted")
    source: str = Field(default="manual", pattern="^(chrome_extension|sms|manual)$", description="Tracking source")
    notes: Optional[str] = Field(None, max_length=500, description="Optional contextual notes")
    current_task: Optional[str] = Field(None, max_length=200, description="Current task being worked on")


class EnergyTrackingEntry(BaseModel):
    """Single energy tracking entry."""
    id: str = Field(..., description="Entry UUID")
    timestamp: str = Field(..., description="ISO timestamp (Pacific)")
    energy_level: int = Field(..., description="Energy level 1-10")
    focus_quality: str = Field(..., description="Focus quality")
    source: str = Field(..., description="Tracking source")
    notes: Optional[str] = Field(None, description="Notes")


class EnergyTrackingResponse(BaseModel):
    """Response for creating energy tracking."""
    id: str = Field(..., description="Created entry UUID")
    recorded_at: str = Field(..., description="Recording timestamp")
    energy_level: int = Field(..., description="Recorded energy level")
    focus_quality: str = Field(..., description="Recorded focus quality")


class EnergyHistoryResponse(BaseModel):
    """Response for energy history query."""
    entries: List[EnergyTrackingEntry] = Field(..., description="Energy entries")
    total: int = Field(..., description="Total entries")
    date_range: dict = Field(..., description="Date range of query")


class EnergySummaryResponse(BaseModel):
    """Response for energy summary/analytics."""
    period: str = Field(..., description="Summary period")
    avg_energy: float = Field(..., description="Average energy level")
    deep_focus_count: int = Field(..., description="Count of deep focus entries")
    shallow_focus_count: int = Field(..., description="Count of shallow focus entries")
    distracted_count: int = Field(..., description="Count of distracted entries")
    total_readings: int = Field(..., description="Total number of readings")
    energy_by_hour: Optional[dict] = Field(None, description="Energy by hour of day")
    focus_distribution: Optional[dict] = Field(None, description="Focus quality percentages")


class EnergyPatternResponse(BaseModel):
    """Response for energy pattern analysis."""
    day_of_week: int = Field(..., description="Day of week (0=Monday)")
    day_name: str = Field(..., description="Day name")
    morning_avg: Optional[float] = Field(None, description="Morning energy average (8-12)")
    afternoon_avg: Optional[float] = Field(None, description="Afternoon energy average (12-17)")
    evening_avg: Optional[float] = Field(None, description="Evening energy average (17-20)")
    overall_avg: Optional[float] = Field(None, description="Overall average")


class EnergyForecastResponse(BaseModel):
    """Response for energy forecast."""
    date: str = Field(..., description="Forecast date")
    morning_forecast: float = Field(..., description="Morning energy forecast")
    afternoon_forecast: float = Field(..., description="Afternoon energy forecast")
    evening_forecast: float = Field(..., description="Evening energy forecast")
    confidence: str = Field(..., description="Forecast confidence level")
    recommendations: List[str] = Field(default_factory=list, description="Scheduling recommendations")


# === Endpoints ===

@router.post("", response_model=APIResponse[EnergyTrackingResponse])
async def record_energy(
    request: Request,
    tracking_request: EnergyTrackingRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[EnergyTrackingResponse]:
    """
    Record an energy tracking entry.

    Stores energy level (1-10) and focus quality for productivity analysis.
    Typically called every 90 minutes during active hours.

    **Request Body:**
    - energy_level: 1 (exhausted) to 10 (peak energy)
    - focus_quality: deep, shallow, or distracted
    - source: chrome_extension, sms, or manual
    - notes: Optional contextual notes

    **Response:**
    - id: Created entry UUID
    - recorded_at: Recording timestamp (Pacific)
    - energy_level: Recorded level
    - focus_quality: Recorded quality

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or user.uid

    try:
        client = get_supabase_client()
        if not client:
            return APIResponse(
                success=False,
                data=None,
                error="Database connection not available",
                meta=ResponseMeta(**meta_dict),
            )

        now = datetime.now(PACIFIC)

        # Insert tracking entry
        result = client.table('energy_tracking').insert({
            'tenant_id': tenant_id,
            'user_id': user.email or user.uid,
            'timestamp': now.isoformat(),
            'energy_level': tracking_request.energy_level,
            'focus_quality': tracking_request.focus_quality,
            'source': tracking_request.source,
            'notes': tracking_request.notes,
        }).execute()

        if result.data:
            entry = result.data[0]
            response_data = EnergyTrackingResponse(
                id=entry['id'],
                recorded_at=now.isoformat(),
                energy_level=tracking_request.energy_level,
                focus_quality=tracking_request.focus_quality,
            )
            return APIResponse(
                success=True,
                data=response_data,
                meta=ResponseMeta(**meta_dict),
            )
        else:
            return APIResponse(
                success=False,
                data=None,
                error="Failed to record energy tracking",
                meta=ResponseMeta(**meta_dict),
            )

    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to record energy: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/history", response_model=APIResponse[EnergyHistoryResponse])
async def get_energy_history(
    request: Request,
    days: int = Query(default=7, ge=1, le=90, description="Number of days to retrieve"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[EnergyHistoryResponse]:
    """
    Get energy tracking history for the specified number of days.

    Returns all energy entries in reverse chronological order.

    **Query Parameters:**
    - days: Number of days to retrieve (default 7, max 90)

    **Response:**
    - entries: List of energy entries
    - total: Total count
    - date_range: Start and end dates

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or user.uid
    user_id = user.email or user.uid

    try:
        client = get_supabase_client()
        if not client:
            return APIResponse(
                success=False,
                data=None,
                error="Database connection not available",
                meta=ResponseMeta(**meta_dict),
            )

        now = datetime.now(PACIFIC)
        start_date = now - timedelta(days=days)

        result = client.table('energy_tracking').select('*').eq(
            'tenant_id', tenant_id
        ).eq('user_id', user_id).gte(
            'timestamp', start_date.isoformat()
        ).order('timestamp', desc=True).execute()

        entries = []
        for row in result.data or []:
            entries.append(EnergyTrackingEntry(
                id=row['id'],
                timestamp=row['timestamp'],
                energy_level=row['energy_level'],
                focus_quality=row['focus_quality'],
                source=row['source'],
                notes=row.get('notes'),
            ))

        response_data = EnergyHistoryResponse(
            entries=entries,
            total=len(entries),
            date_range={
                "start": start_date.isoformat(),
                "end": now.isoformat(),
            },
        )

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to get energy history: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/summary", response_model=APIResponse[EnergySummaryResponse])
async def get_energy_summary(
    request: Request,
    days: int = Query(default=7, ge=1, le=90, description="Number of days to analyze"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[EnergySummaryResponse]:
    """
    Get energy summary and analytics for the specified period.

    Returns average energy, focus quality distribution, and patterns.

    **Query Parameters:**
    - days: Number of days to analyze (default 7, max 90)

    **Response:**
    - period: Summary period description
    - avg_energy: Average energy level
    - deep/shallow/distracted counts
    - energy_by_hour: Optional hourly breakdown
    - focus_distribution: Percentage breakdown

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or user.uid
    user_id = user.email or user.uid

    try:
        client = get_supabase_client()
        if not client:
            return APIResponse(
                success=False,
                data=None,
                error="Database connection not available",
                meta=ResponseMeta(**meta_dict),
            )

        now = datetime.now(PACIFIC)
        start_date = now - timedelta(days=days)

        result = client.table('energy_tracking').select('*').eq(
            'tenant_id', tenant_id
        ).eq('user_id', user_id).gte(
            'timestamp', start_date.isoformat()
        ).execute()

        data = result.data or []

        if not data:
            return APIResponse(
                success=True,
                data=EnergySummaryResponse(
                    period=f"Last {days} days",
                    avg_energy=0.0,
                    deep_focus_count=0,
                    shallow_focus_count=0,
                    distracted_count=0,
                    total_readings=0,
                    energy_by_hour=None,
                    focus_distribution=None,
                ),
                meta=ResponseMeta(**meta_dict),
            )

        # Calculate statistics
        energy_levels = [row['energy_level'] for row in data]
        avg_energy = sum(energy_levels) / len(energy_levels)

        focus_counts = {'deep': 0, 'shallow': 0, 'distracted': 0}
        for row in data:
            focus = row['focus_quality']
            if focus in focus_counts:
                focus_counts[focus] += 1

        total = len(data)
        focus_distribution = {
            k: round(v / total * 100, 1) for k, v in focus_counts.items()
        }

        # Calculate energy by hour of day
        hourly_energy = {}
        for row in data:
            try:
                ts = datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00'))
                hour = ts.hour
                if hour not in hourly_energy:
                    hourly_energy[hour] = []
                hourly_energy[hour].append(row['energy_level'])
            except Exception:
                pass

        energy_by_hour = {
            str(h): round(sum(vals) / len(vals), 1)
            for h, vals in sorted(hourly_energy.items())
        }

        response_data = EnergySummaryResponse(
            period=f"Last {days} days",
            avg_energy=round(avg_energy, 1),
            deep_focus_count=focus_counts['deep'],
            shallow_focus_count=focus_counts['shallow'],
            distracted_count=focus_counts['distracted'],
            total_readings=total,
            energy_by_hour=energy_by_hour if energy_by_hour else None,
            focus_distribution=focus_distribution,
        )

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to get energy summary: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/patterns", response_model=APIResponse[List[EnergyPatternResponse]])
async def get_energy_patterns(
    request: Request,
    days: int = Query(default=30, ge=7, le=90, description="Days to analyze for patterns"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[List[EnergyPatternResponse]]:
    """
    Get energy patterns by day of week.

    Analyzes historical data to identify energy patterns.
    Returns average energy by time of day for each day of week.

    **Query Parameters:**
    - days: Number of days to analyze (default 30, min 7, max 90)

    **Response:**
    List of patterns for each day of week with:
    - day_of_week: 0 (Monday) to 6 (Sunday)
    - morning/afternoon/evening averages
    - overall average

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or user.uid
    user_id = user.email or user.uid

    try:
        client = get_supabase_client()
        if not client:
            return APIResponse(
                success=False,
                data=None,
                error="Database connection not available",
                meta=ResponseMeta(**meta_dict),
            )

        now = datetime.now(PACIFIC)
        start_date = now - timedelta(days=days)

        result = client.table('energy_tracking').select('*').eq(
            'tenant_id', tenant_id
        ).eq('user_id', user_id).gte(
            'timestamp', start_date.isoformat()
        ).execute()

        data = result.data or []

        # Group by day of week and time of day
        day_patterns = {i: {'morning': [], 'afternoon': [], 'evening': [], 'all': []} for i in range(7)}
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        for row in data:
            try:
                ts = datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00'))
                dow = ts.weekday()
                hour = ts.hour
                energy = row['energy_level']

                day_patterns[dow]['all'].append(energy)

                if 8 <= hour < 12:
                    day_patterns[dow]['morning'].append(energy)
                elif 12 <= hour < 17:
                    day_patterns[dow]['afternoon'].append(energy)
                elif 17 <= hour < 20:
                    day_patterns[dow]['evening'].append(energy)
            except Exception:
                pass

        patterns = []
        for dow in range(7):
            data_for_day = day_patterns[dow]

            def avg_or_none(lst):
                return round(sum(lst) / len(lst), 1) if lst else None

            patterns.append(EnergyPatternResponse(
                day_of_week=dow,
                day_name=day_names[dow],
                morning_avg=avg_or_none(data_for_day['morning']),
                afternoon_avg=avg_or_none(data_for_day['afternoon']),
                evening_avg=avg_or_none(data_for_day['evening']),
                overall_avg=avg_or_none(data_for_day['all']),
            ))

        return APIResponse(
            success=True,
            data=patterns,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to get energy patterns: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/forecast", response_model=APIResponse[EnergyForecastResponse])
async def get_energy_forecast(
    request: Request,
    date: Optional[str] = Query(None, description="Forecast date (YYYY-MM-DD). Defaults to today."),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[EnergyForecastResponse]:
    """
    Get energy forecast for a specific date.

    Uses historical patterns to forecast energy levels.
    Includes scheduling recommendations.

    **Query Parameters:**
    - date: Forecast date in YYYY-MM-DD format (defaults to today)

    **Response:**
    - date: Forecast date
    - morning/afternoon/evening forecasts
    - confidence: High, Medium, or Low
    - recommendations: Task scheduling suggestions

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or user.uid
    user_id = user.email or user.uid

    try:
        # Parse target date
        if date:
            target_date = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=PACIFIC)
        else:
            target_date = datetime.now(PACIFIC)

        target_dow = target_date.weekday()

        client = get_supabase_client()
        if not client:
            return APIResponse(
                success=False,
                data=None,
                error="Database connection not available",
                meta=ResponseMeta(**meta_dict),
            )

        # Get last 60 days of data for the same day of week
        now = datetime.now(PACIFIC)
        start_date = now - timedelta(days=60)

        result = client.table('energy_tracking').select('*').eq(
            'tenant_id', tenant_id
        ).eq('user_id', user_id).gte(
            'timestamp', start_date.isoformat()
        ).execute()

        data = result.data or []

        # Filter to same day of week
        morning_vals = []
        afternoon_vals = []
        evening_vals = []

        for row in data:
            try:
                ts = datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00'))
                if ts.weekday() == target_dow:
                    hour = ts.hour
                    energy = row['energy_level']

                    if 8 <= hour < 12:
                        morning_vals.append(energy)
                    elif 12 <= hour < 17:
                        afternoon_vals.append(energy)
                    elif 17 <= hour < 20:
                        evening_vals.append(energy)
            except Exception:
                pass

        def avg_or_default(lst, default=6.0):
            return round(sum(lst) / len(lst), 1) if lst else default

        morning_forecast = avg_or_default(morning_vals)
        afternoon_forecast = avg_or_default(afternoon_vals)
        evening_forecast = avg_or_default(evening_vals)

        # Calculate confidence
        total_data_points = len(morning_vals) + len(afternoon_vals) + len(evening_vals)
        if total_data_points >= 15:
            confidence = "high"
        elif total_data_points >= 5:
            confidence = "medium"
        else:
            confidence = "low"

        # Generate recommendations
        recommendations = []
        peak_energy = max(morning_forecast, afternoon_forecast, evening_forecast)

        if morning_forecast == peak_energy:
            recommendations.append("Schedule demanding tasks for morning when energy is highest")
        elif afternoon_forecast == peak_energy:
            recommendations.append("Peak energy expected in afternoon - save complex work")
        else:
            recommendations.append("Energy peaks in evening - schedule important work later")

        if afternoon_forecast < 5:
            recommendations.append("Consider a short break or walk after lunch")

        if morning_forecast >= 7:
            recommendations.append("Morning is great for deep focus work")

        response_data = EnergyForecastResponse(
            date=target_date.strftime("%Y-%m-%d"),
            morning_forecast=morning_forecast,
            afternoon_forecast=afternoon_forecast,
            evening_forecast=evening_forecast,
            confidence=confidence,
            recommendations=recommendations,
        )

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except ValueError as e:
        return APIResponse(
            success=False,
            data=None,
            error="Invalid date format. Use YYYY-MM-DD",
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to get energy forecast: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/today", response_model=APIResponse[dict])
async def get_today_energy(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[dict]:
    """
    Get today's energy tracking summary.

    Quick view of today's entries and current energy state.

    **Response:**
    - date: Today's date
    - entries_count: Number of entries today
    - latest_entry: Most recent entry
    - avg_energy: Average energy today
    - current_period: Morning/Afternoon/Evening

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or user.uid
    user_id = user.email or user.uid

    try:
        client = get_supabase_client()
        if not client:
            return APIResponse(
                success=False,
                data=None,
                error="Database connection not available",
                meta=ResponseMeta(**meta_dict),
            )

        now = datetime.now(PACIFIC)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        result = client.table('energy_tracking').select('*').eq(
            'tenant_id', tenant_id
        ).eq('user_id', user_id).gte(
            'timestamp', today_start.isoformat()
        ).order('timestamp', desc=True).execute()

        data = result.data or []

        # Determine current period
        hour = now.hour
        if 8 <= hour < 12:
            current_period = "morning"
        elif 12 <= hour < 17:
            current_period = "afternoon"
        elif 17 <= hour < 20:
            current_period = "evening"
        else:
            current_period = "off_hours"

        if data:
            latest = data[0]
            avg_energy = sum(row['energy_level'] for row in data) / len(data)

            response_data = {
                "date": now.strftime("%Y-%m-%d"),
                "entries_count": len(data),
                "latest_entry": {
                    "timestamp": latest['timestamp'],
                    "energy_level": latest['energy_level'],
                    "focus_quality": latest['focus_quality'],
                },
                "avg_energy": round(avg_energy, 1),
                "current_period": current_period,
            }
        else:
            response_data = {
                "date": now.strftime("%Y-%m-%d"),
                "entries_count": 0,
                "latest_entry": None,
                "avg_energy": None,
                "current_period": current_period,
            }

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to get today's energy: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )
