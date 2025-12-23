"""
Vector Embeddings Service using OpenAI + Supabase pgvector
Generates and stores embeddings for semantic search
"""
import os
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from .supabase_client import supabase_service


class EmbeddingsService:
    """
    Service for generating and storing vector embeddings
    Uses OpenAI for embeddings and Supabase pgvector for storage
    """

    _instance = None

    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize OpenAI client"""
        if self._initialized:
            return

        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")

        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = "text-embedding-3-small"  # 1536 dimensions, cost-effective
        self.supabase = supabase_service

        self._initialized = True

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text

        Args:
            text: Text to embed

        Returns:
            Embedding vector (1536 dimensions)
        """
        # Truncate if too long (max ~8000 tokens for embeddings)
        max_chars = 32000  # Roughly 8000 tokens
        if len(text) > max_chars:
            text = text[:max_chars]

        response = await self.client.embeddings.create(
            model=self.model,
            input=text
        )

        return response.data[0].embedding

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch processing)

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        # Truncate each text
        max_chars = 32000
        truncated_texts = [t[:max_chars] for t in texts]

        response = await self.client.embeddings.create(
            model=self.model,
            input=truncated_texts
        )

        return [item.embedding for item in response.data]

    async def store_content_embedding(
        self,
        content_id: str,
        tenant_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate and store embedding for content

        Args:
            content_id: Unique content identifier
            tenant_id: Tenant ID for isolation
            text: Text to embed (summary + key insights recommended)
            metadata: Additional metadata to store

        Returns:
            Vector ID (content_id)
        """
        # Generate embedding
        embedding = await self.generate_embedding(text)

        # Store in Supabase
        # Update the processed_content table with the embedding
        await self.supabase.table('processed_content').update({
            'embedding': embedding,
            'embedding_model': self.model,
            'embedding_text': text[:1000]  # Store first 1000 chars for reference
        }).eq('id', content_id).eq('tenant_id', tenant_id).execute()

        return content_id

    async def search_similar_content(
        self,
        query: str,
        tenant_id: str,
        limit: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for similar content using vector similarity

        Args:
            query: Search query
            tenant_id: Tenant ID for filtering
            limit: Maximum results to return
            similarity_threshold: Minimum similarity score (0-1)

        Returns:
            List of similar content with scores
        """
        # Generate query embedding
        query_embedding = await self.generate_embedding(query)

        # Supabase pgvector similarity search
        # Using RPC function for vector similarity (needs to be created)
        result = await self.supabase.rpc(
            'search_content_by_embedding',
            {
                'query_embedding': query_embedding,
                'match_tenant_id': tenant_id,
                'match_threshold': similarity_threshold,
                'match_count': limit
            }
        ).execute()

        return result.data if result.data else []

    async def get_content_neighbors(
        self,
        content_id: str,
        tenant_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get content pieces most similar to a given content

        Args:
            content_id: Content ID to find neighbors for
            tenant_id: Tenant ID
            limit: Number of neighbors to return

        Returns:
            List of similar content
        """
        # Get the content's embedding
        result = await self.supabase.table('processed_content').select('embedding, embedding_text').eq(
            'id', content_id
        ).eq('tenant_id', tenant_id).single().execute()

        if not result.data or not result.data.get('embedding'):
            return []

        # Use the embedding to find similar content
        return await self.search_similar_content(
            query=result.data['embedding_text'],
            tenant_id=tenant_id,
            limit=limit + 1  # +1 to exclude itself
        )

    async def create_embeddings_search_function(self):
        """
        Create the Postgres function for vector similarity search
        Should be run once during setup
        """
        sql = """
        CREATE OR REPLACE FUNCTION search_content_by_embedding(
            query_embedding vector(1536),
            match_tenant_id text,
            match_threshold float DEFAULT 0.7,
            match_count int DEFAULT 10
        )
        RETURNS TABLE (
            id text,
            title text,
            content_type text,
            summary text,
            tags text[],
            similarity float
        )
        LANGUAGE plpgsql
        AS $$
        BEGIN
            RETURN QUERY
            SELECT
                pc.id,
                pc.title,
                pc.content_type,
                pc.summary,
                pc.tags,
                1 - (pc.embedding <=> query_embedding) as similarity
            FROM processed_content pc
            WHERE pc.tenant_id = match_tenant_id
                AND pc.embedding IS NOT NULL
                AND 1 - (pc.embedding <=> query_embedding) > match_threshold
            ORDER BY pc.embedding <=> query_embedding
            LIMIT match_count;
        END;
        $$;
        """

        # Execute via Supabase SQL editor or migration
        # This is a setup function, not called during normal operation
        return sql


# Singleton instance
_embeddings_service = None


def get_embeddings_service() -> EmbeddingsService:
    """Get or create embeddings service singleton"""
    global _embeddings_service
    if _embeddings_service is None:
        _embeddings_service = EmbeddingsService()
    return _embeddings_service
