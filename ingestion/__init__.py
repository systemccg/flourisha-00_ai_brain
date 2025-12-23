"""
Flourisha Document Ingestion

Multiple ingestion sources for document processing:
- Gmail (label-based)
- Direct upload
- Folder watching
"""

from .document_ingestion import (
    process_document_from_source,
    process_gmail_attachment,
    process_uploaded_file,
    DocumentIngestionResult,
)

__all__ = [
    "process_document_from_source",
    "process_gmail_attachment",
    "process_uploaded_file",
    "DocumentIngestionResult",
]
