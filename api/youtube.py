"""
YouTube API Router
YouTube playlist/channel subscriptions and content processing
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Dict
from datetime import datetime
import uuid

from models.content import (
    YouTubePlaylistSubscription,
    YouTubeChannelSubscription,
    ProcessedContentResponse
)
from auth.middleware import get_current_user
from services.supabase_client import supabase_service
from services.youtube_service import youtube_service
from services.knowledge_graph_service import get_knowledge_graph
from services.embeddings_service import get_embeddings_service
from services.file_storage_service import get_file_storage
from agents.content_processor import ContentProcessorAgent

router = APIRouter()


@router.post("/youtube/playlists/subscribe", status_code=status.HTTP_201_CREATED)
async def subscribe_to_playlist(
    subscription: YouTubePlaylistSubscription,
    user: Dict = Depends(get_current_user)
):
    """
    Subscribe to a YouTube playlist

    When subscribed, new videos added to this playlist will be automatically processed.

    Requires: Authentication
    """
    tenant_id = user.get('tenant_id')
    tenant_user_id = user.get('tenant_user_id')
    user_id = user.get('sub')

    if not all([tenant_id, tenant_user_id, user_id]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required user claims"
        )

    # Get playlist metadata
    try:
        playlist_meta = await youtube_service.get_playlist_metadata(subscription.playlist_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch playlist: {str(e)}"
        )

    # Create subscription
    subscription_data = {
        'id': str(uuid.uuid4()),
        'tenant_id': tenant_id,
        'tenant_user_id': tenant_user_id,
        'source_type': 'youtube_playlist',
        'source_id': subscription.playlist_id,
        'source_name': subscription.playlist_name or playlist_meta['title'],
        'project_id': subscription.project_id,
        'auto_process': subscription.auto_process,
        'active': True,
        'metadata': playlist_meta,
        'created_at': datetime.utcnow().isoformat(),
        'last_checked_at': datetime.utcnow().isoformat()
    }

    created_subscription = await supabase_service.create_youtube_subscription(subscription_data)

    if not created_subscription:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create subscription"
        )

    return created_subscription


@router.post("/youtube/channels/subscribe", status_code=status.HTTP_201_CREATED)
async def subscribe_to_channel(
    subscription: YouTubeChannelSubscription,
    user: Dict = Depends(get_current_user)
):
    """
    Subscribe to a YouTube channel

    When subscribed, new videos from this channel will be automatically processed.

    Requires: Authentication
    """
    tenant_id = user.get('tenant_id')
    tenant_user_id = user.get('tenant_user_id')
    user_id = user.get('sub')

    if not all([tenant_id, tenant_user_id, user_id]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required user claims"
        )

    # Create subscription
    subscription_data = {
        'id': str(uuid.uuid4()),
        'tenant_id': tenant_id,
        'tenant_user_id': tenant_user_id,
        'source_type': 'youtube_channel',
        'source_id': subscription.channel_id,
        'source_name': subscription.channel_name or subscription.channel_id,
        'project_id': subscription.project_id,
        'auto_process': subscription.auto_process,
        'active': True,
        'metadata': {'channel_id': subscription.channel_id},
        'created_at': datetime.utcnow().isoformat(),
        'last_checked_at': datetime.utcnow().isoformat()
    }

    created_subscription = await supabase_service.create_youtube_subscription(subscription_data)

    if not created_subscription:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create subscription"
        )

    return created_subscription


@router.get("/youtube/subscriptions")
async def list_youtube_subscriptions(
    source_type: str = None,
    user: Dict = Depends(get_current_user)
):
    """
    List all YouTube subscriptions

    Optionally filter by source_type (youtube_playlist or youtube_channel)

    Requires: Authentication
    """
    tenant_id = user.get('tenant_id')

    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tenant_id not found in user claims"
        )

    subscriptions = await supabase_service.list_youtube_subscriptions(
        tenant_id=tenant_id,
        source_type=source_type
    )

    return subscriptions


@router.delete("/youtube/subscriptions/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unsubscribe(
    subscription_id: str,
    user: Dict = Depends(get_current_user)
):
    """
    Unsubscribe from a YouTube playlist or channel

    Requires: Authentication
    """
    tenant_id = user.get('tenant_id')

    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tenant_id not found in user claims"
        )

    # Verify subscription exists
    subscription = await supabase_service.get_youtube_subscription(subscription_id)

    if not subscription or subscription.get('tenant_id') != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    # Delete subscription
    success = await supabase_service.delete_youtube_subscription(subscription_id, tenant_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete subscription"
        )

    return None


@router.post("/youtube/process/{video_id}", response_model=ProcessedContentResponse)
async def process_youtube_video(
    video_id: str,
    project_id: str = None,
    background_tasks: BackgroundTasks = None,
    user: Dict = Depends(get_current_user)
):
    """
    Process a single YouTube video

    This endpoint:
    1. Fetches video metadata
    2. Retrieves transcript
    3. Processes content with AI (context-aware if project specified)
    4. Stores in database + Neo4j + Vector DB

    Requires: Authentication
    """
    tenant_id = user.get('tenant_id')
    tenant_user_id = user.get('tenant_user_id')
    user_id = user.get('sub')

    if not all([tenant_id, tenant_user_id, user_id]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required user claims"
        )

    try:
        # 1. Get video metadata
        metadata = await youtube_service.get_video_metadata(video_id)

        # 2. Get transcript
        transcript = await youtube_service.get_video_transcript(video_id)

        if not transcript:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No transcript available for this video"
            )

        # 3. Get project config (if specified)
        project_config = None
        if project_id:
            project = await supabase_service.get_project(project_id, tenant_id)
            if project:
                project_config = {
                    'name': project['name'],
                    'tech_stack': project['tech_stack'],
                    'context_replacements': project['context_replacements']
                }

        # 4. Process with AI
        processor = ContentProcessorAgent()
        ai_output = await processor.process_content(
            title=metadata['title'],
            transcript=transcript,
            content_type="video",
            project_name=project_config['name'] if project_config else None,
            tech_stack=project_config['tech_stack'] if project_config else None,
            context_replacements=project_config['context_replacements'] if project_config else None,
            metadata={
                'channel': metadata['channel_title'],
                'duration': metadata['duration'],
                'published': metadata['published_at']
            }
        )

        # 5. Store in database
        content_data = {
            'id': str(uuid.uuid4()),
            'tenant_id': tenant_id,
            'tenant_user_id': tenant_user_id,
            'created_by_user_id': user_id,
            'title': metadata['title'],
            'content_type': 'youtube_video',
            'source_url': f"https://youtube.com/watch?v={video_id}",
            'source_id': video_id,
            'transcript': transcript,
            'raw_metadata': metadata,
            'project_id': project_id,
            'summary': ai_output.summary,
            'key_insights': ai_output.key_insights,
            'action_items': ai_output.action_items,
            'tags': ai_output.tags,
            'relevance_score': ai_output.relevance_score,
            'visibility': 'private',
            'shared_with': [],
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }

        created_content = await supabase_service.create_content(content_data)

        if not created_content:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create content"
            )

        content_id = created_content['id']

        # Store in Neo4j knowledge graph (background task)
        if background_tasks:
            kg = get_knowledge_graph()
            background_tasks.add_task(
                kg.add_episode,
                content_id=content_id,
                tenant_id=tenant_id,
                title=metadata['title'],
                content=transcript,
                summary=ai_output.summary,
                source_description=f"YouTube video by {metadata['channel_title']}"
            )

        # Generate and store embeddings (background task)
        if background_tasks:
            embeddings = get_embeddings_service()
            embedding_text = f"{metadata['title']}\n\n{ai_output.summary}\n\n" + "\n".join(ai_output.key_insights)
            background_tasks.add_task(
                embeddings.store_content_embedding,
                content_id=content_id,
                tenant_id=tenant_id,
                text=embedding_text
            )

        # Save markdown file to PARA structure (background task)
        if background_tasks:
            storage = get_file_storage()
            background_tasks.add_task(
                storage.save_content,
                content_id=content_id,
                title=metadata['title'],
                content_type='youtube_video',
                summary=ai_output.summary,
                key_insights=ai_output.key_insights,
                action_items=ai_output.action_items,
                tags=ai_output.tags,
                source_url=f"https://youtube.com/watch?v={video_id}",
                transcript=transcript,
                metadata=metadata,
                para_category='projects' if project_id else 'resources',
                project_name=project_config['name'] if project_config else None
            )

        return created_content

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing failed: {str(e)}"
        )
