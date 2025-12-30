/**
 * PARA (Projects, Areas, Resources, Archives) Types
 * Represents the Flourisha folder structure
 */

/**
 * PARA category types
 */
export type PARACategory = 'projects' | 'areas' | 'resources' | 'archives'

/**
 * PARA category metadata
 */
export const PARA_CATEGORIES: Record<PARACategory, { label: string; icon: string; color: string; description: string; path: string }> = {
  projects: {
    label: 'Projects',
    icon: 'rocket',
    color: 'blue',
    description: 'Active projects with specific outcomes',
    path: '01f_Flourisha_Projects',
  },
  areas: {
    label: 'Areas',
    icon: 'layers',
    color: 'green',
    description: 'Ongoing responsibilities (health, business)',
    path: '02f_Flourisha_Areas',
  },
  resources: {
    label: 'Resources',
    icon: 'book',
    color: 'yellow',
    description: 'Reference materials and learning',
    path: '03f_Flourisha_Resources',
  },
  archives: {
    label: 'Archives',
    icon: 'archive',
    color: 'gray',
    description: 'Completed or inactive items',
    path: '04f_Flourisha_Archives',
  },
}

/**
 * File/folder item in PARA structure
 */
export interface PARAItem {
  /** Unique identifier (full path) */
  id: string
  /** Display name */
  name: string
  /** Full path relative to PARA root */
  path: string
  /** Whether this is a directory */
  isDirectory: boolean
  /** File extension if applicable */
  extension?: string
  /** File size in bytes */
  size?: number
  /** Last modified timestamp */
  modifiedAt?: string
  /** Created timestamp */
  createdAt?: string
  /** Child items (for directories) */
  children?: PARAItem[]
  /** Whether children have been loaded */
  childrenLoaded?: boolean
  /** Number of items in directory */
  itemCount?: number
}

/**
 * Browse request parameters
 */
export interface PARABrowseRequest {
  /** Path to browse (relative to PARA root) */
  path?: string
  /** Include nested children */
  recursive?: boolean
  /** Maximum depth for recursive */
  depth?: number
  /** Filter by file types */
  extensions?: string[]
  /** Include hidden files */
  includeHidden?: boolean
}

/**
 * Browse response
 */
export interface PARABrowseResponse {
  /** Current path */
  path: string
  /** Parent path (null if at root) */
  parent: string | null
  /** Items in current path */
  items: PARAItem[]
  /** Breadcrumb path segments */
  breadcrumbs: { name: string; path: string }[]
}

/**
 * Tree node state for UI
 */
export interface TreeNodeState {
  /** Is node expanded */
  isExpanded: boolean
  /** Is node selected */
  isSelected: boolean
  /** Is node loading children */
  isLoading: boolean
}

/**
 * Get PARA category from path
 */
export function getPARACategoryFromPath(path: string): PARACategory | null {
  const normalized = path.toLowerCase()
  if (normalized.includes('project')) return 'projects'
  if (normalized.includes('area')) return 'areas'
  if (normalized.includes('resource')) return 'resources'
  if (normalized.includes('archive')) return 'archives'
  return null
}

/**
 * Get icon for file type
 */
export function getFileIcon(extension?: string, isDirectory?: boolean): string {
  if (isDirectory) return 'folder'

  const ext = extension?.toLowerCase()
  switch (ext) {
    case 'md':
    case 'mdx':
      return 'markdown'
    case 'pdf':
      return 'file-pdf'
    case 'doc':
    case 'docx':
      return 'file-word'
    case 'xls':
    case 'xlsx':
      return 'file-excel'
    case 'ppt':
    case 'pptx':
      return 'file-powerpoint'
    case 'jpg':
    case 'jpeg':
    case 'png':
    case 'gif':
    case 'webp':
    case 'svg':
      return 'image'
    case 'mp4':
    case 'mov':
    case 'avi':
    case 'webm':
      return 'video'
    case 'mp3':
    case 'wav':
    case 'flac':
      return 'audio'
    case 'json':
      return 'file-json'
    case 'ts':
    case 'tsx':
    case 'js':
    case 'jsx':
      return 'file-code'
    case 'py':
      return 'file-python'
    case 'txt':
      return 'file-text'
    default:
      return 'file'
  }
}

/**
 * Format file size for display
 */
export function formatFileSize(bytes?: number): string {
  if (!bytes) return ''

  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }

  return `${size.toFixed(unitIndex > 0 ? 1 : 0)} ${units[unitIndex]}`
}
