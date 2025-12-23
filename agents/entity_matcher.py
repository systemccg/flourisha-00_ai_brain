"""
Entity Matcher Agent

Pydantic AI agent for matching extracted entities against existing
database records. Determines whether to link to existing records
or create new ones.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel

from .models import (
    DocumentExtraction,
    ExtractedCompany,
    ExtractedContact,
    ExtractedProperty,
    EntityMatch,
    MatchingResult,
)


# =============================================================================
# System Prompt
# =============================================================================

ENTITY_MATCHER_SYSTEM_PROMPT = """You are an entity matching expert for Flourisha.
Your job is to match extracted entities from documents against existing database records.

## Your Task

For each extracted entity (company, contact, or property), determine:
1. Does it match an existing record in the database?
2. If so, how confident are you in the match?
3. What action should be taken?

## Matching Guidelines

### Companies
- Consider name variations: "ABC Corp", "ABC Corporation", "ABC Inc" may be same company
- Consider abbreviations: "International Business Machines" = "IBM"
- Consider DBA names: company may operate under different name
- Phone/email/address matches increase confidence significantly

### Contacts
- Consider name variations: "Bob Smith" may be "Robert Smith"
- Consider married names, name changes
- Email match is very strong indicator
- Phone match is strong indicator
- Same company + similar role increases confidence

### Properties
- Addresses must match substantially (allow for formatting differences)
- "123 Main St" = "123 Main Street" = "123 Main St."
- Unit/apartment numbers matter
- City + State must match

## Confidence Levels

- 0.95+: Definite match - same name AND matching contact info
- 0.85-0.95: Very likely match - same/very similar name, partial info matches
- 0.70-0.85: Likely match - similar name, context suggests same entity
- 0.50-0.70: Possible match - some similarity but uncertain, needs review
- Below 0.50: Probably different entity or new

## Actions

- "link_existing": Confidence >= 0.85, auto-link to existing record
- "create_new": Confidence < 0.50 AND no close matches, create new record
- "needs_review": Confidence 0.50-0.85, human should verify

## Important

- When in doubt, recommend "needs_review"
- Consider ALL provided existing records before deciding
- A new entity is fine - not everything will match existing records
- Provide clear reasoning in matched_name field for reviewers"""


# =============================================================================
# Input Models for Matching
# =============================================================================

class ExistingCompany(BaseModel):
    """Existing company record from database"""
    id: str
    name: str
    company_type: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None


class ExistingContact(BaseModel):
    """Existing contact record from database"""
    id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None


class ExistingProperty(BaseModel):
    """Existing property record from database"""
    id: str
    address: str
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None


class MatchingInput(BaseModel):
    """Input for entity matching"""
    extracted_companies: List[ExtractedCompany] = Field(default_factory=list)
    extracted_contacts: List[ExtractedContact] = Field(default_factory=list)
    extracted_properties: List[ExtractedProperty] = Field(default_factory=list)
    existing_companies: List[ExistingCompany] = Field(default_factory=list)
    existing_contacts: List[ExistingContact] = Field(default_factory=list)
    existing_properties: List[ExistingProperty] = Field(default_factory=list)


# =============================================================================
# Agent Definition (Lazy Initialization)
# =============================================================================

_entity_matcher = None


def get_entity_matcher() -> Agent:
    """Get or create the entity matcher agent (lazy initialization)."""
    global _entity_matcher
    if _entity_matcher is None:
        _entity_matcher = Agent(
            model=AnthropicModel('claude-sonnet-4-20250514'),
            output_type=MatchingResult,
            system_prompt=ENTITY_MATCHER_SYSTEM_PROMPT,
            retries=2,
        )
    return _entity_matcher


# Convenience alias for backward compatibility
entity_matcher = get_entity_matcher


# =============================================================================
# Matching Functions
# =============================================================================

async def match_entities(
    extraction: DocumentExtraction,
    existing_companies: List[Dict[str, Any]],
    existing_contacts: List[Dict[str, Any]],
    existing_properties: List[Dict[str, Any]],
) -> MatchingResult:
    """
    Match extracted entities against existing database records.

    Args:
        extraction: The document extraction result
        existing_companies: List of existing company records from Supabase
        existing_contacts: List of existing contact records from Supabase
        existing_properties: List of existing property records from Supabase

    Returns:
        MatchingResult with match decisions for each entity
    """
    # Convert to input format
    matching_input = MatchingInput(
        extracted_companies=extraction.companies,
        extracted_contacts=extraction.contacts,
        extracted_properties=extraction.properties,
        existing_companies=[
            ExistingCompany(
                id=str(c.get('id', c.get('airtable_id', ''))),
                name=c.get('compname', c.get('name', '')),
                company_type=c.get('comptype'),
                phone=c.get('compphone'),
                email=c.get('compemail'),
                website=c.get('websiteurl'),
                address=c.get('compaddress'),
            )
            for c in existing_companies if c.get('compname') or c.get('name')
        ],
        existing_contacts=[
            ExistingContact(
                id=str(c.get('id', c.get('airtable_id', ''))),
                first_name=c.get('contactfirstname'),
                last_name=c.get('contactlastname'),
                full_name=f"{c.get('contactfirstname', '')} {c.get('contactlastname', '')}".strip(),
                email=c.get('contactemail'),
                phone=c.get('contactphone'),
                company=c.get('compname'),
            )
            for c in existing_contacts
        ],
        existing_properties=[
            ExistingProperty(
                id=str(p.get('id', p.get('airtable_id', ''))),
                address=p.get('propertyaddress', p.get('address', '')),
                city=p.get('propertycity'),
                state=p.get('propertystate'),
                zip_code=p.get('propertyzip'),
            )
            for p in existing_properties if p.get('propertyaddress') or p.get('address')
        ],
    )

    # Build the prompt
    prompt = f"""Match these extracted entities against the existing database records.

## Extracted Entities from Document

### Companies ({len(matching_input.extracted_companies)})
{_format_extracted_companies(matching_input.extracted_companies)}

### Contacts ({len(matching_input.extracted_contacts)})
{_format_extracted_contacts(matching_input.extracted_contacts)}

### Properties ({len(matching_input.extracted_properties)})
{_format_extracted_properties(matching_input.extracted_properties)}

## Existing Database Records

### Companies ({len(matching_input.existing_companies)})
{_format_existing_companies(matching_input.existing_companies)}

### Contacts ({len(matching_input.existing_contacts)})
{_format_existing_contacts(matching_input.existing_contacts)}

### Properties ({len(matching_input.existing_properties)})
{_format_existing_properties(matching_input.existing_properties)}

For each extracted entity, determine if it matches an existing record and recommend an action."""

    agent = get_entity_matcher()
    result = await agent.run(prompt)

    # Calculate summary counts
    matching_result = result.output
    matching_result.auto_linkable = sum(
        1 for m in matching_result.company_matches + matching_result.contact_matches + matching_result.property_matches
        if m.suggested_action == "link_existing"
    )
    matching_result.needs_review = sum(
        1 for m in matching_result.company_matches + matching_result.contact_matches + matching_result.property_matches
        if m.suggested_action == "needs_review"
    )
    matching_result.new_entities = sum(
        1 for m in matching_result.company_matches + matching_result.contact_matches + matching_result.property_matches
        if m.suggested_action == "create_new"
    )

    return matching_result


async def match_single_company(
    company: ExtractedCompany,
    existing_companies: List[Dict[str, Any]],
) -> EntityMatch:
    """Match a single company against existing records"""
    extraction = DocumentExtraction(
        document_name="temp",
        category="other",
        summary="temp",
        companies=[company],
        extraction_confidence=1.0,
    )
    result = await match_entities(extraction, existing_companies, [], [])
    if result.company_matches:
        return result.company_matches[0]
    return EntityMatch(
        entity_type="company",
        extracted_name=company.name,
        match_confidence=0.0,
        is_new_entity=True,
        suggested_action="create_new",
    )


# =============================================================================
# Formatting Helpers
# =============================================================================

def _format_extracted_companies(companies: List[ExtractedCompany]) -> str:
    if not companies:
        return "(none)"
    lines = []
    for i, c in enumerate(companies, 1):
        parts = [f"{i}. {c.name}"]
        if c.company_type:
            parts.append(f"Type: {c.company_type}")
        if c.phone:
            parts.append(f"Phone: {c.phone}")
        if c.email:
            parts.append(f"Email: {c.email}")
        if c.role_in_document:
            parts.append(f"Role: {c.role_in_document}")
        lines.append(" | ".join(parts))
    return "\n".join(lines)


def _format_extracted_contacts(contacts: List[ExtractedContact]) -> str:
    if not contacts:
        return "(none)"
    lines = []
    for i, c in enumerate(contacts, 1):
        parts = [f"{i}. {c.full_name}"]
        if c.title:
            parts.append(f"Title: {c.title}")
        if c.company:
            parts.append(f"Company: {c.company}")
        if c.email:
            parts.append(f"Email: {c.email}")
        if c.phone:
            parts.append(f"Phone: {c.phone}")
        lines.append(" | ".join(parts))
    return "\n".join(lines)


def _format_extracted_properties(properties: List[ExtractedProperty]) -> str:
    if not properties:
        return "(none)"
    lines = []
    for i, p in enumerate(properties, 1):
        addr = p.address
        if p.city:
            addr += f", {p.city}"
        if p.state:
            addr += f", {p.state}"
        if p.zip_code:
            addr += f" {p.zip_code}"
        lines.append(f"{i}. {addr}")
    return "\n".join(lines)


def _format_existing_companies(companies: List[ExistingCompany]) -> str:
    if not companies:
        return "(none in database)"
    lines = []
    for c in companies[:50]:  # Limit to 50 for context window
        parts = [f"[{c.id[:8]}...] {c.name}"]
        if c.phone:
            parts.append(f"Phone: {c.phone}")
        if c.email:
            parts.append(f"Email: {c.email}")
        lines.append(" | ".join(parts))
    if len(companies) > 50:
        lines.append(f"... and {len(companies) - 50} more")
    return "\n".join(lines)


def _format_existing_contacts(contacts: List[ExistingContact]) -> str:
    if not contacts:
        return "(none in database)"
    lines = []
    for c in contacts[:50]:
        name = c.full_name or f"{c.first_name or ''} {c.last_name or ''}".strip()
        parts = [f"[{c.id[:8]}...] {name}"]
        if c.email:
            parts.append(f"Email: {c.email}")
        if c.company:
            parts.append(f"Company: {c.company}")
        lines.append(" | ".join(parts))
    if len(contacts) > 50:
        lines.append(f"... and {len(contacts) - 50} more")
    return "\n".join(lines)


def _format_existing_properties(properties: List[ExistingProperty]) -> str:
    if not properties:
        return "(none in database)"
    lines = []
    for p in properties[:50]:
        addr = p.address
        if p.city:
            addr += f", {p.city}"
        if p.state:
            addr += f", {p.state}"
        lines.append(f"[{p.id[:8]}...] {addr}")
    if len(properties) > 50:
        lines.append(f"... and {len(properties) - 50} more")
    return "\n".join(lines)
