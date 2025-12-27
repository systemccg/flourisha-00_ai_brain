"""
Skills Registry Router

Endpoints for discovering and managing PAI skills.
Reads skill definitions from ~/.claude/skills/ directory.
"""
import os
import re
import yaml
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Request, Query, HTTPException
from pydantic import BaseModel, Field

from models.response import APIResponse, ResponseMeta
from middleware.auth import get_current_user, UserContext


router = APIRouter(prefix="/api/skills", tags=["Skills"])

# Default skills directory
SKILLS_DIR = Path(os.path.expanduser("~/.claude/skills"))
PACIFIC = ZoneInfo("America/Los_Angeles")


# === Request/Response Models ===

class SkillWorkflow(BaseModel):
    """Workflow within a skill."""
    name: str = Field(..., description="Workflow filename")
    path: str = Field(..., description="Full path to workflow")
    description: Optional[str] = Field(None, description="Workflow description")


class SkillAsset(BaseModel):
    """Asset file within a skill."""
    name: str = Field(..., description="Asset filename")
    path: str = Field(..., description="Full path to asset")
    size_bytes: int = Field(..., description="File size in bytes")


class SkillInfo(BaseModel):
    """Detailed skill information."""
    name: str = Field(..., description="Skill name (directory name)")
    display_name: Optional[str] = Field(None, description="Display name from frontmatter")
    description: Optional[str] = Field(None, description="Skill description")
    trigger_phrases: List[str] = Field(default_factory=list, description="Activation trigger phrases")
    path: str = Field(..., description="Path to skill directory")
    has_skill_md: bool = Field(..., description="Whether SKILL.md exists")
    workflows: List[SkillWorkflow] = Field(default_factory=list, description="Available workflows")
    assets: List[SkillAsset] = Field(default_factory=list, description="Available assets")
    last_modified: Optional[str] = Field(None, description="Last modification time")


class SkillSummary(BaseModel):
    """Summary info for skill listing."""
    name: str = Field(..., description="Skill name")
    display_name: Optional[str] = Field(None, description="Display name")
    description: Optional[str] = Field(None, description="Short description")
    workflow_count: int = Field(default=0, description="Number of workflows")
    has_assets: bool = Field(default=False, description="Whether skill has assets")


class SkillsListResponse(BaseModel):
    """Response for listing all skills."""
    skills: List[SkillSummary] = Field(..., description="List of skills")
    total: int = Field(..., description="Total number of skills")
    skills_dir: str = Field(..., description="Skills directory path")


class SkillContentResponse(BaseModel):
    """Response for skill content."""
    name: str = Field(..., description="Skill name")
    content: str = Field(..., description="SKILL.md content")
    frontmatter: Optional[Dict[str, Any]] = Field(None, description="Parsed YAML frontmatter")


class WorkflowContentResponse(BaseModel):
    """Response for workflow content."""
    skill_name: str = Field(..., description="Parent skill name")
    workflow_name: str = Field(..., description="Workflow name")
    content: str = Field(..., description="Workflow content")


class SkillSearchResult(BaseModel):
    """Search result for skill matching."""
    skill_name: str = Field(..., description="Skill name")
    display_name: Optional[str] = Field(None, description="Display name")
    description: Optional[str] = Field(None, description="Description")
    match_type: str = Field(..., description="How the query matched: 'name', 'description', 'trigger'")
    match_score: float = Field(..., description="Match score 0-1")


# === Helper Functions ===

def parse_skill_frontmatter(skill_path: Path) -> Dict[str, Any]:
    """Parse YAML frontmatter from SKILL.md."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return {}

    try:
        content = skill_md.read_text()
        # Find frontmatter between ---
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

    # Look for "USE WHEN" section
    use_when_match = re.search(r'USE WHEN\s+([^.]+)', description, re.IGNORECASE)
    if use_when_match:
        triggers_text = use_when_match.group(1)
        # Split on 'OR' or comma
        parts = re.split(r'\s+OR\s+|,\s*', triggers_text, flags=re.IGNORECASE)
        triggers = [p.strip().strip("'\"") for p in parts if p.strip()]

    return triggers


def get_skill_info(skill_path: Path) -> Optional[SkillInfo]:
    """Get detailed information about a skill."""
    if not skill_path.is_dir():
        return None

    name = skill_path.name

    # Skip hidden directories and __pycache__
    if name.startswith('.') or name == '__pycache__':
        return None

    frontmatter = parse_skill_frontmatter(skill_path)
    description = frontmatter.get('description', '')
    if isinstance(description, str):
        description = description.strip()
    else:
        description = ''

    # Get workflows
    workflows = []
    workflows_dir = skill_path / "workflows"
    if workflows_dir.exists():
        for wf_file in workflows_dir.glob("*.md"):
            workflows.append(SkillWorkflow(
                name=wf_file.stem,
                path=str(wf_file),
                description=None,  # Could parse for description
            ))

    # Get assets
    assets = []
    assets_dir = skill_path / "assets"
    if assets_dir.exists():
        for asset_file in assets_dir.iterdir():
            if asset_file.is_file():
                assets.append(SkillAsset(
                    name=asset_file.name,
                    path=str(asset_file),
                    size_bytes=asset_file.stat().st_size,
                ))

    # Get modification time
    skill_md = skill_path / "SKILL.md"
    last_modified = None
    if skill_md.exists():
        mtime = datetime.fromtimestamp(skill_md.stat().st_mtime, PACIFIC)
        last_modified = mtime.isoformat()

    return SkillInfo(
        name=name,
        display_name=frontmatter.get('name', name),
        description=description[:500] if description else None,
        trigger_phrases=extract_trigger_phrases(description),
        path=str(skill_path),
        has_skill_md=skill_md.exists(),
        workflows=workflows,
        assets=assets,
        last_modified=last_modified,
    )


# === Endpoints ===

@router.get("", response_model=APIResponse[SkillsListResponse])
async def list_skills(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[SkillsListResponse]:
    """
    List all available PAI skills.

    Returns summary information for each skill in the skills directory.
    Skills are self-contained containers with workflows and assets.

    **Response:**
    - skills: List of skill summaries
    - total: Total number of skills
    - skills_dir: Path to skills directory

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        if not SKILLS_DIR.exists():
            return APIResponse(
                success=True,
                data=SkillsListResponse(
                    skills=[],
                    total=0,
                    skills_dir=str(SKILLS_DIR),
                ),
                meta=ResponseMeta(**meta_dict),
            )

        skills = []
        for skill_path in sorted(SKILLS_DIR.iterdir()):
            info = get_skill_info(skill_path)
            if info:
                skills.append(SkillSummary(
                    name=info.name,
                    display_name=info.display_name,
                    description=info.description[:200] if info.description else None,
                    workflow_count=len(info.workflows),
                    has_assets=len(info.assets) > 0,
                ))

        response_data = SkillsListResponse(
            skills=skills,
            total=len(skills),
            skills_dir=str(SKILLS_DIR),
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
            error=f"Failed to list skills: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/search", response_model=APIResponse[List[SkillSearchResult]])
async def search_skills(
    request: Request,
    query: str = Query(..., min_length=2, description="Search query"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[List[SkillSearchResult]]:
    """
    Search skills by name, description, or trigger phrases.

    Returns matching skills ranked by relevance.

    **Query Parameters:**
    - query: Search query (min 2 characters)

    **Response:**
    List of matching skills with match type and score.

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        if not SKILLS_DIR.exists():
            return APIResponse(
                success=True,
                data=[],
                meta=ResponseMeta(**meta_dict),
            )

        query_lower = query.lower()
        results = []

        for skill_path in SKILLS_DIR.iterdir():
            info = get_skill_info(skill_path)
            if not info:
                continue

            score = 0.0
            match_type = None

            # Check name match
            if query_lower in info.name.lower():
                score = 0.9 if info.name.lower() == query_lower else 0.7
                match_type = "name"

            # Check display name match
            elif info.display_name and query_lower in info.display_name.lower():
                score = 0.8 if info.display_name.lower() == query_lower else 0.6
                match_type = "name"

            # Check trigger phrases
            elif any(query_lower in trigger.lower() for trigger in info.trigger_phrases):
                score = 0.75
                match_type = "trigger"

            # Check description
            elif info.description and query_lower in info.description.lower():
                score = 0.5
                match_type = "description"

            if score > 0:
                results.append(SkillSearchResult(
                    skill_name=info.name,
                    display_name=info.display_name,
                    description=info.description[:200] if info.description else None,
                    match_type=match_type,
                    match_score=score,
                ))

        # Sort by score descending
        results.sort(key=lambda x: x.match_score, reverse=True)

        return APIResponse(
            success=True,
            data=results[:20],  # Limit to 20 results
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to search skills: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/{skill_name}", response_model=APIResponse[SkillInfo])
async def get_skill(
    request: Request,
    skill_name: str,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[SkillInfo]:
    """
    Get detailed information about a specific skill.

    Returns skill metadata, workflows, assets, and trigger phrases.

    **Path Parameters:**
    - skill_name: Name of the skill (directory name)

    **Response:**
    Full SkillInfo with workflows and assets.

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        skill_path = SKILLS_DIR / skill_name

        if not skill_path.exists():
            return APIResponse(
                success=False,
                data=None,
                error=f"Skill not found: {skill_name}",
                meta=ResponseMeta(**meta_dict),
            )

        info = get_skill_info(skill_path)
        if not info:
            return APIResponse(
                success=False,
                data=None,
                error=f"Could not parse skill: {skill_name}",
                meta=ResponseMeta(**meta_dict),
            )

        return APIResponse(
            success=True,
            data=info,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to get skill: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/{skill_name}/content", response_model=APIResponse[SkillContentResponse])
async def get_skill_content(
    request: Request,
    skill_name: str,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[SkillContentResponse]:
    """
    Get the SKILL.md content for a skill.

    Returns the full markdown content and parsed frontmatter.

    **Path Parameters:**
    - skill_name: Name of the skill

    **Response:**
    - name: Skill name
    - content: Full SKILL.md content
    - frontmatter: Parsed YAML frontmatter

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        skill_md = SKILLS_DIR / skill_name / "SKILL.md"

        if not skill_md.exists():
            return APIResponse(
                success=False,
                data=None,
                error=f"SKILL.md not found for: {skill_name}",
                meta=ResponseMeta(**meta_dict),
            )

        content = skill_md.read_text()
        frontmatter = parse_skill_frontmatter(SKILLS_DIR / skill_name)

        return APIResponse(
            success=True,
            data=SkillContentResponse(
                name=skill_name,
                content=content,
                frontmatter=frontmatter,
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to get skill content: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/{skill_name}/workflows", response_model=APIResponse[List[SkillWorkflow]])
async def get_skill_workflows(
    request: Request,
    skill_name: str,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[List[SkillWorkflow]]:
    """
    Get all workflows for a skill.

    Workflows are specific task definitions within a skill.

    **Path Parameters:**
    - skill_name: Name of the skill

    **Response:**
    List of workflows with names and paths.

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        workflows_dir = SKILLS_DIR / skill_name / "workflows"

        if not workflows_dir.exists():
            return APIResponse(
                success=True,
                data=[],
                meta=ResponseMeta(**meta_dict),
            )

        workflows = []
        for wf_file in sorted(workflows_dir.glob("*.md")):
            # Try to extract description from first line
            description = None
            try:
                content = wf_file.read_text()
                lines = content.strip().split('\n')
                for line in lines:
                    if line.startswith('#'):
                        description = line.lstrip('#').strip()
                        break
            except Exception:
                pass

            workflows.append(SkillWorkflow(
                name=wf_file.stem,
                path=str(wf_file),
                description=description,
            ))

        return APIResponse(
            success=True,
            data=workflows,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to get workflows: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/{skill_name}/workflows/{workflow_name}", response_model=APIResponse[WorkflowContentResponse])
async def get_workflow_content(
    request: Request,
    skill_name: str,
    workflow_name: str,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[WorkflowContentResponse]:
    """
    Get content of a specific workflow.

    **Path Parameters:**
    - skill_name: Name of the skill
    - workflow_name: Name of the workflow (without .md extension)

    **Response:**
    - skill_name: Parent skill
    - workflow_name: Workflow name
    - content: Full workflow content

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        workflow_file = SKILLS_DIR / skill_name / "workflows" / f"{workflow_name}.md"

        if not workflow_file.exists():
            return APIResponse(
                success=False,
                data=None,
                error=f"Workflow not found: {skill_name}/{workflow_name}",
                meta=ResponseMeta(**meta_dict),
            )

        content = workflow_file.read_text()

        return APIResponse(
            success=True,
            data=WorkflowContentResponse(
                skill_name=skill_name,
                workflow_name=workflow_name,
                content=content,
            ),
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to get workflow content: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/{skill_name}/assets", response_model=APIResponse[List[SkillAsset]])
async def get_skill_assets(
    request: Request,
    skill_name: str,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[List[SkillAsset]]:
    """
    Get all assets for a skill.

    Assets are supporting resources like templates and references.

    **Path Parameters:**
    - skill_name: Name of the skill

    **Response:**
    List of assets with names, paths, and sizes.

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        assets_dir = SKILLS_DIR / skill_name / "assets"

        if not assets_dir.exists():
            return APIResponse(
                success=True,
                data=[],
                meta=ResponseMeta(**meta_dict),
            )

        assets = []
        for asset_file in sorted(assets_dir.iterdir()):
            if asset_file.is_file():
                assets.append(SkillAsset(
                    name=asset_file.name,
                    path=str(asset_file),
                    size_bytes=asset_file.stat().st_size,
                ))

        return APIResponse(
            success=True,
            data=assets,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Failed to get assets: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )
