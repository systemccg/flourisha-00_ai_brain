'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState, useCallback } from 'react'
import { api, type APIResponse, endpoints } from '@/lib/api'
import type {
  GraphEntity,
  GraphSearchRequest,
  GraphSearchResponse,
  RelatedEntitiesResponse,
  GraphStats,
  EntityType,
  ForceGraphData,
  ForceGraphNode,
  ForceGraphLink,
  toForceGraphData,
} from '@/lib/types'

/**
 * Query key factory for graph
 */
const graphKeys = {
  all: ['graph'] as const,
  search: (query: string, types?: EntityType[]) =>
    [...graphKeys.all, 'search', query, types?.join(',') ?? 'all'] as const,
  related: (name: string) => [...graphKeys.all, 'related', name] as const,
  stats: () => [...graphKeys.all, 'stats'] as const,
  content: (id: string) => [...graphKeys.all, 'content', id] as const,
}

/**
 * Hook for searching graph entities
 */
export function useGraphSearch() {
  const [query, setQuery] = useState('')
  const [selectedTypes, setSelectedTypes] = useState<EntityType[]>([])

  const searchMutation = useMutation({
    mutationFn: async (request: GraphSearchRequest): Promise<GraphSearchResponse> => {
      const response = await api.post<APIResponse<GraphSearchResponse>>(
        endpoints.graph.search,
        request
      )
      if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error || 'Graph search failed')
      }
      return response.data.data
    },
  })

  const search = useCallback(
    (searchQuery: string, types?: EntityType[]) => {
      setQuery(searchQuery)
      if (types !== undefined) setSelectedTypes(types)

      if (searchQuery.length < 2) {
        return
      }

      searchMutation.mutate({
        query: searchQuery,
        types: types || selectedTypes.length > 0 ? selectedTypes : undefined,
        limit: 50,
      })
    },
    [searchMutation, selectedTypes]
  )

  const toggleType = useCallback((type: EntityType) => {
    setSelectedTypes((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    )
  }, [])

  const clearFilters = useCallback(() => {
    setSelectedTypes([])
  }, [])

  return {
    query,
    selectedTypes,
    results: searchMutation.data?.entities ?? [],
    total: searchMutation.data?.total ?? 0,
    isLoading: searchMutation.isPending,
    error: searchMutation.error,
    search,
    toggleType,
    clearFilters,
  }
}

/**
 * Hook for getting related entities
 */
export function useRelatedEntities(entityName: string | null) {
  return useQuery({
    queryKey: graphKeys.related(entityName ?? ''),
    queryFn: async (): Promise<RelatedEntitiesResponse> => {
      if (!entityName) throw new Error('No entity name provided')

      const response = await api.get<APIResponse<RelatedEntitiesResponse>>(
        endpoints.graph.related(entityName)
      )
      if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error || 'Failed to get related entities')
      }
      return response.data.data
    },
    enabled: !!entityName,
    staleTime: 60000, // 1 minute
  })
}

/**
 * Hook for graph statistics
 */
export function useGraphStats() {
  return useQuery({
    queryKey: graphKeys.stats(),
    queryFn: async (): Promise<GraphStats> => {
      const response = await api.get<APIResponse<GraphStats>>(endpoints.graph.stats)
      if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error || 'Failed to get graph stats')
      }
      return response.data.data
    },
    staleTime: 300000, // 5 minutes
  })
}

/**
 * Hook for managing graph visualization state
 */
export function useGraphVisualization() {
  const [graphData, setGraphData] = useState<ForceGraphData>({ nodes: [], links: [] })
  const [selectedNode, setSelectedNode] = useState<ForceGraphNode | null>(null)
  const [hoveredNode, setHoveredNode] = useState<ForceGraphNode | null>(null)
  const [highlightedNodes, setHighlightedNodes] = useState<Set<string>>(new Set())
  const [highlightedLinks, setHighlightedLinks] = useState<Set<string>>(new Set())

  // Load graph data from search results or related entities
  const loadFromSearch = useCallback((entities: GraphEntity[]) => {
    // Create nodes from entities
    const nodes: ForceGraphNode[] = entities.map((entity) => ({
      id: entity.id,
      name: entity.name,
      type: entity.type,
      val: 1,
    }))
    setGraphData({ nodes, links: [] })
  }, [])

  const loadFromRelated = useCallback((data: RelatedEntitiesResponse) => {
    // Create nodes from source entity and related entities
    const nodes: ForceGraphNode[] = [
      {
        id: data.entity.id,
        name: data.entity.name,
        type: data.entity.type,
        val: data.related.length + 1, // Center node is larger
      },
      ...data.related.map(({ entity }) => ({
        id: entity.id,
        name: entity.name,
        type: entity.type,
        val: 1,
      })),
    ]

    // Create links from relationships
    const links: ForceGraphLink[] = data.related.map(({ entity, relationship }) => ({
      source: data.entity.id,
      target: entity.id,
      type: relationship.type,
      value: relationship.weight || 1,
    }))

    setGraphData({ nodes, links })
  }, [])

  const handleNodeClick = useCallback((node: ForceGraphNode) => {
    setSelectedNode(node)
  }, [])

  const handleNodeHover = useCallback(
    (node: ForceGraphNode | null) => {
      setHoveredNode(node)

      if (node) {
        // Highlight connected nodes and links
        const connectedNodes = new Set<string>([node.id])
        const connectedLinks = new Set<string>()

        for (const link of graphData.links) {
          const sourceId = typeof link.source === 'string' ? link.source : link.source.id
          const targetId = typeof link.target === 'string' ? link.target : link.target.id

          if (sourceId === node.id || targetId === node.id) {
            connectedNodes.add(sourceId)
            connectedNodes.add(targetId)
            connectedLinks.add(`${sourceId}-${targetId}`)
          }
        }

        setHighlightedNodes(connectedNodes)
        setHighlightedLinks(connectedLinks)
      } else {
        setHighlightedNodes(new Set())
        setHighlightedLinks(new Set())
      }
    },
    [graphData.links]
  )

  const clearSelection = useCallback(() => {
    setSelectedNode(null)
    setHoveredNode(null)
    setHighlightedNodes(new Set())
    setHighlightedLinks(new Set())
  }, [])

  const addNodes = useCallback((newNodes: ForceGraphNode[], newLinks: ForceGraphLink[] = []) => {
    setGraphData((prev) => {
      // Filter out duplicates
      const existingIds = new Set(prev.nodes.map((n) => n.id))
      const uniqueNewNodes = newNodes.filter((n) => !existingIds.has(n.id))

      // Filter out duplicate links
      const existingLinkIds = new Set(
        prev.links.map((l) => {
          const sourceId = typeof l.source === 'string' ? l.source : l.source.id
          const targetId = typeof l.target === 'string' ? l.target : l.target.id
          return `${sourceId}-${targetId}`
        })
      )
      const uniqueNewLinks = newLinks.filter((l) => {
        const sourceId = typeof l.source === 'string' ? l.source : l.source.id
        const targetId = typeof l.target === 'string' ? l.target : l.target.id
        return !existingLinkIds.has(`${sourceId}-${targetId}`)
      })

      return {
        nodes: [...prev.nodes, ...uniqueNewNodes],
        links: [...prev.links, ...uniqueNewLinks],
      }
    })
  }, [])

  const clearGraph = useCallback(() => {
    setGraphData({ nodes: [], links: [] })
    clearSelection()
  }, [clearSelection])

  return {
    graphData,
    selectedNode,
    hoveredNode,
    highlightedNodes,
    highlightedLinks,
    loadFromSearch,
    loadFromRelated,
    handleNodeClick,
    handleNodeHover,
    clearSelection,
    addNodes,
    clearGraph,
  }
}

/**
 * Hook for centralized graph state management
 */
export function useKnowledgeGraph() {
  const search = useGraphSearch()
  const stats = useGraphStats()
  const visualization = useGraphVisualization()
  const [focusedEntity, setFocusedEntity] = useState<string | null>(null)
  const related = useRelatedEntities(focusedEntity)

  // Load related entities into visualization when focused entity changes
  const expandEntity = useCallback(
    (entityName: string) => {
      setFocusedEntity(entityName)
    },
    []
  )

  // When related data loads, add to visualization
  const loadRelated = useCallback(() => {
    if (related.data) {
      visualization.loadFromRelated(related.data)
    }
  }, [related.data, visualization])

  return {
    // Search
    search,
    // Stats
    stats: stats.data,
    statsLoading: stats.isLoading,
    statsError: stats.error,
    // Visualization
    visualization,
    // Related entities
    focusedEntity,
    expandEntity,
    relatedData: related.data,
    relatedLoading: related.isLoading,
    relatedError: related.error,
    loadRelated,
  }
}
