"""
Document Upload Models

Pydantic models for document upload and processing API.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class DocumentType(str, Enum):
    """Supported document types for upload."""
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    TXT = "txt"
    MD = "md"
    XLSX = "xlsx"
    XLS = "xls"
    CSV = "csv"
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"
    GIF = "gif"
    WEBP = "webp"


class ProcessingStatus(str, Enum):
    """Document processing status."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingPriority(int, Enum):
    """Processing queue priority (1-10, higher = more urgent)."""
    LOW = 1
    NORMAL = 5
    HIGH = 8
    URGENT = 10


# File type to extension mapping
ALLOWED_EXTENSIONS = {
    "application/pdf": DocumentType.PDF,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": DocumentType.DOCX,
    "application/msword": DocumentType.DOC,
    "text/plain": DocumentType.TXT,
    "text/markdown": DocumentType.MD,
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": DocumentType.XLSX,
    "application/vnd.ms-excel": DocumentType.XLS,
    "text/csv": DocumentType.CSV,
    "image/png": DocumentType.PNG,
    "image/jpeg": DocumentType.JPG,
    "image/gif": DocumentType.GIF,
    "image/webp": DocumentType.WEBP,
}

# Extension to MIME type mapping for filename validation
EXTENSION_MAP = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".doc": "application/msword",
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".markdown": "text/markdown",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".xls": "application/vnd.ms-excel",
    ".csv": "text/csv",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
}

# Max file size: 50MB
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024


class DocumentUploadRequest(BaseModel):
    """Metadata for document upload."""
    title: Optional[str] = Field(None, description="Document title (auto-generated from filename if not provided)")
    document_type: Optional[str] = Field(None, description="Type of document (e.g., 'medical', 'legal', 'general')")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags to apply to document")
    priority: ProcessingPriority = Field(default=ProcessingPriority.NORMAL, description="Processing priority (1-10)")
    extract_entities: bool = Field(default=True, description="Extract entities during processing")
    project_id: Optional[str] = Field(None, description="Project to associate document with")

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Medical Records Q4 2025",
                "document_type": "medical",
                "tags": ["health", "records"],
                "priority": 5,
                "extract_entities": True,
                "project_id": None
            }
        }
    }


class DocumentUploadResponse(BaseModel):
    """Response after successful document upload."""
    document_id: str = Field(..., description="Unique document identifier for tracking")
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    content_type: str = Field(..., description="MIME type of the file")
    status: ProcessingStatus = Field(..., description="Current processing status")
    queue_position: Optional[int] = Field(None, description="Position in processing queue")
    estimated_wait_seconds: Optional[int] = Field(None, description="Estimated wait time before processing starts")

    model_config = {
        "json_schema_extra": {
            "example": {
                "document_id": "doc_abc123xyz",
                "filename": "medical_records.pdf",
                "file_size": 1048576,
                "content_type": "application/pdf",
                "status": "queued",
                "queue_position": 3,
                "estimated_wait_seconds": 45
            }
        }
    }


class DocumentStatus(BaseModel):
    """Document processing status details."""
    document_id: str = Field(..., description="Document identifier")
    status: ProcessingStatus = Field(..., description="Current processing status")
    progress_percent: Optional[int] = Field(None, description="Processing progress (0-100)")
    error_message: Optional[str] = Field(None, description="Error message if processing failed")
    created_at: datetime = Field(..., description="Upload timestamp")
    updated_at: datetime = Field(..., description="Last status update")
    completed_at: Optional[datetime] = Field(None, description="Processing completion time")

    model_config = {
        "json_schema_extra": {
            "example": {
                "document_id": "doc_abc123xyz",
                "status": "processing",
                "progress_percent": 65,
                "error_message": None,
                "created_at": "2025-12-26T10:00:00-08:00",
                "updated_at": "2025-12-26T10:01:30-08:00",
                "completed_at": None
            }
        }
    }


class DocumentList(BaseModel):
    """List of documents with pagination."""
    documents: List[DocumentStatus] = Field(..., description="List of document statuses")
    total: int = Field(..., description="Total document count")
    page: int = Field(..., description="Current page (1-based)")
    page_size: int = Field(..., description="Items per page")
    has_more: bool = Field(..., description="Whether more pages exist")
