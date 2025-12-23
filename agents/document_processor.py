"""
Document Processor Agent

Main Pydantic AI agent for extracting structured information from documents.
Uses Claude's native PDF understanding for document analysis.
"""

import os
import base64
from typing import Optional, Union
from pathlib import Path

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.messages import BinaryContent

from .models import DocumentExtraction, DocumentContext, DocumentCategory


# =============================================================================
# System Prompt
# =============================================================================

DOCUMENT_PROCESSOR_SYSTEM_PROMPT = """You are an expert document analyst for Flourisha, a personal AI system.
Your job is to extract structured information from documents.

## Your Tasks

1. **CLASSIFY** the document:
   - Determine the primary category (contract, invoice, correspondence, etc.)
   - Identify a more specific subcategory if applicable
   - Create a descriptive document name

2. **EXTRACT ENTITIES**:
   - Companies/Organizations: name, type, contact info, role in document
   - People/Contacts: name, title, company, contact info, role in document
   - Properties: full address AND short address, city, state, zip, property type
   - Agreements: type, parties, dates, value, terms
   - Financial details: amounts, account numbers, due dates

3. **IDENTIFY RELATIONSHIPS**:
   - Determine the PRIMARY company, contact, and property this document relates to
   - Note which entities are issuers vs recipients vs parties

4. **SUMMARIZE**:
   - Write a 2-3 sentence summary of what this document is and its purpose

## Critical Rule: DO NOT FABRICATE

**DO NOT try to make up a value for any field. If you cannot find information explicitly stated in the document, leave the field null/empty.**

This is more important than having complete data. Accuracy over completeness.

## Guidelines

- Extract information EXACTLY as it appears IN THE DOCUMENT - don't infer or fabricate
- IMPORTANT: Always prioritize information from the document content over filename or metadata
  - Filenames may contain shorthand, nicknames, or incorrect information
  - The document itself is the source of truth for entity names
- For dates, use YYYY-MM-DD format
- For phone numbers, use E.164 format (+12125551234)
- For partial account numbers, include only visible digits
- If a field cannot be determined, leave it null
- Set needs_human_review=True if:
  - Document is blurry, damaged, or hard to read
  - Important information is ambiguous
  - Document appears incomplete
  - You're uncertain about classification

## Property Extraction

For real estate properties:
- **address**: Full street address (e.g., "1234 S Glendale Dr, Atlanta, GA 85031")
- **short_address**: Street number and name ONLY, no suffix/city/state (e.g., "1234 S Glendale")
  - This is used for file naming where punctuation causes issues
  - Omit street type (St, Dr, Ave, Blvd, etc.)

## Loan/Mortgage Document Guidelines

When processing loan, mortgage, or real estate documents:

### Subject Line Patterns
Email subject lines typically contain: borrower name + property shorthand + loan number
Example: "Smith, John | 1234 Glendale | Purchase" contains borrower and property hints

### Distinguishing People Roles
- **Borrower/Buyer**: The person obtaining the loan or purchasing property
- **Submitter**: The person who sent the document (often a loan officer, NOT the borrower)
- **Contact**: The human to communicate with about this file
- Set is_borrower=True and is_submitter=True appropriately

### Legal Entity vs Contact Person
Many properties are purchased by LLCs, Trusts, or Corporations:
- **legal_entity_name**: The vesting entity (e.g., "Happy Housing Solutions LLC")
- **full_name**: The human contact (e.g., "John Smith")
- These are often DIFFERENT - an LLC buys the property, but John Smith is who you call

### Internal vs External Emails
- Staff emails (e.g., @myremotelender.com, @company.com) are internal submitters
- Borrower emails are external (personal domains, gmail, etc.)
- Don't confuse internal staff with borrowers

## Confidence Scoring

- 0.9-1.0: Clear, high-quality document with unambiguous content
- 0.7-0.9: Good extraction but some fields uncertain
- 0.5-0.7: Partial extraction, several uncertainties
- Below 0.5: Poor quality, recommend human review

You will receive documents as PDFs. Analyze them thoroughly and extract all relevant information."""


# =============================================================================
# Agent Definition (Lazy Initialization)
# =============================================================================

_document_processor = None


def get_document_processor() -> Agent:
    """Get or create the document processor agent (lazy initialization)."""
    global _document_processor
    if _document_processor is None:
        _document_processor = Agent(
            model=AnthropicModel('claude-sonnet-4-20250514'),
            output_type=DocumentExtraction,
            system_prompt=DOCUMENT_PROCESSOR_SYSTEM_PROMPT,
            retries=2,
        )
    return _document_processor


# Convenience alias for backward compatibility
document_processor = get_document_processor


# =============================================================================
# Processing Functions
# =============================================================================

async def process_document(
    document_content: Union[bytes, str, Path],
    context: Optional[DocumentContext] = None,
    additional_prompt: Optional[str] = None,
) -> DocumentExtraction:
    """
    Process a document and extract structured information.

    Args:
        document_content: PDF bytes, base64 string, or file path
        context: Optional context about the document source
        additional_prompt: Optional additional instructions

    Returns:
        DocumentExtraction with all extracted information
    """
    # Handle different input types
    if isinstance(document_content, Path) or (isinstance(document_content, str) and os.path.exists(document_content)):
        path = Path(document_content)
        with open(path, 'rb') as f:
            pdf_bytes = f.read()
        filename = path.name
    elif isinstance(document_content, str):
        # Assume base64
        pdf_bytes = base64.b64decode(document_content)
        filename = "document.pdf"
    else:
        pdf_bytes = document_content
        filename = "document.pdf"

    # Build the prompt
    prompt_parts = ["Please analyze this document and extract all relevant information."]

    if context:
        prompt_parts.append(f"\n\nDocument Context:")
        prompt_parts.append(f"- Source: {context.source}")
        if context.source_detail:
            prompt_parts.append(f"- Details: {context.source_detail}")
        if context.sender_email:
            prompt_parts.append(f"- From: {context.sender_name or ''} <{context.sender_email}>")
        if context.original_filename:
            prompt_parts.append(f"- Original filename: {context.original_filename}")
            filename = context.original_filename

    if additional_prompt:
        prompt_parts.append(f"\n\nAdditional Instructions:\n{additional_prompt}")

    prompt = "\n".join(prompt_parts)

    # Run the agent with the PDF using BinaryContent
    agent = get_document_processor()

    # Create multimodal prompt with PDF content
    pdf_content = BinaryContent(data=pdf_bytes, media_type='application/pdf')

    result = await agent.run([pdf_content, prompt])

    extraction = result.output

    # Add source type from context
    if context:
        extraction.source_type = context.source

    return extraction


async def process_document_from_email(
    pdf_bytes: bytes,
    email_subject: str,
    sender_email: str,
    sender_name: Optional[str] = None,
    email_body: Optional[str] = None,
    filename: Optional[str] = None,
    tenant_id: str = "default",
) -> DocumentExtraction:
    """
    Process a document that came from an email attachment.

    Args:
        pdf_bytes: The PDF file content
        email_subject: Subject line of the email
        sender_email: Sender's email address
        sender_name: Sender's display name
        email_body: Email body text (first 500 chars recommended)
        filename: Original attachment filename
        tenant_id: Tenant ID for multi-tenancy

    Returns:
        DocumentExtraction with all extracted information
    """
    context = DocumentContext(
        source="gmail",
        source_detail=f"Subject: {email_subject}",
        sender_email=sender_email,
        sender_name=sender_name,
        original_filename=filename,
        tenant_id=tenant_id,
    )

    additional_prompt = None
    if email_body:
        additional_prompt = f"""
Email context that may help identify the document:
Subject: {email_subject}
From: {sender_name or ''} <{sender_email}>
Body preview: {email_body[:500]}...
"""

    return await process_document(
        document_content=pdf_bytes,
        context=context,
        additional_prompt=additional_prompt,
    )


async def process_document_from_upload(
    pdf_bytes: bytes,
    filename: str,
    description: Optional[str] = None,
    tenant_id: str = "default",
) -> DocumentExtraction:
    """
    Process a document that was directly uploaded.

    Args:
        pdf_bytes: The PDF file content
        filename: Original filename
        description: Optional user-provided description
        tenant_id: Tenant ID for multi-tenancy

    Returns:
        DocumentExtraction with all extracted information
    """
    context = DocumentContext(
        source="upload",
        source_detail=description,
        original_filename=filename,
        tenant_id=tenant_id,
    )

    return await process_document(
        document_content=pdf_bytes,
        context=context,
        additional_prompt=description,
    )


# =============================================================================
# Utility Functions
# =============================================================================

def get_document_category_label(category: DocumentCategory) -> str:
    """Get human-readable label for a document category"""
    labels = {
        DocumentCategory.CONTRACT: "Contract",
        DocumentCategory.AGREEMENT: "Agreement",
        DocumentCategory.INVOICE: "Invoice",
        DocumentCategory.CORRESPONDENCE: "Correspondence",
        DocumentCategory.LEGAL: "Legal Document",
        DocumentCategory.FINANCIAL: "Financial Document",
        DocumentCategory.INSURANCE: "Insurance Document",
        DocumentCategory.PROPERTY: "Property Document",
        DocumentCategory.IDENTIFICATION: "Identification",
        DocumentCategory.TAX: "Tax Document",
        DocumentCategory.REPORT: "Report",
        DocumentCategory.APPLICATION: "Application",
        DocumentCategory.OTHER: "Other",
    }
    return labels.get(category, "Document")
