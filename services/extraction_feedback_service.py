"""
Extraction Feedback Service

Enables continuous improvement of document extraction through:
1. Human review queue - capture corrections
2. Few-shot examples - inject good examples into prompts
3. Automated validation - cross-check against known entities
"""

import os
import json
import logging
import re
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# =============================================================================
# Address Normalization
# =============================================================================

def normalize_address(address: str) -> str:
    """
    Normalize an address for comparison by standardizing formatting.

    Handles:
    - Extra whitespace
    - Comma placement (city state vs city, state)
    - Common abbreviations (Dr/Drive, St/Street, etc.)
    - Case normalization

    Examples:
        "133 Prince Charles Dr, Davenport FL 33837"
        "133 Prince Charles Dr, Davenport, FL 33837"
        Both normalize to: "133 prince charles dr davenport fl 33837"
    """
    if not address:
        return ""

    # Lowercase
    addr = address.lower().strip()

    # Remove all commas (they're inconsistent)
    addr = addr.replace(',', ' ')

    # Normalize common street abbreviations
    abbreviations = {
        r'\bdrive\b': 'dr',
        r'\bstreet\b': 'st',
        r'\bavenue\b': 'ave',
        r'\bboulevard\b': 'blvd',
        r'\broad\b': 'rd',
        r'\blane\b': 'ln',
        r'\bcourt\b': 'ct',
        r'\bcircle\b': 'cir',
        r'\bplace\b': 'pl',
        r'\bterrace\b': 'ter',
        r'\bhighway\b': 'hwy',
        r'\bapartment\b': 'apt',
        r'\bsuite\b': 'ste',
        r'\bnorth\b': 'n',
        r'\bsouth\b': 's',
        r'\beast\b': 'e',
        r'\bwest\b': 'w',
    }

    for pattern, replacement in abbreviations.items():
        addr = re.sub(pattern, replacement, addr)

    # Collapse multiple spaces to single space
    addr = re.sub(r'\s+', ' ', addr)

    return addr.strip()


def addresses_match(addr1: str, addr2: str, threshold: float = 0.9) -> bool:
    """
    Check if two addresses match after normalization.

    Uses normalized comparison first, then falls back to
    substring matching for partial matches.
    """
    norm1 = normalize_address(addr1)
    norm2 = normalize_address(addr2)

    # Exact match after normalization
    if norm1 == norm2:
        return True

    # One contains the other (for partial addresses)
    if norm1 in norm2 or norm2 in norm1:
        return True

    # Extract just the street number and name for core matching
    # e.g., "133 prince charles dr" from full address
    def extract_street(addr: str) -> str:
        # Take first 3-4 words (number + street name + type)
        words = addr.split()
        return ' '.join(words[:4]) if len(words) >= 4 else addr

    street1 = extract_street(norm1)
    street2 = extract_street(norm2)

    if street1 == street2:
        return True

    return False


@dataclass
class ValidationResult:
    """Result of a validation check"""
    rule_name: str
    passed: bool
    details: Dict[str, Any]
    severity: str
    suggestion: Optional[str] = None


@dataclass
class FeedbackCorrection:
    """A correction from human review"""
    field_name: str
    extracted_value: Any
    corrected_value: Any
    correction_type: str  # 'missing', 'incorrect', 'extra', 'wrong_field'
    notes: Optional[str] = None


class ExtractionFeedbackService:
    """
    Service for managing extraction feedback and continuous improvement.
    """

    def __init__(self, supabase_client=None):
        self._supabase = supabase_client
        self._examples_cache = None
        self._rules_cache = None

    @property
    def supabase(self):
        """Lazy load Supabase client"""
        if self._supabase is None:
            from supabase import create_client

            url = os.environ.get('SUPABASE_URL')
            key = os.environ.get('SUPABASE_SERVICE_KEY') or os.environ.get('SUPABASE_ANON_KEY')

            if not url or not key:
                env_file = os.path.expanduser("~/.claude/.env")
                if os.path.exists(env_file):
                    with open(env_file) as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith("#") and "=" in line:
                                k, v = line.split("=", 1)
                                os.environ[k] = v.strip('"').strip("'")
                    url = os.environ.get('SUPABASE_URL')
                    key = os.environ.get('SUPABASE_SERVICE_KEY') or os.environ.get('SUPABASE_ANON_KEY')

            self._supabase = create_client(url, key)
        return self._supabase

    # =========================================================================
    # Few-Shot Examples
    # =========================================================================

    def get_few_shot_examples(
        self,
        category: str,
        limit: int = 3,
        tenant_id: str = "default",
    ) -> List[Dict[str, Any]]:
        """
        Get few-shot examples for a document category to include in prompt.

        Args:
            category: Document category (insurance, financial, legal, etc.)
            limit: Maximum examples to return
            tenant_id: Tenant ID

        Returns:
            List of example dicts with document_description and expected_extraction
        """
        try:
            response = self.supabase.table("mrl_extraction_examples").select(
                "example_name, document_description, document_snippet, expected_extraction"
            ).eq("document_category", category).eq("is_active", True).eq(
                "tenant_id", tenant_id
            ).order("priority", desc=True).limit(limit).execute()

            return response.data or []
        except Exception as e:
            logger.warning(f"Could not fetch few-shot examples: {e}")
            return []

    def format_examples_for_prompt(self, examples: List[Dict]) -> str:
        """
        Format few-shot examples for inclusion in the system prompt.
        """
        if not examples:
            return ""

        formatted = "\n\n## Reference Examples\n\nHere are examples of correct extractions:\n"

        for i, ex in enumerate(examples, 1):
            formatted += f"\n### Example {i}: {ex.get('example_name', 'Unknown')}\n"
            formatted += f"**Document:** {ex.get('document_description', '')}\n"

            if ex.get('document_snippet'):
                formatted += f"**Key Text:** {ex['document_snippet'][:500]}...\n"

            extraction = ex.get('expected_extraction', {})
            formatted += f"**Correct Extraction:**\n```json\n{json.dumps(extraction, indent=2, default=str)[:1000]}\n```\n"

        return formatted

    def add_example(
        self,
        example_name: str,
        category: str,
        document_description: str,
        expected_extraction: Dict,
        document_snippet: Optional[str] = None,
        difficulty: str = "standard",
        priority: int = 50,
        tenant_id: str = "default",
    ) -> Optional[str]:
        """Add a new few-shot example"""
        record = {
            "example_name": example_name,
            "document_category": category,
            "document_description": document_description,
            "expected_extraction": expected_extraction,
            "document_snippet": document_snippet,
            "difficulty": difficulty,
            "priority": priority,
            "tenant_id": tenant_id,
        }

        try:
            response = self.supabase.table("mrl_extraction_examples").insert(record).execute()
            if response.data:
                return response.data[0]["id"]
        except Exception as e:
            logger.error(f"Failed to add example: {e}")
        return None

    # =========================================================================
    # Automated Validation
    # =========================================================================

    def validate_extraction(
        self,
        extraction: Dict[str, Any],
        resolved_property: Optional[Dict] = None,
        resolved_org: Optional[Dict] = None,
        tenant_id: str = "default",
    ) -> List[ValidationResult]:
        """
        Validate an extraction against known entities and rules.

        Args:
            extraction: The DocumentExtraction as dict
            resolved_property: Property resolved from filename (if any)
            resolved_org: Organization resolved from filename (if any)
            tenant_id: Tenant ID

        Returns:
            List of ValidationResult objects
        """
        results = []

        # 1. Check if extracted properties match known properties
        for prop in extraction.get('properties', []):
            result = self._validate_property_exists(prop, tenant_id)
            results.append(result)

        # 2. Check if resolved property matches extracted property
        if resolved_property and extraction.get('properties'):
            result = self._validate_resolved_matches_extracted(
                resolved_property,
                extraction['properties'],
                'property'
            )
            results.append(result)

        # 3. Check for missing insured party in insurance documents
        category = extraction.get('category', '')
        # Handle both enum and string values
        if hasattr(category, 'value'):
            category = category.value
        if category == 'insurance':
            result = self._validate_insured_party_extracted(extraction, tenant_id)
            results.append(result)

        # 4. Check if extracted companies match known companies
        for company in extraction.get('companies', []):
            result = self._validate_company_exists(company, tenant_id)
            results.append(result)

        return results

    def _validate_property_exists(
        self,
        extracted_property: Dict,
        tenant_id: str,
    ) -> ValidationResult:
        """Check if extracted property matches a known property"""
        address = extracted_property.get('address', '')

        try:
            # Search by address - extract street portion for matching
            address_street = address.split(',')[0].strip() if address else ''
            response = self.supabase.table("mrl_properties").select(
                "id, shorthand, full_address, aliases"
            ).ilike("full_address", f"%{address_street}%").eq("tenant_id", tenant_id).execute()

            if response.data:
                # Use address normalization for accurate matching
                for prop in response.data:
                    if addresses_match(address, prop['full_address']):
                        return ValidationResult(
                            rule_name="known_property_check",
                            passed=True,
                            details={
                                "extracted": address,
                                "matched_to": prop['full_address'],
                                "shorthand": prop['shorthand'],
                                "matched_via": "normalized_address"
                            },
                            severity="medium"
                        )
                # Partial match found but not exact after normalization
                matched = response.data[0]
                return ValidationResult(
                    rule_name="known_property_check",
                    passed=True,
                    details={
                        "extracted": address,
                        "matched_to": matched['full_address'],
                        "shorthand": matched['shorthand'],
                        "matched_via": "partial_street"
                    },
                    severity="medium"
                )
            else:
                return ValidationResult(
                    rule_name="known_property_check",
                    passed=False,
                    details={"extracted": address, "matched_to": None},
                    severity="medium",
                    suggestion=f"Property '{address}' not found in database. May be new or misspelled."
                )
        except Exception as e:
            logger.warning(f"Property validation error: {e}")
            return ValidationResult(
                rule_name="known_property_check",
                passed=True,  # Don't fail on error
                details={"error": str(e)},
                severity="low"
            )

    def _validate_company_exists(
        self,
        extracted_company: Dict,
        tenant_id: str,
    ) -> ValidationResult:
        """Check if extracted company matches a known company"""
        name = extracted_company.get('name', '')

        try:
            response = self.supabase.table("mrl_companies").select(
                "id, compname"
            ).ilike("compname", f"%{name}%").eq("tenant_id", tenant_id).execute()

            if response.data:
                return ValidationResult(
                    rule_name="known_company_check",
                    passed=True,
                    details={"extracted": name, "matched_to": response.data[0]['compname']},
                    severity="low"
                )
            else:
                return ValidationResult(
                    rule_name="known_company_check",
                    passed=False,
                    details={"extracted": name, "matched_to": None},
                    severity="low",
                    suggestion=f"Company '{name}' not in database. Will be created as new."
                )
        except Exception as e:
            return ValidationResult(
                rule_name="known_company_check",
                passed=True,
                details={"error": str(e)},
                severity="low"
            )

    def _validate_resolved_matches_extracted(
        self,
        resolved: Dict,
        extracted_list: List[Dict],
        entity_type: str,
    ) -> ValidationResult:
        """Check if filename-resolved entity matches what was extracted"""
        resolved_name = resolved.get('name', '') or resolved.get('full_address', '')

        # Check if any extracted entity matches the resolved one
        for extracted in extracted_list:
            extracted_name = extracted.get('address', '') or extracted.get('name', '')

            # For properties, use address normalization to handle formatting differences
            if entity_type == 'property':
                if addresses_match(resolved_name, extracted_name):
                    return ValidationResult(
                        rule_name=f"filename_{entity_type}_match",
                        passed=True,
                        details={
                            "resolved_from_filename": resolved_name,
                            "found_in_extraction": extracted_name,
                            "matched_via": "normalized_address"
                        },
                        severity="high"
                    )
            else:
                # For non-property entities, use simple substring matching
                if resolved_name.lower() in extracted_name.lower() or extracted_name.lower() in resolved_name.lower():
                    return ValidationResult(
                        rule_name=f"filename_{entity_type}_match",
                        passed=True,
                        details={
                            "resolved_from_filename": resolved_name,
                            "found_in_extraction": extracted_name
                        },
                        severity="high"
                    )

        return ValidationResult(
            rule_name=f"filename_{entity_type}_match",
            passed=False,
            details={
                "resolved_from_filename": resolved_name,
                "extracted_entities": [e.get('address') or e.get('name') for e in extracted_list]
            },
            severity="high",
            suggestion=f"Filename indicated {entity_type} '{resolved_name}' but extraction found different entities."
        )

    def _validate_insured_party_extracted(
        self,
        extraction: Dict,
        tenant_id: str,
    ) -> ValidationResult:
        """For insurance docs, check if insured party was extracted"""
        companies = extraction.get('companies', [])

        # Look for company with role 'insured' or type containing 'owner'
        for company in companies:
            role = (company.get('role_in_document') or '').lower()
            comp_type = (company.get('company_type') or '').lower()
            if 'insured' in role or 'owner' in comp_type or 'insured' in comp_type:
                return ValidationResult(
                    rule_name="insured_party_check",
                    passed=True,
                    details={"insured_party": company.get('name')},
                    severity="high"
                )

        # Check if we know properties and their owners
        properties = extraction.get('properties', [])
        if properties:
            # Try to find owner from our property database
            for prop in properties:
                addr = prop.get('address', '')
                try:
                    response = self.supabase.table("mrl_properties").select(
                        "owner"
                    ).ilike("full_address", f"%{addr}%").execute()

                    if response.data and response.data[0].get('owner'):
                        owner = response.data[0]['owner']
                        # Check if owner is in extracted companies
                        if not any(owner.lower() in c.get('name', '').lower() for c in companies):
                            return ValidationResult(
                                rule_name="insured_party_check",
                                passed=False,
                                details={
                                    "property": addr,
                                    "expected_owner": owner,
                                    "extracted_companies": [c.get('name') for c in companies]
                                },
                                severity="high",
                                suggestion=f"Property owner '{owner}' should be extracted as the insured party."
                            )
                except Exception:
                    pass

        return ValidationResult(
            rule_name="insured_party_check",
            passed=True,  # Can't determine, don't fail
            details={"note": "Could not verify insured party"},
            severity="medium"
        )

    # =========================================================================
    # Human Review & Corrections
    # =========================================================================

    def submit_correction(
        self,
        document_id: str,
        corrections: List[FeedbackCorrection],
        reviewed_by: str = "human",
        tenant_id: str = "default",
    ) -> bool:
        """
        Submit human corrections for an extraction.

        Args:
            document_id: The document UUID
            corrections: List of corrections
            reviewed_by: Who reviewed
            tenant_id: Tenant ID
        """
        records = []
        for correction in corrections:
            records.append({
                "document_id": document_id,
                "field_name": correction.field_name,
                "extracted_value": correction.extracted_value,
                "corrected_value": correction.corrected_value,
                "correction_type": correction.correction_type,
                "correction_notes": correction.notes,
                "reviewed_by": reviewed_by,
                "tenant_id": tenant_id,
            })

        try:
            self.supabase.table("mrl_extraction_feedback").insert(records).execute()

            # Update document status
            self.supabase.table("mrl_documents").update({
                "humndocreviewstatus": "reviewed"
            }).eq("id", document_id).execute()

            return True
        except Exception as e:
            logger.error(f"Failed to submit corrections: {e}")
            return False

    def get_review_queue(
        self,
        limit: int = 20,
        tenant_id: str = "default",
    ) -> List[Dict]:
        """Get documents needing human review"""
        try:
            response = self.supabase.table("mrl_documents").select(
                "id, docname, doccategory, aimatchsummary, humndocreviewstatus, created_at"
            ).in_("humndocreviewstatus", ["pending", "needs_review"]).eq(
                "tenant_id", tenant_id
            ).order("created_at", desc=True).limit(limit).execute()

            return response.data or []
        except Exception as e:
            logger.error(f"Failed to get review queue: {e}")
            return []

    def get_common_corrections(
        self,
        category: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict]:
        """
        Get most common corrections to identify systematic issues.
        Useful for improving prompts.
        """
        try:
            query = self.supabase.table("mrl_extraction_feedback").select(
                "field_name, correction_type, count"
            )
            # Note: This would need a proper aggregation query
            # For now, just return recent corrections
            response = self.supabase.table("mrl_extraction_feedback").select(
                "field_name, correction_type, correction_notes, corrected_value"
            ).order("created_at", desc=True).limit(limit).execute()

            return response.data or []
        except Exception as e:
            logger.error(f"Failed to get common corrections: {e}")
            return []

    def create_example_from_correction(
        self,
        document_id: str,
        example_name: str,
        tenant_id: str = "default",
    ) -> Optional[str]:
        """
        Create a few-shot example from a corrected document.
        This promotes good corrections to training examples.
        """
        try:
            # Get document and its corrections
            doc = self.supabase.table("mrl_documents").select("*").eq(
                "id", document_id
            ).single().execute()

            corrections = self.supabase.table("mrl_extraction_feedback").select("*").eq(
                "document_id", document_id
            ).execute()

            if not doc.data:
                return None

            # Build the "correct" extraction from original + corrections
            # This is simplified - real implementation would merge corrections
            expected = {
                "document_name": doc.data.get("docname"),
                "category": doc.data.get("doccategory"),
                "summary": doc.data.get("aimatchsummary"),
                # Add corrected entities...
            }

            return self.add_example(
                example_name=example_name,
                category=doc.data.get("doccategory", "general"),
                document_description=doc.data.get("aimatchsummary", ""),
                expected_extraction=expected,
                priority=70,  # Higher priority for human-verified examples
                tenant_id=tenant_id,
            )
        except Exception as e:
            logger.error(f"Failed to create example from correction: {e}")
            return None


# =============================================================================
# Singleton Instance
# =============================================================================

_feedback_service = None


def get_feedback_service() -> ExtractionFeedbackService:
    """Get or create the feedback service singleton"""
    global _feedback_service
    if _feedback_service is None:
        _feedback_service = ExtractionFeedbackService()
    return _feedback_service
