# Document Intelligence System - Pydantic AI Architecture

## Overview

Generalized document processing system using Pydantic AI agents with Claude.
Extracts entities and relationships from any document type, storing to Supabase
with relationship tracking in Neo4j Knowledge Graph.

## Design Principles

1. **Generalized** - Not loan-specific; handles any document type
2. **Relationship-focused** - Documents ↔ Companies ↔ Contacts ↔ Agreements
3. **Multi-source ingestion** - Gmail labels, file uploads, folder watching
4. **Claude-native PDF** - Simple, no extra infrastructure
5. **App-ready backend** - Supabase tables ready for future frontend

## Core Pydantic Models

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import date

# Document Classification
class DocumentCategory(str, Enum):
    CONTRACT = "contract"
    AGREEMENT = "agreement"
    INVOICE = "invoice"
    CORRESPONDENCE = "correspondence"
    LEGAL = "legal"
    FINANCIAL = "financial"
    INSURANCE = "insurance"
    PROPERTY = "property"
    IDENTIFICATION = "identification"
    OTHER = "other"

# Entity Models (matching Supabase mrl_* tables)
class ExtractedCompany(BaseModel):
    """Company/organization found in document"""
    name: str = Field(description="Company or organization name")
    company_type: Optional[str] = Field(None, description="Type: vendor, client, lender, etc.")
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    role_in_document: Optional[str] = Field(None, description="Role in this document: issuer, recipient, party, etc.")

class ExtractedContact(BaseModel):
    """Person/contact found in document"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: str = Field(description="Full name as appears in document")
    email: Optional[str] = None
    phone: Optional[str] = None
    title: Optional[str] = Field(None, description="Job title or role")
    company: Optional[str] = Field(None, description="Associated company name")
    role_in_document: Optional[str] = Field(None, description="Role: signer, recipient, author, etc.")

class ExtractedProperty(BaseModel):
    """Real estate property found in document"""
    address: str = Field(description="Full street address")
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    property_type: Optional[str] = Field(None, description="residential, commercial, land, etc.")

class ExtractedAgreement(BaseModel):
    """Agreement/contract details"""
    agreement_type: Optional[str] = Field(None, description="lease, purchase, service, NDA, etc.")
    parties: List[str] = Field(default_factory=list, description="Names of parties involved")
    effective_date: Optional[date] = None
    expiration_date: Optional[date] = None
    value: Optional[float] = Field(None, description="Contract value if mentioned")

class FinancialDetails(BaseModel):
    """Financial information extracted"""
    amounts: List[float] = Field(default_factory=list)
    account_numbers: List[str] = Field(default_factory=list, description="Partial/masked account numbers")
    dates: List[date] = Field(default_factory=list)

# Main Extraction Result
class DocumentExtraction(BaseModel):
    """Complete extraction from a document"""
    # Classification
    document_name: str = Field(description="Suggested name for this document")
    category: DocumentCategory
    subcategory: Optional[str] = Field(None, description="More specific type within category")
    summary: str = Field(description="2-3 sentence summary of document content")

    # Key dates
    document_date: Optional[date] = Field(None, description="Date on the document")
    effective_date: Optional[date] = None
    expiration_date: Optional[date] = None

    # Extracted entities
    companies: List[ExtractedCompany] = Field(default_factory=list)
    contacts: List[ExtractedContact] = Field(default_factory=list)
    properties: List[ExtractedProperty] = Field(default_factory=list)
    agreement: Optional[ExtractedAgreement] = None
    financial: Optional[FinancialDetails] = None

    # Relationships
    primary_company: Optional[str] = Field(None, description="Main company this document relates to")
    primary_contact: Optional[str] = Field(None, description="Main person this document relates to")
    primary_property: Optional[str] = Field(None, description="Main property this document relates to")

    # Confidence
    extraction_confidence: float = Field(ge=0, le=1, description="Confidence in extraction accuracy")
    needs_human_review: bool = Field(default=False)
    review_reason: Optional[str] = None
```

## Pydantic AI Agents

### 1. Document Processor Agent

```python
from pydantic_ai import Agent

document_processor = Agent(
    'anthropic:claude-sonnet-4-20250514',
    result_type=DocumentExtraction,
    system_prompt="""You are an expert document analyst. Your job is to:

1. CLASSIFY the document type and category
2. EXTRACT all entities: companies, contacts, properties
3. IDENTIFY relationships between entities
4. SUMMARIZE the document purpose

Guidelines:
- Extract information exactly as it appears (don't infer or guess)
- Mark needs_human_review=True if document is unclear or complex
- For dates, use ISO format (YYYY-MM-DD)
- For phone numbers, include country code if visible
- For partial account numbers, include only visible digits with * for hidden
- Identify the PRIMARY entity this document is about

You will receive the document as a PDF. Analyze it thoroughly."""
)
```

### 2. Entity Matcher Agent

```python
class EntityMatch(BaseModel):
    """Result of matching extracted entity to existing records"""
    entity_type: str  # company, contact, property
    extracted_name: str
    matched_id: Optional[str] = None  # Supabase record ID if matched
    match_confidence: float
    is_new_entity: bool
    suggested_action: str  # "link_existing", "create_new", "needs_review"

class MatchingResult(BaseModel):
    company_matches: List[EntityMatch]
    contact_matches: List[EntityMatch]
    property_matches: List[EntityMatch]

entity_matcher = Agent(
    'anthropic:claude-sonnet-4-20250514',
    result_type=MatchingResult,
    system_prompt="""You match extracted entities against existing database records.

For each extracted entity, determine if it matches an existing record or is new.
Consider name variations, abbreviations, and common patterns.

Match confidence:
- 0.9+ : Definite match (same name, same details)
- 0.7-0.9 : Likely match (similar name, some details match)
- 0.5-0.7 : Possible match (needs review)
- <0.5 : Probably new entity"""
)
```

## Ingestion Pipeline

### Gmail Ingestion

```python
async def process_gmail_document(
    email_id: str,
    attachment_index: int,
    gmail_service: GmailService
) -> ProcessingResult:
    """Process a document from Gmail attachment"""

    # 1. Get attachment
    attachment = await gmail_service.get_attachment(email_id, attachment_index)

    # 2. Get email context
    email = await gmail_service.get_email(email_id)
    email_context = f"""
    From: {email.sender}
    Subject: {email.subject}
    Date: {email.date}
    Body preview: {email.body[:500]}
    """

    # 3. Process with agent
    result = await document_processor.run(
        f"Process this document. Email context:\n{email_context}",
        attachments=[attachment.content]  # Claude native PDF
    )

    # 4. Match entities to existing records
    existing_entities = await get_existing_entities()
    matches = await entity_matcher.run(
        f"Match these extracted entities to existing records:\n"
        f"Extracted: {result.data.model_dump_json()}\n"
        f"Existing: {existing_entities}"
    )

    # 5. Store to Supabase
    doc_id = await store_document(result.data, matches.data)

    # 6. Add to Knowledge Graph
    await add_to_knowledge_graph(doc_id, result.data)

    # 7. Move email to processed label
    await gmail_service.move_to_label(email_id, "Flourisha/Processed")

    return ProcessingResult(document_id=doc_id, extraction=result.data)
```

### File Upload Ingestion

```python
@router.post("/documents/upload")
async def upload_document(
    file: UploadFile,
    tenant_id: str = "default",
    source_description: Optional[str] = None
) -> ProcessingResult:
    """API endpoint for document upload"""

    content = await file.read()

    result = await document_processor.run(
        f"Process this document. Source: {source_description or 'Direct upload'}",
        attachments=[content]
    )

    # ... same flow as Gmail
```

### Folder Watch Ingestion

```python
async def watch_folder(folder_path: str):
    """Watch a folder for new documents"""

    async for event in awatch(folder_path):
        for change_type, file_path in event:
            if change_type == Change.added and file_path.endswith('.pdf'):
                with open(file_path, 'rb') as f:
                    content = f.read()

                result = await document_processor.run(
                    f"Process this document from folder: {file_path}",
                    attachments=[content]
                )

                # ... same storage flow
```

## Supabase Integration

### Document Storage

```python
async def store_document(
    extraction: DocumentExtraction,
    matches: MatchingResult,
    supabase: SupabaseService
) -> str:
    """Store extracted document and link entities"""

    # 1. Create document record
    doc_record = {
        "docname": extraction.document_name,
        "doccategory": extraction.category.value,
        "aimatchsummary": extraction.summary,
        "humndocreviewstatus": "pending" if extraction.needs_human_review else "auto_approved",
        "humndocfeedback": extraction.review_reason,
        "tenant_id": "default"
    }

    doc = await supabase.insert("mrl_documents", doc_record)
    doc_id = doc["id"]

    # 2. Link or create companies
    for company_match in matches.company_matches:
        if company_match.matched_id:
            # Link existing
            await link_document_to_company(doc_id, company_match.matched_id)
        elif company_match.suggested_action == "create_new":
            # Create new company
            company = extraction.companies[...] # find by name
            new_company = await supabase.insert("mrl_companies", {...})
            await link_document_to_company(doc_id, new_company["id"])

    # 3. Similar for contacts, properties, agreements

    return doc_id
```

## Knowledge Graph Integration

```python
async def add_to_knowledge_graph(
    doc_id: str,
    extraction: DocumentExtraction,
    kg_service: KnowledgeGraphService
):
    """Add document and relationships to Neo4j via Graphiti"""

    # Build episode content
    content = f"""
    Document: {extraction.document_name}
    Category: {extraction.category.value}
    Summary: {extraction.summary}

    Companies involved: {[c.name for c in extraction.companies]}
    Contacts involved: {[c.full_name for c in extraction.contacts]}
    Properties: {[p.address for p in extraction.properties]}
    """

    await kg_service.add_episode(
        content_id=doc_id,
        tenant_id="default",
        title=extraction.document_name,
        content=content,
        summary=extraction.summary,
        source_description=f"Document: {extraction.category.value}"
    )
```

## File Structure

```
/root/flourisha/00_AI_Brain/
├── agents/
│   ├── __init__.py
│   ├── document_processor.py    # Main extraction agent
│   ├── entity_matcher.py        # Match to existing records
│   └── models.py                # Pydantic models
├── ingestion/
│   ├── __init__.py
│   ├── gmail_ingestion.py       # Gmail label watcher
│   ├── upload_handler.py        # API upload endpoint
│   └── folder_watcher.py        # Local folder monitoring
├── services/
│   ├── supabase_service.py      # (existing)
│   ├── knowledge_graph_service.py # (existing)
│   └── document_store.py        # Document storage logic
└── api/
    ├── __init__.py
    └── documents.py             # FastAPI routes
```

## Implementation Phases

### Phase 1: Core Agents
- [ ] Create Pydantic models (models.py)
- [ ] Implement document_processor agent
- [ ] Implement entity_matcher agent
- [ ] Unit tests with sample documents

### Phase 2: Storage Integration
- [ ] Document storage to Supabase (mrl_documents)
- [ ] Entity linking (companies, contacts, properties)
- [ ] Knowledge Graph integration via existing service

### Phase 3: Ingestion Sources
- [ ] Gmail label ingestion (extend existing gmail worker)
- [ ] API upload endpoint
- [ ] Folder watcher (optional)

### Phase 4: Notifications & App-Ready
- [ ] Processing status notifications
- [ ] Human review queue in Supabase
- [ ] API for frontend app to manage documents

## Dependencies

```toml
[project]
dependencies = [
    "pydantic-ai>=0.0.20",
    "anthropic>=0.40.0",
    "supabase>=2.0.0",
    "watchfiles>=0.21.0",  # For folder watching
]
```

## Configuration

```python
# config.py
DOCUMENT_PROCESSING_CONFIG = {
    "model": "claude-sonnet-4-20250514",  # Or claude-3-5-haiku for speed
    "max_retries": 3,
    "confidence_threshold": 0.7,  # Below this, mark for human review
    "auto_create_entities": True,  # Create new companies/contacts automatically
    "gmail_labels": {
        "unprocessed": "Flourisha/Unprocessed",
        "processed": "Flourisha/Processed",
        "failed": "Flourisha/Failed"
    }
}
```
