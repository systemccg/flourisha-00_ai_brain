"""
PARA Browser Router

Endpoints for browsing the PARA (Projects, Areas, Resources, Archives) folder structure.
Provides tree navigation, category listing, and file content retrieval.
"""
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Request, Query, HTTPException
from pydantic import BaseModel, Field

from models.response import APIResponse, ResponseMeta
from middleware.auth import get_current_user, UserContext


router = APIRouter(prefix="/api/para", tags=["PARA Browser"])

# PARA directory configuration
FLOURISHA_ROOT = Path("/root/flourisha")
PACIFIC = ZoneInfo("America/Los_Angeles")

# PARA category mappings
PARA_CATEGORIES = {
    "projects": "01f_Flourisha_Projects",
    "areas": "02f_Flourisha_Areas",
    "resources": "03f_Flourisha_Resources",
    "archives": "04f_Flourisha_Archives",
}


# === Request/Response Models ===

class FileInfo(BaseModel):
    """Information about a file."""
    name: str = Field(..., description="File name")
    path: str = Field(..., description="Relative path from PARA root")
    size_bytes: int = Field(..., description="File size in bytes")
    is_markdown: bool = Field(default=False, description="Whether file is markdown")
    last_modified: Optional[str] = Field(None, description="Last modification time")


class FolderInfo(BaseModel):
    """Information about a folder."""
    name: str = Field(..., description="Folder name")
    path: str = Field(..., description="Relative path from PARA root")
    file_count: int = Field(default=0, description="Number of files directly in folder")
    subfolder_count: int = Field(default=0, description="Number of subfolders")
    total_items: int = Field(default=0, description="Total files recursively")
    children: List["FolderInfo"] = Field(default_factory=list, description="Subfolders")


class PARACategory(BaseModel):
    """PARA category with statistics."""
    category: str = Field(..., description="Category key: projects, areas, resources, archives")
    display_name: str = Field(..., description="Human-readable name")
    folder_name: str = Field(..., description="Actual folder name on disk")
    file_count: int = Field(default=0, description="Total files in category")
    subfolder_count: int = Field(default=0, description="Top-level subfolders")


class PARATreeResponse(BaseModel):
    """Full PARA tree structure."""
    categories: Dict[str, FolderInfo] = Field(..., description="Tree by category")
    total_files: int = Field(..., description="Total files across all categories")
    last_scanned: str = Field(..., description="Scan timestamp")


class CategoryListingResponse(BaseModel):
    """Response for category listing."""
    category: str = Field(..., description="Category name")
    items: List[FolderInfo] = Field(..., description="Top-level items in category")
    file_count: int = Field(..., description="Total files in category")


class FileContentResponse(BaseModel):
    """Response for file content."""
    path: str = Field(..., description="File path")
    name: str = Field(..., description="File name")
    content: str = Field(..., description="File content as text/markdown")
    size_bytes: int = Field(..., description="File size")
    content_type: str = Field(default="text/markdown", description="Content MIME type")
    last_modified: Optional[str] = Field(None, description="Last modification time")


class FolderContentsResponse(BaseModel):
    """Response for folder contents."""
    path: str = Field(..., description="Folder path")
    name: str = Field(..., description="Folder name")
    files: List[FileInfo] = Field(default_factory=list, description="Files in folder")
    subfolders: List[FolderInfo] = Field(default_factory=list, description="Subfolders")


# === Helper Functions ===

def count_files_recursive(folder_path: Path) -> int:
    """Count all files recursively in a folder."""
    if not folder_path.exists():
        return 0
    count = 0
    try:
        for item in folder_path.rglob("*"):
            if item.is_file() and not item.name.startswith("."):
                count += 1
    except PermissionError:
        pass
    return count


def get_folder_stats(folder_path: Path) -> Dict[str, int]:
    """Get file and subfolder counts for a folder."""
    if not folder_path.exists():
        return {"files": 0, "subfolders": 0}

    files = 0
    subfolders = 0
    try:
        for item in folder_path.iterdir():
            if item.name.startswith("."):
                continue
            if item.is_file():
                files += 1
            elif item.is_dir():
                subfolders += 1
    except PermissionError:
        pass

    return {"files": files, "subfolders": subfolders}


def build_folder_tree(folder_path: Path, base_path: Path, max_depth: int = 2, current_depth: int = 0) -> FolderInfo:
    """Build a folder tree structure up to max_depth."""
    stats = get_folder_stats(folder_path)
    rel_path = str(folder_path.relative_to(base_path))

    folder_info = FolderInfo(
        name=folder_path.name,
        path=rel_path,
        file_count=stats["files"],
        subfolder_count=stats["subfolders"],
        total_items=count_files_recursive(folder_path),
        children=[],
    )

    # Add children if within depth limit
    if current_depth < max_depth:
        try:
            for item in sorted(folder_path.iterdir()):
                if item.is_dir() and not item.name.startswith("."):
                    child = build_folder_tree(item, base_path, max_depth, current_depth + 1)
                    folder_info.children.append(child)
        except PermissionError:
            pass

    return folder_info


def format_timestamp(timestamp: float) -> str:
    """Format a Unix timestamp to Pacific time ISO string."""
    dt = datetime.fromtimestamp(timestamp, tz=PACIFIC)
    return dt.isoformat()


def is_text_file(path: Path) -> bool:
    """Check if a file is likely a text/markdown file."""
    text_extensions = {".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".py", ".js", ".ts"}
    return path.suffix.lower() in text_extensions


def sanitize_path(requested_path: str) -> Path:
    """Sanitize and validate a requested path.

    Raises HTTPException if path attempts directory traversal.
    """
    # Remove leading slashes and normalize
    clean_path = requested_path.lstrip("/").replace("\\", "/")

    # Check for directory traversal attempts
    if ".." in clean_path:
        raise HTTPException(status_code=400, detail="Directory traversal not allowed")

    full_path = FLOURISHA_ROOT / clean_path

    # Ensure resolved path is within FLOURISHA_ROOT
    try:
        full_path = full_path.resolve()
        if not str(full_path).startswith(str(FLOURISHA_ROOT.resolve())):
            raise HTTPException(status_code=403, detail="Access denied: path outside PARA")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid path")

    return full_path


# === Endpoints ===

@router.get("/tree", response_model=APIResponse[PARATreeResponse])
async def get_para_tree(
    request: Request,
    depth: int = Query(default=2, ge=1, le=4, description="Max depth for tree traversal"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[PARATreeResponse]:
    """
    Get the full PARA folder tree structure.

    Returns hierarchical view of Projects, Areas, Resources, and Archives
    with file counts at each level.

    **Query Parameters:**
    - depth: Maximum depth for tree traversal (default 2, max 4)

    **Response:**
    - categories: Tree structure by category (projects, areas, resources, archives)
    - total_files: Total files across all categories
    - last_scanned: Timestamp of this scan

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    categories = {}
    total_files = 0

    for category_key, folder_name in PARA_CATEGORIES.items():
        folder_path = FLOURISHA_ROOT / folder_name
        if folder_path.exists():
            tree = build_folder_tree(folder_path, FLOURISHA_ROOT, max_depth=depth)
            categories[category_key] = tree
            total_files += tree.total_items
        else:
            # Return empty folder info for missing categories
            categories[category_key] = FolderInfo(
                name=folder_name,
                path=folder_name,
                file_count=0,
                subfolder_count=0,
                total_items=0,
                children=[],
            )

    response_data = PARATreeResponse(
        categories=categories,
        total_files=total_files,
        last_scanned=datetime.now(PACIFIC).isoformat(),
    )

    return APIResponse(
        success=True,
        data=response_data,
        meta=ResponseMeta(**meta_dict),
    )


@router.get("/categories", response_model=APIResponse[List[PARACategory]])
async def list_categories(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[List[PARACategory]]:
    """
    List all PARA categories with statistics.

    Returns summary info for Projects, Areas, Resources, and Archives
    including file counts and subfolder counts.

    **Response:**
    - List of PARA categories with statistics

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    display_names = {
        "projects": "Projects",
        "areas": "Areas",
        "resources": "Resources",
        "archives": "Archives",
    }

    categories = []
    for category_key, folder_name in PARA_CATEGORIES.items():
        folder_path = FLOURISHA_ROOT / folder_name

        if folder_path.exists():
            stats = get_folder_stats(folder_path)
            total_files = count_files_recursive(folder_path)
        else:
            stats = {"files": 0, "subfolders": 0}
            total_files = 0

        categories.append(PARACategory(
            category=category_key,
            display_name=display_names.get(category_key, category_key.title()),
            folder_name=folder_name,
            file_count=total_files,
            subfolder_count=stats["subfolders"],
        ))

    return APIResponse(
        success=True,
        data=categories,
        meta=ResponseMeta(**meta_dict),
    )


@router.get("/category/{category}", response_model=APIResponse[CategoryListingResponse])
async def get_category_listing(
    request: Request,
    category: str,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[CategoryListingResponse]:
    """
    Get contents of a specific PARA category.

    Returns top-level folders and files within the category.

    **Path Parameters:**
    - category: One of 'projects', 'areas', 'resources', 'archives'

    **Response:**
    - category: Category name
    - items: List of top-level items (folders with stats)
    - file_count: Total files in category

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    if category not in PARA_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {', '.join(PARA_CATEGORIES.keys())}"
        )

    folder_name = PARA_CATEGORIES[category]
    folder_path = FLOURISHA_ROOT / folder_name

    if not folder_path.exists():
        raise HTTPException(status_code=404, detail=f"Category folder not found: {folder_name}")

    items = []
    total_files = 0

    try:
        for item in sorted(folder_path.iterdir()):
            if item.name.startswith("."):
                continue

            if item.is_dir():
                stats = get_folder_stats(item)
                item_total = count_files_recursive(item)
                total_files += item_total

                items.append(FolderInfo(
                    name=item.name,
                    path=str(item.relative_to(FLOURISHA_ROOT)),
                    file_count=stats["files"],
                    subfolder_count=stats["subfolders"],
                    total_items=item_total,
                    children=[],  # Don't include children at this level
                ))
            elif item.is_file():
                total_files += 1
                # Include files as folder items with zero children
                items.append(FolderInfo(
                    name=item.name,
                    path=str(item.relative_to(FLOURISHA_ROOT)),
                    file_count=0,
                    subfolder_count=0,
                    total_items=1,
                    children=[],
                ))
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied reading category")

    response_data = CategoryListingResponse(
        category=category,
        items=items,
        file_count=total_files,
    )

    return APIResponse(
        success=True,
        data=response_data,
        meta=ResponseMeta(**meta_dict),
    )


@router.get("/folder", response_model=APIResponse[FolderContentsResponse])
async def get_folder_contents(
    request: Request,
    path: str = Query(..., description="Path to folder relative to PARA root"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[FolderContentsResponse]:
    """
    Get contents of a specific folder.

    Returns files and subfolders within the specified path.

    **Query Parameters:**
    - path: Path to folder relative to PARA root (e.g., '01f_Flourisha_Projects/flourisha-app')

    **Response:**
    - path: Folder path
    - name: Folder name
    - files: List of files in folder
    - subfolders: List of subfolders

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    folder_path = sanitize_path(path)

    if not folder_path.exists():
        raise HTTPException(status_code=404, detail="Folder not found")

    if not folder_path.is_dir():
        raise HTTPException(status_code=400, detail="Path is not a folder")

    files = []
    subfolders = []

    try:
        for item in sorted(folder_path.iterdir()):
            if item.name.startswith("."):
                continue

            rel_path = str(item.relative_to(FLOURISHA_ROOT))

            if item.is_file():
                try:
                    stat = item.stat()
                    files.append(FileInfo(
                        name=item.name,
                        path=rel_path,
                        size_bytes=stat.st_size,
                        is_markdown=item.suffix.lower() in {".md", ".markdown"},
                        last_modified=format_timestamp(stat.st_mtime),
                    ))
                except OSError:
                    continue
            elif item.is_dir():
                stats = get_folder_stats(item)
                subfolders.append(FolderInfo(
                    name=item.name,
                    path=rel_path,
                    file_count=stats["files"],
                    subfolder_count=stats["subfolders"],
                    total_items=count_files_recursive(item),
                    children=[],
                ))
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied reading folder")

    response_data = FolderContentsResponse(
        path=str(folder_path.relative_to(FLOURISHA_ROOT)),
        name=folder_path.name,
        files=files,
        subfolders=subfolders,
    )

    return APIResponse(
        success=True,
        data=response_data,
        meta=ResponseMeta(**meta_dict),
    )


@router.get("/file", response_model=APIResponse[FileContentResponse])
async def get_file_content(
    request: Request,
    path: str = Query(..., description="Path to file relative to PARA root"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[FileContentResponse]:
    """
    Get content of a specific file.

    Returns file content as text/markdown. Only text files are supported.

    **Query Parameters:**
    - path: Path to file relative to PARA root

    **Response:**
    - path: File path
    - name: File name
    - content: File content as text
    - size_bytes: File size
    - content_type: MIME type
    - last_modified: Last modification timestamp

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    file_path = sanitize_path(path)

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    if not file_path.is_file():
        raise HTTPException(status_code=400, detail="Path is not a file")

    # Check if file is a text file
    if not is_text_file(file_path):
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Supported: .md, .txt, .json, .yaml, .yml, .toml, .py, .js, .ts"
        )

    # Check file size (limit to 1MB)
    try:
        stat = file_path.stat()
        if stat.st_size > 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large (max 1MB)")
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Cannot read file stats: {e}")

    # Read file content
    try:
        content = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File is not valid UTF-8 text")
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied reading file")
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Cannot read file: {e}")

    # Determine content type
    content_type = "text/markdown" if file_path.suffix.lower() in {".md", ".markdown"} else "text/plain"

    response_data = FileContentResponse(
        path=str(file_path.relative_to(FLOURISHA_ROOT)),
        name=file_path.name,
        content=content,
        size_bytes=stat.st_size,
        content_type=content_type,
        last_modified=format_timestamp(stat.st_mtime),
    )

    return APIResponse(
        success=True,
        data=response_data,
        meta=ResponseMeta(**meta_dict),
    )


@router.get("/search", response_model=APIResponse[List[FileInfo]])
async def search_files(
    request: Request,
    query: str = Query(..., description="Search query for file names", min_length=1),
    category: Optional[str] = Query(None, description="Limit search to category"),
    limit: int = Query(default=50, ge=1, le=200, description="Maximum results"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[List[FileInfo]]:
    """
    Search for files by name within PARA folders.

    Searches file names for the query string (case-insensitive).

    **Query Parameters:**
    - query: Search text (required)
    - category: Limit to specific category (optional)
    - limit: Max results (default 50, max 200)

    **Response:**
    - List of matching files

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    if category and category not in PARA_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {', '.join(PARA_CATEGORIES.keys())}"
        )

    query_lower = query.lower()
    results = []

    # Determine which categories to search
    if category:
        categories_to_search = {category: PARA_CATEGORIES[category]}
    else:
        categories_to_search = PARA_CATEGORIES

    for cat_key, folder_name in categories_to_search.items():
        folder_path = FLOURISHA_ROOT / folder_name
        if not folder_path.exists():
            continue

        try:
            for file_path in folder_path.rglob("*"):
                if len(results) >= limit:
                    break

                if not file_path.is_file():
                    continue

                if file_path.name.startswith("."):
                    continue

                if query_lower in file_path.name.lower():
                    try:
                        stat = file_path.stat()
                        results.append(FileInfo(
                            name=file_path.name,
                            path=str(file_path.relative_to(FLOURISHA_ROOT)),
                            size_bytes=stat.st_size,
                            is_markdown=file_path.suffix.lower() in {".md", ".markdown"},
                            last_modified=format_timestamp(stat.st_mtime),
                        ))
                    except OSError:
                        continue
        except PermissionError:
            continue

        if len(results) >= limit:
            break

    return APIResponse(
        success=True,
        data=results,
        meta=ResponseMeta(**meta_dict),
    )
