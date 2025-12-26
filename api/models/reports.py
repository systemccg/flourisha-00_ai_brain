"""
Morning Report Models

Pydantic models for morning report API endpoints.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field


class TheOneThing(BaseModel):
    """THE ONE THING recommendation for the day."""
    task: str = Field(..., description="The recommended task")
    why: str = Field(..., description="Why this task is most important")
    estimated_hours: Optional[float] = Field(None, description="Estimated time to complete")
    best_window: Optional[str] = Field(None, description="Best time window for this task")
    okr_impact: Optional[float] = Field(None, description="OKR contribution score (0-1)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "task": "Complete Q1 revenue forecast model",
                "why": "95% contribution to OKR 1 (Revenue System), due tomorrow",
                "estimated_hours": 2.5,
                "best_window": "9:00 AM - 11:30 AM",
                "okr_impact": 0.95
            }
        }
    }


class EnergyDataPoint(BaseModel):
    """Energy/focus tracking data point."""
    time: str = Field(..., description="Time of measurement")
    energy_level: int = Field(..., description="Energy level (1-10)")
    focus_level: int = Field(..., description="Focus level (1-10)")
    activity: Optional[str] = Field(None, description="Activity at this time")

    model_config = {
        "json_schema_extra": {
            "example": {
                "time": "09:00",
                "energy_level": 8,
                "focus_level": 7,
                "activity": "Deep work"
            }
        }
    }


class YesterdayRecap(BaseModel):
    """Summary of yesterday's productivity."""
    tasks_completed: int = Field(..., description="Number of tasks completed")
    hours_worked: Optional[float] = Field(None, description="Total hours worked")
    energy_average: Optional[float] = Field(None, description="Average energy level")
    focus_average: Optional[float] = Field(None, description="Average focus level")
    highlights: List[str] = Field(default_factory=list, description="Key accomplishments")
    energy_data: List[EnergyDataPoint] = Field(default_factory=list, description="Energy tracking data")

    model_config = {
        "json_schema_extra": {
            "example": {
                "tasks_completed": 8,
                "hours_worked": 7.5,
                "energy_average": 7.2,
                "focus_average": 6.8,
                "highlights": ["Completed API design", "Shipped v2.1 release"],
                "energy_data": []
            }
        }
    }


class TodayPlan(BaseModel):
    """Today's planned schedule and tasks."""
    scheduled_tasks: List[str] = Field(default_factory=list, description="Tasks scheduled for today")
    meetings: List[Dict[str, str]] = Field(default_factory=list, description="Calendar events")
    energy_forecast: Optional[str] = Field(None, description="Energy forecast for today")
    recommended_windows: List[str] = Field(default_factory=list, description="Recommended focus windows")

    model_config = {
        "json_schema_extra": {
            "example": {
                "scheduled_tasks": ["Review PRs", "Team standup", "API documentation"],
                "meetings": [{"time": "10:00", "title": "Team Standup"}],
                "energy_forecast": "High energy morning, lower afternoon",
                "recommended_windows": ["9:00 AM - 11:30 AM", "2:00 PM - 3:30 PM"]
            }
        }
    }


class OKRProgress(BaseModel):
    """OKR progress summary."""
    objective: str = Field(..., description="OKR objective")
    progress_percent: int = Field(..., description="Progress percentage (0-100)")
    key_results: List[Dict[str, Any]] = Field(default_factory=list, description="Key results status")

    model_config = {
        "json_schema_extra": {
            "example": {
                "objective": "Launch Flourisha MVP",
                "progress_percent": 65,
                "key_results": [
                    {"name": "API complete", "progress": 80},
                    {"name": "Frontend ready", "progress": 50}
                ]
            }
        }
    }


class MorningReport(BaseModel):
    """Complete morning report."""
    date: str = Field(..., description="Report date (YYYY-MM-DD)")
    generated_at: str = Field(..., description="Generation timestamp")
    the_one_thing: Optional[TheOneThing] = Field(None, description="THE ONE THING recommendation")
    yesterday_recap: Optional[YesterdayRecap] = Field(None, description="Yesterday's summary")
    today_plan: Optional[TodayPlan] = Field(None, description="Today's plan")
    okrs: List[OKRProgress] = Field(default_factory=list, description="OKR progress")
    critical_emails: List[str] = Field(default_factory=list, description="Critical emails requiring attention")
    blockers: List[str] = Field(default_factory=list, description="Current blockers")

    model_config = {
        "json_schema_extra": {
            "example": {
                "date": "2025-12-26",
                "generated_at": "2025-12-26T07:00:00-08:00",
                "the_one_thing": None,
                "yesterday_recap": None,
                "today_plan": None,
                "okrs": [],
                "critical_emails": [],
                "blockers": []
            }
        }
    }


class ReportHistoryItem(BaseModel):
    """Summary of a historical report."""
    date: str = Field(..., description="Report date")
    the_one_thing: Optional[str] = Field(None, description="THE ONE THING task")
    tasks_completed: Optional[int] = Field(None, description="Tasks completed that day")
    energy_average: Optional[float] = Field(None, description="Average energy level")

    model_config = {
        "json_schema_extra": {
            "example": {
                "date": "2025-12-25",
                "the_one_thing": "Complete holiday planning",
                "tasks_completed": 5,
                "energy_average": 6.5
            }
        }
    }


class ReportHistory(BaseModel):
    """Paginated list of historical reports."""
    reports: List[ReportHistoryItem] = Field(..., description="Report summaries")
    total: int = Field(..., description="Total report count")
    page: int = Field(..., description="Current page (1-based)")
    page_size: int = Field(..., description="Items per page")
    has_more: bool = Field(..., description="Whether more pages exist")


class GenerateReportResponse(BaseModel):
    """Response after queuing report generation."""
    queued: bool = Field(..., description="Whether report generation was queued")
    message: str = Field(..., description="Status message")
    estimated_seconds: Optional[int] = Field(None, description="Estimated time until ready")
