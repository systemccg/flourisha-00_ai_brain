"""
Reports Router

Morning report and productivity report endpoints.
Wraps the existing morning report generation scripts.
"""
import json
import logging
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import HTMLResponse

from models.response import APIResponse, ResponseMeta
from models.reports import (
    MorningReport,
    GenerateReportResponse,
    ReportHistory,
    ReportHistoryItem,
    TheOneThing,
    YesterdayRecap,
    TodayPlan,
    OKRProgress,
    EnergyDataPoint,
)
from middleware.auth import get_current_user, UserContext


router = APIRouter(prefix="/api/reports", tags=["Reports"])
logger = logging.getLogger(__name__)

# Pacific timezone for timestamps
PACIFIC = ZoneInfo("America/Los_Angeles")

# Paths to data directories
AI_BRAIN_ROOT = Path("/root/flourisha/00_AI_Brain")
DAILY_ANALYSIS_DIR = AI_BRAIN_ROOT / "history" / "daily-analysis"
PARA_ANALYSIS_DIR = AI_BRAIN_ROOT / "history" / "para-analysis"
CONTEXT_DIR = AI_BRAIN_ROOT / "context"
REPORTS_DIR = AI_BRAIN_ROOT / "history" / "morning-reports"


def load_json_file(path: Path) -> dict:
    """Load JSON file, return empty dict if not found."""
    try:
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Error loading {path}: {e}")
    return {}


def load_yesterday_analysis() -> dict:
    """Load yesterday's productivity analysis."""
    yesterday = datetime.now(PACIFIC) - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")
    file_path = DAILY_ANALYSIS_DIR / f"{date_str}.json"
    return load_json_file(file_path)


def load_latest_para_analysis() -> dict:
    """Load most recent PARA analysis."""
    try:
        analysis_files = sorted(PARA_ANALYSIS_DIR.glob("*.json"), reverse=True)
        if analysis_files:
            with open(analysis_files[0], 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Error loading PARA analysis: {e}")
    return {}


def load_okrs() -> list:
    """Load OKR data from context."""
    okr_path = CONTEXT_DIR / "okrs.json"
    data = load_json_file(okr_path)
    return data.get("okrs", [])


def load_blockers() -> list:
    """Load current blockers."""
    blockers_path = CONTEXT_DIR / "blockers.json"
    data = load_json_file(blockers_path)
    return [b.get("description", str(b)) for b in data.get("blockers", [])]


def build_the_one_thing(tasks: list, okrs: list) -> TheOneThing:
    """Build THE ONE THING recommendation."""
    # Simple algorithm: find highest priority task
    if not tasks:
        return TheOneThing(
            task="Review and plan your day",
            why="No specific tasks found - start with planning",
            estimated_hours=0.5,
            best_window="Morning",
        )

    # For now, return first task as placeholder
    # Real implementation would use the scoring algorithm from docs
    top_task = tasks[0] if tasks else {}
    return TheOneThing(
        task=top_task.get("name", "Start your most important project"),
        why="Highest priority item for today",
        estimated_hours=top_task.get("estimated_hours", 2.0),
        best_window="9:00 AM - 11:30 AM (high energy window)",
        okr_impact=0.8,
    )


def build_yesterday_recap(analysis: dict) -> YesterdayRecap:
    """Build yesterday's recap from analysis data."""
    return YesterdayRecap(
        tasks_completed=analysis.get("tasks_completed", 0),
        hours_worked=analysis.get("hours_worked"),
        energy_average=analysis.get("energy_average"),
        focus_average=analysis.get("focus_average"),
        highlights=analysis.get("highlights", []),
        energy_data=[
            EnergyDataPoint(**d) for d in analysis.get("energy_data", [])
        ] if analysis.get("energy_data") else [],
    )


def build_today_plan(para_analysis: dict) -> TodayPlan:
    """Build today's plan from PARA analysis."""
    return TodayPlan(
        scheduled_tasks=para_analysis.get("scheduled_tasks", []),
        meetings=para_analysis.get("meetings", []),
        energy_forecast=para_analysis.get("energy_forecast"),
        recommended_windows=para_analysis.get("recommended_windows", [
            "9:00 AM - 11:30 AM",
            "2:00 PM - 3:30 PM",
        ]),
    )


def build_okr_progress(okrs: list) -> list:
    """Build OKR progress summaries."""
    result = []
    for okr in okrs:
        if isinstance(okr, dict):
            result.append(OKRProgress(
                objective=okr.get("objective", "Unnamed OKR"),
                progress_percent=okr.get("progress", 0),
                key_results=okr.get("key_results", []),
            ))
    return result


async def generate_report_task(date_str: str, tenant_id: str):
    """Background task to generate morning report.

    This invokes the existing morning report generator script.
    """
    try:
        import subprocess
        script_path = AI_BRAIN_ROOT / "scripts" / "morning-report-generator.py"

        if script_path.exists():
            result = subprocess.run(
                ["python3", str(script_path)],
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout
            )
            logger.info(f"Morning report generation: {result.returncode}")
            if result.returncode != 0:
                logger.error(f"Report generation failed: {result.stderr}")
        else:
            logger.warning(f"Morning report script not found: {script_path}")
    except Exception as e:
        logger.error(f"Error generating report: {e}")


@router.post("/morning/generate", response_model=APIResponse[GenerateReportResponse])
async def generate_morning_report(
    request: Request,
    background_tasks: BackgroundTasks,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[GenerateReportResponse]:
    """Queue morning report generation.

    Triggers background generation of the morning report.
    The report will be sent via email when complete.

    Note: This endpoint queues the generation - it doesn't wait for completion.
    Use GET /reports/morning/today to retrieve the generated report.
    """
    now = datetime.now(PACIFIC)
    date_str = now.strftime("%Y-%m-%d")
    tenant_id = user.tenant_id or "default"

    # Queue background generation
    background_tasks.add_task(generate_report_task, date_str, tenant_id)

    meta_dict = request.state.get_meta()

    return APIResponse(
        success=True,
        data=GenerateReportResponse(
            queued=True,
            message=f"Morning report generation queued for {date_str}",
            estimated_seconds=30,
        ),
        meta=ResponseMeta(**meta_dict),
    )


@router.get("/morning/today", response_model=APIResponse[MorningReport])
async def get_today_report(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[MorningReport]:
    """Get today's morning report.

    Returns the morning report for today, assembling data from
    various sources including yesterday's analysis, OKRs, and
    today's planned tasks.

    If no pre-generated report exists, builds one on-demand from
    available data.
    """
    now = datetime.now(PACIFIC)
    date_str = now.strftime("%Y-%m-%d")

    # Load data sources
    yesterday_analysis = load_yesterday_analysis()
    para_analysis = load_latest_para_analysis()
    okrs = load_okrs()
    blockers = load_blockers()

    # Build report components
    the_one_thing = build_the_one_thing(
        para_analysis.get("tasks", []),
        okrs,
    )
    yesterday_recap = build_yesterday_recap(yesterday_analysis)
    today_plan = build_today_plan(para_analysis)
    okr_progress = build_okr_progress(okrs)

    report = MorningReport(
        date=date_str,
        generated_at=now.isoformat(),
        the_one_thing=the_one_thing,
        yesterday_recap=yesterday_recap,
        today_plan=today_plan,
        okrs=okr_progress,
        critical_emails=[],  # Would integrate with Gmail service
        blockers=blockers,
    )

    meta_dict = request.state.get_meta()

    return APIResponse(
        success=True,
        data=report,
        meta=ResponseMeta(**meta_dict),
    )


@router.get("/morning/today/html", response_class=HTMLResponse)
async def get_today_report_html(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> HTMLResponse:
    """Get today's morning report as HTML.

    Returns the morning report formatted as HTML suitable for
    display in a browser or embedding in an email.
    """
    now = datetime.now(PACIFIC)
    date_str = now.strftime("%Y-%m-%d")

    # Load data sources
    yesterday_analysis = load_yesterday_analysis()
    para_analysis = load_latest_para_analysis()
    okrs = load_okrs()
    blockers = load_blockers()

    # Build components
    the_one_thing = build_the_one_thing(
        para_analysis.get("tasks", []),
        okrs,
    )
    yesterday_recap = build_yesterday_recap(yesterday_analysis)

    # Build HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Morning Report - {date_str}</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
            h1 {{ color: #2563eb; }}
            h2 {{ color: #374151; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px; }}
            .one-thing {{ background: #dbeafe; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .one-thing h3 {{ margin-top: 0; color: #1e40af; }}
            .stat {{ display: inline-block; padding: 10px 20px; background: #f3f4f6; border-radius: 8px; margin: 5px; }}
            .stat-value {{ font-size: 24px; font-weight: bold; color: #2563eb; }}
            .stat-label {{ font-size: 12px; color: #6b7280; }}
            .blocker {{ background: #fef2f2; padding: 10px; border-left: 4px solid #ef4444; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <h1>Morning Report</h1>
        <p><strong>{date_str}</strong> - Generated at {now.strftime('%I:%M %p')}</p>

        <div class="one-thing">
            <h3>THE ONE THING</h3>
            <p><strong>{the_one_thing.task}</strong></p>
            <p><em>{the_one_thing.why}</em></p>
            {f'<p>Best time: {the_one_thing.best_window}</p>' if the_one_thing.best_window else ''}
        </div>

        <h2>Yesterday Recap</h2>
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{yesterday_recap.tasks_completed}</div>
                <div class="stat-label">Tasks Completed</div>
            </div>
            {f'<div class="stat"><div class="stat-value">{yesterday_recap.energy_average:.1f}</div><div class="stat-label">Avg Energy</div></div>' if yesterday_recap.energy_average else ''}
            {f'<div class="stat"><div class="stat-value">{yesterday_recap.hours_worked:.1f}h</div><div class="stat-label">Hours Worked</div></div>' if yesterday_recap.hours_worked else ''}
        </div>

        {f'''<h2>Blockers</h2>
        {''.join([f'<div class="blocker">{b}</div>' for b in blockers])}''' if blockers else ''}

        <h2>OKR Progress</h2>
        {'<p>No OKRs configured</p>' if not okrs else ''.join([
            f'<div><strong>{okr.get("objective", "")}</strong>: {okr.get("progress", 0)}%</div>'
            for okr in okrs
        ])}

        <hr>
        <p style="color: #9ca3af; font-size: 12px;">Generated by Flourisha AI Brain</p>
    </body>
    </html>
    """

    return HTMLResponse(content=html)


@router.get("/morning/history", response_model=APIResponse[ReportHistory])
async def get_report_history(
    request: Request,
    page: int = 1,
    page_size: int = 30,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[ReportHistory]:
    """Get historical morning reports.

    Returns paginated list of past morning reports (last 30 days by default).
    """
    # Clamp page size
    page_size = max(1, min(30, page_size))

    # Get daily analysis files (these serve as report history)
    reports = []
    try:
        analysis_files = sorted(DAILY_ANALYSIS_DIR.glob("*.json"), reverse=True)

        offset = (page - 1) * page_size
        for file_path in analysis_files[offset:offset + page_size]:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    date_str = file_path.stem  # filename without extension
                    reports.append(ReportHistoryItem(
                        date=date_str,
                        the_one_thing=data.get("the_one_thing"),
                        tasks_completed=data.get("tasks_completed"),
                        energy_average=data.get("energy_average"),
                    ))
            except Exception as e:
                logger.warning(f"Error loading report {file_path}: {e}")

        total = len(analysis_files)
    except Exception as e:
        logger.error(f"Error listing report history: {e}")
        total = 0

    meta_dict = request.state.get_meta()

    return APIResponse(
        success=True,
        data=ReportHistory(
            reports=reports,
            total=total,
            page=page,
            page_size=page_size,
            has_more=(page * page_size) < total,
        ),
        meta=ResponseMeta(**meta_dict),
    )


@router.get("/morning/{date}", response_model=APIResponse[MorningReport])
async def get_report_by_date(
    request: Request,
    date: str,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[MorningReport]:
    """Get morning report for a specific date.

    Args:
        date: Date in YYYY-MM-DD format

    Returns the morning report for the specified date if available.
    """
    # Validate date format
    try:
        report_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    # Load data for that date
    analysis_path = DAILY_ANALYSIS_DIR / f"{date}.json"
    analysis = load_json_file(analysis_path)

    if not analysis:
        raise HTTPException(status_code=404, detail=f"No report found for {date}")

    # Build report from historical data
    report = MorningReport(
        date=date,
        generated_at=analysis.get("generated_at", f"{date}T07:00:00-08:00"),
        the_one_thing=TheOneThing(
            task=analysis.get("the_one_thing", "Not recorded"),
            why="Historical data",
        ) if analysis.get("the_one_thing") else None,
        yesterday_recap=build_yesterday_recap(analysis),
        today_plan=None,  # Historical reports don't have future plans
        okrs=[],
        critical_emails=[],
        blockers=analysis.get("blockers", []),
    )

    meta_dict = request.state.get_meta()

    return APIResponse(
        success=True,
        data=report,
        meta=ResponseMeta(**meta_dict),
    )
