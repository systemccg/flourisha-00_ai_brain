"""
Cron Endpoints Router

Internal endpoints for scheduled task execution.
These endpoints are called by pg_cron, systemd timers, or manual triggers.

Security: Validates internal cron header (X-Cron-Secret) for all endpoints.
No user authentication - these are system-to-system calls.

Available Cron Jobs:
- morning_report: Generate and send daily morning report (7 AM Pacific)
- queue_process: Process pending items in the processing queue
- cleanup_expired: Clean up expired sessions, tokens, and temp files
- sync_clickup: Sync ClickUp tasks with local cache
- health_check: Internal health check for all services
- daily_analysis: Run daily productivity analysis
- okr_rollup: Calculate OKR progress rollups
- embedding_refresh: Refresh stale embeddings
"""
import os
import hmac
import logging
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Request, HTTPException, Header, BackgroundTasks
from supabase import create_client, Client

from models.response import APIResponse, ResponseMeta
from models.crons import (
    CronJobType,
    CronExecutionStatus,
    CronTriggerRequest,
    CronExecutionResult,
    CronJobInfo,
    CronStatusResponse,
    CronLogEntry,
    CronLogsResponse,
)


router = APIRouter(prefix="/api/crons", tags=["Crons"])
logger = logging.getLogger(__name__)

# Pacific timezone for all cron operations
PACIFIC = ZoneInfo("America/Los_Angeles")

# Cron job configurations
CRON_JOBS: Dict[CronJobType, dict] = {
    CronJobType.MORNING_REPORT: {
        "schedule": "0 7 * * *",
        "description": "Generate and send daily morning report",
        "enabled": True,
    },
    CronJobType.QUEUE_PROCESS: {
        "schedule": "*/5 * * * *",
        "description": "Process pending items in the processing queue",
        "enabled": True,
    },
    CronJobType.CLEANUP_EXPIRED: {
        "schedule": "0 3 * * *",
        "description": "Clean up expired sessions, tokens, and temp files",
        "enabled": True,
    },
    CronJobType.SYNC_CLICKUP: {
        "schedule": "*/15 * * * *",
        "description": "Sync ClickUp tasks with local cache",
        "enabled": True,
    },
    CronJobType.HEALTH_CHECK: {
        "schedule": "*/10 * * * *",
        "description": "Internal health check for all services",
        "enabled": True,
    },
    CronJobType.DAILY_ANALYSIS: {
        "schedule": "0 23 * * *",
        "description": "Run daily productivity analysis",
        "enabled": True,
    },
    CronJobType.OKR_ROLLUP: {
        "schedule": "0 0 * * 0",
        "description": "Calculate weekly OKR progress rollups",
        "enabled": True,
    },
    CronJobType.EMBEDDING_REFRESH: {
        "schedule": "0 4 * * *",
        "description": "Refresh stale embeddings",
        "enabled": True,
    },
}


def get_supabase_client() -> Optional[Client]:
    """Get Supabase client for database operations."""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_KEY', os.getenv('SUPABASE_KEY'))

    if url and key:
        return create_client(url, key)
    return None


def verify_cron_secret(secret: str) -> bool:
    """Verify internal cron secret.

    Args:
        secret: X-Cron-Secret header value

    Returns:
        True if secret matches, False otherwise
    """
    expected_secret = os.getenv('CRON_SECRET', '')

    if not expected_secret:
        logger.warning("CRON_SECRET not set - skipping verification (DEVELOPMENT MODE)")
        return True

    return hmac.compare_digest(expected_secret, secret)


async def log_cron_execution(
    job_type: CronJobType,
    status: CronExecutionStatus,
    started_at: datetime,
    completed_at: datetime,
    message: str,
    error: Optional[str] = None,
) -> None:
    """Log cron execution to database.

    Args:
        job_type: Type of cron job
        status: Execution status
        started_at: Start timestamp
        completed_at: Completion timestamp
        message: Result message
        error: Error message if any
    """
    client = get_supabase_client()
    if not client:
        logger.warning("Supabase not configured - skipping cron log")
        return

    try:
        duration_ms = int((completed_at - started_at).total_seconds() * 1000)

        client.table('cron_logs').insert({
            'id': str(uuid.uuid4()),
            'job_type': job_type.value,
            'status': status.value,
            'executed_at': completed_at.isoformat(),
            'duration_ms': duration_ms,
            'message': message,
            'error': error,
        }).execute()

        logger.info(f"Logged cron execution: {job_type.value} - {status.value}")

    except Exception as e:
        logger.error(f"Failed to log cron execution: {e}")


async def send_alert(job_type: CronJobType, error: str) -> None:
    """Send alert for cron failure.

    Args:
        job_type: Type of cron job that failed
        error: Error message
    """
    # TODO: Integrate with alerting system (email, Slack, etc.)
    logger.error(f"CRON ALERT: {job_type.value} failed - {error}")


# === Cron Job Executors ===

async def execute_morning_report(params: Optional[dict] = None) -> Dict[str, Any]:
    """Execute morning report generation and delivery.

    Returns:
        Execution result details
    """
    try:
        # Import the reports router functions
        from routers.reports import (
            load_yesterday_analysis,
            load_okrs,
            load_blockers,
        )
        from services.email_sender import EmailSender

        # Load report data
        yesterday_data = load_yesterday_analysis()
        okrs = load_okrs()
        blockers = load_blockers()

        # Generate and send report
        email_sender = EmailSender()
        report_data = {
            'yesterday': yesterday_data,
            'okrs': okrs,
            'blockers': blockers,
            'generated_at': datetime.now(PACIFIC).isoformat(),
        }

        success = email_sender.send_morning_report(report_data)

        return {
            'report_sent': success,
            'okrs_count': len(okrs),
            'blockers_count': len(blockers),
        }

    except Exception as e:
        logger.error(f"Morning report execution failed: {e}")
        raise


async def execute_queue_process(params: Optional[dict] = None) -> Dict[str, Any]:
    """Process pending items in the queue.

    Returns:
        Execution result details
    """
    try:
        client = get_supabase_client()
        if not client:
            return {'processed': 0, 'error': 'Supabase not configured'}

        # Get pending items
        result = client.table('processing_queue').select('*').eq(
            'status', 'pending'
        ).order('scheduled_at').limit(10).execute()

        items = result.data if result.data else []
        processed = 0
        failed = 0

        for item in items:
            try:
                # Mark as processing
                client.table('processing_queue').update({
                    'status': 'processing',
                    'started_at': datetime.now(PACIFIC).isoformat(),
                }).eq('id', item['id']).execute()

                # TODO: Process item based on type
                # For now, just mark as completed
                client.table('processing_queue').update({
                    'status': 'completed',
                    'completed_at': datetime.now(PACIFIC).isoformat(),
                }).eq('id', item['id']).execute()

                processed += 1

            except Exception as e:
                logger.error(f"Failed to process queue item {item['id']}: {e}")
                client.table('processing_queue').update({
                    'status': 'failed',
                    'error': str(e),
                }).eq('id', item['id']).execute()
                failed += 1

        return {
            'total_pending': len(items),
            'processed': processed,
            'failed': failed,
        }

    except Exception as e:
        logger.error(f"Queue processing failed: {e}")
        raise


async def execute_cleanup_expired(params: Optional[dict] = None) -> Dict[str, Any]:
    """Clean up expired sessions, tokens, and temp files.

    Returns:
        Execution result details
    """
    try:
        client = get_supabase_client()
        cleaned = {
            'sessions': 0,
            'tokens': 0,
            'temp_files': 0,
        }

        if client:
            # Clean expired sessions (older than 30 days)
            expiry_date = (datetime.now(PACIFIC) - timedelta(days=30)).isoformat()

            try:
                result = client.table('sessions').delete().lt(
                    'last_active', expiry_date
                ).execute()
                cleaned['sessions'] = len(result.data) if result.data else 0
            except Exception as e:
                logger.warning(f"Session cleanup failed: {e}")

            # Clean expired tokens
            try:
                result = client.table('refresh_tokens').delete().lt(
                    'expires_at', datetime.now(PACIFIC).isoformat()
                ).execute()
                cleaned['tokens'] = len(result.data) if result.data else 0
            except Exception as e:
                logger.warning(f"Token cleanup failed: {e}")

        # Clean temp files (older than 24 hours)
        import glob
        from pathlib import Path

        temp_dirs = [
            '/tmp/flourisha_*',
            '/root/flourisha/00_AI_Brain/temp/*',
        ]

        for pattern in temp_dirs:
            for path in glob.glob(pattern):
                try:
                    p = Path(path)
                    if p.exists():
                        age = datetime.now() - datetime.fromtimestamp(p.stat().st_mtime)
                        if age > timedelta(hours=24):
                            if p.is_file():
                                p.unlink()
                                cleaned['temp_files'] += 1
                            elif p.is_dir():
                                import shutil
                                shutil.rmtree(path)
                                cleaned['temp_files'] += 1
                except Exception as e:
                    logger.warning(f"Failed to clean {path}: {e}")

        return cleaned

    except Exception as e:
        logger.error(f"Cleanup execution failed: {e}")
        raise


async def execute_sync_clickup(params: Optional[dict] = None) -> Dict[str, Any]:
    """Sync ClickUp tasks with local cache.

    Returns:
        Execution result details
    """
    try:
        import sys
        sys.path.insert(0, '/root/flourisha/00_AI_Brain/skills/clickup-tasks/reference')
        from clickup_api import ClickUpClient

        client = ClickUpClient()

        # Get all tasks from the API project list
        list_id = params.get('list_id', '901112685055') if params else '901112685055'
        tasks = client.get_list_tasks(list_id)

        # Count by status
        status_counts = {}
        for task in tasks:
            status = task.get('status', {}).get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            'total_tasks': len(tasks),
            'status_breakdown': status_counts,
            'list_id': list_id,
        }

    except Exception as e:
        logger.error(f"ClickUp sync failed: {e}")
        raise


async def execute_health_check(params: Optional[dict] = None) -> Dict[str, Any]:
    """Run internal health check for all services.

    Returns:
        Execution result details
    """
    health = {
        'supabase': False,
        'neo4j': False,
        'api': True,  # If we're here, API is healthy
    }

    # Check Supabase
    try:
        client = get_supabase_client()
        if client:
            # Simple query to check connection
            client.table('energy_tracking').select('id').limit(1).execute()
            health['supabase'] = True
    except Exception as e:
        logger.warning(f"Supabase health check failed: {e}")

    # Check Neo4j
    try:
        from neo4j import GraphDatabase

        uri = os.getenv('NEO4J_URI')
        user = os.getenv('NEO4J_USER')
        password = os.getenv('NEO4J_PASSWORD')

        if uri and user and password:
            driver = GraphDatabase.driver(uri, auth=(user, password))
            with driver.session() as session:
                session.run("RETURN 1")
            driver.close()
            health['neo4j'] = True
    except Exception as e:
        logger.warning(f"Neo4j health check failed: {e}")

    # Calculate overall health
    health['all_healthy'] = all(health.values())

    return health


async def execute_daily_analysis(params: Optional[dict] = None) -> Dict[str, Any]:
    """Run daily productivity analysis.

    Returns:
        Execution result details
    """
    try:
        client = get_supabase_client()
        if not client:
            return {'analyzed': False, 'error': 'Supabase not configured'}

        today = datetime.now(PACIFIC).date()

        # Get today's energy entries
        result = client.table('energy_tracking').select('*').gte(
            'recorded_at', today.isoformat()
        ).execute()

        entries = result.data if result.data else []

        # Calculate averages
        if entries:
            avg_energy = sum(e.get('energy_level', 0) for e in entries) / len(entries)
            focus_counts = {}
            for e in entries:
                focus = e.get('focus_quality', 'unknown')
                focus_counts[focus] = focus_counts.get(focus, 0) + 1

            analysis = {
                'date': today.isoformat(),
                'entries_count': len(entries),
                'avg_energy': round(avg_energy, 2),
                'focus_breakdown': focus_counts,
            }
        else:
            analysis = {
                'date': today.isoformat(),
                'entries_count': 0,
                'avg_energy': 0,
                'focus_breakdown': {},
            }

        return analysis

    except Exception as e:
        logger.error(f"Daily analysis failed: {e}")
        raise


async def execute_okr_rollup(params: Optional[dict] = None) -> Dict[str, Any]:
    """Calculate OKR progress rollups.

    Returns:
        Execution result details
    """
    try:
        client = get_supabase_client()
        if not client:
            return {'rolled_up': False, 'error': 'Supabase not configured'}

        # Get all OKRs
        result = client.table('okrs').select('*').execute()
        okrs = result.data if result.data else []

        updated = 0
        for okr in okrs:
            try:
                # Get key results for this OKR
                kr_result = client.table('key_results').select('*').eq(
                    'okr_id', okr['id']
                ).execute()
                key_results = kr_result.data if kr_result.data else []

                if key_results:
                    # Calculate average progress
                    total_progress = sum(kr.get('progress', 0) for kr in key_results)
                    avg_progress = total_progress / len(key_results)

                    # Update OKR overall progress
                    client.table('okrs').update({
                        'overall_progress': round(avg_progress, 2),
                        'updated_at': datetime.now(PACIFIC).isoformat(),
                    }).eq('id', okr['id']).execute()

                    updated += 1

            except Exception as e:
                logger.warning(f"Failed to update OKR {okr['id']}: {e}")

        return {
            'total_okrs': len(okrs),
            'updated': updated,
        }

    except Exception as e:
        logger.error(f"OKR rollup failed: {e}")
        raise


async def execute_embedding_refresh(params: Optional[dict] = None) -> Dict[str, Any]:
    """Refresh stale embeddings.

    Returns:
        Execution result details
    """
    try:
        client = get_supabase_client()
        if not client:
            return {'refreshed': 0, 'error': 'Supabase not configured'}

        # Find documents with stale embeddings (older than 30 days)
        stale_date = (datetime.now(PACIFIC) - timedelta(days=30)).isoformat()

        result = client.table('documents').select('id,content').lt(
            'embedding_updated_at', stale_date
        ).limit(50).execute()

        stale_docs = result.data if result.data else []
        refreshed = 0

        if stale_docs:
            from services.embeddings_service import get_embeddings_service
            embeddings_service = get_embeddings_service()

            for doc in stale_docs:
                try:
                    # Generate new embedding
                    content = doc.get('content', '')
                    if content:
                        embedding = embeddings_service.generate_embedding(content)

                        # Update document
                        client.table('documents').update({
                            'embedding': embedding,
                            'embedding_updated_at': datetime.now(PACIFIC).isoformat(),
                        }).eq('id', doc['id']).execute()

                        refreshed += 1

                except Exception as e:
                    logger.warning(f"Failed to refresh embedding for {doc['id']}: {e}")

        return {
            'stale_count': len(stale_docs),
            'refreshed': refreshed,
        }

    except Exception as e:
        logger.error(f"Embedding refresh failed: {e}")
        raise


# Executor mapping
EXECUTORS = {
    CronJobType.MORNING_REPORT: execute_morning_report,
    CronJobType.QUEUE_PROCESS: execute_queue_process,
    CronJobType.CLEANUP_EXPIRED: execute_cleanup_expired,
    CronJobType.SYNC_CLICKUP: execute_sync_clickup,
    CronJobType.HEALTH_CHECK: execute_health_check,
    CronJobType.DAILY_ANALYSIS: execute_daily_analysis,
    CronJobType.OKR_ROLLUP: execute_okr_rollup,
    CronJobType.EMBEDDING_REFRESH: execute_embedding_refresh,
}


# === API Endpoints ===

@router.post("/trigger/{job_type}")
async def trigger_cron_job(
    request: Request,
    job_type: CronJobType,
    background_tasks: BackgroundTasks,
    x_cron_secret: Optional[str] = Header(None, alias="X-Cron-Secret"),
) -> APIResponse[CronExecutionResult]:
    """
    Trigger a cron job execution.

    This endpoint is called by pg_cron, systemd timers, or manual triggers.
    Validates the X-Cron-Secret header before execution.

    Args:
        job_type: Type of cron job to execute
        x_cron_secret: Internal secret for authentication

    Returns:
        Execution result with status and details
    """
    # Verify cron secret
    if not verify_cron_secret(x_cron_secret or ""):
        logger.warning(f"Invalid cron secret for job: {job_type.value}")
        raise HTTPException(status_code=401, detail="Invalid cron secret")

    # Check if job is enabled
    job_config = CRON_JOBS.get(job_type)
    if not job_config or not job_config.get('enabled', True):
        return APIResponse(
            success=False,
            error=f"Job '{job_type.value}' is not enabled",
        )

    # Execute job
    started_at = datetime.now(PACIFIC)
    status = CronExecutionStatus.SUCCESS
    message = ""
    details = None
    error = None

    try:
        executor = EXECUTORS.get(job_type)
        if not executor:
            raise ValueError(f"No executor for job type: {job_type.value}")

        details = await executor()
        message = f"Job '{job_type.value}' completed successfully"

    except Exception as e:
        status = CronExecutionStatus.FAILED
        message = f"Job '{job_type.value}' failed"
        error = str(e)
        logger.error(f"Cron job {job_type.value} failed: {e}")

        # Send alert for failures
        background_tasks.add_task(send_alert, job_type, str(e))

    completed_at = datetime.now(PACIFIC)
    duration_ms = int((completed_at - started_at).total_seconds() * 1000)

    # Log execution
    background_tasks.add_task(
        log_cron_execution,
        job_type,
        status,
        started_at,
        completed_at,
        message,
        error,
    )

    result = CronExecutionResult(
        job_type=job_type,
        status=status,
        started_at=started_at,
        completed_at=completed_at,
        duration_ms=duration_ms,
        message=message,
        details=details,
        error=error,
    )

    meta_dict = request.state.get_meta()

    return APIResponse(
        success=status == CronExecutionStatus.SUCCESS,
        data=result,
        error=error,
        meta=ResponseMeta(**meta_dict),
    )


@router.post("/trigger")
async def trigger_cron_job_via_body(
    request: Request,
    payload: CronTriggerRequest,
    background_tasks: BackgroundTasks,
    x_cron_secret: Optional[str] = Header(None, alias="X-Cron-Secret"),
) -> APIResponse[CronExecutionResult]:
    """
    Trigger a cron job execution via request body.

    Alternative to path parameter, allows passing additional params.

    Args:
        payload: Trigger request with job type and optional params

    Returns:
        Execution result with status and details
    """
    # Verify cron secret
    if not verify_cron_secret(x_cron_secret or ""):
        logger.warning(f"Invalid cron secret for job: {payload.job_type.value}")
        raise HTTPException(status_code=401, detail="Invalid cron secret")

    # Check if job is enabled
    job_config = CRON_JOBS.get(payload.job_type)
    if not job_config or not job_config.get('enabled', True):
        return APIResponse(
            success=False,
            error=f"Job '{payload.job_type.value}' is not enabled",
        )

    # Execute job
    started_at = datetime.now(PACIFIC)
    status = CronExecutionStatus.SUCCESS
    message = ""
    details = None
    error = None

    try:
        executor = EXECUTORS.get(payload.job_type)
        if not executor:
            raise ValueError(f"No executor for job type: {payload.job_type.value}")

        details = await executor(payload.params)
        message = f"Job '{payload.job_type.value}' completed successfully"

    except Exception as e:
        status = CronExecutionStatus.FAILED
        message = f"Job '{payload.job_type.value}' failed"
        error = str(e)
        logger.error(f"Cron job {payload.job_type.value} failed: {e}")

        # Send alert for failures
        background_tasks.add_task(send_alert, payload.job_type, str(e))

    completed_at = datetime.now(PACIFIC)
    duration_ms = int((completed_at - started_at).total_seconds() * 1000)

    # Log execution
    background_tasks.add_task(
        log_cron_execution,
        payload.job_type,
        status,
        started_at,
        completed_at,
        message,
        error,
    )

    result = CronExecutionResult(
        job_type=payload.job_type,
        status=status,
        started_at=started_at,
        completed_at=completed_at,
        duration_ms=duration_ms,
        message=message,
        details=details,
        error=error,
    )

    meta_dict = request.state.get_meta()

    return APIResponse(
        success=status == CronExecutionStatus.SUCCESS,
        data=result,
        error=error,
        meta=ResponseMeta(**meta_dict),
    )


@router.get("/status")
async def get_cron_status(
    request: Request,
    x_cron_secret: Optional[str] = Header(None, alias="X-Cron-Secret"),
) -> APIResponse[CronStatusResponse]:
    """
    Get status of all configured cron jobs.

    Returns configuration and last execution status for each job.
    """
    # Verify cron secret
    if not verify_cron_secret(x_cron_secret or ""):
        raise HTTPException(status_code=401, detail="Invalid cron secret")

    jobs = []
    client = get_supabase_client()

    for job_type, config in CRON_JOBS.items():
        job_info = CronJobInfo(
            job_type=job_type,
            schedule=config['schedule'],
            description=config['description'],
            enabled=config.get('enabled', True),
        )

        # Get last execution from logs
        if client:
            try:
                result = client.table('cron_logs').select('*').eq(
                    'job_type', job_type.value
                ).order('executed_at', desc=True).limit(1).execute()

                if result.data:
                    last = result.data[0]
                    job_info.last_run = datetime.fromisoformat(last['executed_at'])
                    job_info.last_status = CronExecutionStatus(last['status'])
            except Exception as e:
                logger.warning(f"Failed to get last execution for {job_type.value}: {e}")

        jobs.append(job_info)

    # Get most recent execution overall
    last_execution = None
    if client:
        try:
            result = client.table('cron_logs').select('*').order(
                'executed_at', desc=True
            ).limit(1).execute()

            if result.data:
                log = result.data[0]
                last_execution = CronExecutionResult(
                    job_type=CronJobType(log['job_type']),
                    status=CronExecutionStatus(log['status']),
                    started_at=datetime.fromisoformat(log['executed_at']),
                    completed_at=datetime.fromisoformat(log['executed_at']),
                    duration_ms=log.get('duration_ms', 0),
                    message=log.get('message', ''),
                    error=log.get('error'),
                )
        except Exception as e:
            logger.warning(f"Failed to get last execution: {e}")

    response = CronStatusResponse(
        jobs=jobs,
        total_jobs=len(jobs),
        enabled_jobs=sum(1 for j in jobs if j.enabled),
        last_execution=last_execution,
    )

    meta_dict = request.state.get_meta()

    return APIResponse(
        success=True,
        data=response,
        meta=ResponseMeta(**meta_dict),
    )


@router.get("/logs")
async def get_cron_logs(
    request: Request,
    job_type: Optional[CronJobType] = None,
    status: Optional[CronExecutionStatus] = None,
    page: int = 1,
    page_size: int = 20,
    x_cron_secret: Optional[str] = Header(None, alias="X-Cron-Secret"),
) -> APIResponse[CronLogsResponse]:
    """
    Get cron execution logs with optional filtering.

    Args:
        job_type: Filter by job type
        status: Filter by execution status
        page: Page number (1-indexed)
        page_size: Items per page

    Returns:
        Paginated list of execution logs
    """
    # Verify cron secret
    if not verify_cron_secret(x_cron_secret or ""):
        raise HTTPException(status_code=401, detail="Invalid cron secret")

    client = get_supabase_client()
    if not client:
        return APIResponse(
            success=False,
            error="Supabase not configured",
        )

    try:
        # Build query
        query = client.table('cron_logs').select('*', count='exact')

        if job_type:
            query = query.eq('job_type', job_type.value)
        if status:
            query = query.eq('status', status.value)

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.order('executed_at', desc=True).range(offset, offset + page_size - 1)

        result = query.execute()

        logs = []
        for row in result.data or []:
            logs.append(CronLogEntry(
                id=row['id'],
                job_type=CronJobType(row['job_type']),
                status=CronExecutionStatus(row['status']),
                executed_at=datetime.fromisoformat(row['executed_at']),
                duration_ms=row.get('duration_ms', 0),
                message=row.get('message', ''),
                error=row.get('error'),
            ))

        response = CronLogsResponse(
            logs=logs,
            total=result.count or 0,
            page=page,
            page_size=page_size,
        )

        meta_dict = request.state.get_meta()

        return APIResponse(
            success=True,
            data=response,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Failed to get cron logs: {e}")
        return APIResponse(
            success=False,
            error=str(e),
        )


@router.get("/health")
async def cron_health_check(
    request: Request,
) -> APIResponse[dict]:
    """
    Health check endpoint for cron system.

    Does NOT require authentication - used for monitoring.

    Returns:
        Basic health status of cron system
    """
    meta_dict = request.state.get_meta()

    return APIResponse(
        success=True,
        data={
            'status': 'healthy',
            'jobs_configured': len(CRON_JOBS),
            'jobs_enabled': sum(1 for c in CRON_JOBS.values() if c.get('enabled', True)),
            'timestamp': datetime.now(PACIFIC).isoformat(),
        },
        meta=ResponseMeta(**meta_dict),
    )
