"""
System Health Dashboard Router

Aggregate health status of all services including Supabase, Neo4j,
Voice server, queue depth, and error logs.
"""
import os
import sys
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import httpx
from fastapi import APIRouter, Depends, Request, Query
from pydantic import BaseModel, Field
from supabase import create_client, Client

from models.response import APIResponse, ResponseMeta
from middleware.auth import get_current_user, get_optional_user, UserContext


logger = logging.getLogger("flourisha.api.health_dashboard")

router = APIRouter(prefix="/api/health/dashboard", tags=["Health Dashboard"])

# Pacific timezone
PACIFIC = ZoneInfo("America/Los_Angeles")

# Log directory
LOG_DIR = Path("/root/flourisha/00_AI_Brain/api/logs")

# Service URLs
VOICE_SERVER_URL = os.getenv("VOICE_SERVER_URL", "http://localhost:8888")
NEO4J_URL = os.getenv("NEO4J_URL", "bolt://neo4j.leadingai.info:7687")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")


def get_supabase_client() -> Optional[Client]:
    """Get Supabase client for database operations."""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_KEY', os.getenv('SUPABASE_KEY'))

    if url and key:
        return create_client(url, key)
    return None


# === Request/Response Models ===

class ServiceHealth(BaseModel):
    """Health status for a single service."""
    name: str = Field(..., description="Service name")
    status: str = Field(..., description="healthy, degraded, or unhealthy")
    latency_ms: Optional[float] = Field(None, description="Response latency in ms")
    last_check: str = Field(..., description="Last check timestamp")
    details: Optional[str] = Field(None, description="Additional details")


class QueueMetrics(BaseModel):
    """Queue depth and processing metrics."""
    pending: int = Field(0, description="Pending jobs")
    processing: int = Field(0, description="Currently processing")
    completed_today: int = Field(0, description="Completed today")
    failed_today: int = Field(0, description="Failed today")
    avg_processing_time_ms: Optional[float] = Field(None, description="Average processing time")


class LogEntry(BaseModel):
    """Error log entry."""
    timestamp: str = Field(..., description="Log timestamp")
    level: str = Field(..., description="Log level")
    message: str = Field(..., description="Log message")
    source: Optional[str] = Field(None, description="Log source")


class HealthDashboardResponse(BaseModel):
    """Complete health dashboard response."""
    overall_status: str = Field(..., description="Overall system status")
    services: List[ServiceHealth] = Field(..., description="Individual service health")
    queue_metrics: QueueMetrics = Field(..., description="Processing queue metrics")
    recent_errors: List[LogEntry] = Field(default_factory=list, description="Recent error logs")
    timestamp: str = Field(..., description="Dashboard generation time")


# === Health Check Functions ===

async def check_supabase_health() -> ServiceHealth:
    """Check Supabase connection health."""
    start = datetime.now()
    try:
        supabase = get_supabase_client()
        if not supabase:
            return ServiceHealth(
                name="Supabase",
                status="unhealthy",
                last_check=datetime.now(PACIFIC).isoformat(),
                details="Supabase credentials not configured"
            )

        # Simple query to test connection
        result = supabase.table('embeddings').select('id').limit(1).execute()
        latency = (datetime.now() - start).total_seconds() * 1000

        return ServiceHealth(
            name="Supabase",
            status="healthy",
            latency_ms=round(latency, 2),
            last_check=datetime.now(PACIFIC).isoformat(),
            details=f"Connected to {SUPABASE_URL}"
        )
    except Exception as e:
        latency = (datetime.now() - start).total_seconds() * 1000
        return ServiceHealth(
            name="Supabase",
            status="unhealthy",
            latency_ms=round(latency, 2),
            last_check=datetime.now(PACIFIC).isoformat(),
            details=f"Connection failed: {str(e)[:100]}"
        )


async def check_neo4j_health() -> ServiceHealth:
    """Check Neo4j connection health."""
    start = datetime.now()
    try:
        # Try to import and use neo4j driver
        from neo4j import GraphDatabase

        neo4j_uri = os.getenv("NEO4J_URI", NEO4J_URL)
        neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        neo4j_password = os.getenv("NEO4J_PASSWORD", "")

        if not neo4j_password:
            return ServiceHealth(
                name="Neo4j",
                status="unhealthy",
                last_check=datetime.now(PACIFIC).isoformat(),
                details="Neo4j password not configured"
            )

        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            result.single()
        driver.close()

        latency = (datetime.now() - start).total_seconds() * 1000

        return ServiceHealth(
            name="Neo4j",
            status="healthy",
            latency_ms=round(latency, 2),
            last_check=datetime.now(PACIFIC).isoformat(),
            details=f"Connected to {neo4j_uri}"
        )
    except ImportError:
        return ServiceHealth(
            name="Neo4j",
            status="degraded",
            last_check=datetime.now(PACIFIC).isoformat(),
            details="Neo4j driver not installed"
        )
    except Exception as e:
        latency = (datetime.now() - start).total_seconds() * 1000
        return ServiceHealth(
            name="Neo4j",
            status="unhealthy",
            latency_ms=round(latency, 2),
            last_check=datetime.now(PACIFIC).isoformat(),
            details=f"Connection failed: {str(e)[:100]}"
        )


async def check_voice_server_health() -> ServiceHealth:
    """Check voice server health."""
    start = datetime.now()
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{VOICE_SERVER_URL}/health")
            response.raise_for_status()

        latency = (datetime.now() - start).total_seconds() * 1000

        return ServiceHealth(
            name="Voice Server",
            status="healthy",
            latency_ms=round(latency, 2),
            last_check=datetime.now(PACIFIC).isoformat(),
            details=f"ElevenLabs TTS available at {VOICE_SERVER_URL}"
        )
    except httpx.ConnectError:
        return ServiceHealth(
            name="Voice Server",
            status="unhealthy",
            last_check=datetime.now(PACIFIC).isoformat(),
            details=f"Cannot connect to {VOICE_SERVER_URL}"
        )
    except Exception as e:
        latency = (datetime.now() - start).total_seconds() * 1000
        return ServiceHealth(
            name="Voice Server",
            status="unhealthy",
            latency_ms=round(latency, 2),
            last_check=datetime.now(PACIFIC).isoformat(),
            details=f"Error: {str(e)[:100]}"
        )


async def get_queue_metrics() -> QueueMetrics:
    """Get processing queue metrics from Supabase."""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return QueueMetrics()

        today = datetime.now(PACIFIC).strftime("%Y-%m-%d")

        # Get pending jobs
        pending = supabase.table('processing_queue').select(
            'id', count='exact'
        ).eq('status', 'pending').execute()

        # Get processing jobs
        processing = supabase.table('processing_queue').select(
            'id', count='exact'
        ).eq('status', 'processing').execute()

        # Get completed today
        completed = supabase.table('processing_queue').select(
            'id', count='exact'
        ).eq('status', 'completed').gte('completed_at', today).execute()

        # Get failed today
        failed = supabase.table('processing_queue').select(
            'id', count='exact'
        ).eq('status', 'failed').gte('updated_at', today).execute()

        return QueueMetrics(
            pending=pending.count or 0,
            processing=processing.count or 0,
            completed_today=completed.count or 0,
            failed_today=failed.count or 0
        )
    except Exception as e:
        logger.warning(f"Failed to get queue metrics: {e}")
        return QueueMetrics()


async def get_recent_errors(limit: int = 100) -> List[LogEntry]:
    """Get recent error logs from log files."""
    errors = []

    try:
        if not LOG_DIR.exists():
            return errors

        # Read log files
        log_files = sorted(LOG_DIR.glob("*.log"), key=lambda f: f.stat().st_mtime, reverse=True)

        for log_file in log_files[:3]:  # Check last 3 log files
            try:
                content = log_file.read_text()
                lines = content.split('\n')

                for line in reversed(lines):
                    if len(errors) >= limit:
                        break

                    line = line.strip()
                    if not line:
                        continue

                    # Look for error indicators
                    is_error = any(level in line.upper() for level in ['ERROR', 'CRITICAL', 'EXCEPTION'])
                    if is_error:
                        # Try to parse timestamp
                        timestamp = datetime.now(PACIFIC).isoformat()
                        if line[:19].replace('-', '').replace(':', '').replace(' ', '').replace('T', '').isdigit():
                            try:
                                timestamp = line[:19]
                            except:
                                pass

                        level = "ERROR"
                        if "CRITICAL" in line.upper():
                            level = "CRITICAL"

                        errors.append(LogEntry(
                            timestamp=timestamp,
                            level=level,
                            message=line[:500],  # Truncate long messages
                            source=log_file.name
                        ))
            except Exception as e:
                logger.warning(f"Failed to read log file {log_file}: {e}")

    except Exception as e:
        logger.warning(f"Failed to get error logs: {e}")

    return errors[:limit]


def determine_overall_status(services: List[ServiceHealth]) -> str:
    """Determine overall system status from service statuses."""
    statuses = [s.status for s in services]

    if all(s == "healthy" for s in statuses):
        return "healthy"
    elif any(s == "unhealthy" for s in statuses):
        # If critical services are down, system is unhealthy
        critical_services = ["Supabase", "Neo4j"]
        for service in services:
            if service.name in critical_services and service.status == "unhealthy":
                return "unhealthy"
        return "degraded"
    else:
        return "degraded"


# === API Endpoints ===

@router.get("", response_model=APIResponse[HealthDashboardResponse])
async def get_health_dashboard(
    request: Request,
    include_logs: bool = Query(True, description="Include recent error logs"),
    log_limit: int = Query(100, ge=1, le=500, description="Max error logs to return"),
    user: UserContext = Depends(get_optional_user),
) -> APIResponse[HealthDashboardResponse]:
    """
    Get complete health dashboard.

    Aggregates health status of all services including:
    - Supabase (PostgreSQL + pgvector)
    - Neo4j (Knowledge graph)
    - Voice Server (ElevenLabs TTS)
    - Queue metrics
    - Recent error logs

    **Query Parameters:**
    - include_logs: Whether to include error logs (default true)
    - log_limit: Max number of error logs (default 100, max 500)

    **Note:** This endpoint does not require authentication for monitoring purposes.
    """
    meta_dict = request.state.get_meta()

    try:
        # Check all services in parallel
        services = [
            await check_supabase_health(),
            await check_neo4j_health(),
            await check_voice_server_health(),
        ]

        # Get queue metrics
        queue_metrics = await get_queue_metrics()

        # Get recent errors
        recent_errors = []
        if include_logs:
            recent_errors = await get_recent_errors(log_limit)

        # Determine overall status
        overall_status = determine_overall_status(services)

        dashboard = HealthDashboardResponse(
            overall_status=overall_status,
            services=services,
            queue_metrics=queue_metrics,
            recent_errors=recent_errors,
            timestamp=datetime.now(PACIFIC).isoformat()
        )

        return APIResponse(
            success=True,
            data=dashboard,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Health dashboard failed: {e}")
        return APIResponse(
            success=False,
            error=f"Dashboard generation failed: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/services/{service_name}", response_model=APIResponse[ServiceHealth])
async def get_service_health(
    request: Request,
    service_name: str,
    user: UserContext = Depends(get_optional_user),
) -> APIResponse[ServiceHealth]:
    """
    Get health for a specific service.

    **Path Parameters:**
    - service_name: supabase, neo4j, or voice

    **Note:** This endpoint does not require authentication for monitoring.
    """
    meta_dict = request.state.get_meta()

    service_checks = {
        "supabase": check_supabase_health,
        "neo4j": check_neo4j_health,
        "voice": check_voice_server_health,
    }

    service_name_lower = service_name.lower()
    if service_name_lower not in service_checks:
        return APIResponse(
            success=False,
            error=f"Unknown service: {service_name}. Valid options: {', '.join(service_checks.keys())}",
            meta=ResponseMeta(**meta_dict),
        )

    try:
        health = await service_checks[service_name_lower]()

        return APIResponse(
            success=True,
            data=health,
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            error=f"Health check failed: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/queue", response_model=APIResponse[QueueMetrics])
async def get_queue_status(
    request: Request,
    user: UserContext = Depends(get_optional_user),
) -> APIResponse[QueueMetrics]:
    """
    Get processing queue metrics.

    Returns current queue depth, processing count, and daily statistics.

    **Note:** This endpoint does not require authentication for monitoring.
    """
    meta_dict = request.state.get_meta()

    try:
        metrics = await get_queue_metrics()

        return APIResponse(
            success=True,
            data=metrics,
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            error=f"Failed to get queue metrics: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/logs", response_model=APIResponse[List[LogEntry]])
async def get_error_logs(
    request: Request,
    limit: int = Query(100, ge=1, le=500, description="Max logs to return"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[List[LogEntry]]:
    """
    Get recent error logs.

    Returns filtered error logs from the application.

    **Query Parameters:**
    - limit: Max number of logs (default 100, max 500)

    **Requires:** Valid Firebase JWT (logs may contain sensitive info)
    """
    meta_dict = request.state.get_meta()

    try:
        errors = await get_recent_errors(limit)

        return APIResponse(
            success=True,
            data=errors,
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            error=f"Failed to get logs: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )
