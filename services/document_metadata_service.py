"""
Document Metadata Service
Manages document_metadata table (n8n RAG pattern)
High-level metadata for videos, notes, documents
"""
import os
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime
from .supabase_client import supabase_service


class DocumentMetadataService:
    """
    Service for managing document_metadata table
    Follows n8n RAG pattern for content tracking
    """

    def __init__(self):
        """Initialize metadata service"""
        self.supabase = supabase_service

    async def create_or_update_document(
        self,
        file_id: str,
        title: str,
        url: str,
        content_hash: str,
        tenant_id: str,
        user_id: str,
        document_type: str = 'youtube_video',
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create or update document metadata with version control (n8n pattern)

        Args:
            file_id: Unique file identifier (video_id, etc.)
            title: Document title
            url: Source URL
            content_hash: SHA-256 hash of content
            tenant_id: Tenant ID
            user_id: User ID
            document_type: Type of document
            metadata: Additional metadata

        Returns:
            Document metadata record
        """
        # Check if document exists with same content hash
        existing = await self.supabase.client.from_('document_metadata').select('*').eq(
            'id', file_id
        ).eq('is_current', True).maybe_single().execute()

        if existing.data and existing.data.get('content_hash') == content_hash:
            # Content unchanged - return existing
            return existing.data

        # Content changed or new document
        version_number = (existing.data['version_number'] + 1) if existing.data else 1

        # Mark old version as not current
        if existing.data:
            await self.supabase.client.from_('document_metadata').update({
                'is_current': False,
                'superseded_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', file_id).eq('is_current', True).execute()

        # Create new version
        document_data = {
            'id': file_id,
            'title': title,
            'url': url,
            'content_hash': content_hash,
            'tenant_id': tenant_id,
            'user_id': user_id,
            'created_by': user_id,
            'version_number': version_number,
            'is_current': True,
            'is_deleted': False,
            'document_type': document_type,
            'source': 'youtube' if document_type == 'youtube_video' else 'other',
            'processing_status': 'completed',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }

        # Add optional metadata fields
        if metadata:
            if 'mime_type' in metadata:
                document_data['mime_type'] = metadata['mime_type']
            if 'custom_tags' in metadata:
                document_data['custom_tags'] = metadata['custom_tags']

        result = await self.supabase.client.from_('document_metadata').insert(
            document_data
        ).execute()

        return result.data[0] if result.data else None

    async def get_document(
        self,
        file_id: str,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get current version of document

        Args:
            file_id: File identifier
            tenant_id: Tenant ID

        Returns:
            Document metadata or None
        """
        result = await self.supabase.client.from_('document_metadata').select('*').eq(
            'id', file_id
        ).eq('tenant_id', tenant_id).eq(
            'is_current', True
        ).eq('is_deleted', False).maybe_single().execute()

        return result.data

    async def soft_delete_document(
        self,
        file_id: str,
        tenant_id: str,
        deleted_by: str
    ) -> bool:
        """
        Soft delete document (n8n pattern)

        Args:
            file_id: File identifier
            tenant_id: Tenant ID
            deleted_by: User ID who deleted

        Returns:
            Success boolean
        """
        await self.supabase.client.from_('document_metadata').update({
            'is_deleted': True,
            'deleted_at': datetime.utcnow().isoformat(),
            'deleted_by': deleted_by,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', file_id).eq('tenant_id', tenant_id).execute()

        # Also soft delete associated chunks in documents_pg
        await self.supabase.client.from_('documents_pg').update({
            'is_deleted': True,
            'deleted_at': datetime.utcnow().isoformat(),
            'deleted_by': deleted_by
        }).eq('metadata->>file_id', file_id).eq('tenant_id', tenant_id).execute()

        return True

    async def list_documents(
        self,
        tenant_id: str,
        document_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> list:
        """
        List documents for tenant

        Args:
            tenant_id: Tenant ID
            document_type: Optional type filter
            limit: Max results
            offset: Pagination offset

        Returns:
            List of documents
        """
        query = self.supabase.client.from_('document_metadata').select('*').eq(
            'tenant_id', tenant_id
        ).eq('is_current', True).eq('is_deleted', False)

        if document_type:
            query = query.eq('document_type', document_type)

        result = query.order('created_at', desc=True).range(
            offset, offset + limit - 1
        ).execute()

        return result.data if result.data else []


# Singleton instance
_metadata_service = None


def get_metadata_service() -> DocumentMetadataService:
    """Get or create metadata service singleton"""
    global _metadata_service
    if _metadata_service is None:
        _metadata_service = DocumentMetadataService()
    return _metadata_service
