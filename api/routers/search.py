"""
Unified Search Router

Single endpoint for semantic search across all content.
Wraps the embeddings_service for vector similarity search.
"""
import sys
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, Request

from models.response import APIResponse, ResponseMeta
from models.search import SearchRequest, SearchResult, SearchResponse
from middleware.auth import get_current_user, UserContext

# Add services to path for imports
services_path = Path(__file__).parent.parent.parent / "services"
sys.path.insert(0, str(services_path))


router = APIRouter(prefix="/api/search", tags=["Search"])


@router.post("", response_model=APIResponse[SearchResponse])
async def unified_search(
    request: Request,
    search_request: SearchRequest,
    user: UserContext = Depends(get_current_user),
) -> APIResponse[SearchResponse]:
    """
    Unified semantic search across all content.

    Searches the Vector Store (pgvector) using embedding similarity.
    Returns ranked results above the threshold.

    **Request Body:**
    - query: Search text (required)
    - limit: Max results (default 10, max 100)
    - threshold: Min similarity score (default 0.7, range 0.5-0.99)

    **Response:**
    - results: List of matching content with similarity scores
    - query: The original query
    - total: Number of results

    **Requires:** Valid Firebase JWT
    """
    meta_dict = request.state.get_meta()

    try:
        # Import embeddings service (lazy import to avoid startup issues)
        from embeddings_service import get_embeddings_service

        embeddings = get_embeddings_service()

        # Search using vector similarity
        # The service uses tenant_id from custom claims for data isolation
        raw_results = await embeddings.search_similar_content(
            query=search_request.query,
            tenant_id=user.tenant_id or user.uid,  # Fallback to uid if no tenant
            limit=search_request.limit,
            similarity_threshold=search_request.threshold,
        )

        # Transform to SearchResult models
        results: List[SearchResult] = []
        for item in raw_results:
            # Extract preview from summary or embedding_text
            summary = item.get("summary", "")
            preview = summary[:200] + "..." if len(summary) > 200 else summary

            results.append(SearchResult(
                id=item["id"],
                title=item.get("title", "Untitled"),
                content_type=item.get("content_type", "unknown"),
                summary=summary or None,
                preview=preview or None,
                tags=item.get("tags", []),
                similarity=round(item.get("similarity", 0), 4),
                source_url=item.get("source_url"),
            ))

        response_data = SearchResponse(
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
        # Service not available - return empty results with message
        return APIResponse(
            success=True,
            data=SearchResponse(
                results=[],
                query=search_request.query,
                total=0,
            ),
            error="Search service initializing - embeddings service not available",
            meta=ResponseMeta(**meta_dict),
        )
    except ValueError as e:
        # Configuration error (e.g., missing API key)
        return APIResponse(
            success=False,
            data=None,
            error=f"Search configuration error: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )
    except Exception as e:
        # Unexpected error
        return APIResponse(
            success=False,
            data=None,
            error=f"Search failed: {str(e)}",
            meta=ResponseMeta(**meta_dict),
        )
