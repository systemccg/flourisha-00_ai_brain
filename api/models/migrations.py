"""
Database Migration Models

Pydantic models for database migration management API.
"""
from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class MigrationStatus(str, Enum):
    """Migration execution status."""
    PENDING = "pending"
    APPLIED = "applied"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class TableInfo(BaseModel):
    """Information about a database table."""
    name: str = Field(..., description="Table name")
    schema_name: str = Field(default="public", description="Schema name", alias="schema")
    row_count: Optional[int] = Field(default=None, description="Approximate row count")
    has_rls: bool = Field(default=False, description="Whether RLS is enabled")
    indexes: List[str] = Field(default_factory=list, description="Index names")
    columns: List[str] = Field(default_factory=list, description="Column names")

    model_config = {"populate_by_name": True}


class MigrationInfo(BaseModel):
    """Information about a migration file."""
    id: str = Field(..., description="Migration ID (filename without extension)")
    name: str = Field(..., description="Migration name")
    filename: str = Field(..., description="Full filename")
    status: MigrationStatus = Field(..., description="Current status")
    applied_at: Optional[datetime] = Field(default=None, description="When applied")
    checksum: Optional[str] = Field(default=None, description="File checksum")
    description: Optional[str] = Field(default=None, description="Migration description")


class MigrationApplyRequest(BaseModel):
    """Request to apply migrations."""
    migration_ids: Optional[List[str]] = Field(
        default=None,
        description="Specific migrations to apply (None = all pending)"
    )
    dry_run: bool = Field(
        default=False,
        description="Preview SQL without executing"
    )
    force: bool = Field(
        default=False,
        description="Force re-apply even if already applied"
    )


class MigrationApplyResult(BaseModel):
    """Result of applying a migration."""
    migration_id: str = Field(..., description="Migration ID")
    status: MigrationStatus = Field(..., description="Result status")
    statements_executed: int = Field(default=0, description="SQL statements executed")
    duration_ms: int = Field(default=0, description="Execution duration")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    sql_preview: Optional[str] = Field(default=None, description="SQL preview (dry run)")


class MigrationStatusResponse(BaseModel):
    """Response for migration status endpoint."""
    migrations: List[MigrationInfo] = Field(..., description="All migrations")
    total: int = Field(..., description="Total migration count")
    applied: int = Field(..., description="Applied count")
    pending: int = Field(..., description="Pending count")
    failed: int = Field(..., description="Failed count")


class DatabaseStatusResponse(BaseModel):
    """Response for database status endpoint."""
    connected: bool = Field(..., description="Database connection status")
    version: Optional[str] = Field(default=None, description="PostgreSQL version")
    tables: List[TableInfo] = Field(default_factory=list, description="Table information")
    extensions: List[str] = Field(default_factory=list, description="Installed extensions")
    database_size: Optional[str] = Field(default=None, description="Database size")


class SQLExecuteRequest(BaseModel):
    """Request to execute raw SQL (admin only)."""
    sql: str = Field(..., min_length=1, max_length=50000, description="SQL to execute")
    confirm: bool = Field(default=False, description="Confirm destructive operations")


class SQLExecuteResult(BaseModel):
    """Result of SQL execution."""
    success: bool = Field(..., description="Execution success")
    rows_affected: Optional[int] = Field(default=None, description="Rows affected")
    data: Optional[List[dict]] = Field(default=None, description="Query results")
    duration_ms: int = Field(default=0, description="Execution duration")
    error: Optional[str] = Field(default=None, description="Error message if failed")
