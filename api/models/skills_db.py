"""
Skills Database Models

Pydantic models for skills database storage and migration.
Skills are migrated from ~/.claude/skills/ filesystem to Supabase.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from uuid import UUID


class SkillStatus(str, Enum):
    """Skill status in database."""
    ACTIVE = "active"
    DISABLED = "disabled"
    DEPRECATED = "deprecated"
    DRAFT = "draft"


class SkillSource(str, Enum):
    """Where the skill was defined."""
    FILESYSTEM = "filesystem"  # Synced from ~/.claude/skills/
    DATABASE = "database"      # Created directly in database
    IMPORTED = "imported"      # Imported from external source


# === Database Schema Models ===

class SkillWorkflowDB(BaseModel):
    """Workflow stored in database."""
    id: Optional[UUID] = Field(None, description="Workflow UUID")
    skill_id: UUID = Field(..., description="Parent skill ID")
    name: str = Field(..., description="Workflow name")
    description: Optional[str] = Field(None, description="Workflow description")
    content: str = Field(..., description="Full workflow content")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class SkillAssetDB(BaseModel):
    """Asset stored in database (metadata only, content in storage)."""
    id: Optional[UUID] = Field(None, description="Asset UUID")
    skill_id: UUID = Field(..., description="Parent skill ID")
    name: str = Field(..., description="Asset filename")
    content_type: Optional[str] = Field(None, description="MIME type")
    size_bytes: int = Field(..., description="File size")
    storage_path: Optional[str] = Field(None, description="Storage bucket path")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")


class SkillDB(BaseModel):
    """Skill stored in database.

    Maps to the `skills` table in Supabase.
    """
    id: Optional[UUID] = Field(None, description="Skill UUID")
    tenant_id: str = Field(default="default", description="Tenant isolation")

    # Core metadata
    name: str = Field(..., description="Skill name (unique identifier)")
    display_name: Optional[str] = Field(None, description="Human-readable display name")
    description: Optional[str] = Field(None, description="Skill description")

    # Content
    skill_md_content: Optional[str] = Field(None, description="Full SKILL.md content")
    frontmatter: Optional[Dict[str, Any]] = Field(None, description="Parsed YAML frontmatter")
    trigger_phrases: Optional[List[str]] = Field(default_factory=list, description="USE WHEN trigger phrases")

    # Status and source
    status: SkillStatus = Field(default=SkillStatus.ACTIVE, description="Current status")
    source: SkillSource = Field(default=SkillSource.FILESYSTEM, description="Where skill originated")

    # Filesystem sync tracking
    filesystem_path: Optional[str] = Field(None, description="Original filesystem path")
    filesystem_hash: Optional[str] = Field(None, description="Hash of filesystem content for sync")
    last_synced_at: Optional[datetime] = Field(None, description="Last filesystem sync")

    # Timestamps
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    # Related data (populated separately)
    workflows: Optional[List[SkillWorkflowDB]] = Field(None, description="Skill workflows")
    assets: Optional[List[SkillAssetDB]] = Field(None, description="Skill assets")


# === API Request/Response Models ===

class SkillCreateRequest(BaseModel):
    """Request to create a new skill."""
    name: str = Field(..., min_length=1, max_length=100, description="Skill name")
    display_name: Optional[str] = Field(None, max_length=200, description="Display name")
    description: Optional[str] = Field(None, max_length=2000, description="Description")
    skill_md_content: Optional[str] = Field(None, description="SKILL.md content")
    trigger_phrases: Optional[List[str]] = Field(default_factory=list, description="Trigger phrases")
    status: Optional[SkillStatus] = Field(SkillStatus.ACTIVE, description="Initial status")


class SkillUpdateRequest(BaseModel):
    """Request to update a skill."""
    display_name: Optional[str] = Field(None, max_length=200, description="Display name")
    description: Optional[str] = Field(None, max_length=2000, description="Description")
    skill_md_content: Optional[str] = Field(None, description="SKILL.md content")
    trigger_phrases: Optional[List[str]] = Field(None, description="Trigger phrases")
    status: Optional[SkillStatus] = Field(None, description="Status")


class SkillSummaryDB(BaseModel):
    """Summary view of a skill for listings."""
    id: UUID = Field(..., description="Skill UUID")
    name: str = Field(..., description="Skill name")
    display_name: Optional[str] = Field(None, description="Display name")
    description: Optional[str] = Field(None, description="Short description")
    status: SkillStatus = Field(..., description="Current status")
    source: SkillSource = Field(..., description="Where skill originated")
    workflow_count: int = Field(default=0, description="Number of workflows")
    asset_count: int = Field(default=0, description="Number of assets")
    last_synced_at: Optional[datetime] = Field(None, description="Last sync from filesystem")
    updated_at: Optional[datetime] = Field(None, description="Last update")


class SkillListResponse(BaseModel):
    """Response for listing skills from database."""
    skills: List[SkillSummaryDB] = Field(..., description="List of skills")
    total: int = Field(..., description="Total count")
    synced_count: int = Field(default=0, description="Count synced from filesystem")
    database_only_count: int = Field(default=0, description="Count created in database only")


class WorkflowCreateRequest(BaseModel):
    """Request to create a workflow for a skill."""
    name: str = Field(..., min_length=1, max_length=100, description="Workflow name")
    description: Optional[str] = Field(None, max_length=500, description="Description")
    content: str = Field(..., description="Workflow markdown content")


class WorkflowUpdateRequest(BaseModel):
    """Request to update a workflow."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Workflow name")
    description: Optional[str] = Field(None, max_length=500, description="Description")
    content: Optional[str] = Field(None, description="Workflow content")


# === Sync Models ===

class SkillSyncStatus(BaseModel):
    """Status of a skill during sync operation."""
    name: str = Field(..., description="Skill name")
    action: str = Field(..., description="Action taken: 'created', 'updated', 'unchanged', 'error'")
    filesystem_path: Optional[str] = Field(None, description="Filesystem path")
    error: Optional[str] = Field(None, description="Error message if action='error'")


class SkillSyncResult(BaseModel):
    """Result of sync operation."""
    total_filesystem_skills: int = Field(..., description="Skills found in filesystem")
    created: int = Field(default=0, description="New skills created")
    updated: int = Field(default=0, description="Skills updated")
    unchanged: int = Field(default=0, description="Skills unchanged")
    errors: int = Field(default=0, description="Skills with errors")
    details: List[SkillSyncStatus] = Field(default_factory=list, description="Per-skill status")
    synced_at: datetime = Field(..., description="Sync timestamp")


class SkillMigrationRequest(BaseModel):
    """Request to migrate skills from filesystem to database."""
    force_update: bool = Field(False, description="Force update even if unchanged")
    include_workflows: bool = Field(True, description="Include workflows in migration")
    include_assets: bool = Field(False, description="Include asset metadata (not content)")
    skill_names: Optional[List[str]] = Field(None, description="Specific skills to migrate (None=all)")


# === SQL Schema (for reference/migration) ===

SKILLS_TABLE_SQL = """
-- Skills table for database persistence
CREATE TABLE IF NOT EXISTS skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL DEFAULT 'default',

    -- Core metadata
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(200),
    description TEXT,

    -- Content
    skill_md_content TEXT,
    frontmatter JSONB,
    trigger_phrases JSONB DEFAULT '[]',

    -- Status and source
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    source VARCHAR(20) NOT NULL DEFAULT 'filesystem',

    -- Filesystem sync tracking
    filesystem_path TEXT,
    filesystem_hash VARCHAR(64),
    last_synced_at TIMESTAMPTZ,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    UNIQUE(tenant_id, name),
    CHECK (status IN ('active', 'disabled', 'deprecated', 'draft')),
    CHECK (source IN ('filesystem', 'database', 'imported'))
);

-- Enable RLS
ALTER TABLE skills ENABLE ROW LEVEL SECURITY;

-- RLS Policy
CREATE POLICY "tenant_skill_access"
ON skills
FOR ALL
USING (tenant_id = current_setting('app.tenant_id', true));

-- Indexes
CREATE INDEX idx_skills_tenant ON skills(tenant_id);
CREATE INDEX idx_skills_name ON skills(name);
CREATE INDEX idx_skills_status ON skills(status);
CREATE INDEX idx_skills_source ON skills(source);
CREATE INDEX idx_skills_trigger_phrases ON skills USING GIN (trigger_phrases);

-- Skill workflows table
CREATE TABLE IF NOT EXISTS skill_workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(skill_id, name)
);

-- Enable RLS
ALTER TABLE skill_workflows ENABLE ROW LEVEL SECURITY;

-- Indexes
CREATE INDEX idx_workflows_skill ON skill_workflows(skill_id);

-- Skill assets table (metadata only)
CREATE TABLE IF NOT EXISTS skill_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    content_type VARCHAR(100),
    size_bytes INTEGER,
    storage_path TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(skill_id, name)
);

-- Enable RLS
ALTER TABLE skill_assets ENABLE ROW LEVEL SECURITY;

-- Indexes
CREATE INDEX idx_assets_skill ON skill_assets(skill_id);

-- Updated trigger
CREATE OR REPLACE FUNCTION update_skills_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER skills_updated_at
    BEFORE UPDATE ON skills
    FOR EACH ROW
    EXECUTE FUNCTION update_skills_updated_at();

CREATE TRIGGER skill_workflows_updated_at
    BEFORE UPDATE ON skill_workflows
    FOR EACH ROW
    EXECUTE FUNCTION update_skills_updated_at();
"""
