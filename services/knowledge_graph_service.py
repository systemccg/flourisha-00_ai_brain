"""
Neo4j Knowledge Graph Service using Graphiti
Temporally-aware knowledge graph for content intelligence
"""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from graphiti_core import Graphiti

from .ontology import get_ontology, ENTITY_TYPES, EDGE_TYPES, EDGE_TYPE_MAP


class KnowledgeGraphService:
    """
    Service for managing knowledge graph with Graphiti
    Stores entities, relationships, and episodic memories
    """

    _instance = None

    def __new__(cls):
        """Singleton pattern to reuse connection"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize Graphiti client"""
        if self._initialized:
            return

        self.neo4j_uri = os.getenv('NEO4J_URL', 'bolt://localhost:7687')
        self.neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
        self.neo4j_password = os.getenv('NEO4J_PASSWORD')

        if not self.neo4j_password:
            raise ValueError("NEO4J_PASSWORD not found in environment")

        # Initialize Graphiti
        self.client = Graphiti(
            uri=self.neo4j_uri,
            user=self.neo4j_user,
            password=self.neo4j_password
        )

        self._initialized = True

    async def add_episode(
        self,
        content_id: str,
        tenant_id: str,
        title: str,
        content: str,
        summary: str,
        source_description: str,
        timestamp: Optional[datetime] = None
    ) -> str:
        """
        Add an episode (content piece) to the knowledge graph

        Args:
            content_id: Unique identifier for the content
            tenant_id: Tenant ID for isolation
            title: Content title
            content: Full content/transcript
            summary: AI-generated summary
            source_description: Description of the source
            timestamp: When the content was created

        Returns:
            Episode node ID
        """
        if timestamp is None:
            timestamp = datetime.utcnow()

        # Build episode data with tenant isolation
        episode_data = {
            "name": f"[{tenant_id}] {title}",
            "content": content,
            "summary": summary,
            "source_description": source_description,
            "reference_time": timestamp,
            "tenant_id": tenant_id,
            "content_id": content_id
        }

        # Add episode to Graphiti with custom ontology
        # Graphiti will extract entities and classify them using our defined types
        await self.client.add_episode(
            name=episode_data["name"],
            episode_body=episode_data["content"],
            source_description=episode_data["source_description"],
            reference_time=episode_data["reference_time"],
            group_id=tenant_id,  # Use tenant as group for isolation
            entity_types=ENTITY_TYPES,  # Custom entity types (Person, Property, etc.)
            edge_types=EDGE_TYPES,  # Custom relationship types (OWNS, MANAGES, etc.)
            edge_type_map=EDGE_TYPE_MAP  # Which edges connect which entity types
        )

        return content_id

    async def add_entities_and_relationships(
        self,
        content_id: str,
        tenant_id: str,
        entities: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]]
    ) -> None:
        """
        Manually add entities and relationships (for more control)

        Args:
            content_id: Content identifier
            tenant_id: Tenant ID
            entities: List of entity dicts with 'name', 'type', 'properties'
            relationships: List of relationship dicts with 'from', 'to', 'type', 'properties'
        """
        # Note: For now, we'll rely on Graphiti's automatic extraction
        # This method can be enhanced later for manual entity/relationship addition
        pass

    async def search_similar_content(
        self,
        query: str,
        tenant_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for similar episodes/content using semantic search

        Args:
            query: Search query
            tenant_id: Tenant ID for filtering
            limit: Maximum results

        Returns:
            List of similar episodes/content with relationship info
        """
        # Graphiti search returns EntityEdge results (relationships)
        results = await self.client.search(
            query=query,
            group_ids=[tenant_id],
            num_results=limit
        )

        # Format results
        formatted = []
        for edge in results:
            formatted.append({
                "uuid": edge.uuid,
                "name": edge.name,
                "fact": edge.fact if hasattr(edge, 'fact') else None,
                "created_at": edge.created_at if hasattr(edge, 'created_at') else None
            })

        return formatted

    async def get_related_entities(
        self,
        entity_name: str,
        tenant_id: str,
        relationship_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get entities related to a given entity

        Args:
            entity_name: Name of the entity
            tenant_id: Tenant ID
            relationship_types: Optional list of relationship types to filter

        Returns:
            List of related entities with relationships
        """
        # Custom Cypher query for tenant-isolated entity retrieval
        query = """
        MATCH (e:Entity {name: $entity_name})-[r]-(related:Entity)
        WHERE e.tenant_id = $tenant_id OR related.tenant_id = $tenant_id
        RETURN related.name as name, type(r) as relationship, related.type as entity_type
        LIMIT 50
        """

        params = {
            "entity_name": entity_name,
            "tenant_id": tenant_id
        }

        # Execute via Graphiti's driver
        with self.client.driver.session() as session:
            result = session.run(query, params)

            entities = []
            for record in result:
                entities.append({
                    "name": record["name"],
                    "relationship": record["relationship"],
                    "type": record["entity_type"]
                })

            return entities

    async def get_content_graph(
        self,
        content_id: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Get the knowledge graph for a specific content piece

        Args:
            content_id: Content identifier
            tenant_id: Tenant ID

        Returns:
            Graph data with nodes and edges
        """
        query = """
        MATCH (episode:Episode {content_id: $content_id, tenant_id: $tenant_id})
        OPTIONAL MATCH (episode)-[:MENTIONS]->(entity:Entity)
        OPTIONAL MATCH (entity)-[r]-(related:Entity)
        RETURN episode, collect(DISTINCT entity) as entities,
               collect(DISTINCT {from: entity.name, to: related.name, type: type(r)}) as relationships
        """

        params = {
            "content_id": content_id,
            "tenant_id": tenant_id
        }

        with self.client.driver.session() as session:
            result = session.run(query, params)
            record = result.single()

            if not record:
                return {"nodes": [], "edges": []}

            return {
                "episode": dict(record["episode"]),
                "entities": [dict(e) for e in record["entities"]],
                "relationships": record["relationships"]
            }

    async def close(self):
        """Close the Graphiti client connection"""
        if hasattr(self, 'client'):
            await self.client.close()


# Singleton instance
_kg_service = None


def get_knowledge_graph() -> KnowledgeGraphService:
    """Get or create knowledge graph service singleton"""
    global _kg_service
    if _kg_service is None:
        _kg_service = KnowledgeGraphService()
    return _kg_service
