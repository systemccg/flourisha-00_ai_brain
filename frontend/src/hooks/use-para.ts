'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useCallback, useState } from 'react'
import { api, type APIResponse, endpoints } from '@/lib/api'
import type {
  PARAItem,
  PARACategory,
  PARABrowseRequest,
  PARABrowseResponse,
  PARA_CATEGORIES,
} from '@/lib/types'

/**
 * Query key factory for PARA
 */
const paraKeys = {
  all: ['para'] as const,
  browse: (path?: string) => [...paraKeys.all, 'browse', path ?? 'root'] as const,
  categories: () => [...paraKeys.all, 'categories'] as const,
}

/**
 * Hook for browsing PARA structure
 */
export function usePARABrowse(path?: string, options?: Partial<PARABrowseRequest>) {
  return useQuery({
    queryKey: paraKeys.browse(path),
    queryFn: async (): Promise<PARABrowseResponse> => {
      const params = new URLSearchParams()
      if (path) params.append('path', path)
      if (options?.recursive) params.append('recursive', 'true')
      if (options?.depth) params.append('depth', String(options.depth))
      if (options?.extensions) params.append('extensions', options.extensions.join(','))
      if (options?.includeHidden) params.append('includeHidden', 'true')

      const queryString = params.toString()
      const url = `${endpoints.para.browse}${queryString ? `?${queryString}` : ''}`

      const response = await api.get<APIResponse<PARABrowseResponse>>(url)
      if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error || 'Failed to browse PARA')
      }
      return response.data.data
    },
    staleTime: 30000, // 30 seconds
  })
}

/**
 * Hook for loading all PARA categories at once
 */
export function usePARACategories() {
  return useQuery({
    queryKey: paraKeys.categories(),
    queryFn: async (): Promise<Record<PARACategory, PARAItem[]>> => {
      // Fetch root of each category
      const categories: PARACategory[] = ['projects', 'areas', 'resources', 'archives']

      const responses = await Promise.all(
        categories.map(async (category) => {
          try {
            const categoryPath = getCategoryPath(category)
            const response = await api.get<APIResponse<PARABrowseResponse>>(
              `${endpoints.para.browse}?path=${encodeURIComponent(categoryPath)}`
            )
            if (response.data.success && response.data.data) {
              return { category, items: response.data.data.items }
            }
            return { category, items: [] }
          } catch {
            return { category, items: [] }
          }
        })
      )

      const result: Record<PARACategory, PARAItem[]> = {
        projects: [],
        areas: [],
        resources: [],
        archives: [],
      }

      for (const { category, items } of responses) {
        result[category] = items
      }

      return result
    },
    staleTime: 60000, // 1 minute
  })
}

/**
 * Get the actual folder path for a PARA category
 */
function getCategoryPath(category: PARACategory): string {
  const paths: Record<PARACategory, string> = {
    projects: '01f_Flourisha_Projects',
    areas: '02f_Flourisha_Areas',
    resources: '03f_Flourisha_Resources',
    archives: '04f_Flourisha_Archives',
  }
  return paths[category]
}

/**
 * Hook for lazy loading folder children
 */
export function usePARALazyLoad() {
  const queryClient = useQueryClient()

  const loadChildren = useCallback(
    async (path: string): Promise<PARAItem[]> => {
      // Check cache first
      const cached = queryClient.getQueryData<PARABrowseResponse>(paraKeys.browse(path))
      if (cached) {
        return cached.items
      }

      // Fetch from API
      const response = await api.get<APIResponse<PARABrowseResponse>>(
        `${endpoints.para.browse}?path=${encodeURIComponent(path)}`
      )

      if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error || 'Failed to load folder')
      }

      // Cache the result
      queryClient.setQueryData(paraKeys.browse(path), response.data.data)

      return response.data.data.items
    },
    [queryClient]
  )

  return { loadChildren }
}

/**
 * Hook for PARA folder navigation with breadcrumbs
 */
export function usePARANavigation(initialPath?: string) {
  const [currentPath, setCurrentPath] = useState(initialPath ?? '')
  const { data, isLoading, error, refetch } = usePARABrowse(currentPath)

  const navigate = useCallback((path: string) => {
    setCurrentPath(path)
  }, [])

  const navigateUp = useCallback(() => {
    if (data?.parent) {
      setCurrentPath(data.parent)
    } else {
      setCurrentPath('')
    }
  }, [data?.parent])

  const navigateToRoot = useCallback(() => {
    setCurrentPath('')
  }, [])

  const navigateToBreadcrumb = useCallback((index: number) => {
    if (data?.breadcrumbs && index < data.breadcrumbs.length) {
      setCurrentPath(data.breadcrumbs[index].path)
    }
  }, [data?.breadcrumbs])

  return {
    currentPath,
    items: data?.items ?? [],
    breadcrumbs: data?.breadcrumbs ?? [],
    parent: data?.parent ?? null,
    isLoading,
    error,
    navigate,
    navigateUp,
    navigateToRoot,
    navigateToBreadcrumb,
    refresh: refetch,
  }
}

/**
 * Hook for managing selected item state
 */
export function usePARASelection() {
  const [selectedItem, setSelectedItem] = useState<PARAItem | null>(null)
  const [selectedPath, setSelectedPath] = useState<string | null>(null)

  const select = useCallback((item: PARAItem) => {
    setSelectedItem(item)
    setSelectedPath(item.path)
  }, [])

  const clear = useCallback(() => {
    setSelectedItem(null)
    setSelectedPath(null)
  }, [])

  return {
    selectedItem,
    selectedPath,
    select,
    clear,
  }
}
