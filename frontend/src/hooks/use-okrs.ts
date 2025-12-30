'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, APIResponse, endpoints } from '@/lib/api'
import type {
  OKRsResponse,
  Objective,
  KeyResult,
  OKRMeasurement,
  CreateOKRPayload,
  RecordMeasurementPayload,
  Quarter,
} from '@/lib/types/okr'
import { getCurrentQuarter } from '@/lib/types/okr'

/**
 * Query keys for OKR data
 */
export const okrKeys = {
  all: ['okrs'] as const,
  lists: () => [...okrKeys.all, 'list'] as const,
  list: (quarter: Quarter) => [...okrKeys.lists(), quarter] as const,
  details: () => [...okrKeys.all, 'detail'] as const,
  detail: (id: string) => [...okrKeys.details(), id] as const,
  measurements: (krId: string) => [...okrKeys.all, 'measurements', krId] as const,
}

/**
 * Fetch OKRs for a specific quarter
 */
async function fetchOKRs(quarter: Quarter): Promise<OKRsResponse> {
  const response = await api.get<APIResponse<OKRsResponse>>(endpoints.okrs.list, {
    params: { quarter },
  })

  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.error || 'Failed to fetch OKRs')
  }

  return response.data.data
}

/**
 * Fetch single objective details
 */
async function fetchObjective(id: string): Promise<Objective> {
  const response = await api.get<APIResponse<Objective>>(`${endpoints.okrs.list}/${id}`)

  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.error || 'Failed to fetch objective')
  }

  return response.data.data
}

/**
 * Fetch measurement history for a key result
 */
async function fetchMeasurements(krId: string): Promise<OKRMeasurement[]> {
  const response = await api.get<APIResponse<OKRMeasurement[]>>(
    `${endpoints.okrs.list}/kr/${krId}/measurements`
  )

  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.error || 'Failed to fetch measurements')
  }

  return response.data.data
}

/**
 * Create a new OKR (objective with key results)
 */
async function createOKR(payload: CreateOKRPayload): Promise<Objective> {
  const response = await api.post<APIResponse<Objective>>(endpoints.okrs.list, payload)

  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.error || 'Failed to create OKR')
  }

  return response.data.data
}

/**
 * Record a measurement for a key result
 */
async function recordMeasurement(payload: RecordMeasurementPayload): Promise<OKRMeasurement> {
  const response = await api.post<APIResponse<OKRMeasurement>>(endpoints.okrs.measure, payload)

  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.error || 'Failed to record measurement')
  }

  return response.data.data
}

/**
 * Update an objective
 */
async function updateObjective(
  id: string,
  updates: Partial<Pick<Objective, 'title' | 'description'>>
): Promise<Objective> {
  const response = await api.put<APIResponse<Objective>>(`${endpoints.okrs.list}/${id}`, updates)

  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.error || 'Failed to update objective')
  }

  return response.data.data
}

/**
 * Update a key result
 */
async function updateKeyResult(
  id: string,
  updates: Partial<Pick<KeyResult, 'title' | 'description' | 'target_value'>>
): Promise<KeyResult> {
  const response = await api.put<APIResponse<KeyResult>>(`${endpoints.okrs.list}/kr/${id}`, updates)

  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.error || 'Failed to update key result')
  }

  return response.data.data
}

/**
 * Hook for fetching OKRs by quarter
 */
export function useOKRs(quarter?: Quarter) {
  const effectiveQuarter = quarter || getCurrentQuarter()

  return useQuery({
    queryKey: okrKeys.list(effectiveQuarter),
    queryFn: () => fetchOKRs(effectiveQuarter),
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

/**
 * Hook for fetching single objective
 */
export function useObjective(id: string | null) {
  return useQuery({
    queryKey: okrKeys.detail(id || ''),
    queryFn: () => fetchObjective(id!),
    enabled: !!id,
    staleTime: 1000 * 60 * 5,
  })
}

/**
 * Hook for fetching measurement history
 */
export function useMeasurements(krId: string | null) {
  return useQuery({
    queryKey: okrKeys.measurements(krId || ''),
    queryFn: () => fetchMeasurements(krId!),
    enabled: !!krId,
    staleTime: 1000 * 60 * 5,
  })
}

/**
 * Hook for creating new OKRs
 */
export function useCreateOKR() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: createOKR,
    onSuccess: (data) => {
      // Invalidate the list for this quarter
      queryClient.invalidateQueries({ queryKey: okrKeys.list(data.quarter) })
    },
  })
}

/**
 * Hook for recording measurements
 */
export function useRecordMeasurement() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: recordMeasurement,
    onSuccess: (data) => {
      // Invalidate measurements for this KR
      queryClient.invalidateQueries({ queryKey: okrKeys.measurements(data.kr_id) })
      // Invalidate all OKR lists to update progress
      queryClient.invalidateQueries({ queryKey: okrKeys.lists() })
    },
  })
}

/**
 * Hook for updating objectives
 */
export function useUpdateObjective() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, updates }: { id: string; updates: Partial<Pick<Objective, 'title' | 'description'>> }) =>
      updateObjective(id, updates),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: okrKeys.detail(data.id) })
      queryClient.invalidateQueries({ queryKey: okrKeys.list(data.quarter) })
    },
  })
}

/**
 * Hook for updating key results
 */
export function useUpdateKeyResult() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      id,
      updates,
    }: {
      id: string
      updates: Partial<Pick<KeyResult, 'title' | 'description' | 'target_value'>>
    }) => updateKeyResult(id, updates),
    onSuccess: () => {
      // Invalidate all lists since we don't know the quarter
      queryClient.invalidateQueries({ queryKey: okrKeys.lists() })
    },
  })
}
