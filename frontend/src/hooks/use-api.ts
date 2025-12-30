'use client'

import { useQuery, useMutation, useQueryClient, type UseQueryOptions } from '@tanstack/react-query'
import { api, type APIResponse } from '@/lib/api'

/**
 * Generic hook for fetching data with React Query
 */
export function useApiQuery<T>(
  key: string | string[],
  url: string,
  options?: Omit<UseQueryOptions<T>, 'queryKey' | 'queryFn'>
) {
  const queryKey = Array.isArray(key) ? key : [key]

  return useQuery<T>({
    queryKey,
    queryFn: async () => {
      const response = await api.get<APIResponse<T>>(url)
      if (!response.data.success) {
        throw new Error(response.data.error || 'Request failed')
      }
      return response.data.data as T
    },
    ...options,
  })
}

/**
 * Generic hook for mutations with React Query
 */
export function useApiMutation<TData, TVariables = unknown>(
  url: string,
  options?: {
    method?: 'POST' | 'PUT' | 'DELETE'
    invalidateKeys?: string[][]
    onSuccess?: (data: TData) => void
    onError?: (error: Error) => void
  }
) {
  const queryClient = useQueryClient()
  const method = options?.method || 'POST'

  return useMutation<TData, Error, TVariables>({
    mutationFn: async (variables) => {
      const response = await api.request<APIResponse<TData>>({
        method,
        url,
        data: variables,
      })
      if (!response.data.success) {
        throw new Error(response.data.error || 'Request failed')
      }
      return response.data.data as TData
    },
    onSuccess: (data) => {
      // Invalidate specified query keys
      if (options?.invalidateKeys) {
        options.invalidateKeys.forEach((key) => {
          queryClient.invalidateQueries({ queryKey: key })
        })
      }
      options?.onSuccess?.(data)
    },
    onError: options?.onError,
  })
}

/**
 * Hook for health check
 */
export function useHealthCheck() {
  return useApiQuery<{
    overall_status: string
    services: Array<{
      name: string
      status: string
      uptime_percent: number
    }>
  }>(['health'], '/health/dashboard', {
    refetchInterval: 30000, // Refetch every 30 seconds
  })
}

/**
 * Hook for current user
 */
export function useCurrentUser() {
  return useApiQuery<{
    id: string
    email: string
    name: string
    workspaces: Array<{ id: string; name: string }>
  }>(['auth', 'me'], '/auth/me', {
    retry: false,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}
