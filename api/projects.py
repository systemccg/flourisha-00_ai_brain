"""
Projects API Router
CRUD operations for projects
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict
from datetime import datetime
import uuid

from models.content import (
    ProjectCreate,
    ProjectResponse,
    VisibilityLevel
)
from auth.middleware import get_current_user
from services.supabase_client import supabase_service

router = APIRouter()


@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects(
    user: Dict = Depends(get_current_user)
):
    """
    List all projects for the current user's tenant

    Requires: Authentication
    """
    tenant_id = user.get('tenant_id')
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tenant_id not found in user claims"
        )

    projects = await supabase_service.list_projects(tenant_id)
    return projects


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    user: Dict = Depends(get_current_user)
):
    """
    Get a specific project by ID

    Requires: Authentication, project must belong to user's tenant
    """
    tenant_id = user.get('tenant_id')
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tenant_id not found in user claims"
        )

    project = await supabase_service.get_project(project_id, tenant_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return project


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    user: Dict = Depends(get_current_user)
):
    """
    Create a new project

    Requires: Authentication
    """
    tenant_id = user.get('tenant_id')
    user_id = user.get('sub')

    if not tenant_id or not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tenant_id or user_id not found in user claims"
        )

    # Prepare project data
    project_data = {
        'id': str(uuid.uuid4()),
        'tenant_id': tenant_id,
        'name': project.name,
        'description': project.description,
        'tech_stack': project.tech_stack,
        'context_replacements': project.context_replacements,
        'default_visibility': project.default_visibility.value,
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }

    created_project = await supabase_service.create_project(project_data)

    if not created_project:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create project"
        )

    return created_project


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    updates: ProjectCreate,
    user: Dict = Depends(get_current_user)
):
    """
    Update a project

    Requires: Authentication, project must belong to user's tenant
    """
    tenant_id = user.get('tenant_id')
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tenant_id not found in user claims"
        )

    # Verify project exists
    existing_project = await supabase_service.get_project(project_id, tenant_id)
    if not existing_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Prepare updates
    update_data = {
        'name': updates.name,
        'description': updates.description,
        'tech_stack': updates.tech_stack,
        'context_replacements': updates.context_replacements,
        'default_visibility': updates.default_visibility.value,
        'updated_at': datetime.utcnow().isoformat()
    }

    updated_project = await supabase_service.update_project(project_id, tenant_id, update_data)

    if not updated_project:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update project"
        )

    return updated_project


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    user: Dict = Depends(get_current_user)
):
    """
    Delete a project

    Requires: Authentication, project must belong to user's tenant
    """
    tenant_id = user.get('tenant_id')
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tenant_id not found in user claims"
        )

    # Verify project exists
    existing_project = await supabase_service.get_project(project_id, tenant_id)
    if not existing_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    success = await supabase_service.delete_project(project_id, tenant_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project"
        )

    return None
