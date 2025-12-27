"""
Graph Store Router

Endpoints for Neo4j knowledge graph queries via Graphiti.
Wraps the knowledge_graph_service for graph traversal and entity lookups.
"""
import sys
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, Request, Query
from pydantic import BaseModel, Field

from models.response import APIResponse, ResponseMeta
from middleware.auth import get_current_user, UserContext

# Add services to path for imports
services_path = Path(__file__).parent.parent.parent / "services"
sys.path.insert(0, str(services_path))


router = APIRouter(prefix="/api/graph", tags=["Knowledge Graph"])


# === Request/Response Models ===

class GraphSearchRequest(BaseModel):
    """Request for semantic graph search."""
    query: str = Field(..., description="Search query", min_length=1, max_length=1000)
    limit: int = Field(default=10, ge=1, le=50, description="Maximum results")


class GraphSearchResult(BaseModel):
    """Single result from graph search."""
    uuid: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Entity or relationship name")
    fact: Optional[str] = Field(None, description="Fact/relationship description")
    created_at: Optional[str] = Field(None, description="Creation timestamp")


class GraphSearchResponse(BaseModel):
    """Response for graph search."""
    results: List[GraphSearchResult] = Field(..., description="Search results")
    query: str = Field(..., description="Original query")
    total: int = Field(..., description="Number of results")


class RelatedEntity(BaseModel):
    """Entity related to a given entity."""
    name: str = Field(..., description="Entity name")
    relationship: str = Field(..., description="Relationship type")
    entity_type: Optional[str] = Field(None, description="Type of entity")


class RelatedEntitiesResponse(BaseModel):
    """Response for related entities query."""
    entity_name: str = Field(..., description="The queried entity")
    related: List[RelatedEntity] = Field(..., description="Related entities")
    total: int = Field(..., description="Number of related entities")


class GraphNode(BaseModel):
    """Node in a knowledge graph."""
    id: Optional[str] = Field(None, description="Node ID")
    name: Optional[str] = Field(None, description="Node name")
    type: Optional[str] = Field(None, description="Node type")
    properties: Optional[dict] = Field(default_factory=dict, description="Node properties")


class GraphEdge(BaseModel):
    """Edge/relationship in a knowledge graph."""
    from_entity: Optional[str] = Field(None, alias="from", description="Source entity name")
    to_entity: Optional[str] = Field(None, alias="to", description="Target entity name")
    relationship_type: Optional[str] = Field(None, alias="type", description="Relationship type")


class ContentGraphResponse(BaseModel):
    """Knowledge graph for a specific content piece."""
    content_id: str = Field(..., description="Content identifier")
    episode: Optional[dict] = Field(None, description="Episode data")
    entities: List[dict] = Field(default_factory=list, description="Entities in the graph")
    relationships: List[GraphEdge] = Field(default_factory=list, description="Relationships")


# === Endpoints ===

@router.post("/search", response_model=APIResponse[GraphSearchResponse])
async def search_graph(
    request: Request,
    search_request: GraphSearchRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[GraphSearchResponse]:
    """
    Search the knowledge graph using semantic similarity.

    Searches for entities and relationships matching the query.
    Uses Graphiti's vector-based search on graph content.

    **Request Body:**
    - query: Search text (required)
    - limit: Max results (default 10, max 50)

    **Response:**
    - results: List of matching entities/relationships
    - query: The original query
    - total: Number of results

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or user.uid

    try:
        from knowledge_graph_service import get_knowledge_graph

        kg = get_knowledge_graph()

        # Search the graph
        raw_results = await kg.search_similar_content(
            query=search_request.query,
            tenant_id=tenant_id,
            limit=search_request.limit,
        )

        # Transform to response models
        results = []
        for item in raw_results:
            results.append(GraphSearchResult(
                uuid=item.get("uuid", ""),
                name=item.get("name", ""),
                fact=item.get("fact"),
                created_at=str(item.get("created_at")) if item.get("created_at") else None,
            ))

        response_data = GraphSearchResponse(
            results=results,
            query=search_request.query,
            total=len(results),
        )

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except ImportError as e:
        return APIResponse(
            success=True,
            data=GraphSearchResponse(
                results=[],
                query=search_request.query,
                total=0,
            ),
            error="Knowledge graph service not available - check Neo4j connection",
            meta=ResponseMeta(**meta_dict),
        )
    except ValueError as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Graph configuration error: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Graph search failed: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/entities/{entity_name}/related", response_model=APIResponse[RelatedEntitiesResponse])
async def get_related_entities(
    request: Request,
    entity_name: str,
    relationship_types: Optional[str] = Query(None, description="Comma-separated relationship types to filter"),
    user: UserContext = Depends(get_current_user),
) -> APIResponse[RelatedEntitiesResponse]:
    """
    Get entities related to a given entity.

    Traverses the knowledge graph to find entities connected
    to the specified entity through relationships.

    **Path Parameters:**
    - entity_name: Name of the entity to find relations for

    **Query Parameters:**
    - relationship_types: Optional comma-separated list of relationship types

    **Response:**
    - entity_name: The queried entity
    - related: List of related entities with relationship types
    - total: Number of related entities

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or user.uid

    try:
        from knowledge_graph_service import get_knowledge_graph

        kg = get_knowledge_graph()

        # Parse relationship types if provided
        rel_types = None
        if relationship_types:
            rel_types = [r.strip() for r in relationship_types.split(",") if r.strip()]

        # Get related entities
        raw_results = await kg.get_related_entities(
            entity_name=entity_name,
            tenant_id=tenant_id,
            relationship_types=rel_types,
        )

        # Transform to response models
        related = []
        for item in raw_results:
            related.append(RelatedEntity(
                name=item.get("name", ""),
                relationship=item.get("relationship", "RELATED"),
                entity_type=item.get("type"),
            ))

        response_data = RelatedEntitiesResponse(
            entity_name=entity_name,
            related=related,
            total=len(related),
        )

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except ImportError as e:
        return APIResponse(
            success=True,
            data=RelatedEntitiesResponse(
                entity_name=entity_name,
                related=[],
                total=0,
            ),
            error="Knowledge graph service not available - check Neo4j connection",
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Related entities lookup failed: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/content/{content_id}", response_model=APIResponse[ContentGraphResponse])
async def get_content_graph(
    request: Request,
    content_id: str,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[ContentGraphResponse]:
    """
    Get the knowledge graph for a specific content piece.

    Retrieves the episode node and all connected entities
    and relationships for a given content ID.

    **Path Parameters:**
    - content_id: Unique identifier of the content

    **Response:**
    - content_id: The content identifier
    - episode: Episode node data
    - entities: List of entities extracted from the content
    - relationships: List of relationships between entities

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or user.uid

    try:
        from knowledge_graph_service import get_knowledge_graph

        kg = get_knowledge_graph()

        # Get content graph
        graph_data = await kg.get_content_graph(
            content_id=content_id,
            tenant_id=tenant_id,
        )

        # Transform relationships
        relationships = []
        for rel in graph_data.get("relationships", []):
            if rel:  # Skip empty relationships
                relationships.append(GraphEdge(
                    from_entity=rel.get("from"),
                    to_entity=rel.get("to"),
                    relationship_type=rel.get("type"),
                ))

        response_data = ContentGraphResponse(
            content_id=content_id,
            episode=graph_data.get("episode"),
            entities=graph_data.get("entities", []),
            relationships=relationships,
        )

        return APIResponse(
            success=True,
            data=response_data,
            meta=ResponseMeta(**meta_dict),
        )

    except ImportError as e:
        return APIResponse(
            success=True,
            data=ContentGraphResponse(
                content_id=content_id,
                episode=None,
                entities=[],
                relationships=[],
            ),
            error="Knowledge graph service not available - check Neo4j connection",
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Content graph retrieval failed: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/stats", response_model=APIResponse[dict])
async def get_graph_stats(
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[dict]:
    """
    Get statistics about the knowledge graph.

    Returns counts of nodes, relationships, and entity types
    for the current tenant's graph data.

    **Response:**
    - entity_count: Total number of entities
    - relationship_count: Total number of relationships
    - episode_count: Total number of episodes (content pieces)
    - entity_types: Breakdown by entity type

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()
    tenant_id = user.tenant_id or user.uid

    try:
        from knowledge_graph_service import get_knowledge_graph

        kg = get_knowledge_graph()

        # Run stats query
        stats_query = """
        MATCH (e:Entity)
        WHERE e.group_id = $tenant_id OR e.tenant_id = $tenant_id
        WITH count(e) as entity_count
        OPTIONAL MATCH ()-[r]->()
        WITH entity_count, count(r) as relationship_count
        OPTIONAL MATCH (ep:Episodic)
        WHERE ep.group_id = $tenant_id
        RETURN entity_count, relationship_count, count(ep) as episode_count
        """

        # Execute via driver session
        with kg.client.driver.session() as session:
            result = session.run(stats_query, {"tenant_id": tenant_id})
            record = result.single()

            if record:
                stats = {
                    "entity_count": record["entity_count"] or 0,
                    "relationship_count": record["relationship_count"] or 0,
                    "episode_count": record["episode_count"] or 0,
                    "tenant_id": tenant_id,
                }
            else:
                stats = {
                    "entity_count": 0,
                    "relationship_count": 0,
                    "episode_count": 0,
                    "tenant_id": tenant_id,
                }

        return APIResponse(
            success=True,
            data=stats,
            meta=ResponseMeta(**meta_dict),
        )

    except ImportError as e:
        return APIResponse(
            success=False,
            data=None,
            error="Knowledge graph service not available - check Neo4j connection",
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            error=f"Graph stats retrieval failed: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )
