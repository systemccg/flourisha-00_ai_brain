"""
Custom Ontology for Flourisha Knowledge Graph

Defines entity types and relationship types for:
- Real Estate (properties, investments, rentals)
- Business (vendors, contacts, organizations)
- Personal (contacts, relationships)
- Financial (policies, accounts, transactions)

Based on Graphiti custom entity/edge types using Pydantic models.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


# =============================================================================
# ENTITY TYPES
# =============================================================================

class Person(BaseModel):
    """A person - contact, family member, business associate"""
    role: Optional[str] = Field(None, description="Role/title (e.g., 'Property Manager', 'Insurance Agent')")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    company: Optional[str] = Field(None, description="Company/organization they work for")
    relationship: Optional[str] = Field(None, description="Relationship to Greg (e.g., 'vendor', 'tenant', 'family')")


class Organization(BaseModel):
    """A company, business, or organization"""
    org_type: Optional[str] = Field(None, description="Type: 'vendor', 'client', 'government', 'financial_institution'")
    industry: Optional[str] = Field(None, description="Industry sector")
    website: Optional[str] = Field(None, description="Website URL")
    phone: Optional[str] = Field(None, description="Main phone number")
    address: Optional[str] = Field(None, description="Physical address")


class Property(BaseModel):
    """A real estate property"""
    property_type: Optional[str] = Field(None, description="Type: 'residential', 'commercial', 'land', 'multi_family'")
    address: Optional[str] = Field(None, description="Full street address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")
    zip_code: Optional[str] = Field(None, description="ZIP code")
    ownership_entity: Optional[str] = Field(None, description="LLC or entity that owns it")
    status: Optional[str] = Field(None, description="Status: 'owned', 'under_contract', 'sold', 'prospective'")


class InsurancePolicy(BaseModel):
    """An insurance policy"""
    policy_number: Optional[str] = Field(None, description="Policy number/ID")
    policy_type: Optional[str] = Field(None, description="Type: 'property', 'liability', 'auto', 'umbrella'")
    carrier: Optional[str] = Field(None, description="Insurance company name")
    premium: Optional[float] = Field(None, description="Annual premium amount")
    expiration_date: Optional[str] = Field(None, description="Policy expiration date")
    coverage_amount: Optional[float] = Field(None, description="Coverage limit")


class LegalEntity(BaseModel):
    """An LLC, corporation, or legal entity"""
    entity_type: Optional[str] = Field(None, description="Type: 'LLC', 'Corporation', 'Trust', 'Partnership'")
    state_of_formation: Optional[str] = Field(None, description="State where formed")
    ein: Optional[str] = Field(None, description="EIN/Tax ID (partial for security)")
    registered_agent: Optional[str] = Field(None, description="Registered agent name")
    purpose: Optional[str] = Field(None, description="Primary purpose/use")


class FinancialAccount(BaseModel):
    """A bank account, investment account, or financial instrument"""
    account_type: Optional[str] = Field(None, description="Type: 'checking', 'savings', 'investment', 'mortgage', 'credit'")
    institution: Optional[str] = Field(None, description="Bank/institution name")
    purpose: Optional[str] = Field(None, description="What this account is used for")


class Project(BaseModel):
    """A project or initiative"""
    project_type: Optional[str] = Field(None, description="Type: 'renovation', 'acquisition', 'development', 'maintenance'")
    status: Optional[str] = Field(None, description="Status: 'planning', 'in_progress', 'completed', 'on_hold'")
    budget: Optional[float] = Field(None, description="Budget amount")
    timeline: Optional[str] = Field(None, description="Expected timeline")


class Document(BaseModel):
    """A document, contract, or file"""
    doc_type: Optional[str] = Field(None, description="Type: 'contract', 'deed', 'invoice', 'report', 'correspondence'")
    date: Optional[str] = Field(None, description="Document date")
    parties: Optional[str] = Field(None, description="Parties involved")


class Event(BaseModel):
    """An event, meeting, or occurrence"""
    event_type: Optional[str] = Field(None, description="Type: 'meeting', 'deadline', 'payment_due', 'inspection'")
    date: Optional[str] = Field(None, description="Event date")
    location: Optional[str] = Field(None, description="Location if applicable")


class Location(BaseModel):
    """A geographic location"""
    location_type: Optional[str] = Field(None, description="Type: 'city', 'neighborhood', 'region', 'address'")
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State")
    country: Optional[str] = Field(None, description="Country")


# =============================================================================
# EDGE (RELATIONSHIP) TYPES
# =============================================================================

class OwnsRelationship(BaseModel):
    """Ownership relationship"""
    ownership_percentage: Optional[float] = Field(None, description="Percentage ownership")
    acquisition_date: Optional[str] = Field(None, description="When ownership began")


class ManagesRelationship(BaseModel):
    """Management relationship"""
    management_type: Optional[str] = Field(None, description="Type: 'property_manager', 'asset_manager', 'operations'")
    start_date: Optional[str] = Field(None, description="When management began")


class InsuresRelationship(BaseModel):
    """Insurance coverage relationship"""
    coverage_type: Optional[str] = Field(None, description="What is covered")
    policy_number: Optional[str] = Field(None, description="Associated policy number")


class WorksForRelationship(BaseModel):
    """Employment/contractor relationship"""
    role: Optional[str] = Field(None, description="Role/position")
    employment_type: Optional[str] = Field(None, description="Type: 'employee', 'contractor', 'consultant'")


class ProvidesServiceRelationship(BaseModel):
    """Vendor/service provider relationship"""
    service_type: Optional[str] = Field(None, description="Type of service provided")
    contract_status: Optional[str] = Field(None, description="Status: 'active', 'past', 'prospective'")


class LocatedAtRelationship(BaseModel):
    """Location relationship"""
    address: Optional[str] = Field(None, description="Specific address if applicable")


class PartyToRelationship(BaseModel):
    """Party to a document/contract"""
    party_role: Optional[str] = Field(None, description="Role: 'buyer', 'seller', 'lender', 'borrower', 'insured'")


# =============================================================================
# ONTOLOGY CONFIGURATION
# =============================================================================

# Entity types dictionary for Graphiti
ENTITY_TYPES = {
    "Person": Person,
    "Organization": Organization,
    "Property": Property,
    "InsurancePolicy": InsurancePolicy,
    "LegalEntity": LegalEntity,
    "FinancialAccount": FinancialAccount,
    "Project": Project,
    "Document": Document,
    "Event": Event,
    "Location": Location,
}

# Edge types dictionary for Graphiti
EDGE_TYPES = {
    "OWNS": OwnsRelationship,
    "MANAGES": ManagesRelationship,
    "INSURES": InsuresRelationship,
    "WORKS_FOR": WorksForRelationship,
    "PROVIDES_SERVICE": ProvidesServiceRelationship,
    "LOCATED_AT": LocatedAtRelationship,
    "PARTY_TO": PartyToRelationship,
}

# Edge type mapping - what relationships can exist between entity types
# Format: (SourceType, TargetType): [AllowedEdgeTypes]
EDGE_TYPE_MAP = {
    # Person relationships
    ("Person", "Organization"): ["WORKS_FOR", "OWNS"],
    ("Person", "Property"): ["OWNS", "MANAGES"],
    ("Person", "LegalEntity"): ["OWNS", "MANAGES"],
    ("Person", "Person"): ["WORKS_FOR", "MANAGES"],

    # Organization relationships
    ("Organization", "Property"): ["OWNS", "MANAGES", "PROVIDES_SERVICE"],
    ("Organization", "Organization"): ["PROVIDES_SERVICE", "OWNS"],
    ("Organization", "Person"): ["PROVIDES_SERVICE"],

    # LegalEntity relationships
    ("LegalEntity", "Property"): ["OWNS"],
    ("LegalEntity", "FinancialAccount"): ["OWNS"],
    ("LegalEntity", "LegalEntity"): ["OWNS"],

    # Insurance relationships
    ("InsurancePolicy", "Property"): ["INSURES"],
    ("InsurancePolicy", "LegalEntity"): ["INSURES"],
    ("InsurancePolicy", "Person"): ["INSURES"],
    ("Organization", "InsurancePolicy"): ["PROVIDES_SERVICE"],  # Carrier provides policy

    # Location relationships
    ("Property", "Location"): ["LOCATED_AT"],
    ("Organization", "Location"): ["LOCATED_AT"],

    # Document relationships
    ("Person", "Document"): ["PARTY_TO"],
    ("Organization", "Document"): ["PARTY_TO"],
    ("LegalEntity", "Document"): ["PARTY_TO"],
    ("Property", "Document"): ["PARTY_TO"],

    # Project relationships
    ("Project", "Property"): ["LOCATED_AT"],
    ("Person", "Project"): ["MANAGES", "WORKS_FOR"],
    ("Organization", "Project"): ["PROVIDES_SERVICE", "MANAGES"],
}


def get_ontology():
    """
    Get the complete ontology configuration for Graphiti.

    Returns:
        tuple: (entity_types, edge_types, edge_type_map)
    """
    return ENTITY_TYPES, EDGE_TYPES, EDGE_TYPE_MAP


# Standard ontology references for future expansion:
# - Schema.org: https://schema.org (general purpose)
# - RESO (Real Estate): https://www.reso.org/data-dictionary/
# - FIBO (Financial): https://spec.edmcouncil.org/fibo/
