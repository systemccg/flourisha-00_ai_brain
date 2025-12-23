"""
Entity Resolver Service

Resolves entity references (from documents, filenames, etc.) to known entities
using aliases, identifiers, and fuzzy matching.

This enables linking documents to properties, organizations, and contacts
even when they use shorthand names or variations.
"""

import os
import re
import logging
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ResolvedEntity:
    """Result of entity resolution"""
    entity_type: str  # 'property', 'organization', 'person'
    entity_id: str
    name: str
    matched_via: str  # 'alias', 'name', 'address', 'filename'
    confidence: float
    attributes: Dict[str, Any]


class EntityResolver:
    """
    Resolves entity references to known entities in Supabase.

    Uses multiple matching strategies:
    1. Exact alias match (highest confidence)
    2. Exact name match
    3. Partial address match (for properties)
    4. Filename parsing (for document shorthand convention)
    """

    def __init__(self, supabase_client=None):
        self._supabase = supabase_client
        self._property_cache = None
        self._org_cache = None

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

    def _load_properties(self) -> List[Dict]:
        """Load all properties with aliases"""
        if self._property_cache is None:
            result = self.supabase.table('mrl_properties').select('*').execute()
            self._property_cache = result.data or []
        return self._property_cache

    def _load_organizations(self) -> List[Dict]:
        """Load all organizations with aliases"""
        if self._org_cache is None:
            result = self.supabase.table('mrl_organizations').select('*').execute()
            self._org_cache = result.data or []
        return self._org_cache

    def invalidate_cache(self):
        """Clear cached entities (call after adding new entities)"""
        self._property_cache = None
        self._org_cache = None

    def resolve_property(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[ResolvedEntity]:
        """
        Resolve a property reference to a known property.

        Args:
            query: The property reference (shorthand, address, etc.)
            context: Optional context (e.g., filename, document content)

        Returns:
            ResolvedEntity if found, None otherwise
        """
        properties = self._load_properties()
        query_lower = query.lower().strip()

        # Strategy 1: Exact alias match
        for prop in properties:
            aliases = [a.lower() for a in (prop.get('aliases') or [])]
            if query_lower in aliases:
                return ResolvedEntity(
                    entity_type='property',
                    entity_id=prop['id'],
                    name=prop['full_address'],
                    matched_via='alias',
                    confidence=1.0,
                    attributes=prop,
                )

        # Strategy 2: Shorthand match
        for prop in properties:
            if prop.get('shorthand', '').lower() == query_lower:
                return ResolvedEntity(
                    entity_type='property',
                    entity_id=prop['id'],
                    name=prop['full_address'],
                    matched_via='shorthand',
                    confidence=1.0,
                    attributes=prop,
                )

        # Strategy 3: Address contains match
        for prop in properties:
            full_addr = (prop.get('full_address') or '').lower()
            street = (prop.get('street') or '').lower()

            # Check if query contains key address parts
            if query_lower in full_addr or full_addr in query_lower:
                return ResolvedEntity(
                    entity_type='property',
                    entity_id=prop['id'],
                    name=prop['full_address'],
                    matched_via='address',
                    confidence=0.9,
                    attributes=prop,
                )

            # Check street name
            if len(query_lower) > 3 and query_lower in street:
                return ResolvedEntity(
                    entity_type='property',
                    entity_id=prop['id'],
                    name=prop['full_address'],
                    matched_via='street',
                    confidence=0.8,
                    attributes=prop,
                )

        return None

    def resolve_organization(
        self,
        query: str,
        org_type: Optional[str] = None,
    ) -> Optional[ResolvedEntity]:
        """
        Resolve an organization reference to a known organization.

        Args:
            query: The organization name or alias
            org_type: Optional filter by type (owner, hoa, insurer, etc.)

        Returns:
            ResolvedEntity if found, None otherwise
        """
        organizations = self._load_organizations()
        query_lower = query.lower().strip()

        for org in organizations:
            # Filter by type if specified
            if org_type and org.get('organization_type') != org_type:
                continue

            # Check aliases
            aliases = [a.lower() for a in (org.get('aliases') or [])]
            if query_lower in aliases:
                return ResolvedEntity(
                    entity_type='organization',
                    entity_id=org['id'],
                    name=org['name'],
                    matched_via='alias',
                    confidence=1.0,
                    attributes=org,
                )

            # Check name
            if org.get('name', '').lower() == query_lower:
                return ResolvedEntity(
                    entity_type='organization',
                    entity_id=org['id'],
                    name=org['name'],
                    matched_via='name',
                    confidence=1.0,
                    attributes=org,
                )

            # Partial name match
            org_name = org.get('name', '').lower()
            if query_lower in org_name or org_name in query_lower:
                return ResolvedEntity(
                    entity_type='organization',
                    entity_id=org['id'],
                    name=org['name'],
                    matched_via='partial_name',
                    confidence=0.8,
                    attributes=org,
                )

        return None

    def parse_filename_convention(
        self,
        filename: str,
    ) -> Dict[str, Optional[str]]:
        """
        Parse the standard filename convention:
        {Company}_{PropertyShorthand}_{Description}_{YYYY-MM-DD}

        Args:
            filename: The document filename

        Returns:
            Dict with parsed components (company, property, description, date)
        """
        result = {
            'company': None,
            'property': None,
            'description': None,
            'date': None,
            'raw_filename': filename,
        }

        # Remove extension
        name = re.sub(r'\.[^.]+$', '', filename)

        # Split by underscore
        parts = name.split('_')

        if len(parts) >= 2:
            result['company'] = parts[0].strip()
            result['property'] = parts[1].strip()

        if len(parts) >= 3:
            # Check if last part is a date
            last_part = parts[-1].strip()
            date_match = re.match(r'(\d{4}-\d{2}-\d{2})', last_part)
            if date_match:
                result['date'] = date_match.group(1)
                # Description is everything between property and date
                if len(parts) >= 4:
                    result['description'] = '_'.join(parts[2:-1]).strip()
            else:
                # No date, description is everything after property
                result['description'] = '_'.join(parts[2:]).strip()

        return result

    def resolve_from_filename(
        self,
        filename: str,
    ) -> Tuple[Optional[ResolvedEntity], Optional[ResolvedEntity], Dict]:
        """
        Resolve entities from a filename using the standard convention.

        Args:
            filename: The document filename

        Returns:
            Tuple of (property, organization, parsed_components)
        """
        parsed = self.parse_filename_convention(filename)

        property_entity = None
        org_entity = None

        # Try to resolve property from shorthand
        if parsed['property']:
            property_entity = self.resolve_property(parsed['property'])

        # Try to resolve company
        if parsed['company']:
            org_entity = self.resolve_organization(parsed['company'])

        return property_entity, org_entity, parsed

    def resolve_all(
        self,
        query: str,
        entity_types: Optional[List[str]] = None,
    ) -> List[ResolvedEntity]:
        """
        Try to resolve a query against all entity types.

        Args:
            query: The search query
            entity_types: Optional list of types to search ('property', 'organization')

        Returns:
            List of all matching entities
        """
        results = []
        types = entity_types or ['property', 'organization']

        if 'property' in types:
            prop = self.resolve_property(query)
            if prop:
                results.append(prop)

        if 'organization' in types:
            org = self.resolve_organization(query)
            if org:
                results.append(org)

        return results


# =============================================================================
# Singleton Instance
# =============================================================================

_resolver = None


def get_entity_resolver() -> EntityResolver:
    """Get or create the entity resolver singleton"""
    global _resolver
    if _resolver is None:
        _resolver = EntityResolver()
    return _resolver


# =============================================================================
# Convenience Functions
# =============================================================================

def resolve_property(query: str) -> Optional[ResolvedEntity]:
    """Resolve a property reference"""
    return get_entity_resolver().resolve_property(query)


def resolve_organization(query: str) -> Optional[ResolvedEntity]:
    """Resolve an organization reference"""
    return get_entity_resolver().resolve_organization(query)


def resolve_from_filename(filename: str) -> Tuple[Optional[ResolvedEntity], Optional[ResolvedEntity], Dict]:
    """Resolve entities from filename convention"""
    return get_entity_resolver().resolve_from_filename(filename)
