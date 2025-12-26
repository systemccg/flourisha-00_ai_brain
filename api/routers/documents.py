"""
Documents Router

File upload and document management endpoints for the AI Brain.
Handles multipart uploads, validation, and queueing for processing.
"""
import os
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse

from models.response import APIResponse, ResponseMeta
from models.documents import (
    DocumentUploadResponse,
    DocumentStatus,
    DocumentList,
    ProcessingStatus,
    ProcessingPriority,
    ALLOWED_EXTENSIONS,
    EXTENSION_MAP,
    MAX_FILE_SIZE_BYTES,
)
from middleware.auth import get_current_user, get_optional_user, UserContext


router = APIRouter(prefix="/api/documents", tags=["Documents"])
logger = logging.getLogger(__name__)

# Upload directory - persistent storage
UPLOAD_DIR = Path("/root/flourisha/00_AI_Brain/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Pacific timezone for timestamps
PACIFIC = ZoneInfo("America/Los_Angeles")


def validate_file_type(filename: str, content_type: str) -> str:
    """Validate file type by extension and content type.

    Returns the validated MIME type.
    Raises HTTPException if invalid.
    """
    # Get extension from filename
    ext = Path(filename).suffix.lower()

    if ext not in EXTENSION_MAP:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed extensions: {', '.join(EXTENSION_MAP.keys())}"
        )

    # Accept the content type from extension if browser sends generic type
    expected_mime = EXTENSION_MAP[ext]

    # Accept either the expected MIME or application/octet-stream (generic)
    if content_type not in [expected_mime, "application/octet-stream"]:
        # Also accept similar MIME types (e.g., image/jpeg for both .jpg and .jpeg)
        if content_type not in ALLOWED_EXTENSIONS:
            logger.warning(f"MIME type mismatch: got {content_type}, expected {expected_mime} for {filename}")

    return expected_mime


def validate_file_size(file_size: int) -> None:
    """Validate file size.

    Raises HTTPException if too large.
    """
    if file_size > MAX_FILE_SIZE_BYTES:
        max_mb = MAX_FILE_SIZE_BYTES / (1024 * 1024)
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {max_mb:.0f}MB"
        )


def generate_document_id() -> str:
    """Generate a unique document ID."""
    return f"doc_{uuid.uuid4().hex[:16]}"


async def save_upload(file: UploadFile, document_id: str) -> tuple[Path, int]:
    """Save uploaded file to disk.

    Returns (file_path, file_size).
    """
    # Create directory for document
    doc_dir = UPLOAD_DIR / document_id
    doc_dir.mkdir(parents=True, exist_ok=True)

    # Save with original filename
    safe_filename = Path(file.filename).name  # Remove any path components
    file_path = doc_dir / safe_filename

    # Read and save file in chunks
    total_size = 0
    with open(file_path, "wb") as f:
        while chunk := await file.read(8192):  # 8KB chunks
            total_size += len(chunk)
            if total_size > MAX_FILE_SIZE_BYTES:
                # Clean up and reject
                f.close()
                file_path.unlink()
                doc_dir.rmdir()
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Maximum size is {MAX_FILE_SIZE_BYTES / (1024*1024):.0f}MB"
                )
            f.write(chunk)

    return file_path, total_size


async def queue_for_processing(
    document_id: str,
    file_path: Path,
    tenant_id: str,
    user_id: str,
    title: Optional[str],
    document_type: Optional[str],
    tags: list,
    priority: int,
    extract_entities: bool,
    project_id: Optional[str],
) -> tuple[int, int]:
    """Queue document for processing.

    Returns (queue_position, estimated_wait_seconds).
    """
    # Import service at runtime to avoid circular imports
    import sys
    sys.path.insert(0, "/root/flourisha/00_AI_Brain")
    from services.supabase_client import SupabaseService

    supabase = SupabaseService()
    now = datetime.now(PACIFIC).isoformat()

    # First, create content record
    content_data = {
        "id": document_id,
        "tenant_id": tenant_id,
        "tenant_user_id": user_id,
        "created_by_user_id": user_id,
        "source_type": "upload",
        "source_id": str(file_path),
        "title": title or file_path.name,
        "raw_content": None,  # Will be filled during processing
        "processing_status": "pending",
        "tags": tags,
        "created_at": now,
        "updated_at": now,
    }

    if project_id:
        content_data["project_id"] = project_id

    try:
        # Insert into processed_content
        supabase.client.table("processed_content").insert(content_data).execute()

        # Add to processing queue
        queue_data = {
            "tenant_id": tenant_id,
            "content_id": document_id,
            "priority": priority,
            "status": "queued",
            "retry_count": 0,
            "created_at": now,
            "metadata": {
                "file_path": str(file_path),
                "document_type": document_type,
                "extract_entities": extract_entities,
            }
        }

        supabase.client.table("processing_queue").insert(queue_data).execute()

        # Get queue position
        queue_result = supabase.client.table("processing_queue").select("id").eq("status", "queued").execute()
        queue_position = len(queue_result.data) if queue_result.data else 1

        # Estimate ~15 seconds per document in queue
        estimated_wait = queue_position * 15

        return queue_position, estimated_wait

    except Exception as e:
        logger.error(f"Failed to queue document {document_id}: {e}")
        # Clean up file on error
        if file_path.exists():
            file_path.unlink()
            file_path.parent.rmdir()
        raise HTTPException(status_code=500, detail=f"Failed to queue document: {str(e)}")


@router.post("/upload", response_model=APIResponse[DocumentUploadResponse])
async def upload_document(
    request: Request,
    file: UploadFile = File(..., description="Document file to upload"),
    title: Optional[str] = Form(None, description="Document title"),
    document_type: Optional[str] = Form(None, description="Document type (medical, legal, general, etc.)"),
    tags: Optional[str] = Form(None, description="Comma-separated tags"),
    priority: int = Form(5, description="Processing priority (1-10, higher = more urgent)"),
    extract_entities: bool = Form(True, description="Extract entities during processing"),
    project_id: Optional[str] = Form(None, description="Project ID to associate with"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[DocumentUploadResponse]:
    """Upload a document for processing.

    Accepts PDF, DOCX, images, and other supported formats.
    Maximum file size: 50MB.

    The document is queued for async processing which includes:
    - Text extraction
    - Entity extraction (if enabled)
    - Embedding generation for semantic search
    - Knowledge graph integration

    Returns a document_id for tracking processing status.
    """
    # Validate file type
    content_type = validate_file_type(file.filename, file.content_type)

    # Generate document ID
    document_id = generate_document_id()

    # Save file
    file_path, file_size = await save_upload(file, document_id)

    # Parse tags
    tag_list = [t.strip() for t in tags.split(",")] if tags else []

    # Clamp priority to 1-10
    priority = max(1, min(10, priority))

    # Queue for processing
    queue_position, estimated_wait = await queue_for_processing(
        document_id=document_id,
        file_path=file_path,
        tenant_id=user.tenant_id or "default",
        user_id=user.uid,
        title=title,
        document_type=document_type,
        tags=tag_list,
        priority=priority,
        extract_entities=extract_entities,
        project_id=project_id,
    )

    # Build response
    meta_dict = request.state.get_meta()

    return APIResponse(
        success=True,
        data=DocumentUploadResponse(
            document_id=document_id,
            filename=file.filename,
            file_size=file_size,
            content_type=content_type,
            status=ProcessingStatus.QUEUED,
            queue_position=queue_position,
            estimated_wait_seconds=estimated_wait,
        ),
        meta=ResponseMeta(**meta_dict),
    )


@router.get("/{document_id}", response_model=APIResponse[DocumentStatus])
async def get_document_status(
    request: Request,
    document_id: str,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[DocumentStatus]:
    """Get processing status for a document.

    Returns current status, progress, and any error messages.
    """
    import sys
    sys.path.insert(0, "/root/flourisha/00_AI_Brain")
    from services.supabase_client import SupabaseService

    supabase = SupabaseService()

    # Get content record
    result = supabase.client.table("processed_content").select("*").eq("id", document_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Document not found")

    doc = result.data[0]

    # Check ownership
    if doc.get("tenant_user_id") != user.uid and doc.get("tenant_id") != user.tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get queue info if still processing
    queue_result = supabase.client.table("processing_queue").select("*").eq("content_id", document_id).execute()

    status_str = doc.get("processing_status", "queued")
    progress = None

    if status_str == "processing":
        progress = 50  # Estimate mid-way
    elif status_str == "completed":
        progress = 100

    meta_dict = request.state.get_meta()

    return APIResponse(
        success=True,
        data=DocumentStatus(
            document_id=document_id,
            status=ProcessingStatus(status_str) if status_str in ProcessingStatus.__members__.values() else ProcessingStatus.QUEUED,
            progress_percent=progress,
            error_message=doc.get("error_message"),
            created_at=doc.get("created_at", datetime.now(PACIFIC).isoformat()),
            updated_at=doc.get("updated_at", datetime.now(PACIFIC).isoformat()),
            completed_at=doc.get("date_completed"),
        ),
        meta=ResponseMeta(**meta_dict),
    )


@router.get("/", response_model=APIResponse[DocumentList])
async def list_documents(
    request: Request,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[DocumentList]:
    """List documents for the current user.

    Supports filtering by status and pagination.
    """
    import sys
    sys.path.insert(0, "/root/flourisha/00_AI_Brain")
    from services.supabase_client import SupabaseService

    supabase = SupabaseService()

    # Build query
    query = supabase.client.table("processed_content").select("*", count="exact")
    query = query.eq("source_type", "upload")
    query = query.eq("tenant_user_id", user.uid)

    if status:
        query = query.eq("processing_status", status)

    # Pagination
    offset = (page - 1) * page_size
    query = query.range(offset, offset + page_size - 1)
    query = query.order("created_at", desc=True)

    result = query.execute()

    total = result.count or 0
    documents = []

    for doc in result.data or []:
        status_str = doc.get("processing_status", "queued")
        progress = 100 if status_str == "completed" else (50 if status_str == "processing" else None)

        documents.append(DocumentStatus(
            document_id=doc["id"],
            status=ProcessingStatus(status_str) if status_str in [s.value for s in ProcessingStatus] else ProcessingStatus.QUEUED,
            progress_percent=progress,
            error_message=doc.get("error_message"),
            created_at=doc.get("created_at", datetime.now(PACIFIC).isoformat()),
            updated_at=doc.get("updated_at", datetime.now(PACIFIC).isoformat()),
            completed_at=doc.get("date_completed"),
        ))

    meta_dict = request.state.get_meta()

    return APIResponse(
        success=True,
        data=DocumentList(
            documents=documents,
            total=total,
            page=page,
            page_size=page_size,
            has_more=(offset + len(documents)) < total,
        ),
        meta=ResponseMeta(**meta_dict),
    )


@router.delete("/{document_id}", response_model=APIResponse[dict])
async def delete_document(
    request: Request,
    document_id: str,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[dict]:
    """Delete a document and its associated data.

    Removes the document from storage and database.
    Cannot delete documents that are currently being processed.
    """
    import sys
    sys.path.insert(0, "/root/flourisha/00_AI_Brain")
    from services.supabase_client import SupabaseService

    supabase = SupabaseService()

    # Get document
    result = supabase.client.table("processed_content").select("*").eq("id", document_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Document not found")

    doc = result.data[0]

    # Check ownership
    if doc.get("tenant_user_id") != user.uid:
        raise HTTPException(status_code=403, detail="Access denied")

    # Check if processing
    if doc.get("processing_status") == "processing":
        raise HTTPException(status_code=400, detail="Cannot delete document while processing")

    # Delete from queue
    supabase.client.table("processing_queue").delete().eq("content_id", document_id).execute()

    # Delete content record
    supabase.client.table("processed_content").delete().eq("id", document_id).execute()

    # Delete file from storage
    doc_dir = UPLOAD_DIR / document_id
    if doc_dir.exists():
        import shutil
        shutil.rmtree(doc_dir)

    meta_dict = request.state.get_meta()

    return APIResponse(
        success=True,
        data={"deleted": True, "document_id": document_id},
        meta=ResponseMeta(**meta_dict),
    )
