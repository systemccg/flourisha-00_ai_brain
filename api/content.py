"""
Content API Router
Operations for processed content
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Optional
from datetime import datetime
import uuid

from models.content import (
    ProcessedContentCreate,
    ProcessedContentResponse,
    ContentType
)
from auth.middleware import get_current_user
from services.supabase_client import supabase_service

router = APIRouter()


@router.get("/content", response_model=List[ProcessedContentResponse])
async def list_content(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    content_type: Optional[ContentType] = Query(None, description="Filter by content type"),
    limit: int = Query(50, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    user: Dict = Depends(get_current_user)
):
    """
    List processed content for the current user's tenant

    Supports filtering by project and content type with pagination.

    Requires: Authentication
    """
    tenant_id = user.get('tenant_id')
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tenant_id not found in user claims"
        )

    content_type_str = content_type.value if content_type else None

    content_list = await supabase_service.list_content(
        tenant_id=tenant_id,
        project_id=project_id,
        content_type=content_type_str,
        limit=limit,
        offset=offset
    )

    return content_list


@router.get("/content/{content_id}", response_model=ProcessedContentResponse)
async def get_content(
    content_id: str,
    user: Dict = Depends(get_current_user)
):
    """
    Get a specific content item by ID

    Requires: Authentication
    Access: Respects RLS policies (visibility + shared_with)
    """
    user_id = user.get('sub')

    content = await supabase_service.get_content(content_id, user_id)

    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found or access denied"
        )

    return content


@router.post("/content", response_model=ProcessedContentResponse, status_code=status.HTTP_201_CREATED)
async def create_content(
    content: ProcessedContentCreate,
    user: Dict = Depends(get_current_user)
):
    """
    Create new processed content (manual upload)

    This is typically used for:
    - Manual content entry
    - Voice notes
    - Meeting transcripts

    YouTube content is usually created via the /youtube/process endpoint.

    Requires: Authentication
    """
    tenant_id = user.get('tenant_id')
    tenant_user_id = user.get('tenant_user_id')
    user_id = user.get('sub')

    if not all([tenant_id, tenant_user_id, user_id]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required user claims (tenant_id, tenant_user_id, sub)"
        )

    # Prepare content data
    content_data = {
        'id': str(uuid.uuid4()),
        'tenant_id': tenant_id,
        'tenant_user_id': tenant_user_id,
        'created_by_user_id': user_id,
        'title': content.title,
        'content_type': content.content_type.value,
        'source_url': str(content.source_url) if content.source_url else None,
        'source_id': content.source_id,
        'transcript': content.transcript,
        'raw_metadata': content.raw_metadata or {},
        'project_id': content.project_id,
        'visibility': content.visibility.value,
        'shared_with': content.shared_with,
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }

    created_content = await supabase_service.create_content(content_data)

    if not created_content:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create content"
        )

    return created_content


@router.put("/content/{content_id}/share", response_model=ProcessedContentResponse)
async def update_content_sharing(
    content_id: str,
    visibility: str = Query(..., description="Visibility level: private, group:X, tenant"),
    shared_with: List[str] = Query([], description="List of groups/users to share with"),
    user: Dict = Depends(get_current_user)
):
    """
    Update content sharing settings

    Examples:
    - Make private: visibility=private, shared_with=[]
    - Share with group: visibility=group, shared_with=['group:engineering']
    - Share with tenant: visibility=tenant, shared_with=[]
    - Share with specific user: visibility=private, shared_with=['user:joanna']

    Requires: Authentication, must be content creator
    """
    user_id = user.get('sub')

    # Get existing content
    content = await supabase_service.get_content(content_id, user_id)

    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )

    # Verify user is the creator
    if content.get('created_by_user_id') != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the content creator can modify sharing settings"
        )

    # Update sharing
    updates = {
        'visibility': visibility,
        'shared_with': shared_with,
        'updated_at': datetime.utcnow().isoformat()
    }

    updated_content = await supabase_service.update_content(content_id, updates)

    if not updated_content:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update content"
        )

    return updated_content


@router.delete("/content/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: str,
    user: Dict = Depends(get_current_user)
):
    """
    Delete content

    Requires: Authentication, must be content creator
    """
    user_id = user.get('sub')

    # Get existing content
    content = await supabase_service.get_content(content_id, user_id)

    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )

    # Verify user is the creator
    if content.get('created_by_user_id') != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the content creator can delete content"
        )

    # Delete content
    # Note: This should also clean up files, Neo4j nodes, and vector embeddings
    # TODO: Implement cascade delete for associated data

    await supabase_service.client.table('processed_content').delete().eq('id', content_id).execute()

    return None
