"""
Flourisha Document Intelligence Agents

Pydantic AI agents for document processing, entity extraction,
and relationship management.
"""

from .models import (
    DocumentCategory,
    ExtractedCompany,
    ExtractedContact,
    ExtractedProperty,
    ExtractedAgreement,
    FinancialDetails,
    DocumentExtraction,
    EntityMatch,
    MatchingResult,
    DocumentContext,
)
from .document_processor import (
    document_processor,
    get_document_processor,
    process_document,
    process_document_from_email,
    process_document_from_upload,
)
from .entity_matcher import (
    entity_matcher,
    get_entity_matcher,
    match_entities,
    match_single_company,
)

__all__ = [
    # Models
    "DocumentCategory",
    "ExtractedCompany",
    "ExtractedContact",
    "ExtractedProperty",
    "ExtractedAgreement",
    "FinancialDetails",
    "DocumentExtraction",
    "EntityMatch",
    "MatchingResult",
    "DocumentContext",
    # Document Processor
    "document_processor",
    "get_document_processor",
    "process_document",
    "process_document_from_email",
    "process_document_from_upload",
    # Entity Matcher
    "entity_matcher",
    "get_entity_matcher",
    "match_entities",
    "match_single_company",
]
