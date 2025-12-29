"""
Fabric Patterns API Router

Endpoints for browsing and executing Fabric prompts.
Fabric is a collection of 228+ specialized prompts for AI analysis,
summarization, threat modeling, content creation, and more.

Pattern source: ~/flourisha/00_AI_Brain/skills/fabric/fabric-repo/data/patterns/
"""
import os
import re
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from zoneinfo import ZoneInfo
from enum import Enum

from fastapi import APIRouter, Depends, Request, Query, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from models.response import APIResponse, ResponseMeta, PaginatedResponse
from middleware.auth import get_current_user, UserContext


router = APIRouter(prefix="/api/fabric", tags=["Fabric Patterns"])

# Fabric patterns directory
PATTERNS_DIR = Path(os.path.expanduser("~/flourisha/00_AI_Brain/skills/fabric/fabric-repo/data/patterns"))
PACIFIC = ZoneInfo("America/Los_Angeles")


# === Pattern Categories ===

class PatternCategory(str, Enum):
    """Categories for organizing Fabric patterns."""
    THREAT_MODELING = "threat_modeling"
    SUMMARIZATION = "summarization"
    EXTRACTION = "extraction"
    ANALYSIS = "analysis"
    CREATION = "creation"
    IMPROVEMENT = "improvement"
    RATING = "rating"
    OTHER = "other"


# Category classification rules based on pattern name prefixes
CATEGORY_RULES = {
    PatternCategory.THREAT_MODELING: [
        "create_threat", "create_stride", "create_sigma", "create_security",
        "analyze_threat", "write_nuclei", "write_semgrep", "t_threat",
        "ask_secure", "create_network_threat", "analyze_incident", "analyze_risk"
    ],
    PatternCategory.SUMMARIZATION: [
        "summarize", "create_summary", "create_5_sentence", "create_micro",
        "create_ul_summary", "create_cyber_summary", "youtube_summary"
    ],
    PatternCategory.EXTRACTION: [
        "extract_"
    ],
    PatternCategory.ANALYSIS: [
        "analyze_"
    ],
    PatternCategory.CREATION: [
        "create_", "write_"
    ],
    PatternCategory.IMPROVEMENT: [
        "improve_", "review_", "refine_", "humanize", "enrich_", "clean_"
    ],
    PatternCategory.RATING: [
        "rate_", "judge_", "label_", "check_agreement", "arbiter"
    ],
}


def classify_pattern(name: str) -> PatternCategory:
    """Classify a pattern into a category based on its name."""
    name_lower = name.lower()

    # Check specific rules first (more specific patterns)
    for category, prefixes in CATEGORY_RULES.items():
        for prefix in prefixes:
            if name_lower.startswith(prefix):
                return category

    return PatternCategory.OTHER


# === Request/Response Models ===

class PatternSummary(BaseModel):
    """Summary of a Fabric pattern for list view."""
    name: str = Field(..., description="Pattern name (directory name)")
    category: PatternCategory = Field(..., description="Pattern category")
    has_system_prompt: bool = Field(..., description="Whether system.md exists")
    has_user_prompt: bool = Field(..., description="Whether user.md exists")
    description: Optional[str] = Field(None, description="First line of system.md as description")


class PatternDetail(BaseModel):
    """Detailed Fabric pattern with full prompt content."""
    name: str = Field(..., description="Pattern name")
    category: PatternCategory = Field(..., description="Pattern category")
    system_prompt: Optional[str] = Field(None, description="Full system.md content")
    user_prompt: Optional[str] = Field(None, description="Full user.md content")
    path: str = Field(..., description="Path to pattern directory")
    files: List[str] = Field(default_factory=list, description="All files in pattern directory")


class PatternExecuteRequest(BaseModel):
    """Request to execute a Fabric pattern on content."""
    content: str = Field(..., description="Content to process with the pattern", min_length=1, max_length=100000)
    model: Optional[str] = Field("claude-3-5-sonnet-20241022", description="AI model to use")
    temperature: Optional[float] = Field(0.7, description="Temperature for generation", ge=0, le=2)


class PatternExecuteResponse(BaseModel):
    """Response from pattern execution."""
    pattern: str = Field(..., description="Pattern name used")
    input_length: int = Field(..., description="Input content length in characters")
    output: str = Field(..., description="Processed output from pattern")
    model: str = Field(..., description="Model used for processing")
    tokens_used: Optional[int] = Field(None, description="Tokens used (if available)")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")


class PatternListResponse(BaseModel):
    """Response for listing patterns."""
    patterns: List[PatternSummary] = Field(..., description="List of patterns")
    total: int = Field(..., description="Total number of patterns")
    by_category: Dict[str, int] = Field(..., description="Count per category")


class CategoryInfo(BaseModel):
    """Information about a pattern category."""
    category: PatternCategory = Field(..., description="Category enum value")
    display_name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Category description")
    pattern_count: int = Field(..., description="Number of patterns in category")
    example_patterns: List[str] = Field(..., description="Example pattern names")


CATEGORY_DESCRIPTIONS = {
    PatternCategory.THREAT_MODELING: "Security threat modeling and assessment patterns (STRIDE, scenarios, rules)",
    PatternCategory.SUMMARIZATION: "Content summarization patterns (micro, meeting, paper, video)",
    PatternCategory.EXTRACTION: "Extract insights, wisdom, ideas, and key information from content",
    PatternCategory.ANALYSIS: "Deep analysis patterns for code, claims, debates, logs, and more",
    PatternCategory.CREATION: "Content creation patterns (PRDs, docs, visualizations, prompts)",
    PatternCategory.IMPROVEMENT: "Improve existing content (writing, code, prompts)",
    PatternCategory.RATING: "Rate and evaluate content quality",
    PatternCategory.OTHER: "Miscellaneous specialized patterns",
}

CATEGORY_DISPLAY_NAMES = {
    PatternCategory.THREAT_MODELING: "Threat Modeling & Security",
    PatternCategory.SUMMARIZATION: "Summarization",
    PatternCategory.EXTRACTION: "Extraction",
    PatternCategory.ANALYSIS: "Analysis",
    PatternCategory.CREATION: "Creation",
    PatternCategory.IMPROVEMENT: "Improvement",
    PatternCategory.RATING: "Rating & Evaluation",
    PatternCategory.OTHER: "Other",
}


# === Helper Functions ===

def get_pattern_description(pattern_path: Path) -> Optional[str]:
    """Extract description from first meaningful line of system.md."""
    system_md = pattern_path / "system.md"
    if not system_md.exists():
        return None

    try:
        content = system_md.read_text(encoding="utf-8")
        lines = content.strip().split("\n")

        for line in lines:
            line = line.strip()
            # Skip empty lines and markdown headers
            if not line or line.startswith("#"):
                continue
            # Return first content line, truncated
            if len(line) > 200:
                return line[:197] + "..."
            return line

        return None
    except Exception:
        return None


def list_all_patterns() -> List[PatternSummary]:
    """List all available Fabric patterns."""
    if not PATTERNS_DIR.exists():
        return []

    patterns = []
    for pattern_dir in sorted(PATTERNS_DIR.iterdir()):
        if not pattern_dir.is_dir():
            continue
        if pattern_dir.name.startswith(".") or pattern_dir.name.startswith("_"):
            continue

        has_system = (pattern_dir / "system.md").exists()
        has_user = (pattern_dir / "user.md").exists()

        patterns.append(PatternSummary(
            name=pattern_dir.name,
            category=classify_pattern(pattern_dir.name),
            has_system_prompt=has_system,
            has_user_prompt=has_user,
            description=get_pattern_description(pattern_dir) if has_system else None
        ))

    return patterns


def get_pattern_detail(pattern_name: str) -> Optional[PatternDetail]:
    """Get detailed information about a specific pattern."""
    pattern_path = PATTERNS_DIR / pattern_name

    if not pattern_path.exists() or not pattern_path.is_dir():
        return None

    system_prompt = None
    user_prompt = None
    files = []

    for file_path in pattern_path.iterdir():
        if file_path.is_file():
            files.append(file_path.name)

            if file_path.name == "system.md":
                try:
                    system_prompt = file_path.read_text(encoding="utf-8")
                except Exception:
                    pass
            elif file_path.name == "user.md":
                try:
                    user_prompt = file_path.read_text(encoding="utf-8")
                except Exception:
                    pass

    return PatternDetail(
        name=pattern_name,
        category=classify_pattern(pattern_name),
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        path=str(pattern_path),
        files=sorted(files)
    )


async def execute_pattern_with_claude(
    pattern_name: str,
    content: str,
    model: str = "claude-3-5-sonnet-20241022",
    temperature: float = 0.7
) -> PatternExecuteResponse:
    """Execute a pattern using Claude API directly."""
    import time
    import anthropic

    start_time = time.time()

    # Get pattern details
    pattern = get_pattern_detail(pattern_name)
    if not pattern or not pattern.system_prompt:
        raise ValueError(f"Pattern '{pattern_name}' not found or has no system prompt")

    # Build messages
    system = pattern.system_prompt
    if pattern.user_prompt:
        # Some patterns have a user.md that provides additional context
        system += "\n\n" + pattern.user_prompt

    # Call Claude API
    client = anthropic.Anthropic()

    message = client.messages.create(
        model=model,
        max_tokens=8192,
        temperature=temperature,
        system=system,
        messages=[
            {"role": "user", "content": content}
        ]
    )

    end_time = time.time()
    processing_time_ms = (end_time - start_time) * 1000

    # Extract output
    output = ""
    for block in message.content:
        if hasattr(block, "text"):
            output += block.text

    # Calculate tokens
    tokens_used = message.usage.input_tokens + message.usage.output_tokens if message.usage else None

    return PatternExecuteResponse(
        pattern=pattern_name,
        input_length=len(content),
        output=output,
        model=model,
        tokens_used=tokens_used,
        processing_time_ms=processing_time_ms
    )


# === Endpoints ===

@router.get(
    "/patterns",
    response_model=APIResponse[PatternListResponse],
    summary="List all Fabric patterns",
    description="Returns all 228+ Fabric patterns organized by category."
)
async def list_patterns(
    request: Request,
    category: Optional[PatternCategory] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search pattern names"),
    user: UserContext = Depends(get_current_user)
) -> APIResponse[PatternListResponse]:
    """
    List all available Fabric patterns.

    - Returns patterns with categories and descriptions
    - Optionally filter by category or search term
    - Includes count by category
    """
    all_patterns = list_all_patterns()

    # Apply filters
    filtered = all_patterns
    if category:
        filtered = [p for p in filtered if p.category == category]
    if search:
        search_lower = search.lower()
        filtered = [p for p in filtered if search_lower in p.name.lower()]

    # Count by category
    by_category = {}
    for p in all_patterns:
        cat_name = p.category.value
        by_category[cat_name] = by_category.get(cat_name, 0) + 1

    response_data = PatternListResponse(
        patterns=filtered,
        total=len(filtered),
        by_category=by_category
    )

    return APIResponse(
        success=True,
        data=response_data,
        meta=ResponseMeta(**request.state.get_meta())
    )


@router.get(
    "/patterns/{pattern_name}",
    response_model=APIResponse[PatternDetail],
    summary="Get pattern details",
    description="Get full details of a Fabric pattern including the complete prompt."
)
async def get_pattern(
    request: Request,
    pattern_name: str,
    user: UserContext = Depends(get_current_user)
) -> APIResponse[PatternDetail]:
    """
    Get detailed information about a specific pattern.

    - Returns full system.md prompt content
    - Returns user.md if available
    - Lists all files in pattern directory
    """
    pattern = get_pattern_detail(pattern_name)

    if not pattern:
        raise HTTPException(
            status_code=404,
            detail=f"Pattern '{pattern_name}' not found"
        )

    return APIResponse(
        success=True,
        data=pattern,
        meta=ResponseMeta(**request.state.get_meta())
    )


@router.get(
    "/categories",
    response_model=APIResponse[List[CategoryInfo]],
    summary="List pattern categories",
    description="Returns all pattern categories with descriptions and counts."
)
async def list_categories(
    request: Request,
    user: UserContext = Depends(get_current_user)
) -> APIResponse[List[CategoryInfo]]:
    """
    List all pattern categories with metadata.

    - Returns category descriptions
    - Includes pattern count per category
    - Shows example patterns for each category
    """
    all_patterns = list_all_patterns()

    # Group patterns by category
    patterns_by_category: Dict[PatternCategory, List[str]] = {}
    for p in all_patterns:
        if p.category not in patterns_by_category:
            patterns_by_category[p.category] = []
        patterns_by_category[p.category].append(p.name)

    categories = []
    for cat in PatternCategory:
        pattern_names = patterns_by_category.get(cat, [])
        categories.append(CategoryInfo(
            category=cat,
            display_name=CATEGORY_DISPLAY_NAMES.get(cat, cat.value),
            description=CATEGORY_DESCRIPTIONS.get(cat, ""),
            pattern_count=len(pattern_names),
            example_patterns=pattern_names[:5]  # Show up to 5 examples
        ))

    return APIResponse(
        success=True,
        data=categories,
        meta=ResponseMeta(**request.state.get_meta())
    )


@router.post(
    "/patterns/{pattern_name}/execute",
    response_model=APIResponse[PatternExecuteResponse],
    summary="Execute a pattern on content",
    description="Process content using a Fabric pattern with Claude."
)
async def execute_pattern(
    request: Request,
    pattern_name: str,
    body: PatternExecuteRequest,
    user: UserContext = Depends(get_current_user)
) -> APIResponse[PatternExecuteResponse]:
    """
    Execute a Fabric pattern on provided content.

    - Sends content to Claude with the pattern's system prompt
    - Returns processed output
    - Tracks token usage and processing time
    """
    # Verify pattern exists
    pattern = get_pattern_detail(pattern_name)
    if not pattern:
        raise HTTPException(
            status_code=404,
            detail=f"Pattern '{pattern_name}' not found"
        )

    if not pattern.system_prompt:
        raise HTTPException(
            status_code=400,
            detail=f"Pattern '{pattern_name}' has no system prompt"
        )

    try:
        result = await execute_pattern_with_claude(
            pattern_name=pattern_name,
            content=body.content,
            model=body.model or "claude-3-5-sonnet-20241022",
            temperature=body.temperature or 0.7
        )

        return APIResponse(
            success=True,
            data=result,
            meta=ResponseMeta(**request.state.get_meta())
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pattern execution failed: {str(e)}"
        )


@router.get(
    "/search",
    response_model=APIResponse[List[PatternSummary]],
    summary="Search patterns",
    description="Search patterns by name or description."
)
async def search_patterns(
    request: Request,
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Max results to return"),
    user: UserContext = Depends(get_current_user)
) -> APIResponse[List[PatternSummary]]:
    """
    Search for patterns by name or description.

    - Searches pattern names and descriptions
    - Returns sorted by relevance
    - Limited to specified count
    """
    all_patterns = list_all_patterns()
    query_lower = q.lower()

    # Score patterns by relevance
    scored = []
    for p in all_patterns:
        score = 0

        # Exact name match
        if p.name.lower() == query_lower:
            score = 100
        # Name starts with query
        elif p.name.lower().startswith(query_lower):
            score = 80
        # Query in name
        elif query_lower in p.name.lower():
            score = 60
        # Query in description
        elif p.description and query_lower in p.description.lower():
            score = 40

        if score > 0:
            scored.append((score, p))

    # Sort by score descending, then name
    scored.sort(key=lambda x: (-x[0], x[1].name))

    results = [p for _, p in scored[:limit]]

    return APIResponse(
        success=True,
        data=results,
        meta=ResponseMeta(**request.state.get_meta())
    )


@router.get(
    "/stats",
    response_model=APIResponse[Dict[str, Any]],
    summary="Get pattern statistics",
    description="Returns statistics about available patterns."
)
async def get_pattern_stats(
    request: Request,
    user: UserContext = Depends(get_current_user)
) -> APIResponse[Dict[str, Any]]:
    """
    Get statistics about available Fabric patterns.

    - Total pattern count
    - Count by category
    - Patterns with/without user prompts
    """
    all_patterns = list_all_patterns()

    by_category = {}
    with_user_prompt = 0
    without_description = 0

    for p in all_patterns:
        cat_name = p.category.value
        by_category[cat_name] = by_category.get(cat_name, 0) + 1

        if p.has_user_prompt:
            with_user_prompt += 1
        if not p.description:
            without_description += 1

    stats = {
        "total_patterns": len(all_patterns),
        "patterns_by_category": by_category,
        "patterns_with_user_prompt": with_user_prompt,
        "patterns_without_description": without_description,
        "patterns_dir": str(PATTERNS_DIR),
        "patterns_dir_exists": PATTERNS_DIR.exists()
    }

    return APIResponse(
        success=True,
        data=stats,
        meta=ResponseMeta(**request.state.get_meta())
    )
