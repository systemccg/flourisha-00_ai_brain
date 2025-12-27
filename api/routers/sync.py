"""
Flourisha Sync Router

Google Drive sync management via rclone bisync.
Triggers sync, checks status, and lists conflicts.
"""
import os
import sys
import logging
import asyncio
import subprocess
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from zoneinfo import ZoneInfo
from enum import Enum

from fastapi import APIRouter, Depends, Request, Query, BackgroundTasks
from pydantic import BaseModel, Field

from models.response import APIResponse, ResponseMeta
from middleware.auth import get_current_user, UserContext


logger = logging.getLogger("flourisha.api.sync")

router = APIRouter(prefix="/api/sync", tags=["Flourisha Sync"])

# Pacific timezone
PACIFIC = ZoneInfo("America/Los_Angeles")

# Paths
FLOURISHA_DIR = Path("/root/flourisha")
LOCK_FILE = Path("/root/.cache/rclone/bisync/root_flourisha..flourisha_.lck")
SYNC_LOG = Path("/var/log/flourisha-sync.log")
RCLONE_REMOTE = "flourisha:"

# State tracking (in-memory for now)
_sync_state = {
    "status": "idle",
    "last_sync": None,
    "last_error": None,
    "files_processed": 0,
    "files_transferred": 0,
    "current_operation": None
}


class SyncStatus(str, Enum):
    """Possible sync statuses."""
    IDLE = "idle"
    SYNCING = "syncing"
    ERROR = "error"
    COMPLETED = "completed"


# === Request/Response Models ===

class SyncTriggerRequest(BaseModel):
    """Request to trigger a sync."""
    force: bool = Field(False, description="Force sync even if lock exists")
    dry_run: bool = Field(False, description="Preview changes without syncing")
    resync: bool = Field(True, description="Use resync mode for conflicts")


class SyncStatusResponse(BaseModel):
    """Current sync status."""
    status: str = Field(..., description="Current status: idle, syncing, error, completed")
    last_sync: Optional[str] = Field(None, description="Last successful sync timestamp")
    last_error: Optional[str] = Field(None, description="Last error message if any")
    files_processed: int = Field(0, description="Files processed in last sync")
    files_transferred: int = Field(0, description="Files transferred in last sync")
    lock_exists: bool = Field(False, description="Whether lock file exists")
    current_operation: Optional[str] = Field(None, description="Current operation if syncing")


class ConflictFile(BaseModel):
    """A file with sync conflict."""
    path: str = Field(..., description="File path")
    local_modified: Optional[str] = Field(None, description="Local modification time")
    remote_modified: Optional[str] = Field(None, description="Remote modification time")
    conflict_type: str = Field(..., description="Type of conflict")


class ConflictsResponse(BaseModel):
    """List of sync conflicts."""
    conflicts: List[ConflictFile] = Field(default_factory=list, description="Files with conflicts")
    total: int = Field(0, description="Total conflicts")


class SyncResult(BaseModel):
    """Result of sync operation."""
    success: bool = Field(..., description="Whether sync completed successfully")
    duration_seconds: float = Field(..., description="Sync duration in seconds")
    files_processed: int = Field(0, description="Total files processed")
    files_transferred: int = Field(0, description="Files transferred")
    errors: List[str] = Field(default_factory=list, description="Any errors encountered")
    dry_run: bool = Field(False, description="Was this a dry run")


# === Helper Functions ===

def check_lock_file() -> tuple[bool, Optional[int]]:
    """Check if lock file exists and its age in seconds."""
    if LOCK_FILE.exists():
        age_seconds = int(datetime.now().timestamp() - LOCK_FILE.stat().st_mtime)
        return True, age_seconds
    return False, None


def remove_stale_lock() -> bool:
    """Remove stale lock file if older than 5 minutes."""
    exists, age = check_lock_file()
    if exists and age and age > 300:  # 5 minutes
        try:
            LOCK_FILE.unlink()
            logger.info(f"Removed stale lock file (age: {age}s)")
            return True
        except Exception as e:
            logger.error(f"Failed to remove lock file: {e}")
    return False


async def run_rclone_sync(
    force: bool = False,
    dry_run: bool = False,
    resync: bool = True
) -> SyncResult:
    """Execute rclone bisync and capture results."""
    global _sync_state

    start_time = datetime.now()
    errors = []

    try:
        _sync_state["status"] = "syncing"
        _sync_state["current_operation"] = "Initializing sync..."

        # Check and clear stale lock
        lock_exists, lock_age = check_lock_file()
        if lock_exists:
            if force or (lock_age and lock_age > 300):
                remove_stale_lock()
            else:
                _sync_state["status"] = "error"
                _sync_state["last_error"] = f"Lock file exists (age: {lock_age}s). Use force=true to override."
                return SyncResult(
                    success=False,
                    duration_seconds=0,
                    errors=[_sync_state["last_error"]]
                )

        # Build rclone command
        cmd = [
            "rclone", "bisync",
            str(FLOURISHA_DIR),
            RCLONE_REMOTE,
            "--exclude", "node_modules/",
            "--exclude", "venv/",
            "--exclude", ".venv/",
            "--exclude", "**/node_modules/",
            "--exclude", "**/venv/",
            "--exclude", "**/.venv/",
            "--interactive=false",
        ]

        if resync:
            cmd.append("--resync")
        if dry_run:
            cmd.append("--dry-run")

        _sync_state["current_operation"] = "Running rclone bisync..."

        # Run rclone
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        # Parse output
        output = stdout.decode() + stderr.decode()
        files_processed = 0
        files_transferred = 0

        for line in output.split('\n'):
            if 'files' in line.lower():
                # Try to extract file counts
                if 'transferred' in line.lower():
                    try:
                        parts = line.split()
                        for i, p in enumerate(parts):
                            if p.isdigit():
                                files_transferred = int(p)
                                break
                    except:
                        pass
            if 'error' in line.lower() or 'fail' in line.lower():
                if line.strip():
                    errors.append(line.strip()[:200])

        duration = (datetime.now() - start_time).total_seconds()

        success = process.returncode == 0
        if success:
            _sync_state["status"] = "completed"
            _sync_state["last_sync"] = datetime.now(PACIFIC).isoformat()
            _sync_state["last_error"] = None
            _sync_state["files_processed"] = files_processed
            _sync_state["files_transferred"] = files_transferred
        else:
            _sync_state["status"] = "error"
            _sync_state["last_error"] = f"rclone exited with code {process.returncode}"
            errors.append(_sync_state["last_error"])

        _sync_state["current_operation"] = None

        return SyncResult(
            success=success,
            duration_seconds=round(duration, 2),
            files_processed=files_processed,
            files_transferred=files_transferred,
            errors=errors[:10],  # Limit errors
            dry_run=dry_run
        )

    except Exception as e:
        _sync_state["status"] = "error"
        _sync_state["last_error"] = str(e)
        _sync_state["current_operation"] = None
        return SyncResult(
            success=False,
            duration_seconds=(datetime.now() - start_time).total_seconds(),
            errors=[str(e)]
        )


async def get_conflicts() -> List[ConflictFile]:
    """Get list of files with sync conflicts."""
    conflicts = []

    try:
        # Check for .conflict files or similar markers
        conflict_patterns = ["*.conflict", "*.conflict.*", "*_conflict_*"]

        for pattern in conflict_patterns:
            for path in FLOURISHA_DIR.rglob(pattern):
                if path.is_file():
                    conflicts.append(ConflictFile(
                        path=str(path.relative_to(FLOURISHA_DIR)),
                        local_modified=datetime.fromtimestamp(
                            path.stat().st_mtime, tz=PACIFIC
                        ).isoformat(),
                        conflict_type="naming_conflict"
                    ))

        # Also check rclone bisync conflict directory if it exists
        conflict_dir = Path("/root/.cache/rclone/bisync/")
        if conflict_dir.exists():
            # Look for conflict markers in bisync cache
            for conflict_file in conflict_dir.glob("*.conflict"):
                conflicts.append(ConflictFile(
                    path=conflict_file.name,
                    conflict_type="bisync_conflict"
                ))

    except Exception as e:
        logger.warning(f"Error checking conflicts: {e}")

    return conflicts


# === API Endpoints ===

@router.post("/trigger", response_model=APIResponse[SyncResult])
async def trigger_sync(
    request: Request,
    sync_request: SyncTriggerRequest,
    background_tasks: BackgroundTasks,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[SyncResult]:
    """
    Trigger Google Drive sync.

    Starts rclone bisync between local Flourisha directory and Google Drive.

    **Request Body:**
    - force: Override lock file if exists (default false)
    - dry_run: Preview changes without syncing (default false)
    - resync: Use resync mode for conflicts (default true)

    **Note:** Sync runs synchronously and may take several minutes.
    For long syncs, consider using status endpoint to check progress.

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    # Check if already syncing
    if _sync_state["status"] == "syncing":
        return APIResponse(
            success=False,
            error="Sync already in progress",
            meta=ResponseMeta(**meta_dict),
        )

    try:
        result = await run_rclone_sync(
            force=sync_request.force,
            dry_run=sync_request.dry_run,
            resync=sync_request.resync
        )

        return APIResponse(
            success=result.success,
            data=result,
            error=result.errors[0] if result.errors and not result.success else None,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        logger.error(f"Sync trigger failed: {e}")
        return APIResponse(
            success=False,
            error=f"Sync failed: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/status", response_model=APIResponse[SyncStatusResponse])
async def get_sync_status(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[SyncStatusResponse]:
    """
    Get current sync status.

    Returns idle/syncing/error status and last sync details.

    **Response:**
    - status: Current status (idle, syncing, error, completed)
    - last_sync: Timestamp of last successful sync
    - last_error: Error message if status is error
    - files_processed: Files processed in last sync
    - lock_exists: Whether lock file exists

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    lock_exists, _ = check_lock_file()

    status = SyncStatusResponse(
        status=_sync_state["status"],
        last_sync=_sync_state["last_sync"],
        last_error=_sync_state["last_error"],
        files_processed=_sync_state["files_processed"],
        files_transferred=_sync_state["files_transferred"],
        lock_exists=lock_exists,
        current_operation=_sync_state["current_operation"]
    )

    return APIResponse(
        success=True,
        data=status,
        meta=ResponseMeta(**meta_dict),
    )


@router.get("/conflicts", response_model=APIResponse[ConflictsResponse])
async def list_conflicts(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[ConflictsResponse]:
    """
    List files with sync conflicts.

    Returns files that need manual resolution due to conflicting changes.

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        conflicts = await get_conflicts()

        return APIResponse(
            success=True,
            data=ConflictsResponse(
                conflicts=conflicts,
                total=len(conflicts)
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=f"Failed to check conflicts: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.delete("/lock", response_model=APIResponse[dict])
async def clear_lock(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[dict]:
    """
    Clear sync lock file.

    Removes the lock file if it exists. Use with caution.

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        lock_exists, age = check_lock_file()

        if not lock_exists:
            return APIResponse(
                success=True,
                data={
                    "message": "No lock file exists",
                    "cleared": False
                },
                meta=ResponseMeta(**meta_dict),
            )

        LOCK_FILE.unlink()
        _sync_state["status"] = "idle"

        return APIResponse(
            success=True,
            data={
                "message": f"Lock file cleared (was {age}s old)",
                "cleared": True
            },
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=f"Failed to clear lock: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/logs", response_model=APIResponse[List[str]])
async def get_sync_logs(
    request: Request,
    lines: int = Query(50, ge=1, le=500, description="Number of log lines"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[List[str]]:
    """
    Get recent sync log entries.

    **Query Parameters:**
    - lines: Number of log lines to return (default 50, max 500)

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        if not SYNC_LOG.exists():
            return APIResponse(
                success=True,
                data=["No sync log file exists yet"],
                meta=ResponseMeta(**meta_dict),
            )

        content = SYNC_LOG.read_text()
        log_lines = content.strip().split('\n')

        # Get last N lines
        recent_lines = log_lines[-lines:]

        return APIResponse(
            success=True,
            data=recent_lines,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=f"Failed to read logs: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )
