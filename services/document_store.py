"""
Document Store Service

Handles storing extracted documents and entities to Supabase,
with relationship management and Knowledge Graph integration.
"""

import os
import uuid
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
import logging

from agents.models import (
    DocumentExtraction,
    MatchingResult,
    EntityMatch,
    ExtractedCompany,
    ExtractedContact,
    ExtractedProperty,
)

logger = logging.getLogger(__name__)


def _generate_airtable_id(prefix: str = "rec") -> str:
    """Generate a placeholder airtable_id for new records."""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class DocumentStore:
    """
    Service for storing documents and entities to Supabase.
    Handles entity linking and relationship management.
    """

    def __init__(self, supabase_service=None, kg_service=None):
        """
        Initialize the document store.

        Args:
            supabase_service: Optional SupabaseService instance
            kg_service: Optional KnowledgeGraphService instance
        """
        self._supabase = supabase_service
        self._kg = kg_service

    @property
    def supabase(self):
        """Lazy load Supabase client"""
        if self._supabase is None:
            import os
            from supabase import create_client

            # Load env if not already loaded
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

    @property
    def kg(self):
        """Lazy load Knowledge Graph service"""
        if self._kg is None:
            from .knowledge_graph_service import get_knowledge_graph
            self._kg = get_knowledge_graph()
        return self._kg

    async def store_document(
        self,
        extraction: DocumentExtraction,
        matching: Optional[MatchingResult] = None,
        pdf_bytes: Optional[bytes] = None,
        tenant_id: str = "default",
    ) -> Dict[str, Any]:
        """
        Store an extracted document and its entities to Supabase.

        Args:
            extraction: The document extraction result
            matching: Optional entity matching result
            pdf_bytes: Optional PDF content for storage
            tenant_id: Tenant ID for multi-tenancy

        Returns:
            Dict with created document ID and linked entity IDs
        """
        result = {
            "document_id": None,
            "linked_companies": [],
            "linked_contacts": [],
            "linked_properties": [],
            "created_companies": [],
            "created_contacts": [],
            "created_properties": [],
        }

        # 1. Create the document record
        doc_record = self._build_document_record(extraction, tenant_id)
        doc_response = self.supabase.table("mrl_documents").insert(doc_record).execute()

        if doc_response.data:
            doc_id = doc_response.data[0]["id"]
            result["document_id"] = doc_id
            logger.info(f"Created document: {doc_id}")
        else:
            logger.error("Failed to create document record")
            return result

        # 2. Process companies
        for i, company in enumerate(extraction.companies):
            match = None
            if matching and i < len(matching.company_matches):
                match = matching.company_matches[i]

            company_id = await self._process_company(company, match, tenant_id)
            if company_id:
                if match and match.suggested_action == "link_existing":
                    result["linked_companies"].append(company_id)
                else:
                    result["created_companies"].append(company_id)

        # 3. Process contacts
        for i, contact in enumerate(extraction.contacts):
            match = None
            if matching and i < len(matching.contact_matches):
                match = matching.contact_matches[i]

            contact_id = await self._process_contact(contact, match, tenant_id)
            if contact_id:
                if match and match.suggested_action == "link_existing":
                    result["linked_contacts"].append(contact_id)
                else:
                    result["created_contacts"].append(contact_id)

        # 4. Process properties
        for i, prop in enumerate(extraction.properties):
            match = None
            if matching and i < len(matching.property_matches):
                match = matching.property_matches[i]

            prop_id = await self._process_property(prop, match, tenant_id)
            if prop_id:
                if match and match.suggested_action == "link_existing":
                    result["linked_properties"].append(prop_id)
                else:
                    result["created_properties"].append(prop_id)

        # 5. Process agreement if present
        if extraction.agreement:
            await self._process_agreement(extraction.agreement, doc_id, tenant_id)

        # 6. Add to Knowledge Graph
        try:
            await self._add_to_knowledge_graph(extraction, doc_id, tenant_id)
        except Exception as e:
            logger.warning(f"Failed to add to knowledge graph: {e}")

        return result

    def _build_document_record(
        self,
        extraction: DocumentExtraction,
        tenant_id: str,
    ) -> Dict[str, Any]:
        """Build a document record for Supabase"""
        record = {
            "airtable_id": _generate_airtable_id("doc"),
            "docname": extraction.document_name,
            "doccategory": extraction.category.value,
            "aimatchsummary": extraction.summary,
            "humndocreviewstatus": "pending" if extraction.needs_human_review else "auto_approved",
            "humndocfeedback": extraction.review_reason,
            "tenant_id": tenant_id,
            "sync_status": "local_only",
        }

        # Add dates if present
        if extraction.document_date:
            record["datedocissued"] = extraction.document_date.isoformat()
        if extraction.effective_date:
            record["datedoceffective"] = extraction.effective_date.isoformat()

        # Add primary entity references
        if extraction.primary_company:
            record["issuingcompanyname"] = extraction.primary_company
        if extraction.primary_contact:
            record["accountholdername"] = extraction.primary_contact
        if extraction.primary_property:
            record["propertyaddress"] = extraction.primary_property

        # Add financial details if present
        if extraction.financial:
            if extraction.financial.total_amount:
                record["totalbalance"] = extraction.financial.total_amount

        return record

    async def _process_company(
        self,
        company: ExtractedCompany,
        match: Optional[EntityMatch],
        tenant_id: str,
    ) -> Optional[str]:
        """Process and store/link a company"""
        if match and match.suggested_action == "link_existing" and match.matched_id:
            # Link to existing
            logger.info(f"Linking to existing company: {match.matched_id}")
            return match.matched_id

        if match and match.suggested_action == "needs_review":
            # Create but flag for review
            logger.info(f"Creating company (needs review): {company.name}")

        # Create new company - using actual mrl_companies schema
        record = {
            "airtable_id": _generate_airtable_id("comp"),
            "compname": company.name,
            "comptype": [company.company_type] if company.company_type else None,  # comptype is text[]
            "websiteurl": company.website,
            "streetaddress": company.address,
            "tenant_id": tenant_id,
            "sync_status": "local_only",
        }

        # Store phone/email in JSONB fields if available
        if company.phone:
            record["primaryphone"] = {"value": company.phone}
        if company.email:
            record["primaryemail"] = {"value": company.email}

        response = self.supabase.table("mrl_companies").insert(record).execute()
        if response.data:
            return response.data[0]["id"]
        return None

    async def _process_contact(
        self,
        contact: ExtractedContact,
        match: Optional[EntityMatch],
        tenant_id: str,
    ) -> Optional[str]:
        """Process and store/link a contact"""
        if match and match.suggested_action == "link_existing" and match.matched_id:
            logger.info(f"Linking to existing contact: {match.matched_id}")
            return match.matched_id

        # Create new contact - using actual mrl_contacts schema
        record = {
            "airtable_id": _generate_airtable_id("cont"),
            "firstname": contact.first_name,
            "lastname": contact.last_name,
            "email": contact.email,
            "phonenumber": contact.phone,
            "employmentrole": contact.title,
            "tenant_id": tenant_id,
            "sync_status": "local_only",
        }

        response = self.supabase.table("mrl_contacts").insert(record).execute()
        if response.data:
            return response.data[0]["id"]
        return None

    async def _process_property(
        self,
        prop: ExtractedProperty,
        match: Optional[EntityMatch],
        tenant_id: str,
    ) -> Optional[str]:
        """Process and store/link a property"""
        if match and match.suggested_action == "link_existing" and match.matched_id:
            logger.info(f"Linking to existing property: {match.matched_id}")
            return match.matched_id

        # Create new property - using actual mrl_properties schema
        # Generate a unique shorthand since it's required
        shorthand = f"NEW_{uuid.uuid4().hex[:6].upper()}"

        record = {
            "shorthand": shorthand,
            "full_address": prop.address,
            "street": prop.address,
            "city": prop.city,
            "state": prop.state,
            "zip": prop.zip_code,
            "property_type": prop.property_type or "residential",
            "tenant_id": tenant_id,
        }

        response = self.supabase.table("mrl_properties").insert(record).execute()
        if response.data:
            return response.data[0]["id"]
        return None

    async def _process_agreement(
        self,
        agreement,
        doc_id: str,
        tenant_id: str,
    ) -> Optional[str]:
        """Process and store an agreement"""
        record = {
            "airtable_id": _generate_airtable_id("agmt"),
            "agreementtype": agreement.agreement_type,
            "agreementtitle": agreement.title,
            "tenant_id": tenant_id,
            "sync_status": "local_only",
        }

        if agreement.effective_date:
            record["effectivedate"] = agreement.effective_date.isoformat()
        if agreement.expiration_date:
            record["expirationdate"] = agreement.expiration_date.isoformat()
        if agreement.value:
            record["agreementvalue"] = agreement.value

        response = self.supabase.table("mrl_agreements").insert(record).execute()
        if response.data:
            return response.data[0]["id"]
        return None

    async def _add_to_knowledge_graph(
        self,
        extraction: DocumentExtraction,
        doc_id: str,
        tenant_id: str,
    ):
        """Add document and entities to Knowledge Graph via Graphiti"""
        # Build content for the episode
        content_parts = [
            f"Document: {extraction.document_name}",
            f"Category: {extraction.category.value}",
            f"Summary: {extraction.summary}",
        ]

        if extraction.companies:
            companies = ", ".join(c.name for c in extraction.companies)
            content_parts.append(f"Companies: {companies}")

        if extraction.contacts:
            contacts = ", ".join(c.full_name for c in extraction.contacts)
            content_parts.append(f"Contacts: {contacts}")

        if extraction.properties:
            properties = ", ".join(p.address for p in extraction.properties)
            content_parts.append(f"Properties: {properties}")

        if extraction.agreement:
            content_parts.append(f"Agreement Type: {extraction.agreement.agreement_type}")
            if extraction.agreement.parties:
                content_parts.append(f"Parties: {', '.join(extraction.agreement.parties)}")

        content = "\n".join(content_parts)

        await self.kg.add_episode(
            content_id=doc_id,
            tenant_id=tenant_id,
            title=extraction.document_name,
            content=content,
            summary=extraction.summary,
            source_description=f"Document: {extraction.category.value}",
        )

    async def get_existing_entities(
        self,
        tenant_id: str = "default",
    ) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """
        Fetch existing entities from Supabase for matching.

        Returns:
            Tuple of (companies, contacts, properties)
        """
        # Use actual column names from mrl_companies schema
        companies = self.supabase.table("mrl_companies").select(
            "id, airtable_id, compname, comptype, websiteurl, streetaddress, city, stateregion, primaryphone, primaryemail"
        ).eq("tenant_id", tenant_id).execute()

        # Use actual column names from mrl_contacts schema
        contacts = self.supabase.table("mrl_contacts").select(
            "id, airtable_id, firstname, lastname, email, phonenumber"
        ).eq("tenant_id", tenant_id).execute()

        # Use actual column names from mrl_properties schema
        properties = self.supabase.table("mrl_properties").select(
            "id, shorthand, full_address, city, state, zip, aliases"
        ).eq("tenant_id", tenant_id).execute()

        return (
            companies.data or [],
            contacts.data or [],
            properties.data or [],
        )

    async def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID"""
        response = self.supabase.table("mrl_documents").select("*").eq("id", doc_id).execute()
        if response.data:
            return response.data[0]
        return None

    async def list_documents(
        self,
        tenant_id: str = "default",
        status: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """List documents with optional filters"""
        query = self.supabase.table("mrl_documents").select("*").eq("tenant_id", tenant_id)

        if status:
            query = query.eq("humndocreviewstatus", status)
        if category:
            query = query.eq("doccategory", category)

        query = query.order("created_at", desc=True).limit(limit)
        response = query.execute()

        return response.data or []

    async def update_document_status(
        self,
        doc_id: str,
        status: str,
        feedback: Optional[str] = None,
    ) -> bool:
        """Update document review status"""
        update_data = {"humndocreviewstatus": status}
        if feedback:
            update_data["humndocfeedback"] = feedback

        response = self.supabase.table("mrl_documents").update(update_data).eq("id", doc_id).execute()
        return bool(response.data)


# =============================================================================
# Singleton Instance
# =============================================================================

_document_store = None


def get_document_store() -> DocumentStore:
    """Get or create the document store singleton"""
    global _document_store
    if _document_store is None:
        _document_store = DocumentStore()
    return _document_store
