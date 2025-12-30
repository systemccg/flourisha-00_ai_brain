/**
 * Search Request/Response Types
 * Mirrors the backend API models
 */

/**
 * Filter options for search
 */
export interface SearchFilters {
  /** Filter by content types */
  types?: string[]
  /** Filter by date range */
  dateRange?: {
    start?: string // ISO date string
    end?: string   // ISO date string
  }
  /** Filter by source/origin */
  sources?: string[]
  /** Filter by tags */
  tags?: string[]
}

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
  /** Optional filters */
  filters?: SearchFilters
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
 * Source/origin definitions for content
 */
export const CONTENT_SOURCES: Record<string, { label: string; color: string }> = {
  youtube: { label: 'YouTube', color: 'red' },
  gmail: { label: 'Gmail', color: 'orange' },
  drive: { label: 'Google Drive', color: 'yellow' },
  obsidian: { label: 'Obsidian', color: 'purple' },
  manual: { label: 'Manual Upload', color: 'blue' },
  web: { label: 'Web Scrape', color: 'cyan' },
}

/**
 * Date range presets for filtering
 */
export const DATE_PRESETS = {
  today: { label: 'Today', days: 0 },
  week: { label: 'Past Week', days: 7 },
  month: { label: 'Past Month', days: 30 },
  quarter: { label: 'Past Quarter', days: 90 },
  year: { label: 'Past Year', days: 365 },
  all: { label: 'All Time', days: -1 },
} as const

export type DatePresetKey = keyof typeof DATE_PRESETS

/**
 * Get content type metadata with fallback
 */
export function getContentTypeMeta(type: string) {
  return CONTENT_TYPES[type] || CONTENT_TYPES.unknown
}

/**
 * Get source metadata with fallback
 */
export function getSourceMeta(source: string) {
  return CONTENT_SOURCES[source] || { label: source, color: 'gray' }
}

/**
 * Calculate date range from preset
 */
export function getDateRangeFromPreset(preset: DatePresetKey): { start?: string; end?: string } {
  const { days } = DATE_PRESETS[preset]
  if (days < 0) return {} // All time

  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - days)

  return {
    start: start.toISOString().split('T')[0],
    end: end.toISOString().split('T')[0],
  }
}
