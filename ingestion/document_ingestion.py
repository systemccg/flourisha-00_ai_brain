"""
Document Ingestion Pipeline

Orchestrates the full document processing pipeline:
1. Receive document from source (Gmail, upload, folder)
2. Extract information using document_processor agent
3. Match entities using entity_matcher agent
4. Store to Supabase and Knowledge Graph
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass

from pydantic import BaseModel

from agents.models import DocumentExtraction, MatchingResult, DocumentContext
from agents.document_processor import process_document, process_document_from_email
from agents.entity_matcher import match_entities
from services.document_store import get_document_store
from services.entity_resolver import resolve_from_filename, ResolvedEntity
from services.extraction_feedback_service import get_feedback_service, ValidationResult

logger = logging.getLogger(__name__)


# =============================================================================
# Result Models
# =============================================================================

@dataclass
class DocumentIngestionResult:
    """Result of document ingestion"""
    success: bool
    document_id: Optional[str] = None
    extraction: Optional[DocumentExtraction] = None
    matching: Optional[MatchingResult] = None
    error: Optional[str] = None
    processing_time_ms: int = 0

    # Entity counts
    companies_found: int = 0
    contacts_found: int = 0
    properties_found: int = 0
    entities_linked: int = 0
    entities_created: int = 0

    # Resolved entities from filename
    resolved_property: Optional[Dict[str, Any]] = None
    resolved_organization: Optional[Dict[str, Any]] = None
    filename_parsed: Optional[Dict[str, str]] = None

    # Validation results from feedback system
    validation_results: Optional[List[Dict[str, Any]]] = None
    validation_passed: bool = True
    needs_review_reason: Optional[str] = None


# =============================================================================
# Main Ingestion Functions
# =============================================================================

async def process_document_from_source(
    pdf_bytes: bytes,
    source: str,
    filename: Optional[str] = None,
    source_detail: Optional[str] = None,
    sender_email: Optional[str] = None,
    sender_name: Optional[str] = None,
    email_subject: Optional[str] = None,
    email_body: Optional[str] = None,
    tenant_id: str = "default",
    skip_matching: bool = False,
    skip_storage: bool = False,
) -> DocumentIngestionResult:
    """
    Process a document from any source through the full pipeline.

    Args:
        pdf_bytes: The PDF file content
        source: Source type: "gmail", "upload", "folder", "api"
        filename: Original filename
        source_detail: Additional source info
        sender_email: Email sender (for gmail source)
        sender_name: Sender name (for gmail source)
        email_subject: Email subject (for gmail source)
        email_body: Email body preview (for gmail source)
        tenant_id: Tenant ID for multi-tenancy
        skip_matching: Skip entity matching step
        skip_storage: Skip storage step (for testing)

    Returns:
        DocumentIngestionResult with all processing details
    """
    start_time = datetime.now()
    result = DocumentIngestionResult(success=False)

    try:
        # 0. Resolve entities from filename (if available)
        resolved_property = None
        resolved_org = None
        parsed_filename = None

        if filename:
            resolved_property, resolved_org, parsed_filename = resolve_from_filename(filename)
            result.filename_parsed = parsed_filename

            if resolved_property:
                result.resolved_property = {
                    'id': resolved_property.entity_id,
                    'name': resolved_property.name,
                    'shorthand': resolved_property.attributes.get('shorthand'),
                    'owner': resolved_property.attributes.get('owner'),
                    'matched_via': resolved_property.matched_via,
                }
                logger.info(f"Resolved property from filename: {resolved_property.name}")

            if resolved_org:
                result.resolved_organization = {
                    'id': resolved_org.entity_id,
                    'name': resolved_org.name,
                    'matched_via': resolved_org.matched_via,
                }
                logger.info(f"Resolved organization from filename: {resolved_org.name}")

        # 1. Build context
        context = DocumentContext(
            source=source,
            source_detail=source_detail or email_subject,
            sender_email=sender_email,
            sender_name=sender_name,
            original_filename=filename,
            tenant_id=tenant_id,
        )

        # 2. Extract document information
        logger.info(f"Processing document: {filename or 'unknown'} from {source}")

        # Build additional prompt with resolved entity context
        additional_prompt_parts = []

        if source == "gmail" and email_body:
            additional_prompt_parts.append(f"""
Email context:
Subject: {email_subject}
From: {sender_name or ''} <{sender_email or ''}>
Body preview: {email_body[:500]}...
""")

        # Add resolved entity context to help extraction
        if resolved_property:
            additional_prompt_parts.append(f"""
Known property context (from filename):
- Property: {resolved_property.name}
- Owner: {resolved_property.attributes.get('owner', 'Unknown')}
- City/State: {resolved_property.attributes.get('city', '')}, {resolved_property.attributes.get('state', '')}
This document likely relates to this property.
""")

        if resolved_org:
            additional_prompt_parts.append(f"""
Known organization context (from filename):
- Organization: {resolved_org.name}
- Type: {resolved_org.attributes.get('organization_type', 'Unknown')}
This document is likely from or about this organization.
""")

        additional_prompt = "\n".join(additional_prompt_parts) if additional_prompt_parts else None

        extraction = await process_document(
            document_content=pdf_bytes,
            context=context,
            additional_prompt=additional_prompt,
        )

        result.extraction = extraction
        result.companies_found = len(extraction.companies)
        result.contacts_found = len(extraction.contacts)
        result.properties_found = len(extraction.properties)

        logger.info(f"Extracted: {extraction.document_name} ({extraction.category.value})")
        logger.info(f"  Companies: {result.companies_found}, Contacts: {result.contacts_found}, Properties: {result.properties_found}")

        # 2.5 Validate extraction against known entities (feedback loop)
        try:
            feedback_service = get_feedback_service()
            validation_results = feedback_service.validate_extraction(
                extraction=extraction.model_dump(),
                resolved_property=result.resolved_property,
                resolved_org=result.resolved_organization,
                tenant_id=tenant_id,
            )

            # Convert to serializable format
            result.validation_results = [
                {
                    "rule": v.rule_name,
                    "passed": v.passed,
                    "severity": v.severity,
                    "details": v.details,
                    "suggestion": v.suggestion,
                }
                for v in validation_results
            ]

            # Check for high-severity failures
            high_severity_failures = [v for v in validation_results if not v.passed and v.severity == "high"]
            if high_severity_failures:
                result.validation_passed = False
                result.needs_review_reason = "; ".join(
                    v.suggestion or f"{v.rule_name} failed" for v in high_severity_failures
                )
                logger.warning(f"  Validation failures: {result.needs_review_reason}")

                # Flag extraction for human review
                if extraction.needs_human_review is False:
                    extraction.needs_human_review = True
                    extraction.review_reason = result.needs_review_reason

        except Exception as e:
            logger.warning(f"Validation check failed (non-fatal): {e}")

        # 3. Match entities (if not skipped)
        matching = None
        if not skip_matching and (extraction.companies or extraction.contacts or extraction.properties):
            store = get_document_store()
            existing_companies, existing_contacts, existing_properties = await store.get_existing_entities(tenant_id)

            matching = await match_entities(
                extraction=extraction,
                existing_companies=existing_companies,
                existing_contacts=existing_contacts,
                existing_properties=existing_properties,
            )

            result.matching = matching
            result.entities_linked = matching.auto_linkable
            result.entities_created = matching.new_entities

            logger.info(f"  Matching: {matching.auto_linkable} linked, {matching.new_entities} new, {matching.needs_review} review")

        # 4. Store to Supabase and Knowledge Graph (if not skipped)
        if not skip_storage:
            store = get_document_store()
            store_result = await store.store_document(
                extraction=extraction,
                matching=matching,
                pdf_bytes=pdf_bytes,
                tenant_id=tenant_id,
            )

            result.document_id = store_result.get("document_id")
            logger.info(f"  Stored document: {result.document_id}")

        result.success = True

    except Exception as e:
        logger.exception(f"Error processing document: {e}")
        result.error = str(e)

    # Calculate processing time
    result.processing_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)

    return result


async def process_gmail_attachment(
    pdf_bytes: bytes,
    email_id: str,
    attachment_id: str,
    email_subject: str,
    sender_email: str,
    sender_name: Optional[str] = None,
    email_body: Optional[str] = None,
    filename: Optional[str] = None,
    tenant_id: str = "default",
) -> DocumentIngestionResult:
    """
    Process a document attachment from Gmail.

    This is the entry point for the Gmail ingestion worker.
    """
    return await process_document_from_source(
        pdf_bytes=pdf_bytes,
        source="gmail",
        filename=filename,
        source_detail=f"Email: {email_subject} (ID: {email_id})",
        sender_email=sender_email,
        sender_name=sender_name,
        email_subject=email_subject,
        email_body=email_body,
        tenant_id=tenant_id,
    )


async def process_uploaded_file(
    pdf_bytes: bytes,
    filename: str,
    description: Optional[str] = None,
    tenant_id: str = "default",
) -> DocumentIngestionResult:
    """
    Process a directly uploaded document.

    This is the entry point for the upload API.
    """
    return await process_document_from_source(
        pdf_bytes=pdf_bytes,
        source="upload",
        filename=filename,
        source_detail=description,
        tenant_id=tenant_id,
    )


async def process_folder_document(
    file_path: Path,
    tenant_id: str = "default",
) -> DocumentIngestionResult:
    """
    Process a document from a watched folder.

    This is the entry point for the folder watcher.
    """
    with open(file_path, 'rb') as f:
        pdf_bytes = f.read()

    return await process_document_from_source(
        pdf_bytes=pdf_bytes,
        source="folder",
        filename=file_path.name,
        source_detail=f"Folder: {file_path.parent}",
        tenant_id=tenant_id,
    )


# =============================================================================
# Batch Processing
# =============================================================================

async def process_multiple_documents(
    documents: List[Dict[str, Any]],
    tenant_id: str = "default",
) -> List[DocumentIngestionResult]:
    """
    Process multiple documents.

    Each document dict should have:
    - pdf_bytes: bytes
    - source: str
    - filename: Optional[str]
    - ... other source-specific fields
    """
    results = []

    for doc in documents:
        result = await process_document_from_source(
            pdf_bytes=doc["pdf_bytes"],
            source=doc.get("source", "api"),
            filename=doc.get("filename"),
            source_detail=doc.get("source_detail"),
            sender_email=doc.get("sender_email"),
            sender_name=doc.get("sender_name"),
            email_subject=doc.get("email_subject"),
            email_body=doc.get("email_body"),
            tenant_id=tenant_id,
        )
        results.append(result)

    return results


# =============================================================================
# Gmail Integration Extension
# =============================================================================

class DocumentGmailWorker:
    """
    Extension to the existing Gmail worker for document processing.

    Monitors a Gmail label for new messages with PDF attachments
    and processes them through the document intelligence pipeline.
    """

    def __init__(
        self,
        unprocessed_label: str = "Flourisha/Documents/Unprocessed",
        processed_label: str = "Flourisha/Documents/Processed",
        failed_label: str = "Flourisha/Documents/Failed",
        tenant_id: str = "default",
    ):
        self.unprocessed_label = unprocessed_label
        self.processed_label = processed_label
        self.failed_label = failed_label
        self.tenant_id = tenant_id
        self._gmail_service = None

    @property
    def gmail(self):
        """Lazy load Gmail service"""
        if self._gmail_service is None:
            from ..services.gmail_service import get_gmail_service
            self._gmail_service = get_gmail_service()
        return self._gmail_service

    async def process_unprocessed_emails(self, max_emails: int = 10) -> List[DocumentIngestionResult]:
        """
        Process emails in the unprocessed label.

        Returns list of processing results.
        """
        results = []

        # Get messages with the unprocessed label
        messages = self.gmail.list_messages_by_label(self.unprocessed_label, max_results=max_emails)

        for msg_info in messages:
            msg_id = msg_info['id']

            try:
                # Get full message
                message = self.gmail.get_message(msg_id)

                # Extract email details
                headers = {h['name']: h['value'] for h in message.get('payload', {}).get('headers', [])}
                subject = headers.get('Subject', 'No Subject')
                from_header = headers.get('From', '')

                # Parse sender
                sender_email = from_header
                sender_name = None
                if '<' in from_header:
                    parts = from_header.split('<')
                    sender_name = parts[0].strip().strip('"')
                    sender_email = parts[1].rstrip('>')

                # Get body preview
                body = self.gmail.get_message_body(message)

                # Process PDF attachments
                attachments = self.gmail.get_attachments(msg_id)

                for att in attachments:
                    if att.get('mimeType') == 'application/pdf':
                        # Get attachment content
                        att_data = self.gmail.get_attachment_content(msg_id, att['attachmentId'])

                        # Process through pipeline
                        result = await process_gmail_attachment(
                            pdf_bytes=att_data,
                            email_id=msg_id,
                            attachment_id=att['attachmentId'],
                            email_subject=subject,
                            sender_email=sender_email,
                            sender_name=sender_name,
                            email_body=body[:500] if body else None,
                            filename=att.get('filename'),
                            tenant_id=self.tenant_id,
                        )

                        results.append(result)

                # Move to processed or failed
                if all(r.success for r in results if r):
                    self.gmail.modify_message_labels(
                        msg_id,
                        add_labels=[self.processed_label],
                        remove_labels=[self.unprocessed_label],
                    )
                else:
                    self.gmail.modify_message_labels(
                        msg_id,
                        add_labels=[self.failed_label],
                        remove_labels=[self.unprocessed_label],
                    )

            except Exception as e:
                logger.exception(f"Error processing email {msg_id}: {e}")
                results.append(DocumentIngestionResult(
                    success=False,
                    error=f"Email processing error: {e}"
                ))

        return results


# =============================================================================
# Utility Functions
# =============================================================================

def is_pdf(content: bytes) -> bool:
    """Check if content is a PDF by magic bytes"""
    return content[:4] == b'%PDF'


def get_mime_type(filename: str) -> str:
    """Get MIME type from filename"""
    ext = Path(filename).suffix.lower()
    mime_types = {
        '.pdf': 'application/pdf',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
    }
    return mime_types.get(ext, 'application/octet-stream')
