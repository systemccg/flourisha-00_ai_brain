"""
Pydantic Models for Document Intelligence System

These models define the structured outputs for document extraction
and entity matching. They map to the Supabase mrl_* tables.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from enum import Enum
from datetime import date


# =============================================================================
# Document Classification
# =============================================================================

class DocumentCategory(str, Enum):
    """Primary document categories"""
    CONTRACT = "contract"
    AGREEMENT = "agreement"
    INVOICE = "invoice"
    CORRESPONDENCE = "correspondence"
    LEGAL = "legal"
    FINANCIAL = "financial"
    INSURANCE = "insurance"
    PROPERTY = "property"
    IDENTIFICATION = "identification"
    TAX = "tax"
    REPORT = "report"
    APPLICATION = "application"
    OTHER = "other"


# =============================================================================
# Entity Models (map to Supabase mrl_* tables)
# =============================================================================

class ExtractedCompany(BaseModel):
    """
    Company or organization extracted from a document.
    Maps to: mrl_companies
    """
    name: str = Field(description="Company or organization name")
    company_type: Optional[str] = Field(
        None,
        description="Type: vendor, client, lender, insurer, government, etc."
    )
    phone: Optional[str] = Field(None, description="Phone number if found")
    email: Optional[str] = Field(None, description="Email address if found")
    website: Optional[str] = Field(None, description="Website URL if found")
    address: Optional[str] = Field(None, description="Physical address if found")
    role_in_document: Optional[str] = Field(
        None,
        description="Role in this document: issuer, recipient, party, servicer, etc."
    )


class ExtractedContact(BaseModel):
    """
    Person or contact extracted from a document.
    Maps to: mrl_contacts

    Note: For loan documents, distinguish between:
    - legal_entity_name: The vesting entity (LLC, Corp, Trust) that owns/purchases
    - full_name: The human contact person (may be different from legal entity)
    """
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    full_name: str = Field(description="Full name as it appears in document")
    legal_entity_name: Optional[str] = Field(
        None,
        description="Legal entity name if different from contact (e.g., 'Happy Housing LLC' when contact is 'John Smith')"
    )
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number in E.164 format (+12125551234)")
    title: Optional[str] = Field(None, description="Job title or role")
    company: Optional[str] = Field(None, description="Associated company name")
    role_in_document: Optional[str] = Field(
        None,
        description="Role in document: signer, recipient, author, witness, borrower, submitter, etc."
    )
    is_borrower: bool = Field(
        default=False,
        description="True if this contact is identified as the borrower/buyer"
    )
    is_submitter: bool = Field(
        default=False,
        description="True if this contact submitted the document (may differ from borrower)"
    )


class ExtractedProperty(BaseModel):
    """
    Real estate property extracted from a document.
    Maps to: mrl_properties
    """
    address: str = Field(description="Full street address")
    short_address: Optional[str] = Field(
        None,
        description="Short form: street number and name only (e.g., '1234 Main')"
    )
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State (2-letter code preferred)")
    zip_code: Optional[str] = Field(None, description="ZIP code")
    property_type: Optional[str] = Field(
        None,
        description="Type: residential, commercial, multi-family, land, etc."
    )


class ExtractedAgreement(BaseModel):
    """
    Agreement or contract details extracted from a document.
    Maps to: mrl_agreements
    """
    agreement_type: Optional[str] = Field(
        None,
        description="Type: lease, purchase, service, NDA, employment, loan, etc."
    )
    title: Optional[str] = Field(None, description="Agreement title if stated")
    parties: List[str] = Field(
        default_factory=list,
        description="Names of all parties to the agreement"
    )
    effective_date: Optional[date] = Field(None, description="When agreement takes effect")
    expiration_date: Optional[date] = Field(None, description="When agreement expires")
    execution_date: Optional[date] = Field(None, description="When agreement was signed")
    value: Optional[float] = Field(None, description="Contract/agreement value if stated")
    term: Optional[str] = Field(None, description="Duration/term of agreement")


class FinancialDetails(BaseModel):
    """Financial information extracted from a document"""
    total_amount: Optional[float] = Field(None, description="Primary amount/total")
    amounts: List[float] = Field(
        default_factory=list,
        description="All monetary amounts found"
    )
    account_numbers: List[str] = Field(
        default_factory=list,
        description="Account numbers (partial/masked OK)"
    )
    payment_due_date: Optional[date] = Field(None, description="Payment due date if found")
    currency: str = Field(default="USD", description="Currency code")


# =============================================================================
# Main Extraction Result
# =============================================================================

class DocumentExtraction(BaseModel):
    """
    Complete extraction result from a document.
    This is the main output of the document_processor agent.
    """
    # Classification
    document_name: str = Field(
        description="Suggested filename for this document (descriptive, no extension)"
    )
    category: DocumentCategory = Field(description="Primary document category")
    subcategory: Optional[str] = Field(
        None,
        description="More specific type within category (e.g., 'W-2' for tax)"
    )
    summary: str = Field(
        description="2-3 sentence summary of document content and purpose"
    )

    # Key Dates
    document_date: Optional[date] = Field(
        None,
        description="Date printed on the document"
    )
    effective_date: Optional[date] = Field(
        None,
        description="When document/agreement takes effect"
    )
    expiration_date: Optional[date] = Field(
        None,
        description="When document/agreement expires"
    )

    # Extracted Entities
    companies: List[ExtractedCompany] = Field(
        default_factory=list,
        description="All companies/organizations found in document"
    )
    contacts: List[ExtractedContact] = Field(
        default_factory=list,
        description="All people/contacts found in document"
    )
    properties: List[ExtractedProperty] = Field(
        default_factory=list,
        description="All real estate properties mentioned"
    )
    agreement: Optional[ExtractedAgreement] = Field(
        None,
        description="Agreement details if this is a contract/agreement"
    )
    financial: Optional[FinancialDetails] = Field(
        None,
        description="Financial details if this contains monetary information"
    )

    # Primary Relationships (for quick linking)
    primary_company: Optional[str] = Field(
        None,
        description="Main company this document is about or from"
    )
    primary_contact: Optional[str] = Field(
        None,
        description="Main person this document is about or from"
    )
    primary_property: Optional[str] = Field(
        None,
        description="Main property this document relates to"
    )

    # Processing Metadata
    extraction_confidence: float = Field(
        ge=0, le=1,
        description="Confidence in extraction accuracy (0-1)"
    )
    needs_human_review: bool = Field(
        default=False,
        description="Flag if document needs human review"
    )
    review_reason: Optional[str] = Field(
        None,
        description="Reason for human review if flagged"
    )
    source_type: Optional[str] = Field(
        None,
        description="How document was received: email, upload, folder, etc."
    )


# =============================================================================
# Entity Matching Models
# =============================================================================

class EntityMatch(BaseModel):
    """Result of matching an extracted entity to existing records"""
    entity_type: Literal["company", "contact", "property"] = Field(
        description="Type of entity being matched"
    )
    extracted_name: str = Field(description="Name as extracted from document")
    matched_id: Optional[str] = Field(
        None,
        description="Supabase record ID if matched to existing"
    )
    matched_name: Optional[str] = Field(
        None,
        description="Name of matched record (may differ slightly)"
    )
    match_confidence: float = Field(
        ge=0, le=1,
        description="Confidence in match (0.9+ = definite, 0.7-0.9 = likely, <0.7 = uncertain)"
    )
    is_new_entity: bool = Field(
        description="True if this appears to be a new entity not in database"
    )
    suggested_action: Literal["link_existing", "create_new", "needs_review"] = Field(
        description="Recommended action for this entity"
    )


class MatchingResult(BaseModel):
    """Complete result of entity matching against existing records"""
    company_matches: List[EntityMatch] = Field(
        default_factory=list,
        description="Matching results for all extracted companies"
    )
    contact_matches: List[EntityMatch] = Field(
        default_factory=list,
        description="Matching results for all extracted contacts"
    )
    property_matches: List[EntityMatch] = Field(
        default_factory=list,
        description="Matching results for all extracted properties"
    )
    auto_linkable: int = Field(
        default=0,
        description="Count of entities that can be auto-linked (high confidence)"
    )
    needs_review: int = Field(
        default=0,
        description="Count of entities needing human review"
    )
    new_entities: int = Field(
        default=0,
        description="Count of new entities to create"
    )


# =============================================================================
# Processing Context (passed to agents)
# =============================================================================

class DocumentContext(BaseModel):
    """Context information passed along with document for processing"""
    source: str = Field(description="Source: gmail, upload, folder, api")
    source_detail: Optional[str] = Field(
        None,
        description="Additional source info (email subject, folder path, etc.)"
    )
    tenant_id: str = Field(default="default", description="Tenant for multi-tenancy")
    sender_email: Optional[str] = Field(None, description="Email sender if from email")
    sender_name: Optional[str] = Field(None, description="Sender name if known")
    received_date: Optional[date] = Field(None, description="When document was received")
    original_filename: Optional[str] = Field(None, description="Original filename")
    file_size_bytes: Optional[int] = Field(None, description="File size")
    mime_type: Optional[str] = Field(None, description="MIME type of file")
