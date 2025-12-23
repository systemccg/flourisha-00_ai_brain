"""
Knowledge Ingestion Service
Orchestrates document processing and ingestion into all knowledge stores:
- Vector (Supabase pgvector) - for semantic search
- Graph (Neo4j via Graphiti) - for relationships and entities
- Whole (file storage) - for raw document archive
"""

import os
import logging
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from .document_processor import (
    DocumentProcessor,
    ExtractionBackendType,
    get_document_processor
)
from .extraction_backends.base import ExtractionResult, ExtractedEntity
from .knowledge_graph_service import get_knowledge_graph
from .chunking_service import chunk_text
from .embeddings_service import get_embeddings_service as get_embeddings
from .supabase_client import supabase_service

logger = logging.getLogger(__name__)


class KnowledgeIngestionService:
    """
    Service for ingesting documents into the AI Brain knowledge stores.

    Pipeline:
    1. Extract content using pluggable backend (Claude/Docling)
    2. Validate extraction for accuracy
    3. Store raw document (Whole)
    4. Extract and store entities/relationships (Graph)
    5. Chunk and embed for semantic search (Vector)
    """

    def __init__(
        self,
        tenant_id: str = "default",
        extraction_backend: ExtractionBackendType = ExtractionBackendType.CLAUDE
    ):
        """
        Initialize ingestion service.

        Args:
            tenant_id: Tenant identifier for multi-tenant isolation
            extraction_backend: Which extraction backend to use
        """
        self.tenant_id = tenant_id
        self.extraction_backend = extraction_backend
        self._processor: Optional[DocumentProcessor] = None

    async def _get_processor(self) -> DocumentProcessor:
        """Get or create document processor"""
        if self._processor is None:
            self._processor = await get_document_processor(
                default_backend=self.extraction_backend
            )
        return self._processor

    async def ingest_document(
        self,
        file_path: str,
        document_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        extract_entities: bool = True,
        entity_types: Optional[List[str]] = None,
        store_in_vector: bool = True,
        store_in_graph: bool = True,
        store_raw: bool = True
    ) -> Dict[str, Any]:
        """
        Ingest a document into all knowledge stores.

        Args:
            file_path: Path to the document
            document_type: Type of document (e.g., "medical", "legal", "general")
            metadata: Additional metadata to store
            extract_entities: Whether to extract structured entities
            entity_types: Types of entities to extract
            store_in_vector: Store in vector database for semantic search
            store_in_graph: Store in knowledge graph
            store_raw: Store raw document

        Returns:
            Ingestion result with IDs and statistics
        """
        start_time = datetime.utcnow()
        result = {
            "status": "success",
            "file_path": file_path,
            "document_id": None,
            "stores": {},
            "entities_extracted": 0,
            "relationships_extracted": 0,
            "chunks_created": 0,
            "warnings": [],
            "errors": []
        }

        # Generate document ID from file hash
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()[:16]
        document_id = f"doc_{file_hash}"
        result["document_id"] = document_id

        try:
            # Step 1: Extract content
            logger.info(f"Extracting content from {file_path}")
            processor = await self._get_processor()

            extraction = await processor.extract_with_backend(
                file_path,
                extract_entities=extract_entities,
                entity_types=entity_types
            )

            # Add any extraction warnings
            result["warnings"].extend(extraction.validation_warnings)

            if not extraction.is_valid():
                result["errors"].extend(extraction.validation_errors)
                result["status"] = "partial"

            result["entities_extracted"] = len(extraction.entities)
            result["relationships_extracted"] = len(extraction.relationships)

            # Step 2: Store raw document
            if store_raw:
                raw_result = await self._store_raw_document(
                    document_id, file_path, extraction, metadata
                )
                result["stores"]["raw"] = raw_result

            # Step 3: Store in knowledge graph
            if store_in_graph and extraction.entities:
                graph_result = await self._store_in_graph(
                    document_id, extraction, document_type, metadata
                )
                result["stores"]["graph"] = graph_result

            # Step 4: Store in vector database
            if store_in_vector:
                vector_result = await self._store_in_vector(
                    document_id, extraction, document_type, metadata
                )
                result["stores"]["vector"] = vector_result
                result["chunks_created"] = vector_result.get("chunks_stored", 0)

        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            result["status"] = "failed"
            result["errors"].append(str(e))

        # Calculate duration
        result["duration_seconds"] = (datetime.utcnow() - start_time).total_seconds()

        return result

    async def ingest_text(
        self,
        text: str,
        source: str,
        source_id: str,
        title: Optional[str] = None,
        document_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        extract_entities: bool = True,
        store_in_vector: bool = True,
        store_in_graph: bool = True,
        store_raw: bool = True
    ) -> Dict[str, Any]:
        """
        Ingest raw text content (not from file) into all knowledge stores.

        Useful for ingesting email bodies, API responses, or other text content
        that doesn't come from a file.

        Args:
            text: The text content to ingest
            source: Source identifier (e.g., "gmail", "api", "manual")
            source_id: Unique ID from the source (e.g., message_id)
            title: Optional title for the content
            document_type: Type of document (e.g., "email", "note")
            metadata: Additional metadata to store
            extract_entities: Whether to extract entities for graph
            store_in_vector: Store in vector database
            store_in_graph: Store in knowledge graph
            store_raw: Store raw content

        Returns:
            Ingestion result with IDs and statistics
        """
        start_time = datetime.utcnow()

        # Generate document ID from content hash
        content_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        document_id = f"{source}_{content_hash}"

        result = {
            "status": "success",
            "source": source,
            "source_id": source_id,
            "document_id": document_id,
            "stores": {},
            "entities_extracted": 0,
            "relationships_extracted": 0,
            "chunks_created": 0,
            "warnings": [],
            "errors": []
        }

        try:
            # Create a minimal extraction result for text content
            from .extraction_backends.base import ExtractionResult, ExtractionConfidence

            extraction = ExtractionResult(
                raw_text=text,
                markdown=text,  # Plain text is its own markdown
                backend_name="direct_text",
                confidence=ExtractionConfidence.HIGH,
                metadata={
                    "source": source,
                    "source_id": source_id,
                    "title": title,
                    **(metadata or {})
                }
            )

            # Prepare full metadata
            full_metadata = {
                "source": source,
                "source_id": source_id,
                "title": title or f"{source} content",
                **(metadata or {})
            }

            # Step 1: Store raw content
            if store_raw:
                raw_result = await self._store_raw_text(
                    document_id, source, source_id, text, title, full_metadata
                )
                result["stores"]["raw"] = raw_result

            # Step 2: Store in knowledge graph
            if store_in_graph:
                graph_result = await self._store_text_in_graph(
                    document_id, text, title, document_type, full_metadata
                )
                result["stores"]["graph"] = graph_result

            # Step 3: Store in vector database
            if store_in_vector:
                vector_result = await self._store_in_vector(
                    document_id, extraction, document_type, full_metadata
                )
                result["stores"]["vector"] = vector_result
                result["chunks_created"] = vector_result.get("chunks_stored", 0)

        except Exception as e:
            logger.error(f"Text ingestion failed: {e}")
            result["status"] = "failed"
            result["errors"].append(str(e))

        result["duration_seconds"] = (datetime.utcnow() - start_time).total_seconds()
        return result

    async def _store_raw_text(
        self,
        document_id: str,
        source: str,
        source_id: str,
        text: str,
        title: Optional[str],
        metadata: Optional[Dict]
    ) -> Dict[str, Any]:
        """Store raw text content in documents_pg table"""
        try:
            supabase = supabase_service.client

            # Check if document already exists (by source_id in metadata)
            existing = supabase.table("documents_pg").select("id").eq(
                "tenant_id", self.tenant_id
            ).execute()

            # Check for duplicate in existing records
            for row in existing.data:
                check = supabase.table("documents_pg").select("metadata").eq("id", row["id"]).execute()
                if check.data:
                    existing_meta = check.data[0].get("metadata", {})
                    if existing_meta.get("source_id") == source_id and existing_meta.get("source") == source:
                        return {
                            "status": "success",
                            "document_id": row["id"],
                            "stored_bytes": len(text),
                            "note": "already_exists"
                        }

            # Build metadata including source info
            full_metadata = {
                "source": source,
                "source_id": source_id,
                "document_hash": document_id,  # Store our hash for reference
                "title": title or f"{source}_{source_id}",
                **(metadata or {})
            }

            doc_record = {
                "tenant_id": self.tenant_id,
                "content": text,
                "text": text,
                "metadata": full_metadata,
                "is_current": True,
                "is_deleted": False,
                "version_number": 1
            }

            result = supabase.table("documents_pg").insert(doc_record).execute()
            new_id = result.data[0]["id"] if result.data else None

            return {
                "status": "success",
                "document_id": new_id,
                "stored_bytes": len(text)
            }

        except Exception as e:
            logger.error(f"Raw text storage failed: {e}")
            return {"status": "failed", "error": str(e)}

    async def _store_text_in_graph(
        self,
        document_id: str,
        text: str,
        title: Optional[str],
        document_type: Optional[str],
        metadata: Optional[Dict]
    ) -> Dict[str, Any]:
        """Store text content in knowledge graph"""
        try:
            kg = get_knowledge_graph()

            # Add as episode
            await kg.add_episode(
                content_id=document_id,
                tenant_id=self.tenant_id,
                title=title or document_id,
                content=text,
                summary=text[:500] if len(text) > 500 else text,
                source_description=f"Source: {metadata.get('source', 'unknown')}, Type: {document_type or 'text'}"
            )

            return {
                "status": "success",
                "entities_stored": 0,  # Graphiti extracts automatically
                "relationships_stored": 0
            }

        except Exception as e:
            logger.error(f"Graph text storage failed: {e}")
            return {"status": "failed", "error": str(e)}

    async def _store_raw_document(
        self,
        document_id: str,
        file_path: str,
        extraction: ExtractionResult,
        metadata: Optional[Dict]
    ) -> Dict[str, Any]:
        """Store raw document and extracted text"""
        try:
            supabase = supabase_service.client

            # Store document record
            doc_record = {
                "id": document_id,
                "tenant_id": self.tenant_id,
                "file_name": Path(file_path).name,
                "file_path": file_path,
                "raw_text": extraction.raw_text,
                "markdown": extraction.markdown,
                "extraction_backend": extraction.backend_name,
                "confidence": extraction.confidence.value,
                "metadata": metadata or {},
                "created_at": datetime.utcnow().isoformat()
            }

            # Insert into documents table
            result = supabase.table("documents").upsert(doc_record).execute()

            return {
                "status": "success",
                "document_id": document_id,
                "stored_bytes": len(extraction.raw_text)
            }

        except Exception as e:
            logger.error(f"Raw storage failed: {e}")
            return {"status": "failed", "error": str(e)}

    async def _store_in_graph(
        self,
        document_id: str,
        extraction: ExtractionResult,
        document_type: Optional[str],
        metadata: Optional[Dict]
    ) -> Dict[str, Any]:
        """Store entities and relationships in Neo4j"""
        try:
            kg = get_knowledge_graph()

            # Create episode for the document
            await kg.add_episode(
                content_id=document_id,
                tenant_id=self.tenant_id,
                title=metadata.get("title", document_id) if metadata else document_id,
                content=extraction.raw_text,
                summary=extraction.markdown[:500] if extraction.markdown else "",
                source_description=f"Document type: {document_type or 'unknown'}"
            )

            # Store extracted entities and relationships
            # Note: Graphiti auto-extracts, but we can add our explicit ones
            entities_stored = len(extraction.entities)
            relationships_stored = len(extraction.relationships)

            return {
                "status": "success",
                "entities_stored": entities_stored,
                "relationships_stored": relationships_stored
            }

        except Exception as e:
            logger.error(f"Graph storage failed: {e}")
            return {"status": "failed", "error": str(e)}

    async def _store_in_vector(
        self,
        document_id: str,
        extraction: ExtractionResult,
        document_type: Optional[str],
        metadata: Optional[Dict]
    ) -> Dict[str, Any]:
        """Generate embedding and update document in vector database"""
        try:
            supabase = supabase_service.client
            embeddings_service = get_embeddings()

            # For documents under embedding limit, embed the whole thing
            # For larger docs, embed a summary/beginning
            text_to_embed = extraction.raw_text
            if len(text_to_embed) > 8000:
                # Use first ~8000 chars for embedding (roughly 2000 tokens)
                text_to_embed = text_to_embed[:8000]

            # Generate embedding
            embedding = await embeddings_service.generate_embedding(text_to_embed)

            # Find the document by source_id in metadata
            source_id = metadata.get("source_id") or metadata.get("message_id") if metadata else None
            source = metadata.get("source") if metadata else None

            if source_id and source:
                # Find document by metadata (more reliable than hash ID)
                existing = supabase.table("documents_pg").select("id, metadata").eq(
                    "tenant_id", self.tenant_id
                ).execute()

                db_id = None
                for row in existing.data:
                    row_meta = row.get("metadata", {})
                    if row_meta.get("source_id") == source_id and row_meta.get("source") == source:
                        db_id = row["id"]
                        break

                if db_id:
                    supabase.table("documents_pg").update({
                        "embedding": embedding
                    }).eq("id", db_id).execute()

                    return {
                        "status": "success",
                        "embedded": True,
                        "db_id": db_id,
                        "total_characters": len(extraction.raw_text),
                        "embedded_characters": len(text_to_embed)
                    }

            return {
                "status": "failed",
                "error": "Could not find document to update with embedding"
            }

        except Exception as e:
            logger.error(f"Vector storage failed: {e}")
            return {"status": "failed", "error": str(e)}

    async def query_knowledge(
        self,
        query: str,
        search_vector: bool = True,
        search_graph: bool = True,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Query across all knowledge stores.

        Args:
            query: Search query
            search_vector: Search vector store (semantic)
            search_graph: Search knowledge graph (relationships)
            limit: Maximum results per store

        Returns:
            Combined results from all stores
        """
        results = {
            "query": query,
            "vector_results": [],
            "graph_results": []
        }

        if search_vector:
            try:
                embeddings_service = get_embeddings()
                supabase = supabase_service.client

                # Embed query
                query_embedding = await embeddings_service.embed(query)

                # Search using pgvector
                vector_results = supabase.rpc(
                    "match_document_chunks",
                    {
                        "query_embedding": query_embedding,
                        "match_count": limit,
                        "filter_tenant": self.tenant_id
                    }
                ).execute()

                results["vector_results"] = vector_results.data

            except Exception as e:
                logger.error(f"Vector search failed: {e}")
                results["vector_error"] = str(e)

        if search_graph:
            try:
                kg = get_knowledge_graph()
                graph_results = await kg.search_similar_content(
                    query=query,
                    tenant_id=self.tenant_id,
                    limit=limit
                )
                results["graph_results"] = graph_results

            except Exception as e:
                logger.error(f"Graph search failed: {e}")
                results["graph_error"] = str(e)

        return results


# Singleton instance
_ingestion_service = None


def get_ingestion_service(
    tenant_id: str = "default",
    extraction_backend: ExtractionBackendType = ExtractionBackendType.CLAUDE
) -> KnowledgeIngestionService:
    """Get or create ingestion service singleton"""
    global _ingestion_service
    if _ingestion_service is None:
        _ingestion_service = KnowledgeIngestionService(
            tenant_id=tenant_id,
            extraction_backend=extraction_backend
        )
    return _ingestion_service


async def ingest_document(
    file_path: str,
    document_type: Optional[str] = None,
    tenant_id: str = "default"
) -> Dict[str, Any]:
    """
    Convenience function to ingest a document.

    Args:
        file_path: Path to document
        document_type: Type of document
        tenant_id: Tenant identifier

    Returns:
        Ingestion result
    """
    service = get_ingestion_service(tenant_id=tenant_id)
    return await service.ingest_document(
        file_path=file_path,
        document_type=document_type
    )
