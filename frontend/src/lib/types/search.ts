/**
 * Search Request/Response Types
 * Mirrors the backend API models
 */

/**
 * Search request parameters
 */
export interface SearchRequest {
  /** Search query text */
  query: string
  /** Maximum results to return (1-100, default 10) */
  limit?: number
  /** Minimum similarity score threshold (0.5-0.99, default 0.7) */
  threshold?: number
}

/**
 * Individual search result
 */
export interface SearchResult {
  /** Content ID */
  id: string
  /** Content title */
  title: string
  /** Type of content (youtube_video, document, etc.) */
  content_type: string
  /** Content summary */
  summary?: string | null
  /** Text preview (first 200 chars) */
  preview?: string | null
  /** Content tags */
  tags: string[]
  /** Similarity score (0-1) */
  similarity: number
  /** Original source URL */
  source_url?: string | null
}

/**
 * Search response with results and metadata
 */
export interface SearchResponse {
  /** Matching content */
  results: SearchResult[]
  /** Original query */
  query: string
  /** Number of results returned */
  total: number
}

/**
 * Content type definitions with display metadata
 */
export const CONTENT_TYPES: Record<string, { label: string; icon: string; color: string }> = {
  youtube_video: { label: 'YouTube', icon: 'video', color: 'red' },
  document: { label: 'Document', icon: 'file', color: 'blue' },
  email: { label: 'Email', icon: 'mail', color: 'green' },
  note: { label: 'Note', icon: 'note', color: 'yellow' },
  webpage: { label: 'Webpage', icon: 'globe', color: 'purple' },
  unknown: { label: 'Content', icon: 'file', color: 'gray' },
}

/**
 * Get content type metadata with fallback
 */
export function getContentTypeMeta(type: string) {
  return CONTENT_TYPES[type] || CONTENT_TYPES.unknown
}
