'use client'

import { useState, useCallback, useRef, useEffect } from 'react'
import { useMutation } from '@tanstack/react-query'
import { api, type APIResponse, endpoints } from '@/lib/api'
import type { SearchRequest, SearchResponse, SearchResult, SearchFilters } from '@/lib/types'

/**
 * Debounce delay for search (ms)
 */
const SEARCH_DEBOUNCE = 300

/**
 * Minimum query length to trigger search
 */
const MIN_QUERY_LENGTH = 2

/**
 * Hook for unified search functionality
 * Provides debounced search with loading states and filters
 */
export function useSearch() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [filters, setFiltersState] = useState<SearchFilters>({})
  const debounceRef = useRef<NodeJS.Timeout | null>(null)

  // Search mutation
  const mutation = useMutation({
    mutationFn: async (searchRequest: SearchRequest): Promise<SearchResponse> => {
      const response = await api.post<APIResponse<SearchResponse>>(
        endpoints.search,
        searchRequest
      )
      if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error || 'Search failed')
      }
      return response.data.data
    },
    onSuccess: (data) => {
      setResults(data.results)
    },
    onError: () => {
      setResults([])
    },
  })

  // Debounced search handler
  const debouncedSearch = useCallback(
    (searchQuery: string, currentFilters: SearchFilters, options?: Partial<SearchRequest>) => {
      // Clear existing timeout
      if (debounceRef.current) {
        clearTimeout(debounceRef.current)
      }

      // Don't search if query is too short
      if (searchQuery.length < MIN_QUERY_LENGTH) {
        setResults([])
        return
      }

      // Set debounce timeout
      debounceRef.current = setTimeout(() => {
        mutation.mutate({
          query: searchQuery,
          limit: options?.limit ?? 10,
          threshold: options?.threshold ?? 0.7,
          filters: hasActiveFilters(currentFilters) ? currentFilters : undefined,
        })
      }, SEARCH_DEBOUNCE)
    },
    [mutation]
  )

  // Handle query change
  const handleQueryChange = useCallback(
    (newQuery: string, options?: Partial<SearchRequest>) => {
      setQuery(newQuery)
      debouncedSearch(newQuery, filters, options)
    },
    [debouncedSearch, filters]
  )

  // Handle filter change
  const handleFiltersChange = useCallback(
    (newFilters: SearchFilters) => {
      setFiltersState(newFilters)
      // Re-search with new filters if there's a query
      if (query.length >= MIN_QUERY_LENGTH) {
        debouncedSearch(query, newFilters)
      }
    },
    [debouncedSearch, query]
  )

  // Remove a specific filter
  const removeFilter = useCallback(
    (filterType: 'type' | 'source' | 'date', value?: string) => {
      const newFilters = { ...filters }

      switch (filterType) {
        case 'type':
          if (value && filters.types) {
            newFilters.types = filters.types.filter((t) => t !== value)
            if (newFilters.types.length === 0) delete newFilters.types
          }
          break
        case 'source':
          if (value && filters.sources) {
            newFilters.sources = filters.sources.filter((s) => s !== value)
            if (newFilters.sources.length === 0) delete newFilters.sources
          }
          break
        case 'date':
          delete newFilters.dateRange
          break
      }

      handleFiltersChange(newFilters)
    },
    [filters, handleFiltersChange]
  )

  // Immediate search (no debounce)
  const searchNow = useCallback(
    (searchQuery: string, options?: Partial<SearchRequest>) => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current)
      }

      if (searchQuery.length < MIN_QUERY_LENGTH) {
        setResults([])
        return
      }

      mutation.mutate({
        query: searchQuery,
        limit: options?.limit ?? 10,
        threshold: options?.threshold ?? 0.7,
        filters: hasActiveFilters(filters) ? filters : undefined,
      })
    },
    [mutation, filters]
  )

  // Clear search
  const clearSearch = useCallback(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current)
    }
    setQuery('')
    setResults([])
    mutation.reset()
  }, [mutation])

  // Clear filters
  const clearFilters = useCallback(() => {
    setFiltersState({})
    // Re-search without filters if there's a query
    if (query.length >= MIN_QUERY_LENGTH) {
      debouncedSearch(query, {})
    }
  }, [debouncedSearch, query])

  // Clear everything
  const clearAll = useCallback(() => {
    clearSearch()
    clearFilters()
  }, [clearSearch, clearFilters])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current)
      }
    }
  }, [])

  return {
    /** Current search query */
    query,
    /** Search results */
    results,
    /** Current filters */
    filters,
    /** Whether search is in progress */
    isLoading: mutation.isPending,
    /** Search error if any */
    error: mutation.error,
    /** Set query and trigger debounced search */
    setQuery: handleQueryChange,
    /** Set filters and trigger re-search */
    setFilters: handleFiltersChange,
    /** Remove a specific filter */
    removeFilter,
    /** Trigger immediate search */
    searchNow,
    /** Clear search state */
    clearSearch,
    /** Clear all filters */
    clearFilters,
    /** Clear everything */
    clearAll,
    /** Raw mutation object for advanced usage */
    mutation,
  }
}

/**
 * Check if there are any active filters
 */
function hasActiveFilters(filters: SearchFilters): boolean {
  return (
    (filters.types?.length || 0) > 0 ||
    (filters.sources?.length || 0) > 0 ||
    !!filters.dateRange?.start ||
    (filters.tags?.length || 0) > 0
  )
}

/**
 * Hook for managing search modal/command palette state
 */
export function useSearchModal() {
  const [isOpen, setIsOpen] = useState(false)

  const open = useCallback(() => setIsOpen(true), [])
  const close = useCallback(() => setIsOpen(false), [])
  const toggle = useCallback(() => setIsOpen((prev) => !prev), [])

  // Handle keyboard shortcut (Cmd/Ctrl + K)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        toggle()
      }
      if (e.key === 'Escape' && isOpen) {
        close()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, toggle, close])

  return {
    isOpen,
    open,
    close,
    toggle,
  }
}
