"""
Database Migrations Router

Admin endpoints for database schema management.
Provides migration status, application, and database introspection.

Security: Requires admin authentication + X-Cron-Secret for mutations.
Read operations require standard auth, write operations require both.

Available Endpoints:
- GET /status - Migration status overview
- GET /database - Database information and table list
- POST /apply - Apply pending migrations
- GET /{migration_id} - Get specific migration details
- POST /execute - Execute raw SQL (admin only)
"""
import os
import hmac
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Request, HTTPException, Header, Depends
from supabase import create_client, Client

from models.response import APIResponse, ResponseMeta
from models.migrations import (
    MigrationStatus,
    TableInfo,
    MigrationInfo,
    MigrationApplyRequest,
    MigrationApplyResult,
    MigrationStatusResponse,
    DatabaseStatusResponse,
    SQLExecuteRequest,
    SQLExecuteResult,
)
from middleware.auth import get_current_user, UserContext


router = APIRouter(prefix="/api/migrations", tags=["Migrations"])
logger = logging.getLogger(__name__)

# Pacific timezone
PACIFIC = ZoneInfo("America/Los_Angeles")

# Migrations directory
MIGRATIONS_DIR = Path("/root/flourisha/00_AI_Brain/database/migrations")


def get_supabase_client() -> Optional[Client]:
    """Get Supabase client for database operations."""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_KEY', os.getenv('SUPABASE_KEY'))

    if url and key:
        return create_client(url, key)
    return None


def verify_admin_secret(secret: str) -> bool:
    """Verify admin secret for mutation operations.

    Args:
        secret: X-Admin-Secret header value

    Returns:
        True if secret matches
    """
    expected = os.getenv('ADMIN_SECRET', os.getenv('CRON_SECRET', ''))

    if not expected:
        logger.warning("ADMIN_SECRET not set - skipping verification (DEVELOPMENT MODE)")
        return True

    return hmac.compare_digest(expected, secret)


def calculate_file_checksum(filepath: Path) -> str:
    """Calculate MD5 checksum of a file."""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def parse_migration_description(filepath: Path) -> Optional[str]:
    """Extract description from migration file header."""
    try:
        with open(filepath, 'r') as f:
            content = f.read(500)  # Read first 500 chars
            for line in content.split('\n'):
                if line.startswith('-- Purpose:'):
                    return line.replace('-- Purpose:', '').strip()
                if line.startswith('-- Description:'):
                    return line.replace('-- Description:', '').strip()
    except Exception:
        pass
    return None


def get_migration_info(filepath: Path, applied_migrations: dict) -> MigrationInfo:
    """Build MigrationInfo from a migration file."""
    filename = filepath.name
    migration_id = filepath.stem  # filename without extension

    # Check if applied
    applied_data = applied_migrations.get(migration_id, {})
    status = MigrationStatus.APPLIED if applied_data else MigrationStatus.PENDING

    return MigrationInfo(
        id=migration_id,
        name=migration_id.split('_', 1)[1] if '_' in migration_id else migration_id,
        filename=filename,
        status=status,
        applied_at=applied_data.get('applied_at'),
        checksum=calculate_file_checksum(filepath),
        description=parse_migration_description(filepath),
    )


async def get_applied_migrations(client: Client) -> dict:
    """Get dictionary of applied migrations from database."""
    try:
        # Try to query migration tracking table
        result = client.table('schema_migrations').select('*').execute()
        return {m['migration_id']: m for m in (result.data or [])}
    except Exception:
        # Table might not exist yet
        return {}


# === API Endpoints ===

@router.get("/status")
async def get_migration_status(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[MigrationStatusResponse]:
    """
    Get status of all database migrations.

    Returns list of migrations with their current status (pending/applied/failed).
    """
    client = get_supabase_client()
    if not client:
        raise HTTPException(status_code=503, detail="Database not configured")

    # Get applied migrations
    applied = await get_applied_migrations(client)

    # Scan migration files
    migrations = []
    if MIGRATIONS_DIR.exists():
        for filepath in sorted(MIGRATIONS_DIR.glob("*.sql")):
            migrations.append(get_migration_info(filepath, applied))

    # Count by status
    applied_count = sum(1 for m in migrations if m.status == MigrationStatus.APPLIED)
    pending_count = sum(1 for m in migrations if m.status == MigrationStatus.PENDING)
    failed_count = sum(1 for m in migrations if m.status == MigrationStatus.FAILED)

    response = MigrationStatusResponse(
        migrations=migrations,
        total=len(migrations),
        applied=applied_count,
        pending=pending_count,
        failed=failed_count,
    )

    meta_dict = request.state.get_meta()

    return APIResponse(
        success=True,
        data=response,
        meta=ResponseMeta(**meta_dict),
    )


@router.get("/database")
async def get_database_status(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[DatabaseStatusResponse]:
    """
    Get database status and table information.

    Returns connection status, PostgreSQL version, table list, and extensions.
    """
    client = get_supabase_client()
    connected = client is not None

    version = None
    tables = []
    extensions = []
    db_size = None

    if client:
        try:
            # Get PostgreSQL version
            result = client.rpc('get_pg_version').execute()
            if result.data:
                version = result.data

            # Get table information
            result = client.rpc('get_table_info').execute()
            if result.data:
                for row in result.data:
                    tables.append(TableInfo(
                        name=row['table_name'],
                        schema=row.get('table_schema', 'public'),
                        row_count=row.get('row_count'),
                        has_rls=row.get('has_rls', False),
                        indexes=row.get('indexes', []),
                        columns=row.get('columns', []),
                    ))

            # Get extensions
            result = client.rpc('get_extensions').execute()
            if result.data:
                extensions = [e['extname'] for e in result.data]

        except Exception as e:
            logger.warning(f"Failed to get database info via RPC: {e}")

            # Fallback: Direct queries for basic info
            try:
                # Try simple table list query
                result = client.table('processed_content').select('id').limit(0).execute()
                tables.append(TableInfo(name='processed_content', schema='public'))
            except Exception:
                pass

    response = DatabaseStatusResponse(
        connected=connected,
        version=version,
        tables=tables,
        extensions=extensions,
        database_size=db_size,
    )

    meta_dict = request.state.get_meta()

    return APIResponse(
        success=True,
        data=response,
        meta=ResponseMeta(**meta_dict),
    )


@router.get("/{migration_id}")
async def get_migration_details(
    request: Request,
    migration_id: str,
    include_sql: bool = False,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[dict]:
    """
    Get details of a specific migration.

    Args:
        migration_id: Migration ID (filename without .sql extension)
        include_sql: Include full SQL content in response

    Returns:
        Migration details including status and optionally SQL content
    """
    # Find migration file
    migration_file = MIGRATIONS_DIR / f"{migration_id}.sql"

    if not migration_file.exists():
        raise HTTPException(status_code=404, detail=f"Migration not found: {migration_id}")

    client = get_supabase_client()
    applied = await get_applied_migrations(client) if client else {}

    info = get_migration_info(migration_file, applied)

    result = {
        "id": info.id,
        "name": info.name,
        "filename": info.filename,
        "status": info.status.value,
        "applied_at": info.applied_at.isoformat() if info.applied_at else None,
        "checksum": info.checksum,
        "description": info.description,
    }

    if include_sql:
        with open(migration_file, 'r') as f:
            result["sql"] = f.read()

    meta_dict = request.state.get_meta()

    return APIResponse(
        success=True,
        data=result,
        meta=ResponseMeta(**meta_dict),
    )


@router.post("/apply")
async def apply_migrations(
    request: Request,
    payload: MigrationApplyRequest,
    user: UserContext = Depends(get_current_user),
    x_admin_secret: Optional[str] = Header(None, alias="X-Admin-Secret"),
) -> APIResponse[List[MigrationApplyResult]]:
    """
    Apply pending database migrations.

    Requires admin authentication (X-Admin-Secret header).

    Args:
        payload: Migration apply request with options

    Returns:
        List of results for each migration applied
    """
    # Verify admin secret for mutations
    if not verify_admin_secret(x_admin_secret or ""):
        raise HTTPException(status_code=403, detail="Admin authentication required")

    client = get_supabase_client()
    if not client:
        raise HTTPException(status_code=503, detail="Database not configured")

    # Get applied migrations
    applied = await get_applied_migrations(client)

    # Find migrations to apply
    migrations_to_apply = []

    if MIGRATIONS_DIR.exists():
        for filepath in sorted(MIGRATIONS_DIR.glob("*.sql")):
            migration_id = filepath.stem

            # Filter by requested IDs if specified
            if payload.migration_ids and migration_id not in payload.migration_ids:
                continue

            # Skip already applied unless forcing
            if migration_id in applied and not payload.force:
                continue

            migrations_to_apply.append(filepath)

    results = []

    for filepath in migrations_to_apply:
        migration_id = filepath.stem
        started_at = datetime.now(PACIFIC)
        status = MigrationStatus.APPLIED
        statements_executed = 0
        error = None
        sql_preview = None

        try:
            with open(filepath, 'r') as f:
                sql_content = f.read()

            if payload.dry_run:
                # Preview only
                sql_preview = sql_content[:2000] + ("..." if len(sql_content) > 2000 else "")
                status = MigrationStatus.PENDING
            else:
                # Execute migration
                statements = [s.strip() for s in sql_content.split(';') if s.strip()]

                for statement in statements:
                    try:
                        # Execute via RPC or direct query
                        client.rpc('exec_sql', {'sql': statement}).execute()
                        statements_executed += 1
                    except Exception as stmt_error:
                        # Handle "already exists" gracefully
                        error_msg = str(stmt_error).lower()
                        if "already exists" in error_msg or "duplicate" in error_msg:
                            logger.info(f"Skipping duplicate: {error_msg[:100]}")
                            continue
                        else:
                            raise stmt_error

                # Record migration as applied
                try:
                    client.table('schema_migrations').upsert({
                        'migration_id': migration_id,
                        'applied_at': datetime.now(PACIFIC).isoformat(),
                        'checksum': calculate_file_checksum(filepath),
                    }).execute()
                except Exception as e:
                    logger.warning(f"Failed to record migration: {e}")

        except Exception as e:
            status = MigrationStatus.FAILED
            error = str(e)
            logger.error(f"Migration {migration_id} failed: {e}")

        completed_at = datetime.now(PACIFIC)
        duration_ms = int((completed_at - started_at).total_seconds() * 1000)

        results.append(MigrationApplyResult(
            migration_id=migration_id,
            status=status,
            statements_executed=statements_executed,
            duration_ms=duration_ms,
            error=error,
            sql_preview=sql_preview,
        ))

    meta_dict = request.state.get_meta()

    return APIResponse(
        success=all(r.status == MigrationStatus.APPLIED or r.status == MigrationStatus.PENDING for r in results),
        data=results,
        meta=ResponseMeta(**meta_dict),
    )


@router.post("/execute")
async def execute_sql(
    request: Request,
    payload: SQLExecuteRequest,
    user: UserContext = Depends(get_current_user),
    x_admin_secret: Optional[str] = Header(None, alias="X-Admin-Secret"),
) -> APIResponse[SQLExecuteResult]:
    """
    Execute raw SQL against the database (ADMIN ONLY).

    This is a dangerous operation and requires:
    - Admin authentication (X-Admin-Secret header)
    - confirm=true for destructive operations (DROP, TRUNCATE, DELETE without WHERE)

    Args:
        payload: SQL to execute

    Returns:
        Execution result with rows affected or query data
    """
    # Verify admin secret
    if not verify_admin_secret(x_admin_secret or ""):
        raise HTTPException(status_code=403, detail="Admin authentication required")

    client = get_supabase_client()
    if not client:
        raise HTTPException(status_code=503, detail="Database not configured")

    # Check for destructive operations
    sql_upper = payload.sql.upper().strip()
    destructive_patterns = ['DROP', 'TRUNCATE', 'DELETE FROM']
    is_destructive = any(sql_upper.startswith(p) or f" {p}" in sql_upper for p in destructive_patterns)

    if is_destructive and not payload.confirm:
        raise HTTPException(
            status_code=400,
            detail="Destructive operation requires confirm=true"
        )

    started_at = datetime.now(PACIFIC)
    success = False
    rows_affected = None
    data = None
    error = None

    try:
        # Execute SQL
        result = client.rpc('exec_sql', {'sql': payload.sql}).execute()

        success = True

        # Try to extract results
        if result.data:
            if isinstance(result.data, list):
                data = result.data
                rows_affected = len(data)
            elif isinstance(result.data, dict):
                data = [result.data]
                rows_affected = 1

    except Exception as e:
        error = str(e)
        logger.error(f"SQL execution failed: {e}")

    completed_at = datetime.now(PACIFIC)
    duration_ms = int((completed_at - started_at).total_seconds() * 1000)

    result = SQLExecuteResult(
        success=success,
        rows_affected=rows_affected,
        data=data[:100] if data and len(data) > 100 else data,  # Limit response size
        duration_ms=duration_ms,
        error=error,
    )

    meta_dict = request.state.get_meta()

    return APIResponse(
        success=success,
        data=result,
        error=error,
        meta=ResponseMeta(**meta_dict),
    )


@router.get("/tables/{table_name}")
async def get_table_info(
    request: Request,
    table_name: str,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[TableInfo]:
    """
    Get detailed information about a specific table.

    Args:
        table_name: Name of the table

    Returns:
        Table information including columns, indexes, and RLS status
    """
    client = get_supabase_client()
    if not client:
        raise HTTPException(status_code=503, detail="Database not configured")

    try:
        # Get table columns
        columns = []
        try:
            result = client.rpc('get_table_columns', {'p_table_name': table_name}).execute()
            if result.data:
                columns = [c['column_name'] for c in result.data]
        except Exception:
            # Fallback - try to query table
            try:
                result = client.table(table_name).select('*').limit(0).execute()
                # Can't easily get column names this way
            except Exception:
                raise HTTPException(status_code=404, detail=f"Table not found: {table_name}")

        # Get indexes
        indexes = []
        try:
            result = client.rpc('get_table_indexes', {'p_table_name': table_name}).execute()
            if result.data:
                indexes = [i['indexname'] for i in result.data]
        except Exception:
            pass

        # Check RLS
        has_rls = False
        try:
            result = client.rpc('check_table_rls', {'p_table_name': table_name}).execute()
            if result.data:
                has_rls = result.data.get('has_rls', False)
        except Exception:
            pass

        # Get row count
        row_count = None
        try:
            result = client.table(table_name).select('*', count='exact').limit(0).execute()
            row_count = result.count
        except Exception:
            pass

        table_info = TableInfo(
            name=table_name,
            schema='public',
            row_count=row_count,
            has_rls=has_rls,
            indexes=indexes,
            columns=columns,
        )

        meta_dict = request.state.get_meta()

        return APIResponse(
            success=True,
            data=table_info,
            meta=ResponseMeta(**meta_dict),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get table info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def migrations_health(request: Request) -> APIResponse[dict]:
    """
    Health check for migrations system.

    No authentication required - used for monitoring.
    """
    client = get_supabase_client()

    # Check database connection
    db_connected = False
    if client:
        try:
            client.table('processed_content').select('id').limit(1).execute()
            db_connected = True
        except Exception:
            pass

    # Check migrations directory
    migrations_available = MIGRATIONS_DIR.exists()
    migration_count = len(list(MIGRATIONS_DIR.glob("*.sql"))) if migrations_available else 0

    meta_dict = request.state.get_meta()

    return APIResponse(
        success=True,
        data={
            'status': 'healthy' if db_connected else 'degraded',
            'database_connected': db_connected,
            'migrations_directory': str(MIGRATIONS_DIR),
            'migrations_available': migrations_available,
            'migration_files': migration_count,
            'timestamp': datetime.now(PACIFIC).isoformat(),
        },
        meta=ResponseMeta(**meta_dict),
    )
