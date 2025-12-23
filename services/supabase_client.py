"""
Supabase Client Service
Centralized Supabase connection and operations
"""
import os
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/root/.claude/.env')


class SupabaseService:
    """Supabase client service for database operations"""

    _instance: Optional['SupabaseService'] = None
    _client: Optional[Client] = None

    def __new__(cls):
        """Singleton pattern to reuse connection"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize Supabase client"""
        if self._client is None:
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_SERVICE_KEY')  # Use service key for backend

            if not url or not key:
                raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")

            self._client = create_client(url, key)

    @property
    def client(self) -> Client:
        """Get Supabase client instance"""
        return self._client

    # Projects operations
    async def get_project(self, project_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get project by ID"""
        response = self.client.table('projects').select('*').eq('id', project_id).eq('tenant_id', tenant_id).single().execute()
        return response.data if response.data else None

    async def list_projects(self, tenant_id: str) -> List[Dict[str, Any]]:
        """List all projects for a tenant"""
        response = self.client.table('projects').select('*').eq('tenant_id', tenant_id).execute()
        return response.data if response.data else []

    async def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project"""
        response = self.client.table('projects').insert(project_data).execute()
        return response.data[0] if response.data else None

    async def update_project(self, project_id: str, tenant_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a project"""
        response = self.client.table('projects').update(updates).eq('id', project_id).eq('tenant_id', tenant_id).execute()
        return response.data[0] if response.data else None

    async def delete_project(self, project_id: str, tenant_id: str) -> bool:
        """Delete a project"""
        response = self.client.table('projects').delete().eq('id', project_id).eq('tenant_id', tenant_id).execute()
        return bool(response.data)

    # Processed content operations
    async def get_content(self, content_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get content by ID (respects RLS policies)"""
        response = self.client.table('processed_content').select('*').eq('id', content_id).execute()
        return response.data[0] if response.data else None

    async def list_content(
        self,
        tenant_id: str,
        project_id: Optional[str] = None,
        content_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List content with filters"""
        query = self.client.table('processed_content').select('*').eq('tenant_id', tenant_id)

        if project_id:
            query = query.eq('project_id', project_id)
        if content_type:
            query = query.eq('content_type', content_type)

        query = query.order('created_at', desc=True).limit(limit).offset(offset)
        response = query.execute()
        return response.data if response.data else []

    async def create_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create processed content"""
        response = self.client.table('processed_content').insert(content_data).execute()
        return response.data[0] if response.data else None

    async def update_content(self, content_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update content"""
        response = self.client.table('processed_content').update(updates).eq('id', content_id).execute()
        return response.data[0] if response.data else None

    # YouTube subscriptions
    async def create_youtube_subscription(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create YouTube playlist/channel subscription"""
        response = self.client.table('youtube_subscriptions').insert(subscription_data).execute()
        return response.data[0] if response.data else None

    async def list_youtube_subscriptions(self, tenant_id: str, source_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List YouTube subscriptions"""
        query = self.client.table('youtube_subscriptions').select('*').eq('tenant_id', tenant_id).eq('active', True)

        if source_type:
            query = query.eq('source_type', source_type)

        response = query.execute()
        return response.data if response.data else []

    async def get_youtube_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get YouTube subscription by ID"""
        response = self.client.table('youtube_subscriptions').select('*').eq('id', subscription_id).single().execute()
        return response.data if response.data else None

    async def delete_youtube_subscription(self, subscription_id: str, tenant_id: str) -> bool:
        """Delete YouTube subscription"""
        response = self.client.table('youtube_subscriptions').delete().eq('id', subscription_id).eq('tenant_id', tenant_id).execute()
        return bool(response.data)

    # Processing queue
    async def add_to_queue(self, queue_item: Dict[str, Any]) -> Dict[str, Any]:
        """Add item to processing queue"""
        response = self.client.table('processing_queue').insert(queue_item).execute()
        return response.data[0] if response.data else None

    async def get_pending_queue_items(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get pending items from processing queue"""
        response = self.client.table('processing_queue').select('*').eq('status', 'pending').order('scheduled_at').limit(limit).execute()
        return response.data if response.data else []

    async def update_queue_status(self, queue_id: str, status: str, error_message: Optional[str] = None) -> Dict[str, Any]:
        """Update processing queue item status"""
        updates = {'status': status}
        if error_message:
            updates['error_message'] = error_message
        if status == 'completed':
            updates['processed_at'] = 'now()'

        response = self.client.table('processing_queue').update(updates).eq('id', queue_id).execute()
        return response.data[0] if response.data else None


# Singleton instance
supabase_service = SupabaseService()
