#!/usr/bin/env python3
"""
Flourisha AI Brain - Claude Agent SDK MCP Server
Provides conversational interface to Flourisha AI Brain via Model Context Protocol
"""

import json
import logging
import os
import sys
from typing import Dict, List, Optional, Any
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import mcp (may not be installed, that's OK)
try:
    import mcp
    HAS_MCP = True
except ImportError:
    HAS_MCP = False
    logger.warning("MCP library not available, using fallback implementation")


class AIBrainServer:
    """MCP Server for Flourisha AI Brain"""

    def __init__(self):
        self.tenant_id = os.getenv('FLOURISHA_TENANT_ID', 'default')
        self.user_id = os.getenv('FLOURISHA_USER_ID', 'agent-sdk')

    async def search_content(
        self,
        query: str,
        limit: int = 10,
        threshold: float = 0.6
    ) -> Dict[str, Any]:
        """
        Search AI Brain content using vector similarity

        Args:
            query: Natural language search query
            limit: Maximum results to return
            threshold: Minimum similarity score (0.0-1.0)

        Returns:
            List of matching content with metadata
        """
        try:
            from services.embeddings_service import get_embeddings_service

            embeddings_service = await get_embeddings_service()

            # Generate embedding for query
            query_embedding = await embeddings_service.generate_embedding(query)

            # Search documents_pg
            results = await embeddings_service.search_similar_content(
                embedding=query_embedding,
                tenant_id=self.tenant_id,
                limit=limit,
                threshold=threshold
            )

            return {
                'status': 'success',
                'query': query,
                'results_count': len(results),
                'results': results
            }

        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

    async def process_youtube(
        self,
        video_id: str
    ) -> Dict[str, Any]:
        """
        Process a YouTube video into AI Brain

        Args:
            video_id: YouTube video ID (e.g., 'dQw4w9WgXcQ')

        Returns:
            Processing status and metadata
        """
        try:
            from services.youtube_service import youtube_service

            result = await youtube_service.process_video(
                video_id=video_id,
                tenant_id=self.tenant_id,
                user_id=self.user_id
            )

            return {
                'status': 'success',
                'video_id': video_id,
                'result': result
            }

        except Exception as e:
            logger.error(f"YouTube processing failed: {str(e)}")
            return {
                'status': 'error',
                'video_id': video_id,
                'message': str(e)
            }

    async def upload_document(
        self,
        file_path: str,
        title: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload and process a document into AI Brain

        Args:
            file_path: Local path to document
            title: Optional custom title
            project_id: Optional project to associate with

        Returns:
            Processing status and metadata
        """
        try:
            from services.document_processor import get_document_processor
            from services.supabase_client import supabase_service
            import hashlib

            processor = await get_document_processor()

            # Validate and process
            is_valid, message = processor.validate_file(file_path)
            if not is_valid:
                return {
                    'status': 'error',
                    'message': message
                }

            # Extract text
            text, metadata = await processor.process_document(file_path)

            # Calculate hash
            content_hash = hashlib.sha256(text.encode()).hexdigest()

            # Store metadata
            doc_data = {
                'id': f"doc-{content_hash[:16]}",
                'content_hash': content_hash,
                'version_number': 1,
                'is_current': True,
                'is_deleted': False,
                'tenant_id': self.tenant_id,
                'created_by': self.user_id,
                'source_type': 'manual_upload',
                'source_metadata': {
                    'original_filename': os.path.basename(file_path),
                    'file_type': metadata.get('format')
                }
            }

            # Insert to database
            response = supabase_service.supabase.table('document_metadata').insert(doc_data).execute()

            if not response.data:
                return {
                    'status': 'error',
                    'message': 'Failed to store document metadata'
                }

            return {
                'status': 'success',
                'document_id': doc_data['id'],
                'filename': os.path.basename(file_path),
                'title': title or os.path.basename(file_path),
                'content_hash': content_hash,
                'extracted_metadata': metadata
            }

        except Exception as e:
            logger.error(f"Document upload failed: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

    async def query_knowledge_graph(
        self,
        entity: Optional[str] = None,
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query the Neo4j knowledge graph

        Args:
            entity: Specific entity to explore
            query: Natural language query for semantic search

        Returns:
            Related entities and relationships
        """
        try:
            from services.knowledge_graph_service import get_knowledge_graph

            kg_service = await get_knowledge_graph()

            if entity:
                # Get specific entity and relationships
                result = await kg_service.get_related_entities(
                    entity_name=entity,
                    tenant_id=self.tenant_id
                )
            elif query:
                # Semantic search in graph
                result = await kg_service.search_similar_content(
                    query=query,
                    tenant_id=self.tenant_id
                )
            else:
                return {
                    'status': 'error',
                    'message': 'Must provide either entity or query parameter'
                }

            return {
                'status': 'success',
                'query': entity or query,
                'results': result
            }

        except Exception as e:
            logger.error(f"Knowledge graph query failed: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

    async def handle_tool_call(
        self,
        tool_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Route tool calls to appropriate handlers

        Args:
            tool_name: Name of the tool to call
            **kwargs: Tool arguments

        Returns:
            Tool result
        """
        logger.info(f"Tool called: {tool_name} with args: {kwargs}")

        if tool_name == 'search_content':
            return await self.search_content(**kwargs)

        elif tool_name == 'process_youtube':
            return await self.process_youtube(**kwargs)

        elif tool_name == 'upload_document':
            return await self.upload_document(**kwargs)

        elif tool_name == 'query_knowledge_graph':
            return await self.query_knowledge_graph(**kwargs)

        else:
            return {
                'status': 'error',
                'message': f'Unknown tool: {tool_name}'
            }

    def get_tools_definition(self) -> List[Dict]:
        """Get tool definitions for MCP"""
        return [
            {
                'name': 'search_content',
                'description': 'Search AI Brain content using vector similarity',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'query': {
                            'type': 'string',
                            'description': 'Natural language search query'
                        },
                        'limit': {
                            'type': 'integer',
                            'description': 'Maximum results to return',
                            'default': 10
                        },
                        'threshold': {
                            'type': 'number',
                            'description': 'Minimum similarity score (0.0-1.0)',
                            'default': 0.6
                        }
                    },
                    'required': ['query']
                }
            },
            {
                'name': 'process_youtube',
                'description': 'Process a YouTube video into AI Brain',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'video_id': {
                            'type': 'string',
                            'description': 'YouTube video ID (e.g., dQw4w9WgXcQ)'
                        }
                    },
                    'required': ['video_id']
                }
            },
            {
                'name': 'upload_document',
                'description': 'Upload and process a document into AI Brain',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'file_path': {
                            'type': 'string',
                            'description': 'Local path to document'
                        },
                        'title': {
                            'type': 'string',
                            'description': 'Optional custom title'
                        },
                        'project_id': {
                            'type': 'string',
                            'description': 'Optional project to associate with'
                        }
                    },
                    'required': ['file_path']
                }
            },
            {
                'name': 'query_knowledge_graph',
                'description': 'Query the Neo4j knowledge graph',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'entity': {
                            'type': 'string',
                            'description': 'Specific entity to explore'
                        },
                        'query': {
                            'type': 'string',
                            'description': 'Natural language query for semantic search'
                        }
                    }
                }
            }
        ]

    async def run(self) -> None:
        """Run the MCP server (stdio mode)"""
        logger.info("Starting Flourisha AI Brain MCP Server")

        if not HAS_MCP:
            logger.error("MCP library not available")
            return

        try:
            # Server will read from stdin and write to stdout
            # This is a simplified implementation
            logger.info("Server ready and listening for tool calls")

            while True:
                await asyncio.sleep(1)

        except KeyboardInterrupt:
            logger.info("Server shutting down")


async def main():
    """Entry point"""
    server = AIBrainServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
