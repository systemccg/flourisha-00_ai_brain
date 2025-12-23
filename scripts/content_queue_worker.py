"""
Background Processing Queue Worker
Processes items from the processing_queue table
"""
import asyncio
import os
import sys
from typing import Optional, Dict, Any
from datetime import datetime
import traceback

# Add parent directory (00_AI_Brain) to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.supabase_client import supabase_service
from services.youtube_service import YouTubeService
from services.knowledge_graph_service import get_knowledge_graph
from services.embeddings_service import get_embeddings_service
from services.file_storage_service import get_file_storage
from agents.content_processor import ContentProcessorAgent
from models.content import ProcessingStatus


class QueueWorker:
    """
    Background worker that processes queue items
    Handles YouTube video processing, playlist monitoring, etc.
    """

    def __init__(self, poll_interval: int = 10):
        """
        Initialize queue worker

        Args:
            poll_interval: Seconds between queue checks
        """
        self.poll_interval = poll_interval
        self.supabase = supabase_service.supabase
        self.youtube = YouTubeService()
        self.kg = get_knowledge_graph()
        self.embeddings = get_embeddings_service()
        self.storage = get_file_storage()
        self.ai_processor = ContentProcessorAgent()
        self.running = False

    async def start(self):
        """Start the worker loop"""
        print(f"[QueueWorker] Starting worker (poll interval: {self.poll_interval}s)")
        self.running = True

        try:
            while self.running:
                await self._process_queue()
                await asyncio.sleep(self.poll_interval)
        except KeyboardInterrupt:
            print("[QueueWorker] Received shutdown signal")
        except Exception as e:
            print(f"[QueueWorker] Fatal error: {e}")
            traceback.print_exc()
        finally:
            await self.stop()

    async def stop(self):
        """Stop the worker"""
        print("[QueueWorker] Stopping worker")
        self.running = False
        await self.kg.close()

    async def _process_queue(self):
        """Process pending items from the queue"""
        try:
            # Get pending items (oldest first, max 10)
            result = await self.supabase.table('processing_queue').select('*').eq(
                'status', ProcessingStatus.PENDING.value
            ).order('scheduled_at').limit(10).execute()

            items = result.data if result.data else []

            if not items:
                return

            print(f"[QueueWorker] Processing {len(items)} queue items")

            for item in items:
                await self._process_item(item)

        except Exception as e:
            print(f"[QueueWorker] Error processing queue: {e}")
            traceback.print_exc()

    async def _process_item(self, item: Dict[str, Any]):
        """Process a single queue item"""
        item_id = item['id']
        source_type = item['source_type']
        source_id = item['source_id']
        tenant_id = item['tenant_id']

        print(f"[QueueWorker] Processing {source_type}: {source_id}")

        try:
            # Mark as processing
            await self.supabase.table('processing_queue').update({
                'status': ProcessingStatus.PROCESSING.value
            }).eq('id', item_id).execute()

            # Process based on source type
            if source_type == 'youtube_video':
                await self._process_youtube_video(item)
            elif source_type == 'youtube_playlist':
                await self._process_youtube_playlist(item)
            elif source_type == 'youtube_channel':
                await self._process_youtube_channel(item)
            else:
                raise ValueError(f"Unknown source type: {source_type}")

            # Mark as completed
            await self.supabase.table('processing_queue').update({
                'status': ProcessingStatus.COMPLETED.value,
                'processed_at': datetime.utcnow().isoformat()
            }).eq('id', item_id).execute()

            print(f"[QueueWorker] Completed {source_type}: {source_id}")

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"[QueueWorker] Error processing {source_type} {source_id}: {error_msg}")
            traceback.print_exc()

            # Increment retry count
            retry_count = item.get('retry_count', 0) + 1
            max_retries = 3

            if retry_count >= max_retries:
                # Mark as failed after max retries
                await self.supabase.table('processing_queue').update({
                    'status': ProcessingStatus.FAILED.value,
                    'error_message': error_msg,
                    'retry_count': retry_count
                }).eq('id', item_id).execute()
            else:
                # Reset to pending for retry
                await self.supabase.table('processing_queue').update({
                    'status': ProcessingStatus.PENDING.value,
                    'error_message': error_msg,
                    'retry_count': retry_count
                }).eq('id', item_id).execute()

    async def _process_youtube_video(self, item: Dict[str, Any]):
        """Process a single YouTube video"""
        video_id = item['source_id']
        tenant_id = item['tenant_id']
        tenant_user_id = item.get('tenant_user_id')
        project_id = item.get('project_id')

        # Get video details
        video_info = await self.youtube.get_video_info(video_id)
        transcript = await self.youtube.get_transcript(video_id)

        if not transcript:
            raise ValueError(f"No transcript available for video {video_id}")

        # Get project config if specified
        project_config = None
        if project_id:
            project_result = await self.supabase.table('projects').select('*').eq(
                'id', project_id
            ).eq('tenant_id', tenant_id).single().execute()
            project_config = project_result.data if project_result.data else None

        # Process with AI
        ai_result = await self.ai_processor.process_content(
            title=video_info['title'],
            transcript=transcript,
            content_type='video',
            project_name=project_config['name'] if project_config else None,
            tech_stack=project_config['tech_stack'] if project_config else None,
            context_replacements=project_config['context_replacements'] if project_config else None,
            metadata={
                'author': video_info.get('author'),
                'duration': video_info.get('duration'),
                'published_at': video_info.get('published_at')
            }
        )

        # Create content record
        content_data = {
            'tenant_id': tenant_id,
            'tenant_user_id': tenant_user_id,
            'created_by_user_id': tenant_user_id,
            'content_type': 'youtube_video',
            'title': video_info['title'],
            'source_url': f"https://www.youtube.com/watch?v={video_id}",
            'source_id': video_id,
            'transcript': transcript,
            'raw_metadata': video_info,
            'summary': ai_result.summary,
            'key_insights': ai_result.key_insights,
            'action_items': ai_result.action_items,
            'tags': ai_result.tags,
            'relevance_score': ai_result.relevance_score,
            'project_id': project_id,
            'visibility': project_config.get('default_visibility', 'private') if project_config else 'private'
        }

        content_result = await self.supabase.table('processed_content').insert(
            content_data
        ).execute()

        content_id = content_result.data[0]['id']

        # Store in knowledge graph
        await self.kg.add_episode(
            content_id=content_id,
            tenant_id=tenant_id,
            title=video_info['title'],
            content=transcript,
            summary=ai_result.summary,
            source_description=f"YouTube video by {video_info.get('author', 'Unknown')}"
        )

        # Generate and store embeddings
        embedding_text = f"{video_info['title']}\n\n{ai_result.summary}\n\n" + "\n".join(ai_result.key_insights)
        await self.embeddings.store_content_embedding(
            content_id=content_id,
            tenant_id=tenant_id,
            text=embedding_text
        )

        # Save as markdown file
        file_path = self.storage.save_content(
            content_id=content_id,
            title=video_info['title'],
            content_type='youtube_video',
            summary=ai_result.summary,
            key_insights=ai_result.key_insights,
            action_items=ai_result.action_items,
            tags=ai_result.tags,
            source_url=f"https://www.youtube.com/watch?v={video_id}",
            transcript=transcript,
            metadata=video_info,
            para_category='projects' if project_id else 'resources',
            project_name=project_config['name'] if project_config else None
        )

        # Update content with file path
        await self.supabase.table('processed_content').update({
            'file_path': file_path
        }).eq('id', content_id).execute()

        print(f"[QueueWorker] Saved content {content_id} to {file_path}")

    async def _process_youtube_playlist(self, item: Dict[str, Any]):
        """Process all videos in a YouTube playlist"""
        playlist_id = item['source_id']
        tenant_id = item['tenant_id']
        tenant_user_id = item.get('tenant_user_id')
        project_id = item.get('project_id')

        # Get playlist videos
        videos = await self.youtube.get_playlist_videos(playlist_id)

        print(f"[QueueWorker] Found {len(videos)} videos in playlist {playlist_id}")

        # Add each video to queue
        for video in videos:
            video_id = video['video_id']

            # Check if already processed
            existing = await self.supabase.table('processed_content').select('id').eq(
                'source_id', video_id
            ).eq('tenant_id', tenant_id).execute()

            if existing.data:
                print(f"[QueueWorker] Skipping already processed video: {video_id}")
                continue

            # Add to queue
            await self.supabase.table('processing_queue').insert({
                'tenant_id': tenant_id,
                'tenant_user_id': tenant_user_id,
                'source_type': 'youtube_video',
                'source_id': video_id,
                'project_id': project_id,
                'status': ProcessingStatus.PENDING.value,
                'scheduled_at': datetime.utcnow().isoformat()
            }).execute()

            print(f"[QueueWorker] Queued video: {video_id}")

    async def _process_youtube_channel(self, item: Dict[str, Any]):
        """Process recent videos from a YouTube channel"""
        channel_id = item['source_id']
        tenant_id = item['tenant_id']
        tenant_user_id = item.get('tenant_user_id')
        project_id = item.get('project_id')

        # Get channel videos (max 50 most recent)
        videos = await self.youtube.get_channel_videos(channel_id, max_results=50)

        print(f"[QueueWorker] Found {len(videos)} videos in channel {channel_id}")

        # Add each video to queue
        for video in videos:
            video_id = video['video_id']

            # Check if already processed
            existing = await self.supabase.table('processed_content').select('id').eq(
                'source_id', video_id
            ).eq('tenant_id', tenant_id).execute()

            if existing.data:
                continue

            # Add to queue
            await self.supabase.table('processing_queue').insert({
                'tenant_id': tenant_id,
                'tenant_user_id': tenant_user_id,
                'source_type': 'youtube_video',
                'source_id': video_id,
                'project_id': project_id,
                'status': ProcessingStatus.PENDING.value,
                'scheduled_at': datetime.utcnow().isoformat()
            }).execute()


async def main():
    """Main entry point for worker"""
    worker = QueueWorker(poll_interval=10)
    await worker.start()


if __name__ == "__main__":
    asyncio.run(main())
