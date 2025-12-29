"""
Skills Database Router

API endpoints for managing skills in the database.
Supports CRUD operations and filesystem-to-database sync.
"""
import os
import re
import yaml
import hashlib
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from zoneinfo import ZoneInfo
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Query, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from models.response import APIResponse, ResponseMeta
from models.skills_db import (
    SkillDB, SkillSummaryDB, SkillListResponse, SkillStatus, SkillSource,
    SkillCreateRequest, SkillUpdateRequest,
    SkillWorkflowDB, WorkflowCreateRequest, WorkflowUpdateRequest,
    SkillAssetDB, SkillSyncResult, SkillSyncStatus, SkillMigrationRequest,
)
from middleware.auth import get_current_user, UserContext

router = APIRouter(prefix="/api/skills-db", tags=["Skills Database"])

# Default skills directory
SKILLS_DIR = Path(os.path.expanduser("~/.claude/skills"))
PACIFIC = ZoneInfo("America/Los_Angeles")

# In-memory storage (will be replaced with Supabase)
# This allows the API to work before the database table is created
_skills_store: Dict[str, SkillDB] = {}
_workflows_store: Dict[str, List[SkillWorkflowDB]] = {}


def get_supabase_client():
    """Get Supabase client for database operations.

    Returns None if not configured, falling back to in-memory storage.
    """
    try:
        import os
        from supabase import create_client

        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY")

        if url and key:
            return create_client(url, key)
    except Exception:
        pass
    return None


def compute_skill_hash(skill_path: Path) -> str:
    """Compute hash of skill content for sync detection."""
    hasher = hashlib.sha256()
    skill_md = skill_path / "SKILL.md"

    if skill_md.exists():
        hasher.update(skill_md.read_bytes())

    # Include workflows in hash
    workflows_dir = skill_path / "workflows"
    if workflows_dir.exists():
        for wf in sorted(workflows_dir.glob("*.md")):
            hasher.update(wf.read_bytes())

    return hasher.hexdigest()[:16]


def parse_skill_frontmatter(skill_path: Path) -> Dict[str, Any]:
    """Parse YAML frontmatter from SKILL.md."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return {}

    try:
        content = skill_md.read_text()
        match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if match:
            return yaml.safe_load(match.group(1)) or {}
    except Exception:
        pass
    return {}


def extract_trigger_phrases(description: str) -> List[str]:
    """Extract trigger phrases from description using 'USE WHEN' pattern."""
    triggers = []
    if not description:
        return triggers

    use_when_match = re.search(r'USE WHEN\s+([^.]+)', description, re.IGNORECASE)
    if use_when_match:
        triggers_text = use_when_match.group(1)
        parts = re.split(r'\s+OR\s+|,\s*', triggers_text, flags=re.IGNORECASE)
        triggers = [p.strip().strip("'\"") for p in parts if p.strip()]

    return triggers


def read_skill_from_filesystem(skill_path: Path) -> Optional[SkillDB]:
    """Read a skill from the filesystem and return as SkillDB."""
    if not skill_path.is_dir():
        return None

    name = skill_path.name
    if name.startswith('.') or name == '__pycache__':
        return None

    skill_md = skill_path / "SKILL.md"
    frontmatter = parse_skill_frontmatter(skill_path)
    description = frontmatter.get('description', '')

    skill_md_content = None
    if skill_md.exists():
        skill_md_content = skill_md.read_text()

    return SkillDB(
        name=name,
        display_name=frontmatter.get('name', name),
        description=description[:2000] if description else None,
        skill_md_content=skill_md_content,
        frontmatter=frontmatter,
        trigger_phrases=extract_trigger_phrases(description),
        status=SkillStatus.ACTIVE,
        source=SkillSource.FILESYSTEM,
        filesystem_path=str(skill_path),
        filesystem_hash=compute_skill_hash(skill_path),
        last_synced_at=datetime.now(PACIFIC),
    )


def read_workflows_from_filesystem(skill_path: Path, skill_id: UUID) -> List[SkillWorkflowDB]:
    """Read workflows from a skill's workflows directory."""
    workflows = []
    workflows_dir = skill_path / "workflows"

    if not workflows_dir.exists():
        return workflows

    for wf_file in sorted(workflows_dir.glob("*.md")):
        content = wf_file.read_text()

        # Extract description from first heading
        description = None
        for line in content.strip().split('\n'):
            if line.startswith('#'):
                description = line.lstrip('#').strip()
                break

        workflows.append(SkillWorkflowDB(
            skill_id=skill_id,
            name=wf_file.stem,
            description=description,
            content=content,
        ))

    return workflows


# === CRUD Endpoints ===

@router.get("", response_model=APIResponse[SkillListResponse])
async def list_skills_db(
    request: Request,
    status: Optional[SkillStatus] = Query(None, description="Filter by status"),
    source: Optional[SkillSource] = Query(None, description="Filter by source"),
    search: Optional[str] = Query(None, min_length=2, description="Search in name/description"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[SkillListResponse]:
    """
    List all skills from the database.

    Supports filtering by status, source, and text search.
    Returns summary information for each skill.

    **Query Parameters:**
    - status: Filter by skill status (active, disabled, etc.)
    - source: Filter by source (filesystem, database)
    - search: Text search in name and description

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        supabase = get_supabase_client()

        if supabase:
            # Query from Supabase
            query = supabase.table('skills').select('*')

            if status:
                query = query.eq('status', status.value)
            if source:
                query = query.eq('source', source.value)
            if search:
                query = query.or_(f'name.ilike.%{search}%,description.ilike.%{search}%')

            result = query.execute()
            skills_data = result.data or []

            # Get workflow counts
            skills = []
            for s in skills_data:
                wf_result = supabase.table('skill_workflows').select('id', count='exact').eq('skill_id', s['id']).execute()
                asset_result = supabase.table('skill_assets').select('id', count='exact').eq('skill_id', s['id']).execute()

                skills.append(SkillSummaryDB(
                    id=s['id'],
                    name=s['name'],
                    display_name=s.get('display_name'),
                    description=s.get('description', '')[:200] if s.get('description') else None,
                    status=SkillStatus(s['status']),
                    source=SkillSource(s['source']),
                    workflow_count=wf_result.count or 0,
                    asset_count=asset_result.count or 0,
                    last_synced_at=s.get('last_synced_at'),
                    updated_at=s.get('updated_at'),
                ))

        else:
            # Fall back to in-memory store
            skills = []
            for name, skill in _skills_store.items():
                if status and skill.status != status:
                    continue
                if source and skill.source != source:
                    continue
                if search and search.lower() not in name.lower() and (not skill.description or search.lower() not in skill.description.lower()):
                    continue

                workflows = _workflows_store.get(name, [])
                skills.append(SkillSummaryDB(
                    id=skill.id or UUID(int=hash(name) & ((1 << 128) - 1)),
                    name=skill.name,
                    display_name=skill.display_name,
                    description=skill.description[:200] if skill.description else None,
                    status=skill.status,
                    source=skill.source,
                    workflow_count=len(workflows),
                    asset_count=0,
                    last_synced_at=skill.last_synced_at,
                    updated_at=skill.updated_at,
                ))

        # Count by source
        synced = sum(1 for s in skills if s.source == SkillSource.FILESYSTEM)
        db_only = sum(1 for s in skills if s.source == SkillSource.DATABASE)

        return APIResponse(
            success=True,
            data=SkillListResponse(
                skills=skills,
                total=len(skills),
                synced_count=synced,
                database_only_count=db_only,
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=f"Failed to list skills: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/{skill_id}", response_model=APIResponse[SkillDB])
async def get_skill_db(
    request: Request,
    skill_id: str,
    include_workflows: bool = Query(True, description="Include workflows"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[SkillDB]:
    """
    Get a skill by ID or name from the database.

    **Path Parameters:**
    - skill_id: UUID or skill name

    **Query Parameters:**
    - include_workflows: Whether to include workflow details

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        supabase = get_supabase_client()

        if supabase:
            # Try by UUID first, then by name
            try:
                UUID(skill_id)
                result = supabase.table('skills').select('*').eq('id', skill_id).single().execute()
            except ValueError:
                result = supabase.table('skills').select('*').eq('name', skill_id).single().execute()

            if not result.data:
                return APIResponse(
                    success=False,
                    error=f"Skill not found: {skill_id}",
                    meta=ResponseMeta(**meta_dict),
                )

            skill = SkillDB(**result.data)

            if include_workflows:
                wf_result = supabase.table('skill_workflows').select('*').eq('skill_id', skill.id).execute()
                skill.workflows = [SkillWorkflowDB(**w) for w in (wf_result.data or [])]

        else:
            # In-memory lookup
            if skill_id in _skills_store:
                skill = _skills_store[skill_id]
            else:
                # Check by name
                skill = next((s for s in _skills_store.values() if s.name == skill_id), None)

            if not skill:
                return APIResponse(
                    success=False,
                    error=f"Skill not found: {skill_id}",
                    meta=ResponseMeta(**meta_dict),
                )

            if include_workflows:
                skill.workflows = _workflows_store.get(skill.name, [])

        return APIResponse(
            success=True,
            data=skill,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=f"Failed to get skill: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.post("", response_model=APIResponse[SkillDB])
async def create_skill_db(
    request: Request,
    skill: SkillCreateRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[SkillDB]:
    """
    Create a new skill in the database.

    Creates a skill that exists only in the database (not filesystem).
    Use /sync to migrate filesystem skills.

    **Request Body:**
    - name: Unique skill name
    - display_name: Human-readable name
    - description: Skill description
    - skill_md_content: SKILL.md content
    - trigger_phrases: List of trigger phrases
    - status: Initial status

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        now = datetime.now(PACIFIC)
        supabase = get_supabase_client()

        new_skill = SkillDB(
            name=skill.name,
            display_name=skill.display_name,
            description=skill.description,
            skill_md_content=skill.skill_md_content,
            trigger_phrases=skill.trigger_phrases or [],
            status=skill.status or SkillStatus.ACTIVE,
            source=SkillSource.DATABASE,
            created_at=now,
            updated_at=now,
        )

        if supabase:
            result = supabase.table('skills').insert({
                'name': new_skill.name,
                'display_name': new_skill.display_name,
                'description': new_skill.description,
                'skill_md_content': new_skill.skill_md_content,
                'trigger_phrases': new_skill.trigger_phrases,
                'status': new_skill.status.value,
                'source': new_skill.source.value,
                'tenant_id': 'default',
            }).execute()

            if result.data:
                new_skill = SkillDB(**result.data[0])
        else:
            # In-memory
            new_skill.id = UUID(int=hash(skill.name) & ((1 << 128) - 1))
            _skills_store[skill.name] = new_skill

        return APIResponse(
            success=True,
            data=new_skill,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=f"Failed to create skill: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.put("/{skill_id}", response_model=APIResponse[SkillDB])
async def update_skill_db(
    request: Request,
    skill_id: str,
    updates: SkillUpdateRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[SkillDB]:
    """
    Update a skill in the database.

    Only updates provided fields.

    **Path Parameters:**
    - skill_id: UUID or skill name

    **Request Body (all optional):**
    - display_name: New display name
    - description: New description
    - skill_md_content: New SKILL.md content
    - trigger_phrases: New trigger phrases
    - status: New status

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        supabase = get_supabase_client()

        # Build update dict
        update_data = {}
        if updates.display_name is not None:
            update_data['display_name'] = updates.display_name
        if updates.description is not None:
            update_data['description'] = updates.description
        if updates.skill_md_content is not None:
            update_data['skill_md_content'] = updates.skill_md_content
        if updates.trigger_phrases is not None:
            update_data['trigger_phrases'] = updates.trigger_phrases
        if updates.status is not None:
            update_data['status'] = updates.status.value

        if not update_data:
            return APIResponse(
                success=False,
                error="No updates provided",
                meta=ResponseMeta(**meta_dict),
            )

        if supabase:
            # Try by UUID first, then by name
            try:
                UUID(skill_id)
                result = supabase.table('skills').update(update_data).eq('id', skill_id).execute()
            except ValueError:
                result = supabase.table('skills').update(update_data).eq('name', skill_id).execute()

            if not result.data:
                return APIResponse(
                    success=False,
                    error=f"Skill not found: {skill_id}",
                    meta=ResponseMeta(**meta_dict),
                )

            skill = SkillDB(**result.data[0])

        else:
            # In-memory
            skill = _skills_store.get(skill_id)
            if not skill:
                skill = next((s for s in _skills_store.values() if s.name == skill_id), None)

            if not skill:
                return APIResponse(
                    success=False,
                    error=f"Skill not found: {skill_id}",
                    meta=ResponseMeta(**meta_dict),
                )

            for key, value in update_data.items():
                setattr(skill, key, value if key != 'status' else SkillStatus(value))
            skill.updated_at = datetime.now(PACIFIC)

        return APIResponse(
            success=True,
            data=skill,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=f"Failed to update skill: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.delete("/{skill_id}", response_model=APIResponse[dict])
async def delete_skill_db(
    request: Request,
    skill_id: str,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[dict]:
    """
    Delete a skill from the database.

    Note: This only removes the database record. Filesystem skills
    will be re-created on next sync.

    **Path Parameters:**
    - skill_id: UUID or skill name

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        supabase = get_supabase_client()

        if supabase:
            # Try by UUID first, then by name
            try:
                UUID(skill_id)
                result = supabase.table('skills').delete().eq('id', skill_id).execute()
            except ValueError:
                result = supabase.table('skills').delete().eq('name', skill_id).execute()

            deleted_count = len(result.data) if result.data else 0

        else:
            # In-memory
            if skill_id in _skills_store:
                del _skills_store[skill_id]
                _workflows_store.pop(skill_id, None)
                deleted_count = 1
            else:
                # Check by name
                to_delete = None
                for name, s in _skills_store.items():
                    if s.name == skill_id:
                        to_delete = name
                        break
                if to_delete:
                    del _skills_store[to_delete]
                    _workflows_store.pop(to_delete, None)
                    deleted_count = 1
                else:
                    deleted_count = 0

        return APIResponse(
            success=True,
            data={"deleted": deleted_count > 0, "skill_id": skill_id},
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=f"Failed to delete skill: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


# === Workflow Endpoints ===

@router.get("/{skill_id}/workflows", response_model=APIResponse[List[SkillWorkflowDB]])
async def get_skill_workflows_db(
    request: Request,
    skill_id: str,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[List[SkillWorkflowDB]]:
    """
    Get all workflows for a skill from the database.

    **Path Parameters:**
    - skill_id: UUID or skill name

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        supabase = get_supabase_client()

        if supabase:
            # Get skill ID
            try:
                UUID(skill_id)
                skill_uuid = skill_id
            except ValueError:
                skill_result = supabase.table('skills').select('id').eq('name', skill_id).single().execute()
                if not skill_result.data:
                    return APIResponse(
                        success=False,
                        error=f"Skill not found: {skill_id}",
                        meta=ResponseMeta(**meta_dict),
                    )
                skill_uuid = skill_result.data['id']

            result = supabase.table('skill_workflows').select('*').eq('skill_id', skill_uuid).execute()
            workflows = [SkillWorkflowDB(**w) for w in (result.data or [])]

        else:
            workflows = _workflows_store.get(skill_id, [])

        return APIResponse(
            success=True,
            data=workflows,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=f"Failed to get workflows: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.post("/{skill_id}/workflows", response_model=APIResponse[SkillWorkflowDB])
async def create_workflow_db(
    request: Request,
    skill_id: str,
    workflow: WorkflowCreateRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[SkillWorkflowDB]:
    """
    Create a workflow for a skill.

    **Path Parameters:**
    - skill_id: UUID or skill name

    **Request Body:**
    - name: Workflow name
    - description: Workflow description
    - content: Workflow markdown content

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        supabase = get_supabase_client()

        if supabase:
            # Get skill ID
            try:
                UUID(skill_id)
                skill_uuid = skill_id
            except ValueError:
                skill_result = supabase.table('skills').select('id').eq('name', skill_id).single().execute()
                if not skill_result.data:
                    return APIResponse(
                        success=False,
                        error=f"Skill not found: {skill_id}",
                        meta=ResponseMeta(**meta_dict),
                    )
                skill_uuid = skill_result.data['id']

            result = supabase.table('skill_workflows').insert({
                'skill_id': skill_uuid,
                'name': workflow.name,
                'description': workflow.description,
                'content': workflow.content,
            }).execute()

            new_workflow = SkillWorkflowDB(**result.data[0])

        else:
            # In-memory
            new_workflow = SkillWorkflowDB(
                skill_id=UUID(int=hash(skill_id) & ((1 << 128) - 1)),
                name=workflow.name,
                description=workflow.description,
                content=workflow.content,
            )
            if skill_id not in _workflows_store:
                _workflows_store[skill_id] = []
            _workflows_store[skill_id].append(new_workflow)

        return APIResponse(
            success=True,
            data=new_workflow,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=f"Failed to create workflow: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


# === Sync Endpoints ===

@router.post("/sync", response_model=APIResponse[SkillSyncResult])
async def sync_skills_from_filesystem(
    request: Request,
    migration: Optional[SkillMigrationRequest] = None,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[SkillSyncResult]:
    """
    Sync skills from filesystem to database.

    Reads all skills from ~/.claude/skills/ and syncs them to the database.
    Uses content hashing to detect changes and avoid unnecessary updates.

    **Request Body (optional):**
    - force_update: Force update even if content hash matches
    - include_workflows: Include workflows in sync (default: true)
    - include_assets: Include asset metadata (default: false)
    - skill_names: Specific skills to sync (None = all)

    **Returns:**
    - Sync statistics and per-skill status

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        migration = migration or SkillMigrationRequest()
        now = datetime.now(PACIFIC)
        supabase = get_supabase_client()

        result = SkillSyncResult(
            total_filesystem_skills=0,
            synced_at=now,
            details=[],
        )

        if not SKILLS_DIR.exists():
            return APIResponse(
                success=True,
                data=result,
                meta=ResponseMeta(**meta_dict),
            )

        # Get existing skills from database
        existing_skills = {}
        if supabase:
            existing_result = supabase.table('skills').select('name, filesystem_hash').execute()
            existing_skills = {s['name']: s['filesystem_hash'] for s in (existing_result.data or [])}
        else:
            existing_skills = {name: s.filesystem_hash for name, s in _skills_store.items()}

        # Process each skill
        for skill_path in sorted(SKILLS_DIR.iterdir()):
            if not skill_path.is_dir():
                continue

            name = skill_path.name
            if name.startswith('.') or name == '__pycache__':
                continue

            # Filter by specific names if provided
            if migration.skill_names and name not in migration.skill_names:
                continue

            result.total_filesystem_skills += 1

            try:
                skill = read_skill_from_filesystem(skill_path)
                if not skill:
                    result.details.append(SkillSyncStatus(
                        name=name,
                        action="error",
                        filesystem_path=str(skill_path),
                        error="Could not parse skill",
                    ))
                    result.errors += 1
                    continue

                current_hash = skill.filesystem_hash
                existing_hash = existing_skills.get(name)

                # Check if needs update
                if existing_hash and existing_hash == current_hash and not migration.force_update:
                    result.unchanged += 1
                    result.details.append(SkillSyncStatus(
                        name=name,
                        action="unchanged",
                        filesystem_path=str(skill_path),
                    ))
                    continue

                # Prepare data
                skill_data = {
                    'name': skill.name,
                    'display_name': skill.display_name,
                    'description': skill.description,
                    'skill_md_content': skill.skill_md_content,
                    'frontmatter': skill.frontmatter,
                    'trigger_phrases': skill.trigger_phrases,
                    'status': skill.status.value,
                    'source': skill.source.value,
                    'filesystem_path': skill.filesystem_path,
                    'filesystem_hash': skill.filesystem_hash,
                    'last_synced_at': now.isoformat(),
                    'tenant_id': 'default',
                }

                if supabase:
                    if name in existing_skills:
                        # Update
                        update_result = supabase.table('skills').update(skill_data).eq('name', name).execute()
                        skill_id = update_result.data[0]['id'] if update_result.data else None
                        action = "updated"
                        result.updated += 1
                    else:
                        # Create
                        insert_result = supabase.table('skills').insert(skill_data).execute()
                        skill_id = insert_result.data[0]['id'] if insert_result.data else None
                        action = "created"
                        result.created += 1

                    # Sync workflows if requested
                    if migration.include_workflows and skill_id:
                        # Delete existing workflows
                        supabase.table('skill_workflows').delete().eq('skill_id', skill_id).execute()

                        # Insert new workflows
                        workflows = read_workflows_from_filesystem(skill_path, UUID(skill_id))
                        for wf in workflows:
                            supabase.table('skill_workflows').insert({
                                'skill_id': skill_id,
                                'name': wf.name,
                                'description': wf.description,
                                'content': wf.content,
                            }).execute()

                else:
                    # In-memory storage
                    if name in _skills_store:
                        action = "updated"
                        result.updated += 1
                    else:
                        action = "created"
                        result.created += 1

                    skill.id = UUID(int=hash(name) & ((1 << 128) - 1))
                    _skills_store[name] = skill

                    if migration.include_workflows:
                        _workflows_store[name] = read_workflows_from_filesystem(skill_path, skill.id)

                result.details.append(SkillSyncStatus(
                    name=name,
                    action=action,
                    filesystem_path=str(skill_path),
                ))

            except Exception as e:
                result.errors += 1
                result.details.append(SkillSyncStatus(
                    name=name,
                    action="error",
                    filesystem_path=str(skill_path),
                    error=str(e),
                ))

        return APIResponse(
            success=True,
            data=result,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=f"Failed to sync skills: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/sync/status", response_model=APIResponse[dict])
async def get_sync_status(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[dict]:
    """
    Get current sync status between filesystem and database.

    Compares skills in filesystem with database to identify:
    - Skills only in filesystem (need sync)
    - Skills only in database (database-only)
    - Skills with content changes
    - Skills that are in sync

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        supabase = get_supabase_client()

        # Get filesystem skills
        fs_skills = {}
        if SKILLS_DIR.exists():
            for skill_path in SKILLS_DIR.iterdir():
                if skill_path.is_dir():
                    name = skill_path.name
                    if not name.startswith('.') and name != '__pycache__':
                        fs_skills[name] = compute_skill_hash(skill_path)

        # Get database skills
        db_skills = {}
        if supabase:
            result = supabase.table('skills').select('name, filesystem_hash, source').execute()
            for s in (result.data or []):
                db_skills[s['name']] = {
                    'hash': s.get('filesystem_hash'),
                    'source': s.get('source'),
                }
        else:
            for name, skill in _skills_store.items():
                db_skills[name] = {
                    'hash': skill.filesystem_hash,
                    'source': skill.source.value,
                }

        # Analyze differences
        fs_only = []
        db_only = []
        changed = []
        in_sync = []

        for name, fs_hash in fs_skills.items():
            if name not in db_skills:
                fs_only.append(name)
            elif db_skills[name]['hash'] != fs_hash:
                changed.append(name)
            else:
                in_sync.append(name)

        for name, info in db_skills.items():
            if name not in fs_skills and info['source'] != 'database':
                db_only.append(name)

        return APIResponse(
            success=True,
            data={
                "filesystem_count": len(fs_skills),
                "database_count": len(db_skills),
                "filesystem_only": fs_only,
                "database_only": db_only,
                "changed": changed,
                "in_sync": in_sync,
                "needs_sync": len(fs_only) > 0 or len(changed) > 0,
            },
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=f"Failed to get sync status: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )
