/**
 * Knowledge Graph Types
 * Types for Neo4j-powered entity and relationship queries
 */

/**
 * Entity node in the knowledge graph
 */
export interface GraphEntity {
  /** Unique identifier */
  id: string
  /** Entity name */
  name: string
  /** Entity type (person, medication, organization, etc.) */
  type: EntityType
  /** Optional properties */
  properties?: Record<string, unknown>
  /** Creation timestamp */
  created_at?: string
  /** Last updated timestamp */
  updated_at?: string
}

/**
 * Relationship/edge between entities
 */
export interface GraphRelationship {
  /** Unique identifier */
  id: string
  /** Source entity ID */
  source: string
  /** Target entity ID */
  target: string
  /** Relationship type (PRESCRIBED, TREATS, WORKS_AT, etc.) */
  type: RelationshipType
  /** Optional properties */
  properties?: Record<string, unknown>
  /** Relationship weight/strength */
  weight?: number
}

/**
 * Entity types in the knowledge graph
 */
export type EntityType =
  | 'person'
  | 'organization'
  | 'medication'
  | 'condition'
  | 'document'
  | 'project'
  | 'topic'
  | 'date'
  | 'location'
  | 'unknown'

/**
 * Relationship types in the knowledge graph
 */
export type RelationshipType =
  | 'PRESCRIBED'
  | 'TREATS'
  | 'STOPPED'
  | 'WORKS_AT'
  | 'RELATED_TO'
  | 'MENTIONS'
  | 'CREATED'
  | 'BELONGS_TO'
  | 'COLLABORATED_WITH'
  | 'DEPENDS_ON'
  | 'REFERENCES'

/**
 * Entity type metadata for UI display
 */
export const ENTITY_TYPES: Record<EntityType, { label: string; color: string; icon: string }> = {
  person: { label: 'Person', color: 'blue', icon: 'user' },
  organization: { label: 'Organization', color: 'purple', icon: 'building' },
  medication: { label: 'Medication', color: 'green', icon: 'pill' },
  condition: { label: 'Condition', color: 'red', icon: 'heart' },
  document: { label: 'Document', color: 'yellow', icon: 'file' },
  project: { label: 'Project', color: 'orange', icon: 'folder' },
  topic: { label: 'Topic', color: 'cyan', icon: 'tag' },
  date: { label: 'Date', color: 'gray', icon: 'calendar' },
  location: { label: 'Location', color: 'green', icon: 'map-pin' },
  unknown: { label: 'Unknown', color: 'gray', icon: 'circle' },
}

/**
 * Relationship type metadata for UI display
 */
export const RELATIONSHIP_TYPES: Record<RelationshipType, { label: string; color: string }> = {
  PRESCRIBED: { label: 'Prescribed', color: 'green' },
  TREATS: { label: 'Treats', color: 'blue' },
  STOPPED: { label: 'Stopped', color: 'red' },
  WORKS_AT: { label: 'Works At', color: 'purple' },
  RELATED_TO: { label: 'Related To', color: 'gray' },
  MENTIONS: { label: 'Mentions', color: 'yellow' },
  CREATED: { label: 'Created', color: 'blue' },
  BELONGS_TO: { label: 'Belongs To', color: 'cyan' },
  COLLABORATED_WITH: { label: 'Collaborated With', color: 'purple' },
  DEPENDS_ON: { label: 'Depends On', color: 'orange' },
  REFERENCES: { label: 'References', color: 'gray' },
}

/**
 * Graph search request
 */
export interface GraphSearchRequest {
  /** Search query */
  query: string
  /** Filter by entity types */
  types?: EntityType[]
  /** Maximum results */
  limit?: number
}

/**
 * Graph search response
 */
export interface GraphSearchResponse {
  /** Matching entities */
  entities: GraphEntity[]
  /** Total count */
  total: number
}

/**
 * Related entities response
 */
export interface RelatedEntitiesResponse {
  /** Source entity */
  entity: GraphEntity
  /** Related entities with relationships */
  related: Array<{
    entity: GraphEntity
    relationship: GraphRelationship
  }>
}

/**
 * Graph statistics
 */
export interface GraphStats {
  /** Total entity count */
  total_entities: number
  /** Entity counts by type */
  entities_by_type: Record<EntityType, number>
  /** Total relationship count */
  total_relationships: number
  /** Relationship counts by type */
  relationships_by_type: Record<RelationshipType, number>
  /** Last updated timestamp */
  last_updated?: string
}

/**
 * Force graph node data (for react-force-graph)
 */
export interface ForceGraphNode {
  /** Unique ID */
  id: string
  /** Display name */
  name: string
  /** Entity type */
  type: EntityType
  /** Node size (based on connections) */
  val?: number
  /** Color override */
  color?: string
  /** X position */
  x?: number
  /** Y position */
  y?: number
  /** Fixed X position */
  fx?: number
  /** Fixed Y position */
  fy?: number
}

/**
 * Force graph link data (for react-force-graph)
 */
export interface ForceGraphLink {
  /** Source node ID */
  source: string | ForceGraphNode
  /** Target node ID */
  target: string | ForceGraphNode
  /** Relationship type */
  type: RelationshipType
  /** Link weight */
  value?: number
  /** Color override */
  color?: string
}

/**
 * Force graph data structure
 */
export interface ForceGraphData {
  nodes: ForceGraphNode[]
  links: ForceGraphLink[]
}

/**
 * Get entity type metadata with fallback
 */
export function getEntityTypeMeta(type: EntityType | string) {
  return ENTITY_TYPES[type as EntityType] || ENTITY_TYPES.unknown
}

/**
 * Get relationship type metadata with fallback
 */
export function getRelationshipTypeMeta(type: RelationshipType | string) {
  return RELATIONSHIP_TYPES[type as RelationshipType] || { label: type, color: 'gray' }
}

/**
 * Convert graph data to force graph format
 */
export function toForceGraphData(
  entities: GraphEntity[],
  relationships: GraphRelationship[]
): ForceGraphData {
  const nodes: ForceGraphNode[] = entities.map((entity) => ({
    id: entity.id,
    name: entity.name,
    type: entity.type,
    val: 1, // Will be calculated based on connections
    color: getEntityTypeColor(entity.type),
  }))

  const links: ForceGraphLink[] = relationships.map((rel) => ({
    source: rel.source,
    target: rel.target,
    type: rel.type,
    value: rel.weight || 1,
  }))

  // Calculate node sizes based on connections
  const connectionCounts = new Map<string, number>()
  for (const link of links) {
    const sourceId = typeof link.source === 'string' ? link.source : link.source.id
    const targetId = typeof link.target === 'string' ? link.target : link.target.id
    connectionCounts.set(sourceId, (connectionCounts.get(sourceId) || 0) + 1)
    connectionCounts.set(targetId, (connectionCounts.get(targetId) || 0) + 1)
  }

  for (const node of nodes) {
    node.val = Math.max(1, connectionCounts.get(node.id) || 1)
  }

  return { nodes, links }
}

/**
 * Get color for entity type
 */
function getEntityTypeColor(type: EntityType): string {
  const colors: Record<EntityType, string> = {
    person: '#3b82f6',      // blue-500
    organization: '#8b5cf6', // purple-500
    medication: '#22c55e',   // green-500
    condition: '#ef4444',    // red-500
    document: '#eab308',     // yellow-500
    project: '#f97316',      // orange-500
    topic: '#06b6d4',        // cyan-500
    date: '#6b7280',         // gray-500
    location: '#10b981',     // emerald-500
    unknown: '#9ca3af',      // gray-400
  }
  return colors[type] || colors.unknown
}
